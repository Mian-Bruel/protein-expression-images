import pandas as pd
import streamlit as st

from xml_utils.xml_parser import load_xml, process_xml
from xml_utils.xml_loader import download_xml, get_gene_xml, download_lookup_df

st.set_page_config(layout="wide", page_title="Pathology Summary", page_icon=":tada")


def main(lookup_df):
    with st.sidebar:
        # Show available checkpoints
        genes = lookup_df["gene"].unique()
        genes.sort()
        gene = st.selectbox(label="gene", options=genes)
        st.markdown("Selected gene:")
        st.markdown(gene)

    # Load selected gene:
    xml_url = get_gene_xml(gene, lookup_df)
    xml_filename = download_xml(xml_url, gene)
    xml = load_xml(xml_filename)
    info = process_xml(xml)
    info_df = pd.DataFrame(info)

    st.dataframe(info_df)


if __name__ == "__main__":
    lookup_df = download_lookup_df()
    main(lookup_df)
