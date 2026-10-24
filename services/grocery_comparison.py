from .comparison import DATA_DIR, load_items

def get_grocery_data():
    """Replace this source with normalized scraper output when supplied."""
    return load_items(DATA_DIR / 'sample_grocery.json')
