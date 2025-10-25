"""UI components for the Global Welfare Dashboard."""

import streamlit as st
from typing import List, Dict, Any, Optional, Tuple
from components.data_handler import filter_data_by_selection
import pandas as pd
from constants import (
    SELECTION_LABELS,
    BUTTON_LABELS,
    MESSAGES,
    LAYOUT,
    COUNTRY_NAME,
    INCOME_CASE,
    FAMILY_CASES,
    INCOME_GENDER,
    CASES,
    COLUMN_INDICES,
    COLUMN_NAME_MAPPING,
    EXCLUDED_DISPLAY_COLUMNS,
    CLASS_A_BENEFITS,
    CLASS_B_COSTS
)

def create_selectbox(label: str, options: list, format_func=None) -> str:
    """Create a selectbox with the given label and options in the sidebar.
    
    Args:
        label: The label for the selectbox
        options: List of options to display
        format_func: Optional function to format the display of options
        
    Returns:
        The selected option
    """
    if format_func is None:
        return st.sidebar.selectbox(label, options)
    return st.sidebar.selectbox(label, options, format_func=format_func)

def get_filtered_data(worksheet: List[List[str]], country_code: str) -> Dict[str, List[int]]:
    """Get filtered data for a specific country.
    
    Args:
        worksheet: The worksheet data
        country_code: The country code to filter by
        
    Returns:
        Dictionary containing filtered data for each category
    """
    country_data = [row for row in worksheet if row[COLUMN_INDICES['country']] == country_code]
    
    return {
        'incomecase': sorted(list(set(int(row[COLUMN_INDICES['incomecase']]) 
                                    for row in country_data if row[COLUMN_INDICES['incomecase']]))),
        'familytype': sorted(list(set(int(row[COLUMN_INDICES['familytype']]) 
                                    for row in country_data if row[COLUMN_INDICES['familytype']]))),
        'incomegender': sorted(list(set(int(row[COLUMN_INDICES['incomegender']]) 
                                      for row in country_data if row[COLUMN_INDICES['incomegender']]))),
        'case': sorted(list(set(int(row[COLUMN_INDICES['case']]) 
                              for row in country_data if row[COLUMN_INDICES['case']]))),
        'alternative': sorted(list(set(int(row[COLUMN_INDICES['alternative']]) 
                                     for row in country_data if row[COLUMN_INDICES['alternative']])))
    }

def filter_data_by_selection_criteria(worksheet: List[List[str]], 
                                    country_code: str,
                                    selection_criteria: Dict[str, int]) -> List[List[str]]:
    """Filter worksheet data based on selection criteria.
    
    Args:
        worksheet: The worksheet data
        country_code: The country code
        selection_criteria: Dictionary of selection criteria and their values
        
    Returns:
        Filtered worksheet data
    """
    filtered_data = [row for row in worksheet if row[COLUMN_INDICES['country']] == country_code]
    
    for field, value in selection_criteria.items():
        filtered_data = [row for row in filtered_data 
                        if int(row[COLUMN_INDICES[field]]) == value]
    
    return filtered_data

def create_selection_fields(data: dict, worksheet: list, import_mode: bool = False) -> dict:
    """Create selection fields for data analysis with strict cascading filtering."""
    # Start with all worksheet data
    filtered_rows = worksheet

    # Country selection (multi-select)
    country_options = sorted(set(row[COLUMN_INDICES['country']] for row in filtered_rows if row[COLUMN_INDICES['country']]))
    selected_country_names = st.sidebar.multiselect(
        SELECTION_LABELS['country'],
        [COUNTRY_NAME[code] for code in country_options],
        default=[]
    )

    # If no countries selected, use all countries by default
    if not selected_country_names:
        selected_country_codes = country_options
    else:
        selected_country_codes = [code for code, name in COUNTRY_NAME.items() if name in selected_country_names]
    filtered_rows = [row for row in filtered_rows if row[COLUMN_INDICES['country']] in selected_country_codes]
    
    # In import mode, show information about selected countries and return early
    if import_mode:
        st.sidebar.info(f"**Import Mode Active**\nSelected {len(selected_country_codes)} countries:\n" + 
                       "\n".join([f"• {COUNTRY_NAME[code]}" for code in selected_country_codes]))
        
        # Count total combinations for selected countries
        total_combinations = 0
        for country in selected_country_codes:
            country_data = [row for row in worksheet if row[COLUMN_INDICES['country']] == country]
            if country_data:
                unique_combos = set()
                for row in country_data:
                    if len(row) > 6:
                        combo = (row[2], row[3], row[4], row[5], row[6])
                        unique_combos.add(combo)
                total_combinations += len(unique_combos)
        
        st.sidebar.info(f"**{total_combinations}** total case combinations will be imported")
        
        if len(selected_country_codes) == 1:
            return {
                'country': selected_country_codes[0],
                'incomecase': '',
                'familytype': '',
                'incomegender': '',
                'case': '',
                'alternative': ''
            }
        else:
            return {
                'countries': selected_country_codes,
                'multiple_countries': True,
                'incomecase': '',
                'familytype': '',
                'incomegender': '',
                'case': '',
                'alternative': ''
            }

    # Income case selection
    incomecase_options = sorted(set(int(row[COLUMN_INDICES['incomecase']]) for row in filtered_rows if row[COLUMN_INDICES['incomecase']]))
    selected_incomecase_idx = create_selectbox(
        SELECTION_LABELS['incomecase'],
        incomecase_options,
        format_func=lambda x: f"{x}: {INCOME_CASE[x]}"
    )
    filtered_rows = [row for row in filtered_rows if int(row[COLUMN_INDICES['incomecase']]) == selected_incomecase_idx]

    # Family type selection
    familytype_options = sorted(set(int(row[COLUMN_INDICES['familytype']]) for row in filtered_rows if row[COLUMN_INDICES['familytype']]))
    selected_familytype_idx = create_selectbox(
        SELECTION_LABELS['familytype'],
        familytype_options,
        format_func=lambda x: f"{x}: {FAMILY_CASES[x]}"
    )
    filtered_rows = [row for row in filtered_rows if int(row[COLUMN_INDICES['familytype']]) == selected_familytype_idx]

    # Income gender selection
    incomegender_options = sorted(set(int(row[COLUMN_INDICES['incomegender']]) for row in filtered_rows if row[COLUMN_INDICES['incomegender']]))
    selected_incomegender_idx = create_selectbox(
        SELECTION_LABELS['incomegender'],
        incomegender_options,
        format_func=lambda x: f"{x}: {INCOME_GENDER[x]}"
    )
    filtered_rows = [row for row in filtered_rows if int(row[COLUMN_INDICES['incomegender']]) == selected_incomegender_idx]

    # Case selection
    case_options = sorted(set(int(row[COLUMN_INDICES['case']]) for row in filtered_rows if row[COLUMN_INDICES['case']]))
    selected_case_idx = create_selectbox(
        SELECTION_LABELS['case'],
        case_options,
        format_func=lambda x: f"{x}: {CASES[x]}"
    )
    filtered_rows = [row for row in filtered_rows if int(row[COLUMN_INDICES['case']]) == selected_case_idx]

    # Alternative selection
    alternative_options = sorted(set(int(row[COLUMN_INDICES['alternative']]) for row in filtered_rows if row[COLUMN_INDICES['alternative']]))
    selected_alternative = create_selectbox(
        SELECTION_LABELS['alternative'],
        alternative_options
    )

    # Return selections for all selected countries
    if len(selected_country_codes) == 1:
        # Single country - return as before
        return {
            'country': selected_country_codes[0],
            'incomecase': str(selected_incomecase_idx),
            'familytype': str(selected_familytype_idx),
            'incomegender': str(selected_incomegender_idx),
            'case': str(selected_case_idx),
            'alternative': str(selected_alternative)
        }
    else:
        # Multiple countries - return a list of selections
        return {
            'countries': selected_country_codes,
            'incomecase': str(selected_incomecase_idx),
            'familytype': str(selected_familytype_idx),
            'incomegender': str(selected_incomegender_idx),
            'case': str(selected_case_idx),
            'alternative': str(selected_alternative),
            'multiple_countries': True
        }

def display_selections(selections: list, scenario_num: int) -> None:
    """Display cached selections in an interactive data editor."""
    if not selections:
        st.info(MESSAGES['no_selections'])
        return

    st.markdown(f"<h3 style='margin-bottom: 1.5em;'>Scenario {scenario_num} Selections:</h3>", unsafe_allow_html=True)
    
    # Prepare data for the data editor
    df_data = []
    country_counters = {}
    for selection in selections:
        # Create country-based label (e.g., "Japan-1", "Japan-2")
        country_code = selection['country']
        country_name = COUNTRY_NAME[country_code]
        country_counters[country_code] = country_counters.get(country_code, 0) + 1
        selection_label = f"{country_name}-{country_counters[country_code]}"

        # Convert selection to display format
        row_data = {
            'Delete': False,  # Add checkbox column
            'Selection': selection_label,
            'Country': country_name,
            'Income Case': INCOME_CASE[int(selection['incomecase'])],
            'Family Type': FAMILY_CASES[int(selection['familytype'])],
            'Income Gender': INCOME_GENDER[int(selection['incomegender'])],
            'Case': CASES[int(selection['case'])],
            'Alternative': selection['alternative']
        }
        df_data.append(row_data)
    
    # Create DataFrame
    import pandas as pd
    df = pd.DataFrame(df_data)
    
    # Configure column display with compact widths
    column_config = {
        'Delete': st.column_config.CheckboxColumn(
            '🗑️',
            help='Check to mark for deletion',
            width='small'
        ),
        'Selection': st.column_config.TextColumn(
            'Selection',
            width='small',
            disabled=True
        ),
        'Country': st.column_config.TextColumn(
            'Country',
            width='small',
            disabled=True
        ),
        'Income Case': st.column_config.TextColumn(
            'Income Case',
            width='small',
            disabled=True
        ),
        'Family Type': st.column_config.TextColumn(
            'Family Type',
            width='small',
            disabled=True
        ),
        'Income Gender': st.column_config.TextColumn(
            'Income Gender',
            width='small',
            disabled=True
        ),
        'Case': st.column_config.TextColumn(
            'Case',
            width='small',
            disabled=True
        ),
        'Alternative': st.column_config.NumberColumn(
            'Alternative',
            width='small',
            disabled=True
        )
    }
    
    # Display the data editor with checkbox selection and sorting
    st.info("💡 **Check the boxes next to selections you want to delete, then click the delete button**")
    
    edited_df = st.data_editor(
        df,
        column_config=column_config,
        use_container_width=True,
        hide_index=True,
        num_rows="fixed",
        disabled=["Selection", "Country", "Income Case", "Family Type", "Income Gender", "Case", "Alternative"],
        key=f"selections_editor_{scenario_num}"
    )
    
    # Update selected_to_delete based on checkbox column for existing sidebar delete button
    if len(edited_df) > 0:
        # Get rows marked for deletion
        rows_to_delete = edited_df[edited_df['Delete'] == True].index.tolist()
        
        # Update the session state with selected items
        if 'selected_to_delete' not in st.session_state:
            st.session_state['selected_to_delete'] = []
        
        # Only update if there are changes
        if set(rows_to_delete) != set(st.session_state['selected_to_delete']):
            st.session_state['selected_to_delete'] = rows_to_delete
        
        if rows_to_delete:
            st.info(f"💡 **{len(rows_to_delete)} selection(s) marked for deletion** - Use the 'Delete' button in the sidebar to remove them")

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

    st.dataframe(chart_df_display)

    # Create melted dataframe for plotly (already has correct signs from above)
    chart_df_melted = chart_df_display.reset_index().melt(
        id_vars=['index'],
        var_name='Selection',
        value_name='Value'
    )
    chart_df_melted = chart_df_melted.rename(columns={'index': 'Category'})

    import plotly.express as px

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

    fig = px.bar(
        chart_df_melted,
        x="Selection",
        y="Value",
        color="Category",
        barmode="relative",  # Changed from 'stack' to 'relative' for proper positive/negative handling
        title=f"Stacked Bar Chart (Total: {chart_df_melted['Value'].sum():,.0f})",
        labels={"Selection": "Selections", "Value": "Amount", "Category": "Category"},
        color_discrete_sequence=distinct_colors
    )

    fig.update_traces(texttemplate='%{y:.1f}', textposition='inside')
    fig.update_layout(
        barmode="relative",
        xaxis_title="Selections",
        yaxis_title="Amount",
        yaxis=dict(dtick=200),
        height=600,
        hovermode='x unified'
    )

    import hashlib
    chart_key = hashlib.md5(str(chart_df_melted.values.tolist()).encode()).hexdigest()[:8]
    st.plotly_chart(fig, use_container_width=True, key=f"stacked_bar_{chart_key}")
