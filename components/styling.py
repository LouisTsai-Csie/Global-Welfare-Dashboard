"""Shared styling components for the Global Welfare Dashboard."""

import streamlit as st
from constants import STYLES, COLORS

def apply_global_styling():
    """Apply global styling to the Streamlit app."""
    st.markdown("""
    <style>
        {app}
        {title}
        {subtitle}
        {card}
        {button}
    </style>
    """.format(
        app=STYLES['app'],
        title=STYLES['title'],
        subtitle=STYLES['subtitle'],
        card=STYLES['card'],
        button=STYLES['button']
    ), unsafe_allow_html=True)

def create_feature_card(title: str, description: str) -> str:
    """Create a feature card with consistent styling."""
    return f"""
    <div class="card">
        <h3>{title}</h3>
        <p>{description}</p>
    </div>
    """ 