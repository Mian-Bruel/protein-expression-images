import io

import pandas as pd

import streamlit as st
from xml_utils.image_downloader import zip_images, download_images


def handle_downloads(filtered_df, interactions_df):
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

    buffer_csv = io.BytesIO()
    filtered_df.to_csv(buffer_csv, index=False)
    buffer_csv.seek(0)
    col[1].download_button(label="Download Filtered Data as CSV", data=buffer_csv, file_name="filtered_data.csv", mime="text/csv")

    # Download the filtered dataframe as Excel
    buffer_excel = io.BytesIO()
    with pd.ExcelWriter(buffer_excel, engine="openpyxl") as writer:
        filtered_df.to_excel(writer, index=False)
    buffer_excel.seek(0)
    col[2].download_button(
        label="Download Filtered Data as Excel",
        data=buffer_excel,
        file_name="filtered_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
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
        image_urls = filtered_df["images"]
        # handle rows with multiple images
        image_urls = image_urls.str.split(",").explode().str.strip().dropna().tolist()

        image_files = download_images(image_urls)
        zip_file_path = zip_images(image_files)

        # Provide the zip file for download
        with open(zip_file_path, "rb") as file:
            col[3].download_button(label="Download Images", data=file, file_name="images.zip", mime="application/zip")
