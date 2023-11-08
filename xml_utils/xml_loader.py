import os
from io import StringIO

import requests
import pandas as pd


def download_lookup_df():
    # Download the data
    response = requests.get("https://www.proteinatlas.org/search?format=tsv")
    response.raise_for_status()

    # Convert the downloaded data to a DataFrame
    data = StringIO(response.text)
    query_df = pd.read_csv(data, sep="\t")

    # Create a subset with only 'Gene' and 'Ensembl' columns
    lookup_df = query_df[["Gene", "Ensembl"]].rename(columns={"Gene": "gene", "Ensembl": "ensembl"})

    return lookup_df


def version_to_xml_url(ensembl_id: str, version: str = "latest") -> str:
    version = "www" if version == "latest" else version
    return f"https://{version}.proteinatlas.org/{ensembl_id}.xml"


def version_to_interactions_url(ensembl_id: str, gene: str, version: str = "latest") -> str:
    version = "www" if version == "latest" else version
    return f"https://{version}.proteinatlas.org/{ensembl_id}-{gene}/interaction"


def get_gene_xml_url(gene: str, lookup_df: pd.DataFrame, version: str = "latest"):
    """
    returns links to xml and interactions
    """
    ensembl_id = lookup_df.loc[lookup_df["gene"] == gene, "ensembl"].iat[0]
    return version_to_xml_url(ensembl_id, version), version_to_interactions_url(ensembl_id, gene, version)


def download_xml(url: str, gene: str, version: str = "latest") -> None:
    response = requests.get(url)
    response.raise_for_status()

    folder_name = "./xml_files"
    os.makedirs(folder_name, exist_ok=True)

    file_name = f"{folder_name}/{gene}_{version}.xml"
    with open(file_name, "w") as file:
        file.write(response.text)

    return file_name


if __name__ == "__main__":
    gene = "A1BG"
    lookup_df = download_lookup_df()
    xml_url = get_gene_xml_url(gene, lookup_df)
    file_name = download_xml(xml_url, gene)
