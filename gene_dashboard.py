import io
import base64

import pandas as pd
import streamlit as st

from xml_utils.xml_parser import load_xml, process_xml
from xml_utils.interactions import get_interactions_from_html
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


def apply_filters(df, filters):
    # Check and apply patient ID filter
    if "patientId" in filters and filters["patientId"]:
        df = df[df["patientId"] == filters["patientId"]]

    # Check and apply sex filter, if 'Any' is not selected
    if "sex" in filters and filters["sex"] != "Any":
        df = df[df["sex"] == filters["sex"]]

    # Check and apply age filter
    if "age" in filters:
        min_age, max_age = filters["age"]
        df = df[(df["age"] >= min_age) & (df["age"] <= max_age)]

    # Check and apply staining filter, if 'Any' is not selected
    if "staining" in filters and filters["staining"] != "Any":
        df = df[df["staining"] == filters["staining"]]

    # Check and apply intensity filter, if 'Any' is not selected
    if "intensity" in filters and filters["intensity"] != "Any":
        df = df[df["intensity"] == filters["intensity"]]

    # Check and apply quantity filter
    if "quantity" in filters and filters["quantity"] != "Any":
        df = df[df["quantity"] == filters["quantity"]]

    # Check and apply location filter
    if "location" in filters and filters["location"]:
        df = df[df["location"].astype(str).str.contains(filters["location"])]

    # Check and apply tissue descriptions filter
    if "selected_tissues" in filters and filters["selected_tissues"]:
        # extract items from tissueDescriptions column and check if filters['selected_tissues'] matches regex
        df = df[df["tissueDescriptions"].astype(str).str.contains(filters["selected_tissues"])]

    return df


def main(lookup_df):
    # Initialize session state to store the filtered dataframe and gene selections
    if "filters" not in st.session_state:
        st.session_state.filters = {}

    if "selected_genes" not in st.session_state:
        st.session_state.selected_genes = []

    # empty DFs
    if "filtered_df" not in st.session_state:
        st.session_state.filtered_df = pd.DataFrame()
    if "interactions" not in st.session_state:
        st.session_state.interactions = pd.DataFrame()

    # Use a form for the entire sidebar to prevent refreshes
    with st.sidebar:
        with st.form(key="sidebar_form"):
            # Gene selection multiselect
            genes = lookup_df["gene"].unique()
            genes.sort()
            st.session_state.selected_genes = st.multiselect(label="Select genes", options=genes, default=[])

            # Text input for patient ID
            patient_id = st.text_input(
                "Patient ID",
                value=st.session_state.filters.get("patientId", ""),
            )

            # Radio buttons for sex
            sex = st.radio(
                "Sex",
                ["Male", "Female", "Any"],
                index=2
                if "sex" not in st.session_state.filters
                else ["Male", "Female", "Any"].index(st.session_state.filters["sex"]),
            )

            # Slider for age
            age = st.slider(
                "Age",
                0,
                100,
                (st.session_state.filters.get("age", [0, 100])),
            )

            # Selectbox for staining
            staining = st.selectbox(
                "Staining",
                ["Any", "Low", "Medium", "High", "Not detected"],
                index=0
                if "staining" not in st.session_state.filters
                else ["Any", "Low", "Medium", "High", "Not detected"].index(st.session_state.filters["staining"]),
            )

            # Radio buttons for intensity
            intensity = st.selectbox(
                "Intensity",
                ["Any", "Weak", "Moderate", "Negative"],
                index=0
                if "intensity" not in st.session_state.filters
                else ["Any", "Weak", "Moderate", "Negative"].index(st.session_state.filters["intensity"]),
            )

            quantity_options = ["Any", "75%-25%", ">75%", "None", "<25%"]
            quantity = st.selectbox(
                "Quantity",
                quantity_options,
                index=0
                if "quantity" not in st.session_state.filters or st.session_state.filters["quantity"] not in quantity_options
                else quantity_options.index(st.session_state.filters["quantity"]),
            )
            # Text input for location
            location = st.text_input(
                "Location",
                value=st.session_state.filters.get("location", ""),
            )

            # Multiselect for tissue descriptions
            tissue_descriptions = st.text_input(
                "Tissue Descriptions",
                value=st.session_state.filters.get("selected_tissues", ""),
            )

            # Apply filters button
            submit_button = st.form_submit_button("Apply Changes")

    if submit_button:
        # Update the rest of the filters
        st.session_state.filters.update(
            {
                "patientId": patient_id,
                "sex": "Any" if sex == "Any" else sex,
                "age": age,
                "staining": "Any" if staining == "Any" else staining,
                "intensity": "Any" if intensity == "Any" else intensity,
                "quantity": quantity,
                "location": location,
                "selected_tissues": tissue_descriptions,
            }
        )

        # Perform the data processing only when the 'Apply Changes' button is clicked
        all_info = []
        interactions = pd.DataFrame(columns=["Interaction", "Interaction type", "Confidence", "MI score", "# Interactions"])
        for gene in st.session_state.selected_genes:
            xml_url, interaction_url = get_gene_xml_url(gene, lookup_df)
            xml_filename = download_xml(xml_url, gene)
            xml = load_xml(xml_filename)
            info = process_xml(xml)
            all_info.extend(info)

            interaction_df = get_interactions_from_html(gene=gene, url=interaction_url)
            interactions = interactions.merge(interaction_df, how="outer")

        # Update the data in the session state
        if len(all_info) == 0:
            info_df = pd.DataFrame(
                columns=[
                    "gene_names",
                    "patientId",
                    "sex",
                    "age",
                    "staining",
                    "intensity",
                    "quantity",
                    "location",
                    "tissueDescriptions",
                    "imageUrl",
                ]
            )
        else:
            info_df = pd.DataFrame(all_info)

        filtered_df = apply_filters(info_df, st.session_state.filters)
        st.session_state.filtered_df = filtered_df
        st.session_state.interactions = interactions

    # Always show the DataFrame and interaction data

    st.write(f"Total Data Points in DataFrame: {len(st.session_state.filtered_df)}")
    st.dataframe(st.session_state.filtered_df)
    st.write("Gene interactions to consider: ")
    st.dataframe(st.session_state.interactions)

    # Download the dataframe as CSV
    buffer_csv = io.BytesIO()
    st.session_state.filtered_df.to_csv(buffer_csv, index=False)
    buffer_csv.seek(0)
    st.download_button(label="Download Data as CSV", data=buffer_csv, file_name="filtered_data.csv", mime="text/csv")

    # Download the dataframe as Excel
    buffer_excel = io.BytesIO()
    with pd.ExcelWriter(buffer_excel, engine="openpyxl") as writer:
        st.session_state.filtered_df.to_excel(writer, index=False)
    buffer_excel.seek(0)
    st.download_button(
        label="Download Data as Excel",
        data=buffer_excel,
        file_name="filtered_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

    # The image download functionality remains unchanged
    if st.button("Prepare Image download link"):
        image_urls = st.session_state.filtered_df["imageUrl"].tolist()
        image_files = download_images(image_urls)
        zip_file_path = zip_images(image_files)

        # Provide the zip file for download
        with open(zip_file_path, "rb") as file:
            st.download_button(label="Download Images", data=file, file_name="images.zip", mime="application/zip")


if __name__ == "__main__":
    lookup_df = download_lookup_df()
    main(lookup_df)
