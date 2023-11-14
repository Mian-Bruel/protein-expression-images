import xml.etree.ElementTree as ET

import pandas as pd


def load_xml(filename):
    tree = ET.parse(filename)
    root = tree.getroot()
    return root


def get_name(entry):
    return entry.find("name").text


def get_synonyms(entry):
    return [syn.text for syn in entry.findall("synonym")]


def get_patient_info(root, names):
    # FIXME there appears to be an invalid symbol in some XMLs that causes an error

    # Create an empty list to store patient info for each image
    patient_images_info = []

    # Iterate through each tissueCell element in the XML
    for tissue_cell in root.findall(".//tissueExpression"):
        summary = tissue_cell.find("summary")

        # if type is not 'pathology', skip this tissueCell
        if summary.attrib["type"] != "pathology":
            continue
        # Iterate through each patient element inside the current tissueCell
        for patient in tissue_cell.findall(".//patient"):
            # Extract basic patient info
            patient_id = int(patient.find("patientId").text)
            sex = patient.find("sex").text
            age = int(patient.find("age").text)

            staining_element = patient.find("level[@type='staining']")
            staining = staining_element.text if staining_element is not None else None

            intensity = patient.find("level[@type='intensity']")
            intensity = intensity.text if intensity is not None else None

            quantity = patient.find("quantity")
            quantity = quantity.text if quantity is not None else None

            location = patient.find("location")
            location = location.text if location is not None else None

            # Extract SNOMED descriptions and images
            for sample in patient.findall(".//sample"):
                snomed_parameters = sample.find("snomedParameters")
                tissue_descriptions = [snomed.attrib["tissueDescription"] for snomed in snomed_parameters.findall("snomed")]

                assay_image = sample.find("assayImage")
                for image in assay_image.findall("image"):
                    image_url = image.find("imageUrl").text
                    patient_images_info.append(
                        {
                            "gene_names": names,  # This is a list of gene synonyms
                            "patientId": str(patient_id),
                            "sex": sex,
                            "age": age,
                            "staining": staining,
                            "intensity": intensity,
                            "quantity": quantity,
                            "location": location,
                            "tissueDescriptions": tissue_descriptions,
                            "imageUrl": image_url,
                        }
                    )
    return patient_images_info


def process_xml(xml):
    synonyms = []
    for entry in xml.findall("entry"):
        name = get_name(entry)
        synonyms = get_synonyms(entry)

    names = [name] + synonyms
    info = get_patient_info(xml, names)

    return info


if __name__ == "__main__":
    filename = "xml_files/ANGPTL8_latest.xml"
    xml = load_xml(filename)
    info = process_xml(xml)
    if len(info) == 0:
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
        info_df = pd.DataFrame(info)
    print(info_df.head())
