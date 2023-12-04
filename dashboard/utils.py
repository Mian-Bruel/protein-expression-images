import os
from io import StringIO

import bs4
import requests
import pandas as pd
from constants import PER_PAGE, API_PATHS


def send_request(filters, request_type, df=None, selected_genes=None, page=1):
    url = os.getenv("API_URL")

    filtered_filters = {"perPage": PER_PAGE, "page": page}

    if len(selected_genes) > 0:
        filtered_filters["genes[]"] = selected_genes

    if filters["patientId"] != "":
        filtered_filters["patientId"] = int(filters["patientId"])

    if filters["sex"] != "Any":
        filtered_filters["sex"] = filters["sex"].upper()

    filtered_filters["ageFrom"] = filters["age"][0]
    filtered_filters["ageTo"] = (filters["age"][1],)

    if len(filters["staining"]) > 0:
        filtered_filters["stainings[]"] = filters["staining"]

    if len(filters["intensity"]) > 0:  # FIXME: I want to live
        filtered_filters["intensities[]"] = filters["intensity"]

    if len(filters["quantity"]) > 0:
        filtered_filters["quantities[]"] = [quantity if quantity != "None" else None for quantity in filters["quantity"]]

    if filters["location"] != "":
        filtered_filters["location"] = filters["location"]

    if filters["selected_tissues"] != "":
        filtered_filters["tissueDescription"] = filters["selected_tissues"]

    response = requests.get(url + API_PATHS[request_type], filtered_filters)

    return response


# Copies from xml utils for correct imports in streamlit deployment
# =================================================================
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


def get_gene_xml_url(gene: str, lookup_df: pd.DataFrame, version: str = "latest"):
    """
    returns links to xml and interactions
    """
    ensembl_id = lookup_df.loc[lookup_df["gene"] == gene, "ensembl"].iat[0]
    return version_to_xml_url(ensembl_id, version), version_to_interactions_url(ensembl_id, gene, version)


def version_to_xml_url(ensembl_id: str, version: str = "latest") -> str:
    version = "www" if version == "latest" else version
    return f"https://{version}.proteinatlas.org/{ensembl_id}.xml"


def version_to_interactions_url(ensembl_id: str, gene: str, version: str = "latest") -> str:
    version = "www" if version == "latest" else version
    return f"https://{version}.proteinatlas.org/{ensembl_id}-{gene}/interaction"


def get_interactions_from_html(gene: str, url: str) -> pd.DataFrame:
    response = requests.get(url)

    parsed = bs4.BeautifulSoup(response.text, "html.parser")

    # dataframe of interactions
    table = parsed.find("table", class_="sortable")

    if table is None:
        return pd.DataFrame(columns=["Interaction", "Interaction type", "Confidence", "MI score", "# Interactions"])

    headers = [header.text for header in table.find("thead").find_all("th")]

    rows = table.find("tbody").find_all("tr")

    # Initialize an empty list to store the data
    data = []

    # Iterate through the rows and extract data
    for row in rows:
        cells = row.find_all(["td", "th"])  # Both data cells and header cells
        row_data = [cell.get_text(strip=True) for cell in cells]
        data.append(row_data)

    gene_list = [gene] * len(rows)
    # Create a Pandas DataFrame
    df = pd.DataFrame(data, columns=headers)
    df["gene"] = gene_list

    # change column types for filtering
    df["MI score"] = df["MI score"].astype(float)
    df["# Interactions"] = df["# Interactions"].astype(int)

    return df
