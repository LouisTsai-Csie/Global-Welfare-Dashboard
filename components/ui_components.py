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
    COLUMN_INDICES
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
        default=[COUNTRY_NAME[country_options[0]]] if country_options else []
    )
    
    if not selected_country_names:
        st.warning("Please select at least one country.")
        return {}
    
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
    for idx, selection in enumerate(selections):
        # Convert selection to display format
        row_data = {
            'Delete': False,  # Add checkbox column
            'Selection': f"Selection {selection.get('index', idx + 1)}",
            'Country': COUNTRY_NAME[selection['country']],
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
        st.dataframe(chart_df_display)

        # Create melted dataframe for plotly
        chart_df_melted = chart_df_display.reset_index().melt(
            id_vars=['index'], 
            var_name='Selection', 
            value_name='Value'
        )
        chart_df_melted = chart_df_melted.rename(columns={'index': 'Category'})
        
        import plotly.express as px
        
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
        
        fig = px.bar(
            chart_df_melted,
            x="Selection",
            y="Value",
            color="Category",
            barmode="stack",
            title=f"Stacked Bar Chart (Total: {chart_df_melted['Value'].sum():,.0f})",
            labels={"Selection": "Selections", "Value": "Amount", "Category": "Category"},
            color_discrete_sequence=distinct_colors
        )

        fig.update_traces(texttemplate='%{y:.1f}', textposition='inside')
        fig.update_layout(barmode="stack", xaxis_title="Selections", yaxis_title="Amount", height=600)

        import hashlib
        chart_key = hashlib.md5(str(chart_df_melted.values.tolist()).encode()).hexdigest()[:8]
        st.plotly_chart(fig, use_container_width=True, key=f"stacked_bar_{chart_key}")
