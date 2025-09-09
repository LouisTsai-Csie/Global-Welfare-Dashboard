"""Home page for the Global Welfare Dashboard."""

import streamlit as st
from components.styling import apply_global_styling, create_feature_card
from constants import (
    PAGE_TITLES,
    FEATURES,
    DESCRIPTION_CONTENT,
    BUTTON_LABELS
)

def home():
    """Render the home page."""
    apply_global_styling()

    # Main content
    st.markdown(f'<div class="title">{PAGE_TITLES["home"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="subtitle">{DESCRIPTION_CONTENT["subtitle"]}</div>', unsafe_allow_html=True)

    # Feature cards
    with st.container():
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(create_feature_card(
                FEATURES['multi_country']['title'],
                FEATURES['multi_country']['description']
            ), unsafe_allow_html=True)
        
        with col2:
            st.markdown(create_feature_card(
                FEATURES['data_viz']['title'],
                FEATURES['data_viz']['description']
            ), unsafe_allow_html=True)
        
        with col3:
            st.markdown(create_feature_card(
                FEATURES['detailed_comp']['title'],
                FEATURES['detailed_comp']['description']
            ), unsafe_allow_html=True)

    # Call to action
    st.markdown(f"""
    <div style="text-align: center; margin-top: 2rem;">
        <h2 style="color: #FFFFFF;">{DESCRIPTION_CONTENT['cta_title']}</h2>
        <p style="color: #D1D5DB;">{DESCRIPTION_CONTENT['cta_text']}</p>
    </div>
    """, unsafe_allow_html=True)

    if st.button(BUTTON_LABELS['get_started'], key='start_button'):
        st.switch_page("pages/Data_Analytic.py")

if __name__ == '__main__':
    home()