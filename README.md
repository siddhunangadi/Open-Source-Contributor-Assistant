# ContribAgent: Open Source Contribution Copilot

ContribAgent is an autonomous, evidence-driven agent designed to help developers—from beginners to experienced contributors—find, evaluate, and plan their open-source contributions. 

Equipped with GitHub repository searching, AST-based dependency tracing, RAG-powered code chunk retrieval, and a strict evidence-verification gate, ContribAgent ensures that recommendations are grounded in actual repository contents and aligned with the user's skill level.

---

## 🚀 Key Features

* **Autonomous Supervisor Agent**: Uses a dynamic planning loop to decide the next best action, reducing uncertainty at each step.
* **Beginner Suitability Gate & Ranking**: Evaluates candidates based on safety and complexity, strictly rejecting issues with high-risk elements (e.g., public API changes, benchmarking, deep framework internals) for beginner goals.
* **AST Dependency & Test Tracing**: Analyzes symbol imports, references, and test files to verify dependency relationships instead of relying on simple flat list paths.
* **Strict Evidence Verification**: Uses a deterministic logic check to require repository, issue, code, dependency, and test evidence before producing a recommendation.
* **Interactive UI**: A sleek, dark-themed Streamlit application providing a live visual trace of the agent's thoughts, tools executed, and final reports.

---

## 🛠️ Tech Stack

* **Core Logic**: Python 3.11+, Pydantic schemas, AST module analysis
* **Agent Framework**: Custom autonomous loop with LangGraph-style state tracking
* **RAG & Indexing**: Qdrant Vector DB, SentenceTransformers
* **Frontend**: Streamlit
* **Testing**: Pytest

---

## 📂 Project Structure

```text
├── agents/             # Autonomous agent loop & final answer generation
├── models/             # Pydantic schema models & initial state tracking
├── rag/                # RAG ingestion pipelines & vector store interface
├── services/           # GitHub & LLM API integrations
├── tools/              # Ingest, dependency tracing, verification, & GitHub tools
├── tests/              # Scoped unit & integration tests
├── app.py              # Streamlit Web App interface
└── requirements.txt    # Project dependencies
```

---

## ⚙️ Setup and Installation

1. **Activate Environment & Install Dependencies**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Configure Environment Variables**:
   Create a `.env` file in the root directory:
   ```env
   MISTRAL_API_KEY=your_mistral_api_key
   GITHUB_TOKEN=your_github_token
   ```

---

## 🖥️ Running the Application

Start the interactive development server:
```bash
streamlit run app.py
```

---

## 🧪 Running Tests

Verify the complete test suite:
```bash
pytest tests/
```
