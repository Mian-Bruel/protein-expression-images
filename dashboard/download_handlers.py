import base64
import datetime

import streamlit as st
from utils import send_request
from streamlit.components.v1 import html


def handle_downloads(filters, selected_genes):
    """
    Handle the download buttons. Show the buttons and download the data when they're clicked.

    Args:
        filtered_df (pd.DataFrame): The filtered dataframe.
        interactions_df (pd.DataFrame): The interactions dataframe.

    Returns:
        None

    Note:
        The interactions_df is not used in this function. Left here for future use.
    TODO:
        Remove the note when the interactions_df is used.
    """
    # Download the filtered dataframe as CSV
    col = st.columns([1, 1, 1, 1, 1])

    if col[1].button("Download csv"):
        response = send_request(filters, "csv", selected_genes=selected_genes)
        if response.status_code == 200:
            b64 = base64.b64encode(response.content).decode()
            href = f'<a href="data:text/csv;base64,{b64}" download="samples_{datetime.datetime.now().strftime("%x_%X")}.csv">Download samples.csv file</a>'
            html_content = f"""
                    <script src="http://code.jquery.com/jquery-3.2.1.min.js"></script>
                    <script>
                    $('{href}')[0].click()
                    </script>
                    """
            html(html_content)
            st.success("Downloaded images.txt file")
        else:
            st.error(
                "Failed to download samples.csv file"
                if response.status_code != 413
                else "Too many images, please apply more filters (pretty please(MAX=20_000))"
            )

    if col[2].button("Download xlsx"):
        response = send_request(filters, "excel", selected_genes=selected_genes)
        if response.status_code == 200:
            b64 = base64.b64encode(response.content).decode()
            href = f'<a href="data:file/xlsx;base64,{b64}" download="samples_{datetime.datetime.now().strftime("%x_%X")}.xlsx">Download samples.xlsx file</a>'
            html_content = f"""
                    <script src="http://code.jquery.com/jquery-3.2.1.min.js"></script>
                    <script>
                    $('{href}')[0].click()
                    </script>
                    """
            html(html_content)
            st.success("Downloaded samples.txt file")
        else:
            st.error(
                "Failed to download samples.xlsx file"
                if response.status_code != 413
                else "Too many images, please apply more filters (pretty please(MAX=20_000))"
            )

    # The image download functionality remains unchanged
    if col[3].button("Prepare Image download link"):
        st.info(
            """
                We have moved the functionality to download images to a separate package \n
                Install with:  ```pip install PaTho``` \n
                images.txt file should have been downloaded \n
                you can now run ```PaTho -f images.txt -d <where/to/save> -b http://images.proteinatlas.org/```
                """,
            icon="🤖",
        )
        response = send_request(filters, "images", selected_genes=selected_genes)
        if response.status_code == 200:
            b64 = base64.b64encode(response.content).decode()
            href = f'<a href="data:file/txt;base64,{b64}" download="images_{datetime.datetime.now().strftime("%x_%X")}.txt">Download images.txt file</a>'
            html_content = f"""
                    <script src="http://code.jquery.com/jquery-3.2.1.min.js"></script>
                    <script>
                    $('{href}')[0].click()
                    </script>
                    """
            html(html_content)
            st.success("Downloaded images.txt file")
        # Automatically download the images.txt file
        else:
            st.error(
                "Failed to download images.txt file"
                if response.status_code != 413
                else "Too many images, please apply more filters (pretty please(MAX=20_000))"
            )
