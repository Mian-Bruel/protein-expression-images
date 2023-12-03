import pandas as pd

from xml_utils.xml_loader import get_gene_xml_url
from xml_utils.interactions import get_interactions_from_html


def process_data(filters, selected_genes, lookup_df):
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
    all_info = []

    interactions = pd.DataFrame(columns=["Interaction", "Interaction type", "Confidence", "MI score", "# Interactions"])
    for gene in selected_genes:
        xml_url, interaction_url = get_gene_xml_url(gene, lookup_df)
        interaction_df = get_interactions_from_html(gene=gene, url=interaction_url)
        interactions = interactions.merge(interaction_df, how="outer")

    if len(all_info) == 0:
        filtered_df = pd.DataFrame(
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
        filtered_df = pd.DataFrame(all_info)

    # Apply additional filtering based on 'filters' argument
    # You need to implement this part based on how you want to filter the data
    # Example: filtered_df = filtered_df[filtered_df['patientId'] == filters['patientId']]

    return filtered_df, interactions
