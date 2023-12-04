import pandas as pd
from constants import PAGE_CONFIG
from sidebar import render_sidebar
from data_processing import process_data
from download_handlers import handle_downloads

import streamlit as st
from xml_utils.xml_loader import download_lookup_df

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
    page = st.number_input("Page", min_value=1, max_value=max_pages, value=1, step=1)

    st.session_state["filtered_df"], st.session_state["interactions_df"], st.session_state["total_number"] = process_data(
        filters, selected_genes, lookup_df, page
    )

    # Display the data
    st.markdown(f"Displaying **{len(st.session_state['filtered_df'])}** out of **{st.session_state['total_number']}** results")
    st.dataframe(st.session_state["filtered_df"])

    # TODO: st.dataframe(st.session_state["interactions_df"])

    # Display download buttons / handle their clicks
    handle_downloads(st.session_state["filtered_df"], st.session_state["interactions_df"])


if __name__ == "__main__":
    lookup_df = download_lookup_df()
    main(lookup_df=lookup_df)
