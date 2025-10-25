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
    CASES,
    COUNTRY_NAME,
    COLUMN_NAME_MAPPING,
    EXCLUDED_DISPLAY_COLUMNS,
    CLASS_A_BENEFITS,
    CLASS_B_COSTS
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

    # Get the exchange rate columns (PPP and Nominal)
    rate_columns = [col for col in df.columns if col in ['PPP exchange rates', 'Nominal exchange rates']]
    return rate_columns

def get_exchange_rate_for_country(country_code, rate_type):
    """Get exchange rate for a specific country and rate type."""
    df = load_exchange_rates()
    if df is None:
        return None

    # Find the country in the exchange rate data
    country_data = df[df['country'] == country_code]
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

    return df[['countryname', 'country']].dropna().to_dict('records')



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

def display_final_results(selections, worksheet, exchange_rate_type: str = None, selected_columns: list = None) -> None:
    if not selections:
        st.warning(MESSAGES['no_data'])
        return

    # Helper function to process dataframe with filters and transformations
    def process_dataframe(df, sel_labels, sel_cols):
        df_display = df.T
        df_display.columns = sel_labels

        # Filter out excluded columns
        df_display = df_display.drop(index=EXCLUDED_DISPLAY_COLUMNS, errors='ignore')

        # Filter by selected columns if provided
        if sel_cols:
            column_code_map = {v: k for k, v in COLUMN_NAME_MAPPING.items()}
            selected_codes = [column_code_map.get(col, col) for col in sel_cols]
            available_codes = [code for code in selected_codes if code in df_display.index]
            if available_codes:
                df_display = df_display.loc[available_codes]

        # Apply proper signs based on category classification
        for category in df_display.index:
            if category in CLASS_A_BENEFITS:
                df_display.loc[category] = df_display.loc[category].abs()
            elif category in CLASS_B_COSTS:
                df_display.loc[category] = -df_display.loc[category].abs()

        # Map column names to readable names
        df_display.index = df_display.index.map(lambda x: COLUMN_NAME_MAPPING.get(x, x))
        return df_display

    try:
        from pages.Data_Analytic import prepare_chart_data

        # Prepare exchange rate adjusted data (if applicable)
        chart_df = prepare_chart_data(selections, worksheet, exchange_rate_type)

        # Always prepare raw data (without exchange rate conversion)
        chart_df_raw = prepare_chart_data(selections, worksheet, None)
    except Exception as e:
        st.error(f"Error preparing chart data: {e}")
        return

    if exchange_rate_type:
        st.info(f"Values converted using exchange rate: **{exchange_rate_type}**")
    else:
        st.info("Values shown in original currency (no exchange rate conversion applied)")

    # Create labels with country name and counter (e.g., "Japan-1", "Japan-2")
    country_counters = {}
    selection_labels = []
    for sel in selections:
        country_code = sel.get('country') or sel.get('countries', [None])[0]
        if country_code:
            country_name = COUNTRY_NAME.get(country_code, country_code)
            country_counters[country_code] = country_counters.get(country_code, 0) + 1
            selection_labels.append(f"{country_name}-{country_counters[country_code]}")
        else:
            selection_labels.append(f"Selection {len(selection_labels)+1}")

    # Process both dataframes with the same transformations
    chart_df_display = process_dataframe(chart_df, selection_labels, selected_columns)
    chart_df_raw_display = process_dataframe(chart_df_raw, selection_labels, selected_columns)

    # Display the data table
    st.subheader("Data Table")

    # Add download buttons for both versions
    col1, col2 = st.columns(2)

    with col1:
        if exchange_rate_type:
            csv_data_converted = chart_df_display.to_csv()
            st.download_button(
                label=f"📥 Download Data ({exchange_rate_type})",
                data=csv_data_converted,
                file_name=f"welfare_data_{exchange_rate_type}.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            csv_data = chart_df_display.to_csv()
            st.download_button(
                label="📥 Download Data as CSV",
                data=csv_data,
                file_name="welfare_data_table.csv",
                mime="text/csv",
                use_container_width=True
            )

    with col2:
        csv_data_raw = chart_df_raw_display.to_csv()
        st.download_button(
            label="📥 Download Raw Data (Original Currency)",
            data=csv_data_raw,
            file_name="welfare_data_raw.csv",
            mime="text/csv",
            use_container_width=True
        )

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

    # Define distinct colors using a scientifically-designed palette
    # Colors chosen to maximize perceptual difference and avoid duplicates
    distinct_colors = [
        '#FF1744',  # 1. Vivid Red
        '#2979FF',  # 2. Vivid Blue
        '#00E676',  # 3. Vivid Green
        '#FF9100',  # 4. Vivid Orange
        '#D500F9',  # 5. Vivid Purple
        '#00E5FF',  # 6. Vivid Cyan
        '#FFEA00',  # 7. Vivid Yellow
        '#FF4081',  # 8. Vivid Pink
        '#00BFA5',  # 9. Vivid Teal
        '#6200EA',  # 10. Deep Purple
        '#76FF03',  # 11. Lime
        '#FF6E40',  # 12. Deep Orange
        '#304FFE',  # 13. Indigo
        '#AEEA00',  # 14. Light Lime
        '#DD2C00',  # 15. Dark Red
        '#0091EA',  # 16. Light Blue
        '#64DD17',  # 17. Light Green
        '#AA00FF',  # 18. Deep Purple Accent
        '#FFD600',  # 19. Gold
        '#FF3D00',  # 20. Red Orange
        '#1DE9B6',  # 21. Aqua
        '#651FFF',  # 22. Purple
        '#C6FF00',  # 23. Yellow Green
        '#F50057',  # 24. Magenta
        '#00B8D4',  # 25. Dark Cyan
        '#FFAB00',  # 26. Amber
        '#448AFF',  # 27. Sky Blue
        '#69F0AE',  # 28. Mint
        '#E040FB',  # 29. Orchid
        '#FFC400',  # 30. Bright Amber
        '#18FFFF',  # 31. Electric Cyan
    ]

    # Add traces for each category (signs already applied above)
    for idx, row in chart_df_plot.iterrows():
        category = row['index']
        values = [row[col] for col in selection_cols]

        fig.add_trace(go.Bar(
            name=category,
            x=selection_cols,
            y=values,
            text=[f"{v:.0f}" if v != 0 else "" for v in values],
            textposition='inside',
            marker_color=distinct_colors[idx % len(distinct_colors)],
        ))

    fig.update_layout(
        barmode='relative',  # Changed from 'stack' to 'relative' for proper positive/negative handling
        title="Stacked Bar Chart",
        xaxis_title="Selections",
        yaxis_title="Amount",
        yaxis=dict(dtick=200),
        height=600,
        showlegend=True,
        hovermode='x unified'
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

    # Column selection for display
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Display Category")

    # Get all available columns (excluding the excluded ones)
    available_columns = [col for col in NUMERIC_COLUMNS if col not in EXCLUDED_DISPLAY_COLUMNS]
    # Convert to readable names for display
    available_column_names = [COLUMN_NAME_MAPPING.get(col, col) for col in available_columns]

    selected_column_names = st.sidebar.multiselect(
        "Select columns to display:",
        options=available_column_names,
        default=[],
        help="Choose which columns to show in the data table and chart. Leave empty to show all columns."
    )

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
        # If no columns selected, pass None to show all columns
        columns_to_show = selected_column_names if selected_column_names else None
        display_final_results(
            st.session_state['scenario1_selections'],
            worksheet,
            exchange_rate_type,
            columns_to_show
        )

    # Display cached selections
    display_selections(st.session_state['scenario1_selections'], 1)

if __name__ == '__main__':
    run()
