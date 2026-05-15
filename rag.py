import chromadb
from sentence_transformers import SentenceTransformer
from pypdf import PdfReader
import openpyxl, io

model = SentenceTransformer("all-MiniLM-L6-v2")
chroma = chromadb.Client()
collection = chroma.get_or_create_collection("financial_docs")

def chunk_text(text: str, size=500, overlap=50):
    words = text.split()
    chunks = []
    for i in range(0, len(words), size - overlap):
        chunks.append(" ".join(words[i:i+size]))
    return chunks

def ingest_document(content: bytes, filename: str):
    if filename.endswith(".pdf"):
        reader = PdfReader(io.BytesIO(content))
        text = " ".join(p.extract_text() or "" for p in reader.pages)
    elif filename.endswith((".xlsx", ".xls")):
        wb = openpyxl.load_workbook(io.BytesIO(content))
        rows = []
        for sheet in wb.worksheets:
            for row in sheet.iter_rows(values_only=True):
                rows.append(" | ".join(str(c) for c in row if c))
        text = "\n".join(rows)
    else:
        text = content.decode("utf-8", errors="ignore")

    chunks = chunk_text(text)
    embeddings = model.encode(chunks).tolist()
    ids = [f"{filename}_{i}" for i in range(len(chunks))]
    collection.upsert(ids=ids, embeddings=embeddings, documents=chunks)
    return chunks

def retrieve_context(query: str, top_k=5):
    embedding = model.encode([query]).tolist()
    results = collection.query(query_embeddings=embedding, n_results=top_k)
    return "\n\n".join(results["documents"][0])