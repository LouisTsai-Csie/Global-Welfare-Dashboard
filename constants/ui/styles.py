"""Constants for UI styling."""

# CSS styles
STYLES = {
    'app': """
        .stApp {
            background-color: #0E1117;
            color: #FFFFFF;
        }
    """,
    'title': """
        .title {
            font-size: 4rem;
            font-weight: bold;
            text-align: center;
            margin-top: 1rem;
            background: -webkit-linear-gradient(#4F46E5, #9333EA);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
    """,
    'subtitle': """
        .subtitle {
            font-size: 1.5rem;
            text-align: center;
            margin-bottom: 2rem;
            color: #D1D5DB;
        }
    """,
    'card': """
        .card {
            background: rgba(31, 41, 55, 0.7);
            border-radius: 15px;
            padding: 2rem;
            margin: 1rem 0;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            color: #F3F4F6;
        }
        .card h3 {
            color: #FFFFFF;
        }
    """,
    'button': """
        .stButton>button {
            width: 100%;
            border: none;
            color: white;
            padding: 15px 32px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 16px;
            margin: 4px 2px;
            cursor: pointer;
            background-color: #4F46E5;
            border-radius: 8px;
            transition: all 0.3s ease;
        }
        .stButton>button:hover {
            background-color: #3730A3;
            transform: scale(1.05);
        }
    """
}

# Layout constants
LAYOUT = {
    'feature_cards': {
        'columns': 3,
        'column_ratios': [1, 1, 1]
    },
    'selection_display': {
        'columns': [0.1, 0.8, 0.1]
    }
}

# Colors
COLORS = {
    'primary': '#4F46E5',
    'primary_dark': '#3730A3',
    'background': '#0E1117',
    'text': '#FFFFFF',
    'text_secondary': '#D1D5DB',
    'card_background': 'rgba(31, 41, 55, 0.7)'
} 