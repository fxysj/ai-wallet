from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter

from travel_ai.app.graph.vector_search import vectorstore


def load_pdfs_to_vectorstore(pdf_path):
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()
    text_splitter = CharacterTextSplitter(chunk_size=3000, chunk_overlap=0)
    docs = text_splitter.split_documents(documents)
    vectorstore.add_documents(docs)