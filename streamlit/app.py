import pandas as pd
from constants import PAGE_CONFIG
from sidebar import render_sidebar
from data_processing import process_data
from download_handlers import handle_downloads

import streamlit as st
from xml_utils.xml_loader import download_lookup_df

# Set page configuration
st.set_page_config(**PAGE_CONFIG)


def main(lookup_df):
    # Initialize session state to store the filtered dataframe and gene selections
    if "filtered_df" not in st.session_state or "interactions_df" not in st.session_state:
        st.session_state["filtered_df"] = pd.DataFrame()
        st.session_state["interactions_df"] = pd.DataFrame()

    # FIXME: streamlit refreshes this every two-ish seconds
    # It's not a huge deal, but it might be beneficial to fix.

    # Render the sidebar and get the values from it
    submit_button, filters, selected_genes = render_sidebar(lookup_df)

    # Only process the data when the 'Apply Changes' button is clicked
    if submit_button:
        st.session_state["filtered_df"], st.session_state["interactions_df"] = process_data(filters, selected_genes, lookup_df)

        # TODO: Remove this print
        print("filters:", filters, "Selected genes:", selected_genes, sep="\n")

    # Display the data
    st.dataframe(st.session_state["filtered_df"])
    st.dataframe(st.session_state["interactions_df"])

    # Display download buttons / handle their clicks
    handle_downloads(st.session_state["filtered_df"], st.session_state["interactions_df"])


if __name__ == "__main__":
    lookup_df = download_lookup_df()
    main(lookup_df=lookup_df)
