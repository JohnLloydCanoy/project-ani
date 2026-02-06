"""
API Key Manager for Project A.N.I.
Provides:
- Multiple API key rotation
- Rate limit monitoring
- Usage alerts before quota exceeded
- Per-key usage tracking
"""

import streamlit as st
import google.generativeai as genai
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple
import time
import threading
from dataclasses import dataclass, field
from collections import deque


# ============================================================================
# CONFIGURATION
# ============================================================================

@dataclass
class APIKeyConfig:
    """Configuration for API key limits."""
    # Gemini API limits (adjust based on your plan)
    REQUESTS_PER_MINUTE: int = 60  # RPM limit
    REQUESTS_PER_DAY: int = 1500   # Daily limit for free tier
    TOKENS_PER_MINUTE: int = 32000  # TPM limit
    
    # Alert thresholds (percentage of limit)
    WARNING_THRESHOLD: float = 0.7   # 70% - show warning
    CRITICAL_THRESHOLD: float = 0.9  # 90% - show critical alert
    
    # Rotation settings
    COOLDOWN_MINUTES: int = 1  # Cooldown after hitting rate limit
    AUTO_ROTATE_ON_LIMIT: bool = True  # Automatically switch keys


@dataclass
class APIKeyStats:
    """Statistics for a single API key."""
    key_id: str  # Last 4 chars of key for identification
    requests_minute: deque = field(default_factory=lambda: deque(maxlen=100))
    requests_day: deque = field(default_factory=lambda: deque(maxlen=2000))
    total_requests: int = 0
    total_tokens: int = 0
    errors: int = 0
    last_used: Optional[datetime] = None
    last_error: Optional[str] = None
    is_rate_limited: bool = False
    rate_limit_until: Optional[datetime] = None
    
    def add_request(self, tokens_used: int = 0):
        """Record a new request."""
        now = datetime.now()
        self.requests_minute.append(now)
        self.requests_day.append(now)
        self.total_requests += 1
        self.total_tokens += tokens_used
        self.last_used = now
    
    def get_rpm(self) -> int:
        """Get requests in the last minute."""
        cutoff = datetime.now() - timedelta(minutes=1)
        return sum(1 for t in self.requests_minute if t > cutoff)
    
    def get_daily_requests(self) -> int:
        """Get requests in the last 24 hours."""
        cutoff = datetime.now() - timedelta(hours=24)
        return sum(1 for t in self.requests_day if t > cutoff)
    
    def mark_rate_limited(self, cooldown_minutes: int = 1):
        """Mark key as rate limited."""
        self.is_rate_limited = True
        self.rate_limit_until = datetime.now() + timedelta(minutes=cooldown_minutes)
        self.errors += 1
    
    def check_rate_limit_expired(self) -> bool:
        """Check if rate limit cooldown has expired."""
        if not self.is_rate_limited:
            return True
        if self.rate_limit_until and datetime.now() > self.rate_limit_until:
            self.is_rate_limited = False
            self.rate_limit_until = None
            return True
        return False


# ============================================================================
# API KEY MANAGER
# ============================================================================

class APIKeyManager:
    """
    Manages multiple API keys with rotation, rate limiting, and usage tracking.
    Singleton pattern - only one instance per app.
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.config = APIKeyConfig()
        self.keys: List[str] = []
        self.key_stats: Dict[str, APIKeyStats] = {}
        self.current_key_index: int = 0
        self.alerts: List[Dict] = []
        self._initialized = True
        
        # Load keys from secrets
        self._load_keys()
    
    def _load_keys(self):
        """Load API keys from Streamlit secrets."""
        try:
            # Support multiple keys: GEMINI_API_KEY, GEMINI_API_KEY_2, etc.
            if "GEMINI_API_KEY" in st.secrets:
                self.keys.append(st.secrets["GEMINI_API_KEY"])
            
            # Check for additional keys
            for i in range(2, 11):  # Support up to 10 keys
                key_name = f"GEMINI_API_KEY_{i}"
                if key_name in st.secrets:
                    self.keys.append(st.secrets[key_name])
            
            # Initialize stats for each key
            for key in self.keys:
                key_id = key[-4:] if len(key) >= 4 else key
                self.key_stats[key] = APIKeyStats(key_id=key_id)
            
            if not self.keys:
                st.error("❌ No GEMINI_API_KEY found in secrets!")
                
        except Exception as e:
            st.error(f"❌ Error loading API keys: {e}")
    
    def get_current_key(self) -> Optional[str]:
        """Get the current active API key."""
        if not self.keys:
            return None
        
        # Check if current key needs rotation
        current_key = self.keys[self.current_key_index]
        stats = self.key_stats.get(current_key)
        
        if stats and self.config.AUTO_ROTATE_ON_LIMIT:
            # Rotate if rate limited
            if stats.is_rate_limited and not stats.check_rate_limit_expired():
                self._rotate_key("rate_limit")
                current_key = self.keys[self.current_key_index]
            
            # Rotate if approaching limits
            elif stats.get_rpm() >= self.config.REQUESTS_PER_MINUTE * self.config.CRITICAL_THRESHOLD:
                self._rotate_key("rpm_critical")
                current_key = self.keys[self.current_key_index]
        
        return current_key
    
    def _rotate_key(self, reason: str = "manual") -> bool:
        """Rotate to the next available API key."""
        if len(self.keys) <= 1:
            return False
        
        original_index = self.current_key_index
        attempts = 0
        
        while attempts < len(self.keys):
            self.current_key_index = (self.current_key_index + 1) % len(self.keys)
            next_key = self.keys[self.current_key_index]
            stats = self.key_stats.get(next_key)
            
            # Check if this key is usable
            if stats and stats.check_rate_limit_expired():
                self._add_alert("info", f"🔄 Rotated API key (reason: {reason})")
                return True
            
            attempts += 1
        
        # All keys are rate limited
        self.current_key_index = original_index
        self._add_alert("error", "⚠️ All API keys are rate limited!")
        return False
    
    def record_request(self, tokens_used: int = 0, success: bool = True, error_msg: str = None):
        """Record an API request."""
        current_key = self.keys[self.current_key_index] if self.keys else None
        if not current_key:
            return
        
        stats = self.key_stats.get(current_key)
        if not stats:
            return
        
        if success:
            stats.add_request(tokens_used)
            self._check_thresholds(stats)
        else:
            stats.errors += 1
            stats.last_error = error_msg
            
            # Check for rate limit errors
            if error_msg and ("rate" in error_msg.lower() or "quota" in error_msg.lower()):
                stats.mark_rate_limited(self.config.COOLDOWN_MINUTES)
                if self.config.AUTO_ROTATE_ON_LIMIT:
                    self._rotate_key("error_rate_limit")
    
    def _check_thresholds(self, stats: APIKeyStats):
        """Check if usage thresholds are exceeded and create alerts."""
        rpm = stats.get_rpm()
        daily = stats.get_daily_requests()
        
        # RPM checks
        rpm_pct = rpm / self.config.REQUESTS_PER_MINUTE
        if rpm_pct >= self.config.CRITICAL_THRESHOLD:
            self._add_alert("error", f"🔴 CRITICAL: {rpm_pct*100:.0f}% of RPM limit reached!")
        elif rpm_pct >= self.config.WARNING_THRESHOLD:
            self._add_alert("warning", f"⚠️ Warning: {rpm_pct*100:.0f}% of RPM limit reached")
        
        # Daily checks
        daily_pct = daily / self.config.REQUESTS_PER_DAY
        if daily_pct >= self.config.CRITICAL_THRESHOLD:
            self._add_alert("error", f"🔴 CRITICAL: {daily_pct*100:.0f}% of daily quota used!")
        elif daily_pct >= self.config.WARNING_THRESHOLD:
            self._add_alert("warning", f"⚠️ Warning: {daily_pct*100:.0f}% of daily quota used")
    
    def _add_alert(self, level: str, message: str):
        """Add an alert (prevents duplicates within 1 minute)."""
        now = datetime.now()
        
        # Check for recent duplicate
        for alert in self.alerts[-10:]:
            if alert["message"] == message:
                if (now - alert["time"]).seconds < 60:
                    return
        
        self.alerts.append({
            "level": level,
            "message": message,
            "time": now
        })
        
        # Keep only last 50 alerts
        if len(self.alerts) > 50:
            self.alerts = self.alerts[-50:]
    
    def get_usage_stats(self) -> Dict:
        """Get current usage statistics."""
        stats_list = []
        
        for i, key in enumerate(self.keys):
            stats = self.key_stats.get(key)
            if stats:
                stats_list.append({
                    "key_id": f"Key #{i+1} (***{stats.key_id})",
                    "is_active": i == self.current_key_index,
                    "rpm": stats.get_rpm(),
                    "rpm_limit": self.config.REQUESTS_PER_MINUTE,
                    "rpm_pct": (stats.get_rpm() / self.config.REQUESTS_PER_MINUTE) * 100,
                    "daily": stats.get_daily_requests(),
                    "daily_limit": self.config.REQUESTS_PER_DAY,
                    "daily_pct": (stats.get_daily_requests() / self.config.REQUESTS_PER_DAY) * 100,
                    "total_requests": stats.total_requests,
                    "errors": stats.errors,
                    "is_rate_limited": stats.is_rate_limited,
                    "last_used": stats.last_used.strftime("%H:%M:%S") if stats.last_used else "Never"
                })
        
        return {
            "keys": stats_list,
            "total_keys": len(self.keys),
            "active_key_index": self.current_key_index,
            "alerts": self.alerts[-5:]  # Last 5 alerts
        }
    
    def get_recent_alerts(self) -> List[Dict]:
        """Get recent alerts for display."""
        return self.alerts[-5:]
    
    def configure_genai(self) -> bool:
        """Configure google.generativeai with the current key."""
        key = self.get_current_key()
        if key:
            genai.configure(api_key=key)
            return True
        return False
    
    def force_rotate(self) -> bool:
        """Manually force key rotation."""
        return self._rotate_key("manual")


# ============================================================================
# STREAMLIT UI COMPONENTS
# ============================================================================

def render_api_usage_sidebar():
    """Render API usage stats in sidebar."""
    manager = APIKeyManager()
    stats = manager.get_usage_stats()
    
    with st.sidebar:
        with st.expander("📊 API Usage", expanded=False):
            # Show active key
            if stats["keys"]:
                active = next((k for k in stats["keys"] if k["is_active"]), None)
                if active:
                    # RPM gauge
                    st.markdown(f"**🔑 Active:** {active['key_id']}")
                    
                    # RPM progress
                    rpm_color = "normal" if active["rpm_pct"] < 70 else "warning" if active["rpm_pct"] < 90 else "error"
                    st.progress(min(active["rpm_pct"] / 100, 1.0), text=f"RPM: {active['rpm']}/{active['rpm_limit']}")
                    
                    # Daily progress
                    st.progress(min(active["daily_pct"] / 100, 1.0), text=f"Daily: {active['daily']}/{active['daily_limit']}")
                    
                    # Stats
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Total", active["total_requests"])
                    with col2:
                        st.metric("Errors", active["errors"])
                
                # Multi-key info
                if stats["total_keys"] > 1:
                    st.caption(f"📦 {stats['total_keys']} API keys configured")
                    if st.button("🔄 Rotate Key", key="rotate_key_btn"):
                        if manager.force_rotate():
                            st.success("Key rotated!")
                            st.rerun()
                        else:
                            st.error("No available keys to rotate to")
            
            # Show alerts
            alerts = manager.get_recent_alerts()
            if alerts:
                st.markdown("**Recent Alerts:**")
                for alert in reversed(alerts[-3:]):
                    if alert["level"] == "error":
                        st.error(alert["message"])
                    elif alert["level"] == "warning":
                        st.warning(alert["message"])
                    else:
                        st.info(alert["message"])


def render_api_usage_dashboard():
    """Render detailed API usage dashboard (for admin page)."""
    manager = APIKeyManager()
    stats = manager.get_usage_stats()
    
    st.markdown("### 📊 API Key Usage Dashboard")
    
    if not stats["keys"]:
        st.error("No API keys configured!")
        return
    
    # Overview metrics
    col1, col2, col3, col4 = st.columns(4)
    
    total_requests = sum(k["total_requests"] for k in stats["keys"])
    total_errors = sum(k["errors"] for k in stats["keys"])
    
    with col1:
        st.metric("🔑 Total Keys", stats["total_keys"])
    with col2:
        st.metric("📤 Total Requests", total_requests)
    with col3:
        st.metric("❌ Total Errors", total_errors)
    with col4:
        active_key = stats["keys"][stats["active_key_index"]] if stats["keys"] else None
        st.metric("⚡ Active Key", f"#{stats['active_key_index'] + 1}" if active_key else "None")
    
    st.divider()
    
    # Per-key details
    st.markdown("#### 🔐 API Key Status")
    
    for key_stat in stats["keys"]:
        with st.container():
            is_active = "🟢" if key_stat["is_active"] else "⚪"
            is_limited = "🔴 RATE LIMITED" if key_stat["is_rate_limited"] else ""
            
            st.markdown(f"**{is_active} {key_stat['key_id']}** {is_limited}")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                rpm_pct = key_stat["rpm_pct"]
                rpm_status = "🟢" if rpm_pct < 70 else "🟡" if rpm_pct < 90 else "🔴"
                st.progress(min(rpm_pct / 100, 1.0))
                st.caption(f"{rpm_status} RPM: {key_stat['rpm']}/{key_stat['rpm_limit']} ({rpm_pct:.1f}%)")
            
            with col2:
                daily_pct = key_stat["daily_pct"]
                daily_status = "🟢" if daily_pct < 70 else "🟡" if daily_pct < 90 else "🔴"
                st.progress(min(daily_pct / 100, 1.0))
                st.caption(f"{daily_status} Daily: {key_stat['daily']}/{key_stat['daily_limit']} ({daily_pct:.1f}%)")
            
            with col3:
                st.caption(f"📊 Total: {key_stat['total_requests']}")
                st.caption(f"❌ Errors: {key_stat['errors']}")
                st.caption(f"🕐 Last: {key_stat['last_used']}")
            
            st.divider()
    
    # Recent alerts
    st.markdown("#### ⚠️ Recent Alerts")
    alerts = manager.get_recent_alerts()
    
    if alerts:
        for alert in reversed(alerts):
            time_str = alert["time"].strftime("%H:%M:%S")
            if alert["level"] == "error":
                st.error(f"[{time_str}] {alert['message']}")
            elif alert["level"] == "warning":
                st.warning(f"[{time_str}] {alert['message']}")
            else:
                st.info(f"[{time_str}] {alert['message']}")
    else:
        st.success("✅ No alerts - all systems normal!")
    
    # Manual controls
    st.markdown("#### 🎮 Manual Controls")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Force Key Rotation", use_container_width=True):
            if manager.force_rotate():
                st.success("Successfully rotated to next key!")
                st.rerun()
            else:
                st.error("Failed to rotate - no available keys")
    
    with col2:
        if st.button("🧹 Clear Alerts", use_container_width=True):
            manager.alerts.clear()
            st.success("Alerts cleared!")
            st.rerun()


# ============================================================================
# DECORATOR FOR API CALLS
# ============================================================================

def track_api_call(func):
    """
    Decorator to track API calls and handle rate limiting.
    
    Usage:
        @track_api_call
        def my_gemini_function(prompt):
            response = model.generate_content(prompt)
            return response
    """
    def wrapper(*args, **kwargs):
        manager = APIKeyManager()
        manager.configure_genai()
        
        try:
            result = func(*args, **kwargs)
            
            # Estimate tokens (rough estimate based on response length)
            tokens = 0
            if hasattr(result, 'text'):
                tokens = len(result.text) // 4  # Rough estimate
            
            manager.record_request(tokens_used=tokens, success=True)
            return result
            
        except Exception as e:
            error_msg = str(e)
            manager.record_request(success=False, error_msg=error_msg)
            raise
    
    return wrapper


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_api_key() -> Optional[str]:
    """Get the current active API key (replaces old get_api_key function)."""
    manager = APIKeyManager()
    return manager.get_current_key()


def init_api_manager():
    """Initialize the API manager and configure genai."""
    manager = APIKeyManager()
    manager.configure_genai()
    return manager


def check_api_health() -> Tuple[bool, str]:
    """Check if API is healthy and has quota remaining."""
    manager = APIKeyManager()
    stats = manager.get_usage_stats()
    
    if not stats["keys"]:
        return False, "No API keys configured"
    
    active = next((k for k in stats["keys"] if k["is_active"]), None)
    if not active:
        return False, "No active API key"
    
    if active["is_rate_limited"]:
        return False, "Current key is rate limited"
    
    if active["daily_pct"] >= 95:
        return False, "Daily quota nearly exhausted"
    
    if active["rpm_pct"] >= 95:
        return False, "RPM limit nearly reached"
    
    return True, "API healthy"
