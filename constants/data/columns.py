"""Constants for data columns and data processing."""

# Numeric columns for data analysis
NUMERIC_COLUMNS = [
    'earning', 'iliving', 'inutrition', 'iCCare', 'iCBenefit', 'ifertility',
    'ieducation', 'ihousing', 'imedical', 'iutility', 'itransport', 'isocsec',
    'itax', 'iwork', 'iunempinsurance', 'iunempsub', 'iother', 'totalbenefit',
    'incometax', 'localtax', 'pension', 'healthinsurance', 'unempinsurance',
    'othercontribution', 'ccarecost', 'schlcosts', 'healthcost', 'rent',
    'utilitycost', 'foodcost', 'telecost', 'transportcost', 'othercosts',
    'totalexpense'
]

# Mapping of column abbreviations to full names for better readability
COLUMN_NAME_MAPPING = {
    'earning': 'Earnings',
    'iliving': 'Living subsidy',
    'inutrition': 'Nutrition/food-related subsidy',
    'iCCare': 'Childcare related subsidy',
    'iCBenefit': 'Child benefits',
    'ifertility': 'Fertility benefits',
    'ieducation': 'Education related subsidy',
    'ihousing': 'Housing related subsidy',
    'imedical': 'Medical related subsidy',
    'iutility': 'Utility subsidy',
    'itransport': 'Transportation subsidy',
    'isocsec': 'Social security subsidy',
    'itax': 'Tax subsidy (e.g., EITC)',
    'iwork': 'Work related subsidy',
    'iunempinsurance': 'Unemployment insurance payment',
    'iunempsub': 'Unemployment subsidy',
    'iother': 'Other benefits',
    'totalbenefit': 'Total Benefits',
    'incometax': 'Income Tax',
    'localtax': 'Local Tax',
    'pension': 'Pension',
    'healthinsurance': 'Health insurance',
    'unempinsurance': 'Unemployment insurance',
    'othercontribution': 'Other contributions',
    'ccarecost': 'Childcare cost',
    'schlcosts': 'School cost',
    'healthcost': 'Healthcare cost',
    'rent': 'Housing rent',
    'utilitycost': 'Utility cost',
    'foodcost': 'Food & Groceries',
    'telecost': 'Telecommunications cost',
    'transportcost': 'Transportation cost',
    'othercosts': 'Other costs',
    'totalexpense': 'Total Expenses'
}

# Columns to exclude from display
EXCLUDED_DISPLAY_COLUMNS = ['totalexpense', 'othercosts', 'totalbenefit']

# Class A: Benefits/Income - should display as positive values (stacked upward)
CLASS_A_BENEFITS = [
    'earning',
    'iliving',
    'inutrition',
    'iCCare',
    'iCBenefit',
    'ifertility',
    'ieducation',
    'ihousing',
    'imedical',
    'iutility',
    'itransport',
    'isocsec',
    'itax',
    'iwork',
    'iunempinsurance',
    'iunempsub',
    'iother'
]

# Class B: Costs/Expenses - should display as negative values (stacked downward)
CLASS_B_COSTS = [
    'incometax',
    'localtax',
    'pension',
    'healthinsurance',
    'unempinsurance',
    'othercontribution',
    'ccarecost',
    'schlcosts',
    'healthcost',
    'rent',
    'utilitycost',
    'foodcost',
    'telecost',
    'othercosts'
]

# Google Sheets URLs
SHEET_URLS = {
    'sheet0': 'https://docs.google.com/spreadsheets/d/13TAI7o_WFd71JGlDBh0iCFVkHTeZA8UvTNiNYU0xR6U/edit?gid=0#gid=0',
    'sheet1': 'https://docs.google.com/spreadsheets/d/1P9wvWrZdNjPSO_vHwElFYPyRdlAtLQXxgZ31FfV0G1s/edit?gid=0#gid=0'
}

# Data column indices
COLUMN_INDICES = {
    'country': 0,
    'incomecase': 2,
    'familytype': 3,
    'incomegender': 4,
    'case': 5,
    'alternative': 6
} 