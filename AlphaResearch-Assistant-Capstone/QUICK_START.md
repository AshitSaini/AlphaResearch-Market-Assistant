# QUICK START GUIDE - Build Your Project from Scratch

**For:** Your step-by-step implementation after AI builds it  
**Duration:** ~2 weeks from scratch  
**Difficulty:** Intermediate Python Developer  

---

## 🚀 QUICK START (5 MINUTES)

```bash
# 1. Clone or open the project
cd e:\AgenticAI\projects\Capstone Project\broking-ai-assistant

# 2. Create virtual environment
python -m venv venv

# 3. Activate it
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Create .env file
copy .env.example .env
# (Edit .env with your OpenAI API key)

# 6. You're ready to start Phase 2!
```

---

## 📝 PHASE 2: BUILD BACKEND (FIRST STEPS)

### Step 1: Create Document Service

**Create:** `app/services/document_service.py`

```python
import pdfplumber
from docx import Document as DocxDocument
import openpyxl
import json
from pathlib import Path
from typing import List, Dict

class DocumentService:
    """Handle document ingestion from various formats"""
    
    @staticmethod
    def ingest_pdf(file_path: str) -> str:
        """Extract text from PDF"""
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() + "\n"
        return text
    
    @staticmethod
    def ingest_docx(file_path: str) -> str:
        """Extract text from Word document"""
        doc = DocxDocument(file_path)
        return "\n".join([para.text for para in doc.paragraphs])
    
    @staticmethod
    def ingest_txt(file_path: str) -> str:
        """Read text file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    @staticmethod
    def ingest_markdown(file_path: str) -> str:
        """Read markdown file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    @staticmethod
    def ingest(file_path: str) -> str:
        """Auto-detect format and ingest"""
        ext = Path(file_path).suffix.lower()
        
        handlers = {
            '.pdf': DocumentService.ingest_pdf,
            '.docx': DocumentService.ingest_docx,
            '.doc': DocumentService.ingest_docx,
            '.txt': DocumentService.ingest_txt,
            '.md': DocumentService.ingest_markdown,
        }
        
        if ext in handlers:
            return handlers[ext](file_path)
        else:
            raise ValueError(f"Unsupported format: {ext}")
```

### Step 2: Create Text Chunking Service

**Create:** `app/core/text_chunking.py`

```python
import tiktoken
import nltk
from typing import List, Dict

nltk.download('punkt')

class SemanticChunker:
    """Chunk text with semantic awareness"""
    
    def __init__(self, chunk_size: int = 500, overlap: int = 100):
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.encoding = tiktoken.encoding_for_model("gpt-4")
    
    def chunk_text(self, text: str, metadata: Dict = None) -> List[Dict]:
        """Split text into chunks with overlap"""
        
        # Split by sentences first
        sentences = nltk.sent_tokenize(text)
        
        chunks = []
        current_chunk = ""
        current_tokens = 0
        chunk_id = 0
        
        for sentence in sentences:
            sentence_tokens = len(self.encoding.encode(sentence))
            
            if current_tokens + sentence_tokens > self.chunk_size:
                # Save current chunk
                if current_chunk:
                    chunks.append({
                        "id": f"chunk_{chunk_id}",
                        "text": current_chunk.strip(),
                        "token_count": current_tokens,
                        "metadata": metadata or {}
                    })
                    chunk_id += 1
                
                # Start new chunk with overlap
                current_chunk = ""
                current_tokens = 0
            
            current_chunk += " " + sentence
            current_tokens += sentence_tokens
        
        # Add last chunk
        if current_chunk:
            chunks.append({
                "id": f"chunk_{chunk_id}",
                "text": current_chunk.strip(),
                "token_count": current_tokens,
                "metadata": metadata or {}
            })
        
        return chunks
```

### Step 3: Create Embeddings Service

**Create:** `app/core/embeddings.py`

```python
import openai
from typing import List
import os

class EmbeddingsGenerator:
    """Generate embeddings using OpenAI"""
    
    def __init__(self, model: str = "text-embedding-3-small"):
        self.model = model
        self.api_key = os.getenv("OPENAI_API_KEY")
        openai.api_key = self.api_key
    
    def generate(self, text: str) -> List[float]:
        """Generate single embedding"""
        response = openai.Embedding.create(
            input=text,
            model=self.model
        )
        return response['data'][0]['embedding']
    
    def batch_generate(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        response = openai.Embedding.create(
            input=texts,
            model=self.model
        )
        return [item['embedding'] for item in response['data']]
```

### Step 4: Create Chroma Vector Store

**Create:** `app/core/vector_store.py`

```python
import chromadb
from typing import List, Dict
import os

class ChromaVectorStore:
    """Manage vector embeddings in Chroma"""
    
    def __init__(self):
        self.db_path = os.getenv(
            "CHROMA_DB_PATH", 
            "./data/embeddings/chroma_db"
        )
        self.client = chromadb.PersistentClient(path=self.db_path)
        self.collection = self.client.get_or_create_collection(
            name="broking_knowledge_base",
            metadata={"hnsw:space": "cosine"}
        )
    
    def add_documents(self, chunks: List[Dict], embeddings: List[List[float]]):
        """Add documents with embeddings to vector store"""
        self.collection.add(
            ids=[chunk["id"] for chunk in chunks],
            embeddings=embeddings,
            documents=[chunk["text"] for chunk in chunks],
            metadatas=[chunk["metadata"] for chunk in chunks]
        )
    
    def search(self, query_embedding: List[float], top_k: int = 5):
        """Search for similar documents"""
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        return results
```

### Step 5: Test Your Pipeline

**Create:** `test_phase2.py`

```python
from app.services.document_service import DocumentService
from app.core.text_chunking import SemanticChunker
from app.core.embeddings import EmbeddingsGenerator
from app.core.vector_store import ChromaVectorStore

# Load a knowledge base document
doc_path = "./knowledge-base/SEBI_Regulations.md"
text = DocumentService.ingest(doc_path)
print(f"✓ Loaded document: {len(text)} characters")

# Chunk the text
chunker = SemanticChunker(chunk_size=500, overlap=100)
chunks = chunker.chunk_text(
    text,
    metadata={"source": "SEBI_Regulations.md"}
)
print(f"✓ Created {len(chunks)} chunks")

# Generate embeddings
generator = EmbeddingsGenerator()
embeddings = generator.batch_generate(
    [chunk["text"] for chunk in chunks]
)
print(f"✓ Generated {len(embeddings)} embeddings")

# Store in Chroma
vector_store = ChromaVectorStore()
vector_store.add_documents(chunks, embeddings)
print(f"✓ Stored in Chroma vector database")

print("\n✨ Phase 2 foundation complete!")
```

**Run it:**
```bash
python test_phase2.py
```

---

## 🤖 PHASE 3: BUILD AI AGENTS

### Step 1: LLM Service

**Create:** `app/services/llm_service.py`

```python
import openai
import os
from typing import List

class LLMService:
    """Generate responses using OpenAI"""
    
    def __init__(self):
        openai.api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
    
    def generate_with_context(
        self,
        question: str,
        context: str,
        system_prompt: str = None
    ) -> str:
        """Generate answer based on context"""
        
        if not system_prompt:
            system_prompt = """You are an expert on Indian broking and securities trading.
Use the provided context to answer questions accurately.
Always cite your sources.
Provide clear, actionable advice."""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"}
        ]
        
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=messages,
            temperature=0.7,
            max_tokens=1500
        )
        
        return response.choices[0].message.content
```

### Step 2: RAG Pipeline

**Create:** `app/core/rag_pipeline.py`

```python
from app.core.vector_store import ChromaVectorStore
from app.core.embeddings import EmbeddingsGenerator
from app.services.llm_service import LLMService
from typing import Dict

class RAGPipeline:
    """Orchestrate retrieval + generation"""
    
    def __init__(self):
        self.vector_store = ChromaVectorStore()
        self.embeddings_gen = EmbeddingsGenerator()
        self.llm = LLMService()
    
    def execute(self, question: str, top_k: int = 5) -> Dict:
        """Run full RAG pipeline"""
        
        # Step 1: Generate query embedding
        query_embedding = self.embeddings_gen.generate(question)
        
        # Step 2: Search for similar documents
        results = self.vector_store.search(query_embedding, top_k)
        
        # Step 3: Format context
        context = self._format_context(results)
        
        # Step 4: Generate answer
        answer = self.llm.generate_with_context(question, context)
        
        return {
            "question": question,
            "answer": answer,
            "sources": self._extract_sources(results)
        }
    
    def _format_context(self, results: Dict) -> str:
        """Format search results as context"""
        context = ""
        for i, doc in enumerate(results['documents'][0]):
            context += f"[{i+1}] {doc}\n\n"
        return context
    
    def _extract_sources(self, results: Dict) -> List[str]:
        """Extract source references"""
        sources = []
        for metadata in results['metadatas'][0]:
            sources.append(f"{metadata.get('source', 'Unknown')}")
        return list(set(sources))  # Unique sources
```

### Step 3: Test RAG

**Create:** `test_phase3.py`

```python
from app.core.rag_pipeline import RAGPipeline

# Initialize RAG
rag = RAGPipeline()

# Test queries
questions = [
    "What is SEBI and why is it important?",
    "How do I open a trading account?",
    "What is the T+1 settlement?",
    "Explain margin requirement in equity trading"
]

for question in questions:
    print(f"\n❓ Q: {question}")
    result = rag.execute(question)
    print(f"✓ A: {result['answer'][:200]}...")
    print(f"📚 Sources: {result['sources']}")
```

**Run it:**
```bash
python test_phase3.py
```

---

## 🎨 PHASE 4: BUILD FRONTEND

### Step 1: Create React App

```bash
# In frontend directory
npm create next-app@latest . --typescript

# Install additional packages
npm install tailwindcss postcss autoprefixer axios zustand
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

### Step 2: Create Chat Component

**Create:** `frontend/components/ChatInterface.tsx`

```typescript
'use client'
import { useState } from 'react'
import axios from 'axios'

interface Message {
  id: string
  type: 'question' | 'answer'
  content: string
  sources?: string[]
  timestamp: Date
}

export default function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSend = async () => {
    if (!input.trim()) return

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'question',
      content: input,
      timestamp: new Date()
    }

    setMessages([...messages, userMessage])
    setInput('')
    setLoading(true)

    try {
      const response = await axios.post('/api/ask', {
        question: input
      })

      const aiMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'answer',
        content: response.data.answer,
        sources: response.data.sources,
        timestamp: new Date()
      }

      setMessages(prev => [...prev, aiMessage])
    } catch (error) {
      console.error('Error:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex flex-col h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <div className="bg-indigo-600 text-white p-6">
        <h1 className="text-3xl font-bold">Broking AI Assistant</h1>
        <p>Your expert guide to Indian securities trading</p>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {messages.map(msg => (
          <div
            key={msg.id}
            className={`flex ${msg.type === 'question' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-xl p-4 rounded-lg ${
                msg.type === 'question'
                  ? 'bg-indigo-500 text-white'
                  : 'bg-white text-gray-800 border border-gray-200'
              }`}
            >
              <p>{msg.content}</p>
              {msg.sources && msg.sources.length > 0 && (
                <div className="mt-2 text-sm">
                  <p className="font-semibold">Sources:</p>
                  <ul>{msg.sources.map(s => <li key={s}>• {s}</li>)}</ul>
                </div>
              )}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-white p-4 rounded-lg border border-gray-200">
              <div className="animate-pulse">Thinking...</div>
            </div>
          </div>
        )}
      </div>

      {/* Input */}
      <div className="bg-white border-t p-6">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyPress={e => e.key === 'Enter' && handleSend()}
            placeholder="Ask about trading, SEBI rules, account opening..."
            className="flex-1 border border-gray-300 rounded-lg p-2 focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
          <button
            onClick={handleSend}
            disabled={loading}
            className="bg-indigo-600 text-white px-6 py-2 rounded-lg hover:bg-indigo-700 disabled:opacity-50"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  )
}
```

---

## 📦 FINAL SUBMISSION CHECKLIST

Before creating ZIP for LMS:

- [ ] All 6 phases completed
- [ ] README.md updated with your name
- [ ] ROADMAP.md in project root
- [ ] requirements.txt verified
- [ ] .env.example configured
- [ ] Knowledge base markdown files present
- [ ] Python files structured correctly
- [ ] React/Next.js frontend created
- [ ] Docker files included
- [ ] All dependencies installable
- [ ] Project runs without errors

**Create ZIP:**
```bash
# Windows
tar -a -c -f broking-ai-capstone-final.zip broking-ai-assistant/

# macOS/Linux
zip -r broking-ai-capstone-final.zip broking-ai-assistant/
```

---

## 🆘 COMMON ISSUES & FIXES

| Issue | Solution |
|-------|----------|
| OpenAI API error | Check OPENAI_API_KEY in .env |
| Chroma not found | Run: `python -c "import chromadb; chromadb.PersistentClient()"` |
| Slow embeddings | Use smaller model: `text-embedding-3-small` |
| Port 8000 in use | Change port in main.py |
| React build errors | Delete node_modules, reinstall |

---

**Good luck with your implementation! You've got this! 🚀**
