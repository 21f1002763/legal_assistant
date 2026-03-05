from vector_store import initialize_vector_store, get_embeddings
from models import DocumentType

import pdfplumber
import re

PDF_PATH = "app/documents/bare_acts/BNS.pdf"
SECTION_REGEX = re.compile(
    r"\n(?P<section>\d+)\.\s+(?P<title>[A-Z][^\n—]+)—",
    re.MULTILINE
)
CHAPTER_REGEX = re.compile(
    r"CHAPTER\s+([IVXLCDM]+)\n([A-Z\s]+)"
)
CLAUSE_REGEX = re.compile(r"\(\w+\)")

def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                lines = page_text.split("\n")
                # remove page numbers / headers heuristically
                lines = [l for l in lines if not l.strip().isdigit()]
                text += "\n".join(lines) + "\n"
    return text

def split_into_sections(text):
    sections = []
    matches = list(SECTION_REGEX.finditer(text))

    for i, match in enumerate(matches):
        start = match.start()
        end = matches[i+1].start() if i+1 < len(matches) else len(text)

        section_text = text[start:end].strip()

        sections.append({
            "section_number": match.group("section"),
            "section_title": match.group("title").strip(),
            "text": section_text
        })

    return sections

def map_sections_to_chapters(text, sections):
    chapter_positions = []
    for m in CHAPTER_REGEX.finditer(text):
        chapter_positions.append((m.start(), m.group(1), m.group(2)))

    for section in sections:
        sec_pos = text.find(section["text"])
        for i in range(len(chapter_positions)):
            start, chap_no, chap_title = chapter_positions[i]
            end = chapter_positions[i+1][0] if i+1 < len(chapter_positions) else len(text)

            if start <= sec_pos < end:
                section["chapter_number"] = chap_no
                section["chapter_title"] = chap_title.title()
                break

    return sections

def split_section_clauses(section, max_chars=1000):
    text = section["text"]
    clauses = CLAUSE_REGEX.split(text)

    chunks = []

    for i, clause in enumerate(clauses):
        clause = clause.strip()
        if not clause:
            continue

        # HARD SAFETY CUT
        for j in range(0, len(clause), max_chars):
            chunk_text = clause[j:j + max_chars]

            chunk = section.copy()
            chunk["subsection"] = f"clause_{i+1}_part_{j//max_chars + 1}"
            chunk["text"] = chunk_text

            chunks.append(chunk)

    return chunks

def seed_documents(final_chunks):
    print("Seeding sample legal documents...")
    
    embeddings = get_embeddings()
    vector_store = initialize_vector_store(embeddings, final_chunks)
    print(f"Documents seeded successfully! ({len(final_chunks)} chunks)")


if __name__ == "__main__":
    raw_text = extract_text_from_pdf(PDF_PATH)
    sections = split_into_sections(raw_text)
    sections = map_sections_to_chapters(raw_text, sections)

    final_chunks = []
    for sec in sections:
        final_chunks.extend(split_section_clauses(sec))

    seed_documents(final_chunks)
