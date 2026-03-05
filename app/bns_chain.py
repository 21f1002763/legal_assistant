from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from vector_store import get_retriever
import json

LLAMA_MODEL = "llama3.2"

DISCLAIMER = "This is an AI-powered legal research tool. It does not constitute legal advice. Please consult a qualified advocate for legal matters."


def create_bns_search_chain():
    model = OllamaLLM(model=LLAMA_MODEL)
    retriever = get_retriever(search_kwargs={"k": 5})
    
    template = """You are an expert legal assistant specializing in the Bharatiya Nyaya Sanhita (BNS), 2023 - the new Indian criminal code that replaced the Indian Penal Code.

You must provide accurate, helpful information about BNS sections with proper citations.

IMPORTANT RULES:
1. Always cite section numbers in format "Section X – [Title] (BNS)"
2. If discussing punishment, mention the specific section
3. Never provide legal advice - always include the disclaimer
4. Be precise about which chapter and section you're referring to

Context from BNS document:
{context}

User Question: {question}

Provide your response with:
1. A clear, concise answer
2. Relevant section citations in format "Section [number] – [Title] (BNS)"
3. The disclaimer at the end

Response:
"""
    
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | model
    
    return chain, retriever


def search_bns(query: str, chapter_filter: str = None, section_filter: str = None, limit: int = 10):
    chain, _ = create_bns_search_chain()
    retriever = get_retriever(search_kwargs={"k": limit})
    
    if section_filter:
        query_with_filter = f"{query} section {section_filter}"
    else:
        query_with_filter = query
    
    context_docs = retriever.invoke(query_with_filter)
    context = "\n\n".join([doc.page_content for doc in context_docs])
    
    result = chain.invoke({
        "context": context,
        "question": query,
        "DISCLAIMER": DISCLAIMER
    })
    
    sections = []
    citations = []
    seen_sections = set()
    
    for doc in context_docs:
        section_num = doc.metadata.get("section", "Unknown")
        if section_num and section_num not in seen_sections:
            seen_sections.add(section_num)
            sections.append({
                "section_number": section_num,
                "section_title": doc.metadata.get("section_title", "Unknown"),
                "chapter_number": doc.metadata.get("chapter_number", "Unknown"),
                "chapter_title": doc.metadata.get("chapter_title", "Unknown"),
                "preview": doc.page_content[:300] + "..." if len(doc.page_content) > 300 else doc.page_content
            })
            citations.append(f"Section {section_num} – {doc.metadata.get('section_title', 'Unknown')} (BNS)")
    
    return {
        "answer": result,
        "sections": sections,
        "citations": citations
    }


def get_all_sections():
    from vector_store import get_vector_store, get_embeddings
    embeddings = get_embeddings()
    vector_store = get_vector_store(embeddings)
    
    results = vector_store.get(include=["metadatas"])
    
    sections_map = {}
    for i, metadata in enumerate(results.get("metadatas", [])):
        section_num = metadata.get("section", "")
        if section_num and section_num not in sections_map:
            sections_map[section_num] = {
                "section_number": section_num,
                "section_title": metadata.get("section_title", "Unknown"),
                "chapter_number": metadata.get("chapter_number", "Unknown"),
                "chapter_title": metadata.get("chapter_title", "Unknown")
            }
    
    chapters_map = {}
    for section in sections_map.values():
        chap_num = section["chapter_number"]
        if chap_num not in chapters_map:
            chapters_map[chap_num] = {
                "chapter_number": chap_num,
                "chapter_title": section["chapter_title"]
            }
    
    return {
        "sections": list(sections_map.values()),
        "chapters": list(chapters_map.values())
    }


def get_section_by_number(section_number: str):
    from vector_store import get_vector_store, get_embeddings
    embeddings = get_embeddings()
    vector_store = get_vector_store(embeddings)
    
    results = vector_store.get(where={"section": section_number}, include=["documents", "metadatas"])
    
    if not results["documents"]:
        return None
    
    doc = results["documents"][0]
    metadata = results["metadatas"][0]
    
    return {
        "section_number": metadata.get("section", section_number),
        "section_title": metadata.get("section_title", "Unknown"),
        "chapter_number": metadata.get("chapter_number", "Unknown"),
        "chapter_title": metadata.get("chapter_title", "Unknown"),
        "text": doc,
        "act": metadata.get("act", "Bharatiya Nyaya Sanhita, 2023")
    }


def create_chat_chain():
    model = OllamaLLM(model=LLAMA_MODEL)
    retriever = get_retriever(search_kwargs={"k": 3})
    
    template = """You are an expert legal assistant specializing in the Bharatiya Nyaya Sanhita (BNS), 2023.

Previous conversation:
{chat_history}

Context from BNS:
{context}

Current question: {question}

Provide a helpful response citing relevant BNS sections. Include the disclaimer at the end.

{DISCLAIMER}
"""
    
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | model
    
    return chain, retriever


def chat_bns(messages: list, context_sections: list = None):
    chain, retriever = create_chat_chain()
    
    chat_history = ""
    for msg in messages[:-1]:
        role = "User" if msg["role"] == "user" else "Assistant"
        chat_history += f"{role}: {msg['content']}\n"
    
    current_question = messages[-1]["content"] if messages else ""
    
    context_docs = retriever.invoke(current_question)
    context = "\n\n".join([doc.page_content for doc in context_docs])
    
    citations = []
    for doc in context_docs:
        section_num = doc.metadata.get("section", "Unknown")
        citations.append(f"Section {section_num} – {doc.metadata.get('section_title', 'Unknown')} (BNS)")
    
    result = chain.invoke({
        "chat_history": chat_history,
        "context": context,
        "question": current_question,
        "DISCLAIMER": DISCLAIMER
    })
    
    return {
        "message": result,
        "citations": list(set(citations))
    }
