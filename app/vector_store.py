from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
import os


EMBEDDING_MODEL = "mxbai-embed-large"
_APP_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(_APP_DIR, "db", "legal_docs")


def get_embeddings():
    return OllamaEmbeddings(model=EMBEDDING_MODEL)


def get_vector_store(embeddings):
    return Chroma(
        collection_name="legal_documents",
        embedding_function=embeddings,
        persist_directory=DB_PATH
    )


def initialize_vector_store(embeddings, documents=None):
    os.makedirs(DB_PATH, exist_ok=True)
    vector_store = get_vector_store(embeddings)
    
    print("Adding documents to vector store...")
    if documents:
        documents = chunks_to_documents(documents)
        ids = [str(i) for i in range(len(documents))]
        vector_store.add_documents(documents=documents, ids=ids)
    print("Documents added successfully!")
    
    return vector_store


def get_retriever(search_kwargs=None):
    embeddings = get_embeddings()
    vector_store = get_vector_store(embeddings)
    
    if search_kwargs is None:
        search_kwargs = {"k": 5}
    
    return vector_store.as_retriever(
        search_kwargs=search_kwargs,
        search_type="similarity"
    )

def chunks_to_documents(chunks):
    documents = []

    for chunk in chunks:
        doc = Document(
            page_content=chunk["text"],
            metadata={
                "act": "Bharatiya Nyaya Sanhita, 2023",
                "section": chunk.get("section_number"),
                "section_title": chunk.get("section_title"),
                "chapter_number": chunk.get("chapter_number"),
                "chapter_title": chunk.get("chapter_title"),
                "subsection": chunk.get("subsection")
            }
        )
        documents.append(doc)

    return documents