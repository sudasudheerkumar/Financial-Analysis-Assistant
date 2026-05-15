from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import anthropic, os
from dotenv import load_dotenv
from rag import ingest_document, retrieve_context

load_dotenv()
app = FastAPI()

app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173"],
    allow_methods=["*"], allow_headers=["*"])

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

class AnalyzeRequest(BaseModel):
    query: str
    period: str

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    content = await file.read()
    chunks = ingest_document(content, file.filename)
    return {"status": "ok", "chunks": len(chunks)}

@app.post("/analyze")
async def analyze(req: AnalyzeRequest):
    context = retrieve_context(req.query)
    system_prompt = """You are a senior financial analyst AI. Respond ONLY in JSON:
{"summary":{"period":"","headline":"","metrics":[{"label":"","value":"","delta":"","trend":""}],"bullets":[]},"variance":{"explanation":"","items":[{"name":"","budget":"","actual":"","delta":"","deltaPct":0,"direction":"","reason":""}]},"exec":{"paragraphs":[],"risks":[],"actions":[]}}"""
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1500,
        system=system_prompt,
        messages=[{"role":"user","content":f"Period: {req.period}\nContext:\n{context}\nQuestion: {req.query}"}]
    )
    return {"result": message.content[0].text}