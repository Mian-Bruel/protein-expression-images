import pandas as pd
from utils import send_request, get_gene_xml_url, get_interactions_from_html


def process_data(filters, selected_genes, lookup_df, page):
    """
    Process the data based on the filters and selected genes

    This function is called when the 'Apply Changes' button is clicked.


    Args:
        filters (dict): A dictionary of the values of the filters.
        selected_genes (list): A list of the selected genes.
        lookup_df (pd.DataFrame): The lookup dataframe. With the gene names and their corresponding XML URLs.

    Returns:
        filtered_df (pd.DataFrame): The filtered dataframe.
        interactions (pd.DataFrame): The interactions dataframe.

    TODO: Communicate with the server with the selected genes and filters to get the filtered dataframe.
        We'll be using requests library to do this.
    For now the interactions dataframe is left as is. We might add it to PHP later.

    """
    # Perform the data processing only when the 'Apply Changes' button is clicked

    interactions = pd.DataFrame(columns=["Interaction", "Interaction type", "Confidence", "MI score", "# Interactions"])
    for gene in selected_genes:
        break
        # TODO: interactions from rest api
        xml_url, interaction_url = get_gene_xml_url(gene, lookup_df)
        interaction_df = get_interactions_from_html(gene=gene, url=interaction_url)
        interactions = interactions.merge(interaction_df, how="outer")

    response = send_request(filters, "list", selected_genes=selected_genes, page=page)

    # If the response is not 200, return an empty dataframe
    if response.status_code != 200:
        return pd.DataFrame(), interactions, 0

    response_data = response.json()

    total_number = response_data["totalItems"]
    data = response_data["data"]
    processed_data = []

    for entry in data:
        entry_data = {
            "staining": entry["staining"],
            "intensity": entry["intensity"],  # FIXME: Grep failed
            "quantity": entry["quantity"],
            "location": entry["location"],
            "patientId": entry["patient"]["id"],
            "patientAge": entry["patient"]["age"],
            "patientSex": entry["patient"]["sex"],
            "geneName": entry["gene"]["name"],
        }

        images = []
        tissue_description = ""

        for sample in entry["samples"]:
            images.append(sample["img"])
            description = sample["tissueDescription"]

            if len(description) > len(tissue_description):
                tissue_description = description

        entry_data["tissue_description"] = tissue_description
        entry_data["images"] = ", ".join(images)

        processed_data.append(entry_data)

    filtered_df = pd.DataFrame(processed_data)

    return filtered_df, interactions, total_number
