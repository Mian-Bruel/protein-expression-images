import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from constants import PAGE_CONFIG
from sidebar import render_sidebar
from utils import download_lookup_df
from data_processing import process_data
from download_handlers import handle_downloads

# Set page configuration
st.set_page_config(**PAGE_CONFIG)

PAGE_SIZE = 100


def main(lookup_df):
    # Initialize session state to store the filtered dataframe and gene selections
    if (
        "filtered_df" not in st.session_state
        or "interactions_df" not in st.session_state
        or "total_number" not in st.session_state
    ):
        st.session_state["filtered_df"] = pd.DataFrame()
        st.session_state["interactions_df"] = pd.DataFrame()
        st.session_state["total_number"] = 0

    # FIXME: streamlit refreshes this every two-ish seconds
    # It's not a huge deal, but it might be beneficial to fix.

    # Render the sidebar and get the values from it
    _, filters, selected_genes = render_sidebar(lookup_df)

    max_pages = (st.session_state["total_number"] // PAGE_SIZE + 1) if st.session_state["total_number"] > 0 else 1
    # page button:
    cols = st.columns([2, 1, 2])
    page = cols[1].number_input("Page", min_value=1, max_value=max_pages, value=1, step=1)

    st.session_state["filtered_df"], st.session_state["interactions_df"], st.session_state["total_number"] = process_data(
        filters, selected_genes, lookup_df, page
    )

    dataframe_columns = st.columns([1, 5, 1])
    # Display the data
    dataframe_columns[1].markdown(
        f"Displaying **{len(st.session_state['filtered_df'])}** out of **{st.session_state['total_number']}** results"
    )
    dataframe_columns[1].dataframe(st.session_state["filtered_df"])

    # TODO: st.dataframe(st.session_state["interactions_df"])

    # Display download buttons / handle their clicks
    handle_downloads(filters, selected_genes)


if __name__ == "__main__":
    load_dotenv()
    lookup_df = download_lookup_df()
    main(lookup_df=lookup_df)
