import io
import base64

import pandas as pd
import streamlit as st
from pandas.api.types import is_object_dtype, is_numeric_dtype, is_categorical_dtype, is_datetime64_any_dtype
from xml_utils.interactions import get_interactions_from_html

from xml_utils.xml_parser import load_xml, process_xml
from xml_utils.image_downloader import zip_images, download_images
from xml_utils.xml_loader import download_xml, get_gene_xml_url, download_lookup_df

st.set_page_config(layout="wide", page_title="Pathology Summary", page_icon=":tada")


def create_download_link(df, format: str, filename: str = "filtered_data"):
    if format == "csv":
        data = df.to_csv(index=False)
        filename = "filtered_data.csv"
    elif format == "excel":
        with pd.ExcelWriter(f"{filename}.xlsx") as writer:
            df.to_excel(writer, index=False)

    b64_data = base64.b64encode(data.encode()).decode()
    href = f'<a href="data:file/{format};base64,{b64_data}" download="{filename}">Download as {format.upper()}</a>'
    return href


def filter_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds a UI on top of a dataframe to let viewers filter columns

    Args:
        df (pd.DataFrame): Original dataframe

    Returns:
        pd.DataFrame: Filtered dataframe
    """
    with st.sidebar:
        modify = st.checkbox("Add filters")

        if not modify:
            return df

        df = df.copy()

        # Try to convert datetimes into a standard format (datetime, no timezone)
        for col in df.columns:
            if is_object_dtype(df[col]):
                try:
                    df[col] = pd.to_datetime(df[col])
                except Exception:
                    pass

            if is_datetime64_any_dtype(df[col]):
                df[col] = df[col].dt.tz_localize(None)

        modification_container = st.container()

        with modification_container:
            to_filter_columns = st.multiselect("Filter dataframe on", df.columns)
            for column in to_filter_columns:
                left, right = st.columns((1, 20))
                # Treat columns with < 10 unique values as categorical
                if is_categorical_dtype(df[column]) or df[column].nunique() < 10:
                    user_cat_input = right.multiselect(
                        f"Values for {column}",
                        df[column].unique(),
                        default=list(df[column].unique()),
                    )
                    df = df[df[column].isin(user_cat_input)]
                elif is_numeric_dtype(df[column]):
                    _min = float(df[column].min())
                    _max = float(df[column].max())
                    step = (_max - _min) / 100
                    user_num_input = right.slider(
                        f"Values for {column}",
                        min_value=_min,
                        max_value=_max,
                        value=(_min, _max),
                        step=step,
                    )
                    df = df[df[column].between(*user_num_input)]
                elif is_datetime64_any_dtype(df[column]):
                    user_date_input = right.date_input(
                        f"Values for {column}",
                        value=(
                            df[column].min(),
                            df[column].max(),
                        ),
                    )
                    if len(user_date_input) == 2:
                        user_date_input = tuple(map(pd.to_datetime, user_date_input))
                        start_date, end_date = user_date_input
                        df = df.loc[df[column].between(start_date, end_date)]
                else:
                    user_text_input = right.text_input(
                        f"Substring or regex in {column}",
                    )
                    if user_text_input:
                        df = df[df[column].astype(str).str.contains(user_text_input)]

    return df


def main(lookup_df):
    with st.sidebar:
        # Allow selection of multiple genes
        genes = lookup_df["gene"].unique()
        genes.sort()
        selected_genes = st.multiselect(label="Select genes", options=genes)
        st.markdown("Selected genes:")
        st.markdown(", ".join(selected_genes))

    all_info = []  # Initialize an empty list to collect all info
    interactions = pd.DataFrame(columns=["Interaction", "Interaction type", "Confidence", "MI score", "# Interactions"])
    for gene in selected_genes:
        xml_url, interaction_url = get_gene_xml_url(gene, lookup_df)
        xml_filename = download_xml(xml_url, gene)
        xml = load_xml(xml_filename)
        info = process_xml(xml)
        all_info.extend(info)

        interaction_df = get_interactions_from_html(gene=gene, url=interaction_url)
        interactions = interactions.merge(interaction_df, how="outer")

    info_df = pd.DataFrame(all_info)  # with info from all of the selected genes

    filtered_df = filter_dataframe(info_df)
    st.dataframe(filtered_df)
    st.write(f"Gene interactions to consider: ")
    st.dataframe(interactions)

    # download the dataframe
    file_format = st.selectbox("Select file format", ["CSV", "Excel"], index=0)

    buffer = io.BytesIO()
    if file_format == "CSV":
        filtered_df.to_csv(buffer, index=False)
        mime_type = "text/csv"
        file_ext = "csv"
    elif file_format == "Excel":
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            filtered_df.to_excel(writer, index=False)
        mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        file_ext = "xlsx"

    buffer.seek(0)

    st.download_button(
        label=f"Download Data as {file_format}", data=buffer, file_name=f"filtered_data.{file_ext}", mime=mime_type
    )

    if st.button("Prepare Image download link"):
        image_urls = filtered_df["imageUrl"].tolist()
        image_files = download_images(image_urls)
        zip_file_path = zip_images(image_files)

        # Provide the zip file for download
        with open(zip_file_path, "rb") as file:
            st.download_button(label="Download Images", data=file, file_name="images.zip", mime="application/zip")


if __name__ == "__main__":
    lookup_df = download_lookup_df()
    main(lookup_df)
