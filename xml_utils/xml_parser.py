import xml.etree.ElementTree as ET


def load_xml(filename):
    tree = ET.parse(filename)
    root = tree.getroot()
    return root


def get_name(entry):
    return entry.find("name").text


def get_synonyms(entry):
    return [syn.text for syn in entry.findall("synonym")]


def process_xml(xml):
    info = {}
    synonyms = []
    for entry in xml.findall("entry"):
        name = get_name(entry)
        synonyms = get_synonyms(entry)

    info["names"] = [name] + synonyms
    return info


if __name__ == "__main__":
    filename = "xml_files/SLC2A3_latest.xml"
    xml = load_xml(filename)
    info = process_xml(xml)
    print(info)
