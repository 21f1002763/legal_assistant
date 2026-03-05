from pydantic import BaseModel
from typing import Optional, List
from enum import Enum


class DocumentType(str, Enum):
    GOVERNMENT_NOTICE = "government_notice"
    UNIVERSITY_RULE = "university_rule"
    APPLICATION_FORM = "application_form"
    BANK_POLICY = "bank_policy"
    COURT_NOTICE = "court_notice"


class BNSChapter(BaseModel):
    chapter_number: str
    chapter_title: str


class BNSSection(BaseModel):
    section_number: str
    section_title: str
    chapter_number: str
    chapter_title: str
    text: str


class BNSSectionPreview(BaseModel):
    section_number: str
    section_title: str
    chapter_number: str
    chapter_title: str
    preview: str


class SearchRequest(BaseModel):
    query: str
    chapter_filter: Optional[str] = None
    section_filter: Optional[str] = None
    limit: int = 10


class SearchResponse(BaseModel):
    answer: str
    sections: List[BNSSectionPreview]
    citations: List[str]


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    context_sections: Optional[List[str]] = None


class ChatResponse(BaseModel):
    message: str
    citations: List[str]


class DocumentInput(BaseModel):
    text: str
    document_type: DocumentType
    title: Optional[str] = None
    source_authority: Optional[str] = None


class ClauseReference(BaseModel):
    clause_id: str
    original_text: str
    source_document: str


class ExplanationOutput(BaseModel):
    plain_explanation: str
    action_checklist: List[str]
    common_mistakes: List[str]
    clause_references: List[ClauseReference]
    disclaimer: str = "This tool explains documents in plain language. It does not provide legal advice."


class AnalyzeRequest(BaseModel):
    document_text: str
    document_type: DocumentType
    title: Optional[str] = None
    authority: Optional[str] = None


class AnalyzeResponse(BaseModel):
    plain_explanation: str
    action_checklist: List[str]
    common_mistakes: List[str]
    clause_references: List[dict]
    disclaimer: str
