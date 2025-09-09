"""Description page for the Global Welfare Dashboard."""

import streamlit as st
from components.styling import apply_global_styling, create_feature_card
from constants import (
    PAGE_TITLES,
    DESCRIPTION_CONTENT,
    BUTTON_LABELS
)

def show_description():
    """Render the description page."""
    st.set_page_config(page_title=PAGE_TITLES['description'], layout="wide")
    apply_global_styling()
    
    # Header Section
    st.title(DESCRIPTION_CONTENT['title'])
    st.subheader(DESCRIPTION_CONTENT['subtitle'])
    
    # Columns Layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Project Overview
        st.markdown(f"""
        ## {DESCRIPTION_CONTENT['about_title']}
        {DESCRIPTION_CONTENT['about_text']}
        
        {chr(10).join(f"- **{feature}**" for feature in DESCRIPTION_CONTENT['features'])}
        """)
        
        # Features Section
        st.markdown(f"""
        ## {DESCRIPTION_CONTENT['key_features_title']}
        {chr(10).join(f"- **{feature}**" for feature in DESCRIPTION_CONTENT['key_features'])}
        """)
        
    with col2:
        # Stats Section
        st.markdown(f"""
        ## {DESCRIPTION_CONTENT['metrics_title']}
        {chr(10).join(f"- **{metric}**" for metric in DESCRIPTION_CONTENT['metrics'])}
        """)
        
        # Additional Information
        st.markdown(create_feature_card(
            DESCRIPTION_CONTENT['mission']['title'],
            DESCRIPTION_CONTENT['mission']['text']
        ), unsafe_allow_html=True)
    
    # Call to Action
    st.markdown(f"""
    ## {DESCRIPTION_CONTENT['cta_title']}
    {DESCRIPTION_CONTENT['cta_text']}
    """)
    
    if st.button(BUTTON_LABELS['get_started'], key="start_analysis"):
        st.switch_page("pages/Data_Analytic.py")

if __name__ == "__main__":
    show_description()
