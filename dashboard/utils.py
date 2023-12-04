import os

import requests
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
