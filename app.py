import streamlit as st
from pages.home import dashboard_view
from config.app_config import app_config

app_config()
dashboard_view()