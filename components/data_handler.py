"""Data handling functions for the Global Welfare Dashboard."""

import streamlit as st
import pandas as pd
from typing import List, Dict, Any, Tuple
from auth import authenticate
from constants import NUMERIC_COLUMNS, SHEET_URLS, COLUMN_INDICES

@st.cache_data
def load_sheet_data() -> List[List[str]]:
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

@st.cache_data
def process_data(workSheet: List[List[str]]) -> Dict[str, List[str]]:
    """Process worksheet data and extract unique values for each category."""
    return {
        'county': sorted(list(set(row[COLUMN_INDICES['country']] for row in workSheet if row[COLUMN_INDICES['country']]))),
        'incomecase': sorted(list(set(row[COLUMN_INDICES['incomecase']] for row in workSheet if row[COLUMN_INDICES['incomecase']]))),
        'familytype': sorted(list(set(row[COLUMN_INDICES['familytype']] for row in workSheet if row[COLUMN_INDICES['familytype']]))),
        'incomegender': sorted(list(set(row[COLUMN_INDICES['incomegender']] for row in workSheet if row[COLUMN_INDICES['incomegender']]))),
        'case': sorted(list(set(row[COLUMN_INDICES['case']] for row in workSheet if row[COLUMN_INDICES['case']]))),
        'alternative': sorted(list(set(row[COLUMN_INDICES['alternative']] for row in workSheet if row[COLUMN_INDICES['alternative']])))
    }

def filter_data_by_selection(worksheet: List[List[str]], selection: Dict[str, str]) -> List[List[str]]:
    """Filter worksheet data based on selection criteria."""
    return [row for row in worksheet 
            if row[COLUMN_INDICES['country']] == selection['country']
            and str(row[COLUMN_INDICES['incomecase']]) == str(selection['incomecase'])
            and str(row[COLUMN_INDICES['familytype']]) == str(selection['familytype'])
            and str(row[COLUMN_INDICES['incomegender']]) == str(selection['incomegender'])
            and str(row[COLUMN_INDICES['case']]) == str(selection['case'])
            and str(row[COLUMN_INDICES['alternative']]) == str(selection['alternative'])]

def prepare_chart_data(selections: List[Dict[str, str]], worksheet: List[List[str]], exchange_rate_type: str = None) -> pd.DataFrame:
    """Prepare data for chart visualization."""
    chart_data = {col: [] for col in NUMERIC_COLUMNS}
    
    # Import exchange rate functions if needed
    if exchange_rate_type:
        try:
            from pages.Data_Analytic import get_exchange_rate_for_country
        except ImportError:
            exchange_rate_type = None
    
    for selection in selections:
        filtered_data = filter_data_by_selection(worksheet, selection)
        
        if filtered_data:
            # Get exchange rate for this country if specified
            exchange_rate = None
            if exchange_rate_type:
                try:
                    exchange_rate = get_exchange_rate_for_country(selection['country'], exchange_rate_type)
                    if exchange_rate is None:
                        st.warning(f"No exchange rate found for {selection['country']} with type {exchange_rate_type}. Using original values.")
                except Exception:
                    exchange_rate = None
            
            for i, col in enumerate(NUMERIC_COLUMNS):
                try:
                    column_index = 7 + i  # Updated: numeric data starts at column 7 (0-indexed)
                    raw_value = filtered_data[0][column_index] if len(filtered_data[0]) > column_index else "0"
                    value = float(raw_value) if raw_value else 0
                    
                    # Apply exchange rate if available
                    if exchange_rate is not None:
                        value = value / exchange_rate
                    
                    chart_data[col].append(value)
                except (ValueError, IndexError):
                    chart_data[col].append(0)
        else:
            for col in NUMERIC_COLUMNS:
                chart_data[col].append(0)
    
    return pd.DataFrame(chart_data) 