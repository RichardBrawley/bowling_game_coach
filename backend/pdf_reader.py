from pathlib import Path
from pypdf import PdfReader
from haystack.dataclasses import Document
from haystack.components.preprocessors import DocumentSplitter

def load_pdf_to_documents(path: str):
    reader = PdfReader(path)
    docs = []

    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        if not text:
            continue
        docs.append(
            Document(
                id=f"{Path(path).stem}_page{i+1}",
                content=text,
                meta={"source": path, "page": i+1}
            )
        )

    # Optional: split into smaller chunks (e.g., 200 chars overlap 20)
    splitter = DocumentSplitter(split_length=200, split_overlap=20)
    chunks = splitter.run(docs)["documents"]

    return chunks
