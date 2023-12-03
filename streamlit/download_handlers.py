import io

import pandas as pd

import streamlit as st
from xml_utils.image_downloader import zip_images, download_images


def handle_downloads(filtered_df, interactions_df):
    # Download the filtered dataframe as CSV
    buffer_csv = io.BytesIO()
    filtered_df.to_csv(buffer_csv, index=False)
    buffer_csv.seek(0)
    st.download_button(label="Download Filtered Data as CSV", data=buffer_csv, file_name="filtered_data.csv", mime="text/csv")

    # Download the filtered dataframe as Excel
    buffer_excel = io.BytesIO()
    with pd.ExcelWriter(buffer_excel, engine="openpyxl") as writer:
        filtered_df.to_excel(writer, index=False)
    buffer_excel.seek(0)
    st.download_button(
        label="Download Filtered Data as Excel",
        data=buffer_excel,
        file_name="filtered_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

    # The image download functionality remains unchanged
    if st.button("Prepare Image download link"):
        image_urls = filtered_df["imageUrl"].tolist()
        image_files = download_images(image_urls)
        zip_file_path = zip_images(image_files)

        # Provide the zip file for download
        with open(zip_file_path, "rb") as file:
            st.download_button(label="Download Images", data=file, file_name="images.zip", mime="application/zip")
