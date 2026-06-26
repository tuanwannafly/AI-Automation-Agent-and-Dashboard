import pdfplumber
from docx import Document
import asyncio


class FileProcessor:
    async def extract_text(self, file_path: str, content_type: str) -> str:
        """Extract text from PDF, DOCX, or plain text file."""
        if "pdf" in content_type:
            return await asyncio.to_thread(self._extract_pdf, file_path)
        elif "docx" in content_type or "wordprocessingml" in content_type:
            return await asyncio.to_thread(self._extract_docx, file_path)
        else:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()

    def _extract_pdf(self, path: str) -> str:
        text = ""
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
        return text.strip()

    def _extract_docx(self, path: str) -> str:
        doc = Document(path)
        return "\n".join([para.text for para in doc.paragraphs if para.text.strip()])