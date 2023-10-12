"""
This module contains functions for performing mathematical operations.
"""
__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
import chromadb
import streamlit as st
from PyPDF2 import PdfReader
#from dotenv import load_dotenv
from htmlTemplates import css, table_template
from langchain.text_splitter import RecursiveCharacterTextSplitter



def get_pdf_text(pdf_docs):
    pdf_text = []
    for pdf in pdf_docs:
        text = ""
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
        pdf_text.append(text)
    return pdf_text


def get_text_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=10000,
        chunk_overlap=0,
        length_function=len
    )
    chunks = []
    for txt in text:
        chunk = text_splitter.split_text(txt)
        chunks.extend(chunk)
    return chunks


def get_vectorstore(text_chunks, job_description):
    chroma_client = chromadb.Client()
    collection = chroma_client.create_collection(name="my_collection")
    #metadata = ["mysource" for i in range(len(text_chunks))]
    collection.add(
        documents=[f"{text_chunks[i]}" for i in range(len(text_chunks))],
        ids=[f"{k}" for k in range(len(text_chunks))]
    )
    query1 = job_description
    results = collection.query(
        query_texts=query1,
        n_results=len(text_chunks)
    )
    return results

def percentage(match):
    res = (1/(1+match))*100
    return f'{res:.2f}%'

def get_rank_table(vectorstore):
    rank_table = []
    for i in range(len((vectorstore["ids"])[0])):
        l2_dist = (vectorstore["distances"][0])[i]
        rank_table.append({
            "Rank": f'{i+1}',
            "Name": f'{(vectorstore["ids"][0])[i]}',
            "Match": f'{percentage(l2_dist)}'
        })
    return rank_table

def create_rank_table(rank_table):
    for rank in rank_table:
        st.write(table_template.replace("{{Rank}}", rank["Rank"]).replace("{{Name}}", rank["Name"])
                 .replace("{{Match}}", rank["Match"]), unsafe_allow_html=True)

def normalize_rank_table(rank_table):
    # use this as an extra feature button
    pass

def main():
    #load_dotenv()
    st.set_page_config(page_title="Resume Ranker", page_icon=":books:")
    st.write(css, unsafe_allow_html=True)

    if "rank_table" not in st.session_state:
        st.session_state.rank_table = None

    st.header("Resume Ranker :books:")
    job_description = st.text_input("Enter Job Description: ")

    with st.sidebar:
        st.subheader("Analyze Resume")
        pdf_docs = st.file_uploader(
            "Input Resume and click Analyze", accept_multiple_files=True)

    if st.button("Analyze"):
        with st.spinner("Processing"):
            # get pdf text
            raw_text = get_pdf_text(pdf_docs)

            # get the text chunks
            text_chunks = get_text_chunks(raw_text)
            # st.write(text_chunks)

            # create vector store
            if job_description:
                vectorstore = get_vectorstore(text_chunks, job_description)

            rank = get_rank_table(vectorstore)

            create_rank_table(rank)

            # st.session_state.rank_table = create_rank_table(rank)

    #     # Print the table in the main page
    # if st.session_state.rank_table:
    #     table_container = st.container()
    #     with table_container:
    #         st.write("Rank Table:")
    #         st.dataframe(st.session_state.rank_table)


if __name__ == "__main__":
    main()