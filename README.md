# Explainable AI Decision Support

An explainable Retrieval-Augmented Generation (RAG) prototype designed to explore evidence-grounded answers, source traceability, uncertainty handling and automated evaluation.

The current prototype uses publicly available fire-safety guidance documents as a non-clinical test domain. It is intended for research, learning and software engineering experimentation, not for operational fire-safety or clinical decision-making.

## Overview

The application extracts text from PDF documents, generates semantic embeddings using Sentence Transformers, stores document chunks in ChromaDB and retrieves relevant evidence in response to user questions.

A locally hosted Llama 3.2 model, accessed through Ollama, generates answers using the retrieved context.

The API returns the answer together with supporting evidence and status indicators to help users assess whether the available documentation supports a response.

## Key Features

- PDF upload and text extraction using PyPDF
- Overlapping document chunking
- Semantic embeddings using Sentence Transformers
- Vector storage and similarity search using ChromaDB
- Locally hosted Llama 3.2 model through Ollama
- Retrieval-augmented answer generation
- Source attribution, including document filename, page number and supporting evidence
- Retrieval-status indicator for evidence sufficiency
- Answer-status indicator distinguishing answered and abstained responses
- Abstention behaviour for questions with insufficient supporting evidence
- Automated evaluation of expected versus actual answer status
- Evaluation of expected source retrieval and API response latency
- Interactive API documentation through FastAPI Swagger UI

## Architecture

```text
PDF Documents
     |
     v
Text Extraction (PyPDF)
     |
     v
Document Chunking
     |
     v
Sentence Transformers
     |
     v
ChromaDB Vector Store
     |
     v
User Question
     |
     v
Semantic Retrieval
     |
     v
Evidence Sufficiency Check
     |
     v
Ollama / Llama 3.2
     |
     v
Answer + Sources + Status Indicators
```

## How It Works

1. A PDF document is uploaded.
2. Text is extracted and divided into overlapping chunks.
3. Sentence Transformers generates embeddings for the chunks.
4. ChromaDB stores the embeddings and document metadata.
5. A user submits a natural-language question.
6. The system retrieves relevant document passages.
7. Retrieved evidence is assessed for sufficiency.
8. The language model generates an evidence-grounded answer or abstains when it cannot provide a supported response.
9. The API returns the answer, retrieved sources and status indicators.

## Technologies

- Python
- FastAPI
- PyPDF
- Sentence Transformers
- ChromaDB
- Ollama
- Llama 3.2
- Requests (evaluation script)

## Available APIs

### Upload

Uploads a PDF, extracts its text, generates embeddings and stores document chunks in ChromaDB.

### Search

Retrieves document passages using semantic similarity search.

### Ask

Accepts a question and returns an AI-generated response with supporting evidence and status indicators.

Example response structure:

```json
{
  "question": "What are the responsibilities of a responsible person?",
  "answer": "An answer based on the retrieved guidance.",
  "sources": [
    {
      "filename": "fire_safety_offices_shops.pdf",
      "page": 7,
      "chunk_index": 0,
      "evidence": "Relevant retrieved document passage."
    }
  ],
  "retrieval_status": "sufficient_evidence",
  "answer_status": "answered"
}
```

The example is illustrative. Source passages and status values depend on the retrieved documents and generated response.

## Automated Evaluation

The `evaluation/` directory contains a lightweight evaluation framework.

- `questions.json` defines test questions and expected outcomes.
- `evaluate.py` sends test questions to the running API.
- `results/` stores generated evaluation reports.

The framework records:

- Expected and actual answer status
- Answer-status agreement
- Whether manually identified expected sources were retrieved
- API response latency
- Generated answers and supporting evidence

### Running the Evaluation

First, start the FastAPI application.

Then, from the project root, run:

```bash
python evaluation/evaluate.py
```

### Initial Evaluation Findings

An initial three-question evaluation included:

1. A question answerable from the supplied documents.
2. An unrelated question requiring abstention.
3. An ambiguous question requiring cautious handling.

In one evaluation run:

| Metric                         | Result                     |
| ------------------------------ | -------------------------- |
| Test questions                 | 3                          |
| Expected answer-status matches | 3/3                        |
| Expected-source matches        | 1/1 labelled source check  |
| Average API response time      | Approximately 26.2 seconds |

These are preliminary results from a very small test set and should not be interpreted as general model accuracy or production readiness.

Manual review also identified limitations:

- Relevant evidence was sometimes retrieved but incompletely represented in the answer.
- An abstention response included a potentially misleading interpretation.
- Answer-status outcomes varied across runs for an ambiguous question.

The current answer-status classification uses simple response-text checks and may not reliably identify every form of abstention.

These findings demonstrate why automated metrics should be supplemented by manual review of factual accuracy, completeness, consistency and explanation quality.

## Running the Application

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Install and Prepare Ollama

Ensure Ollama is installed and running, then pull the model:

```bash
ollama pull llama3.2:3b
```

### 3. Start the API

```bash
uvicorn main:app --reload
```

### 4. Open Swagger UI

Visit:

http://127.0.0.1:8000/docs

Swagger UI is the current development and testing interface. A dedicated end-user interface has not yet been implemented.

## Responsible AI Considerations

The prototype explores several responsible AI principles:

- **Traceability:** Responses include supporting document references and evidence passages.
- **Uncertainty:** The system can abstain when evidence is insufficient.
- **Transparency:** Retrieval and answer-status indicators expose aspects of system behaviour.
- **Evaluation:** Labelled questions and saved results support repeatable testing.
- **Privacy-conscious development:** The prototype uses publicly available fire-safety PDFs and a locally hosted language model.

These mechanisms do not guarantee factual correctness, fairness or regulatory compliance.

No clinical validation, formal demographic bias audit or external user study has been conducted.

## Current Limitations

- Small evaluation dataset
- No formal expert-reviewed ground-truth benchmark
- Potentially incomplete or misleading generated explanations
- Variation in responses across evaluation runs
- Heuristic evidence-sufficiency assessment
- Simple answer-status classification
- Relatively high response latency
- Swagger UI only; no dedicated professional-user interface
- No clinical deployment or healthcare-data integration

## Future Improvements

- Expand evaluation datasets and assess answer correctness and completeness
- Improve abstention detection and evidence-sufficiency calibration
- Add repeated-run consistency testing
- Introduce token-aware chunking
- Add OCR for scanned PDFs
- Improve metadata filtering and retrieval ranking
- Develop a user-friendly interface for evidence inspection
- Add Docker support and automated testing
- Explore Azure OpenAI integration
- Conduct structured usability testing with external users
- Investigate subgroup fairness evaluation where suitable datasets are available

## Project Scope

This is an independent, non-clinical AI engineering prototype.

It demonstrates transferable techniques for explainable AI and decision-support research but is not a validated system for fire-safety compliance, optometry or medical decision-making.
