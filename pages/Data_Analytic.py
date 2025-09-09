"""Data Analytics page for the Global Welfare Dashboard."""

import streamlit as st
import pandas as pd
import numpy as np
import time
from components.styling import apply_global_styling
from components.data_handler import load_sheet_data, process_data
from components.ui_components import (
    create_selection_fields,
    display_selections
)
from constants import (
    PAGE_TITLES,
    BUTTON_LABELS,
    MESSAGES,
    NUMERIC_COLUMNS,
    SHEET_URLS,
    INCOME_CASE,
    FAMILY_CASES,
    INCOME_GENDER,
    CASES
)

from auth import authenticate

# Load exchange rate data
@st.cache_data
def load_exchange_rates():
    """Load exchange rate data from CSV file."""
    try:
        df = pd.read_csv('exchange_rate.csv')
        return df
    except FileNotFoundError:
        st.error("Exchange rate file not found: exchange_rate.csv")
        return None
    except Exception as e:
        st.error(f"Error loading exchange rate data: {e}")
        return None

def get_exchange_rate_options():
    """Get available exchange rate column options."""
    df = load_exchange_rates()
    if df is None:
        return []
    
    # Get columns that start with 'ppp' or 'ER_'
    rate_columns = [col for col in df.columns if col.startswith(('ppp', 'ER_'))]
    return rate_columns

def get_exchange_rate_for_country(country_code, rate_type):
    """Get exchange rate for a specific country and rate type."""
    df = load_exchange_rates()
    if df is None:
        return None
    
    # Find the country in the exchange rate data
    country_data = df[df['countrycode'] == country_code]
    if country_data.empty:
        return None
    
    # Get the exchange rate for the specified type
    rate = country_data[rate_type].iloc[0]
    
    # Handle missing values
    if pd.isna(rate) or rate == '':
        return None
    
    return float(rate)

def get_available_countries_with_rates():
    """Get list of countries available in exchange rate data."""
    df = load_exchange_rates()
    if df is None:
        return []
    
    return df[['countryname', 'countrycode']].dropna().to_dict('records')



# Add caching for expensive operations
@st.cache_data
def load_sheet_data():
    """Load data from Google Sheets and combine both worksheets."""
    try:
        sheet0 = authenticate(SHEET_URLS['sheet0'])
        sheet1 = authenticate(SHEET_URLS['sheet1'])
        workSheet0 = list(sheet0.worksheets())[0].get_all_values()
        workSheet1 = list(sheet1.worksheets())[0].get_all_values()
        
        # Skip headers and combine data
        combined_data = workSheet0[1:] + workSheet1[1:]
        
            
        return combined_data
    except Exception as e:
        st.error(f"Error loading Google Sheets data: {e}")
        return []

# Cache the processed data
@st.cache_data
def process_data(workSheet):
    countryList = set()
    for row in workSheet:
        if row[0]:
            countryList.add(row[0])
    return {
        'county': sorted(list(countryList)),
        'incomecase': sorted(list(set(row[2] for row in workSheet if row[2]))),
        'familytype': sorted(list(set(row[3] for row in workSheet if row[3]))),
        'incomegender': sorted(list(set(row[4] for row in workSheet if row[4]))),
        'case': sorted(list(set(row[5] for row in workSheet if row[5]))),
        'alternative': sorted(list(set(row[6] for row in workSheet if row[6])))
    }

# Use cached functions
workSheet = load_sheet_data()
data = process_data(workSheet)

def initialize_session_state():
    """Initialize session state variables."""
    if 'scenario1_selections' not in st.session_state:
        st.session_state['scenario1_selections'] = []
    if 'selected_to_delete' not in st.session_state:
        st.session_state['selected_to_delete'] = []
    if 'card_order' not in st.session_state:
        st.session_state['card_order'] = []

def get_all_combinations_for_countries(worksheet, selected_countries):
    """Get all possible combinations of parameters for the selected countries."""
    from itertools import product
    
    all_combinations = []
    
    for country in selected_countries:
        # Filter data for this country
        country_data = [row for row in worksheet if row[0] == country]
        
        if not country_data:
            continue
            
        # Get all unique values for each parameter for this country
        country_combinations = {
            'incomecase': sorted(list(set(row[2] for row in country_data if row[2]))),
            'familytype': sorted(list(set(row[3] for row in country_data if row[3]))),
            'incomegender': sorted(list(set(row[4] for row in country_data if row[4]))),
            'case': sorted(list(set(row[5] for row in country_data if row[5]))),
            'alternative': sorted(list(set(row[6] for row in country_data if row[6])))
        }
        
        # Generate all possible combinations for this country
        for combo in product(
            country_combinations['incomecase'],
            country_combinations['familytype'],
            country_combinations['incomegender'],
            country_combinations['case'],
            country_combinations['alternative']
        ):
            # Verify this combination actually exists in the data
            combo_exists = any(
                row[0] == country and
                str(row[2]) == str(combo[0]) and
                str(row[3]) == str(combo[1]) and
                str(row[4]) == str(combo[2]) and
                str(row[5]) == str(combo[3]) and
                str(row[6]) == str(combo[4])
                for row in country_data
            )
            
            if combo_exists:
                all_combinations.append({
                    'country': country,
                    'incomecase': str(combo[0]),
                    'familytype': str(combo[1]),
                    'incomegender': str(combo[2]),
                    'case': str(combo[3]),
                    'alternative': str(combo[4])
                })
    
    return all_combinations

def import_all_cases_for_countries(selection: dict, scenario_num: int) -> None:
    """Import all possible case combinations for selected countries."""
    if not selection:
        st.warning("No valid selection to import.")
        return
    
    # Get selected countries
    if selection.get('multiple_countries', False):
        countries = selection.get('countries', [])
    else:
        countries = [selection.get('country')]
    
    if not countries or countries == [None]:
        st.warning("No countries selected.")
        return
    
    # Get all combinations for selected countries
    worksheet = load_sheet_data()
    all_combinations = get_all_combinations_for_countries(worksheet, countries)
    
    if not all_combinations:
        st.warning("No valid combinations found for the selected countries.")
        return
    
    # Add all combinations to session state
    added_count = 0
    for combo in all_combinations:
        if combo not in st.session_state['scenario1_selections']:
            combo['index'] = len(st.session_state['scenario1_selections']) + 1
            st.session_state['scenario1_selections'].append(combo)
            added_count += 1
    
    if added_count > 0:
        st.success(f"Successfully imported {added_count} case combinations from {len(countries)} countries to scenario {scenario_num}")
    else:
        st.info("All combinations for the selected countries are already cached.")

def cache_selection(selection: dict, scenario_num: int) -> None:
    """Cache a selection for the specified scenario."""
    if not selection:  # Handle empty selection
        st.warning("No valid selection to cache.")
        return
        
    # Handle multiple countries
    if selection.get('multiple_countries', False):
        countries = selection.get('countries', [])
        for country in countries:
            individual_selection = {
                'country': country,
                'incomecase': selection['incomecase'],
                'familytype': selection['familytype'],
                'incomegender': selection['incomegender'],
                'case': selection['case'],
                'alternative': selection['alternative']
            }
            
            if individual_selection not in st.session_state['scenario1_selections']:
                individual_selection['index'] = len(st.session_state['scenario1_selections']) + 1
                st.session_state['scenario1_selections'].append(individual_selection)
        
        st.success(f"Added {len(countries)} country selections to scenario {scenario_num}")
    else:
        # Single country selection - existing logic
        if selection in st.session_state['scenario1_selections']:
            st.warning(MESSAGES['selection_exists'])
        else:
            # Add index to the selection
            selection_with_index = selection.copy()
            selection_with_index['index'] = len(st.session_state['scenario1_selections']) + 1
            st.session_state['scenario1_selections'].append(selection_with_index)
            st.success(MESSAGES['selection_cached'].format(scenario_num))

def delete_or_clear_items() -> None:
    """Delete selected items or clear all selections."""
    if st.session_state['selected_to_delete']:
        st.session_state['scenario1_selections'] = [
            selection for idx, selection in enumerate(st.session_state['scenario1_selections'])
            if idx not in st.session_state['selected_to_delete']
        ]
        # Re-index the remaining selections
        for i, selection in enumerate(st.session_state['scenario1_selections']):
            selection['index'] = i + 1
        # Reset card order since selections changed
        st.session_state['card_order'] = []
        st.session_state['selected_to_delete'] = []
        st.success(MESSAGES['items_deleted'])
    else:
        st.session_state['scenario1_selections'] = []
        st.session_state['card_order'] = []
        st.success(MESSAGES['all_cleared'])

# Data Analysis and Visualization
def filter_data_by_selection(worksheet, selection):
    filtered_rows = []
    for row in worksheet:
        if len(row) > 6:  # Ensure row has enough columns
            if (row[0] == selection['country']
                and str(row[2]) == str(selection['incomecase'])
                and str(row[3]) == str(selection['familytype']) 
                and str(row[4]) == str(selection['incomegender'])
                and str(row[5]) == str(selection['case'])
                and str(row[6]) == str(selection['alternative'])):
                filtered_rows.append(row)
    
    return filtered_rows

def prepare_chart_data(selections, worksheet, exchange_rate_type=None):
    chart_data = {col: [] for col in NUMERIC_COLUMNS}
    
    for selection_idx, selection in enumerate(selections):
        filtered_data = filter_data_by_selection(worksheet, selection)
        
        if filtered_data:
            # Get exchange rate for this country if specified
            exchange_rate = None
            if exchange_rate_type:
                exchange_rate = get_exchange_rate_for_country(selection['country'], exchange_rate_type)
                if exchange_rate is None:
                    st.warning(f"No exchange rate found for {selection['country']} with type {exchange_rate_type}. Using original values.")
            
            for i, col in enumerate(NUMERIC_COLUMNS):
                try:
                    column_index = 7 + i  # Updated: numeric data starts at column 7 (0-indexed)
                    raw_value = filtered_data[0][column_index] if len(filtered_data[0]) > column_index else "0"
                    
                    value = float(raw_value) if raw_value and raw_value != '' else 0
                    
                    # Apply exchange rate if available
                    if exchange_rate is not None:
                        value = value / exchange_rate
                    
                    chart_data[col].append(value)
                except (ValueError, IndexError) as e:
                    chart_data[col].append(0)
        else:
            for col in NUMERIC_COLUMNS:
                chart_data[col].append(0)
    
    df = pd.DataFrame(chart_data)
    return df

def get_selection_indices(selection):
    """Convert selection values to indices for data handler compatibility."""
    return {
        'country': selection['country'],
        'incomecase': int(selection['incomecase']),
        'familytype': int(selection['familytype']),
        'incomegender': int(selection['incomegender']),
        'case': int(selection['case']),
        'alternative': int(selection['alternative'])
    }

def display_final_results(selections, worksheet, exchange_rate_type: str = None) -> None:
    if not selections:
        st.warning(MESSAGES['no_data'])
        return

    try:
        from pages.Data_Analytic import prepare_chart_data
        # Don't convert to indices - use the original selection values
        chart_df = prepare_chart_data(selections, worksheet, exchange_rate_type)
    except Exception as e:
        st.error(f"Error preparing chart data: {e}")
        return

    with st.expander("Display result"):
        if exchange_rate_type:
            st.info(f"Values converted using exchange rate: **{exchange_rate_type}**")
        else:
            st.info("Values shown in original currency (no exchange rate conversion applied)")

        # Table view (transpose so categories = rows)
        chart_df_display = chart_df.T
        selection_labels = [f"Selection {sel.get('index', i+1)}" for i, sel in enumerate(selections)]
        chart_df_display.columns = selection_labels
        
        # Display the data table
        st.subheader("Data Table")
        st.dataframe(chart_df_display, use_container_width=True)

        # Chart visualization
        st.subheader("Stacked Bar Chart")
        
        # Use the transposed data directly for plotting
        import plotly.graph_objects as go
        
        # Reset index to make categories a column
        chart_df_plot = chart_df_display.reset_index()
        
        # Get selection columns (exclude 'index' column)
        selection_cols = [col for col in chart_df_plot.columns if col != 'index']
        
        # Create the stacked bar chart
        fig = go.Figure()
        
        # Define distinct colors for better visibility
        distinct_colors = [
            '#FF6B6B',  # Red
            '#4ECDC4',  # Teal
            '#45B7D1',  # Blue
            '#96CEB4',  # Green
            '#FFEAA7',  # Yellow
            '#DDA0DD',  # Plum
            '#FFB347',  # Orange
            '#87CEEB',  # Sky Blue
            '#F0E68C',  # Khaki
            '#FA8072',  # Salmon
            '#98FB98',  # Pale Green
            '#DEB887',  # Burlywood
            '#FF69B4',  # Hot Pink
            '#40E0D0',  # Turquoise
            '#9370DB'   # Medium Purple
        ]
        
        # Add a trace for each category
        for idx, row in chart_df_plot.iterrows():
            category = row['index']
            values = [row[col] for col in selection_cols]
            
            fig.add_trace(go.Bar(
                name=category,
                x=selection_cols,
                y=values,
                text=[f"{v:.0f}" if v != 0 else "" for v in values],  # Show values on bars
                textposition='inside',
                marker_color=distinct_colors[idx % len(distinct_colors)]  # Assign distinct colors
            ))
        
        fig.update_layout(
            barmode='stack',
            title="Stacked Bar Chart",
            xaxis_title="Selections",
            yaxis_title="Amount",
            height=600,
            showlegend=True
        )

        import hashlib
        chart_key = hashlib.md5(str(chart_df_plot.values.tolist()).encode()).hexdigest()[:8]
        st.plotly_chart(fig, use_container_width=True, key=f"stacked_bar_{chart_key}")

def run():
    """Run the data analytics page."""
    st.markdown(
        f"""
        <h1 style='text-align: center;'>{PAGE_TITLES['data_analytic']}</h1>
        """,
        unsafe_allow_html=True
    )
    
    # Initialize data and session state
    worksheet = load_sheet_data()
    data = process_data(worksheet)
    initialize_session_state()

    # Import mode toggle
    import_mode = st.sidebar.checkbox(
        "Import All Cases Mode",
        help="When enabled, selecting countries will automatically import all possible case combinations for those countries"
    )
    
    # Selection interface
    selection = create_selection_fields(data, worksheet, import_mode)
    
    st.sidebar.markdown("---")
    
    # Action buttons
    if import_mode:
        if st.sidebar.button("Import All Cases for Selected Countries", use_container_width=True):
            import_all_cases_for_countries(selection, 1)
    else:
        if st.sidebar.button(BUTTON_LABELS['confirm'], use_container_width=True):
            cache_selection(selection, 1)

    if st.sidebar.button(BUTTON_LABELS['delete'], use_container_width=True):
        delete_or_clear_items()

    # Exchange rate selection
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Exchange Rate Settings")
    
    # Get available exchange rate options
    rate_options = get_exchange_rate_options()
    if rate_options:
        selected_rate = st.sidebar.selectbox(
            "Select Exchange Rate Type:",
            ["None"] + rate_options,
            help="Select an exchange rate type to convert values. 'None' means no conversion."
        )
    else:
        selected_rate = "None"
        st.sidebar.warning("No exchange rate data available")

    if st.sidebar.button(BUTTON_LABELS['show_result'], use_container_width=True):
        exchange_rate_type = selected_rate if selected_rate != "None" else None
        display_final_results(st.session_state['scenario1_selections'], worksheet, exchange_rate_type)

    # Display cached selections
    display_selections(st.session_state['scenario1_selections'], 1)

if __name__ == '__main__':
    run()
