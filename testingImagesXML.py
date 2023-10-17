import xml.etree.ElementTree as ET

# Parse the XML file
tree = ET.parse("FUT3.xml")
root = tree.getroot()

gene_name = "FUT3"
gene_entry = None

for entry in root.findall(".//entry"):
    name = entry.find("name").text
    if name == gene_name:
        gene_entry = entry
        break

if gene_entry is not None:
    # Extract image URLs related to the gene FUT3
    image_urls = []
    for image in gene_entry.findall(".//image"):
        image_url = image.find("imageUrl").text
        image_type = image.get("imageType")
        image_urls.append((image_type, image_url))

    # Print the image URLs
    for image_type, image_url in image_urls:
        print(f"Image Type: {image_type}")
        print(f"Image URL: {image_url}")
else:
    print(f"Gene {gene_name} not found in the XML data.")
