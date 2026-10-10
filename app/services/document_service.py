from pathlib import Path
from pypdf import PdfReader


class DocumentService:

    def extract_pdf(self, file_path: str):

        reader = PdfReader(file_path)

        pages = []
        total_characters = 0

        for page_number, page in enumerate(reader.pages, start=1):

            page_text = page.extract_text()

            if page_text:
                pages.append({
                    "page": page_number,
                    "text": page_text
                })

                total_characters += len(page_text)

        return {
            "pages": len(reader.pages),
            "characters": total_characters,
            "page_content": pages
        }


    def chunk_text(self,text: str,chunk_size: int = 800,overlap: int = 150):
        chunks = []

        start = 0

        while start < len(text):
            end = start + chunk_size

            chunk = text[start:end].strip()

            if chunk:
                chunks.append(chunk)

            start += chunk_size - overlap

        return chunks