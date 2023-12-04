"""Constants for the streamlit app."""
PAGE_CONFIG = {"layout": "wide", "page_title": "Pathology Summary", "page_icon": ":tada"}

API_PATHS = {
    "list": "api/samples",
    "excel": "api/samples/download",
    "csv": "api/samples/download/csv",
    "images": "api/samples/images",
}

PER_PAGE = 150
