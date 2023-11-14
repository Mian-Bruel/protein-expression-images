import bs4
import requests
import pandas as pd


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


if __name__ == "__main__":
    gene = "SLC2A3"
    ensID = "ENSG00000059804"
    url = f"https://www.proteinatlas.org/{ensID}-{gene}/interaction"
    print(get_interactions_from_html(gene, url))
