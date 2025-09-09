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