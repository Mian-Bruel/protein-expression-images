import streamlit as st


def render_sidebar(lookup_df):
    """
    Render the sidebar and return the values from it.

    Args:
        lookup_df (pd.DataFrame): The lookup dataframe.

    Returns:
        submit_button (streamlit.form_submit_button): The 'Apply Changes' button. Used to determine if the button was clicked in the `app.py` file.
        filters (dict): A dictionary of the values of the filters.
        selected_genes (list): A list of the selected genes.
    """
    with st.sidebar:
        with st.form(key="sidebar_form"):
            # Apply filters button
            submit_button = st.form_submit_button("Apply Changes")

            st.title("Filter main dataframe")

            # Gene selection multiselect
            genes = lookup_df["gene"].unique()
            genes.sort()
            selected_genes = st.multiselect(label="Select genes", options=genes, default=[])

            # Text input for patient ID
            patient_id = st.text_input("Patient ID")

            # Radio buttons for sex
            sex = st.radio("Sex", ["Male", "Female", "Any"], index=2)

            # Slider for age
            age = st.slider("Age", 0, 100, (0, 100))

            # Selectbox for staining
            staining = st.multiselect("Staining", options=["Low", "Medium", "High", "Not detected"], default=[])

            # Radio buttons for intensity
            intensity = st.multiselect("Intensity", options=["Weak", "Moderate", "Strong", "Negative"], default=[])

            quantity_options = ["75%-25%", ">75%", "None", "<25%"]
            quantity = st.multiselect("Quantity", quantity_options, default=[])

            # Text input for location
            location = st.text_input("Location")

            # Multiselect for tissue descriptions
            tissue_descriptions = st.text_input("Tissue Descriptions")

            # st.title("Filter interactions dataframe")

            # # Selectbox for interaction type
            # interaction_type_options = ["Any", "Physical association", "Direct interaction"]
            # interaction_type = st.selectbox("Interaction type", interaction_type_options, index=0)

            # # Selectbox for confidence
            # confidence_options = ["Any", "High", "Medium", "Low"]
            # confidence = st.selectbox("Confidence", confidence_options, index=0)

            # # Slider for MI score for floats between 0 and 1
            # mi_score = st.slider("MI score", 0.0, 1.0, (0.0, 1.0))

            # # Slider for # Interactions
            # num_interactions = st.slider("# Interactions", 0, 500, (0, 500))

    # Return the values from the sidebar
    filters = {
        "patientId": patient_id,
        "sex": sex,
        "age": age,
        "staining": staining,
        "intensity": intensity,
        "quantity": quantity,
        "location": location,
        "selected_tissues": tissue_descriptions,
        # "interaction_type": interaction_type,
        # "confidence": confidence,
        # "mi_score": mi_score,
        # "num_interactions": num_interactions,
    }

    return submit_button, filters, selected_genes
