from pathlib import Path

from fastapi import FastAPI
from fastapi import UploadFile
from fastapi import File
from fastapi import Body

from app.services.document_service import DocumentService
from app.services.vector_service import VectorService
from app.services.llm_service import LLMService
app = FastAPI()

document_service = DocumentService()
vector_service = VectorService()
llm_service = LLMService()

UPLOAD_FOLDER = "documents"

Path(UPLOAD_FOLDER).mkdir(exist_ok=True)


@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):

    file_location = f"{UPLOAD_FOLDER}/{file.filename}"

    with open(file_location, "wb") as f:
        f.write(await file.read())

    result = document_service.extract_pdf(file_location)

    chunks = []

    for page in result["page_content"]:

        page_chunks = document_service.chunk_text(page["text"])

        for chunk in page_chunks:
            chunks.append({
                "text": chunk,
                "page": page["page"]
            })

    stored_chunks = vector_service.store_chunks(
        chunks,
        file.filename
    )

    return {
        "filename": file.filename,
        "pages": result["pages"],
        "characters": result["characters"],
        "chunks_created": len(chunks),
        "chunks_stored": stored_chunks
    }

@app.post("/search")
def search_documents(question: str = Body(embed=True)):

    results = vector_service.search(question)

    return results

@app.post("/ask")
def ask_question(
    question: str = Body(embed=True)
):
    results = vector_service.search(
        question,
        top_k=3
    )

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    # Best result has the lowest distance
    best_distance = distances[0]

    # Prototype relevance threshold.
    # This value should be calibrated using evaluation data.
    relevance_threshold = 0.8

    if best_distance > relevance_threshold:
        return {
            "question": question,
            "answer": "The supplied documents do not contain enough relevant information to answer this reliably.",
            "sources": [],
            "retrieval_status": "insufficient_evidence",
            "answer_status": "abstained"
        }

    context = "\n\n".join(documents)

    answer = llm_service.generate_answer(
        question=question,
        context=context
    )

    abstention_phrases = [
    "i cannot answer this from the supplied documents",
    "the supplied documents do not contain enough",
    "i don't have enough information",
]

    answer_status = (
        "abstained"
        if any(
            phrase in answer.lower()
            for phrase in abstention_phrases
        )
        else "answered"
    )

    sources = []

    for document, metadata in zip(
        documents,
        metadatas
    ):
        sources.append({
            "filename": metadata["filename"],
            "page": metadata["page"],
            "chunk_index": metadata["chunk_index"],
            "evidence": document
        })

    return {
    "question": question,
    "answer": answer,
    "sources": sources,
    "retrieval_status": "sufficient_evidence",
    "answer_status": answer_status
}