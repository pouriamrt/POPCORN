# 🤖 GraphRAG POPCORN Q&A Interface
Population Health Modelling Consensus Reporting Network (POPCORN)

A powerful question-answering interface powered by [Neo4j](https://neo4j.com/), [OpenAI](https://openai.com/), and [Streamlit](https://streamlit.io/), built using the [`neo4j-graphrag`](https://github.com/neo4j/neo4j-graphrag-python) framework. This app enables natural language queries over a Neo4j knowledge graph, providing contextual answers along with interactive graph visualizations.

**Live System**: [POPCORN_GraphRAG App](http://ec2-52-60-155-21.ca-central-1.compute.amazonaws.com/popcorn)

---

## 🚀 Features

- 🔍 Natural Language Querying over Neo4j graphs using OpenAI's GPT-4o
- 🧠 GraphRAG retrieval combining full-text and vector search (`HybridCypherRetriever`)
- 📎 Contextual Answers generated via customizable RAG templates
- 🌐 Interactive Graph Visualization with PyVis and NetworkX
- 🎛 Advanced Filter Controls for refining visualizations by node and edge type
- 🔐 Google OAuth Authentication for secure user access
- 📚 Expandable Context and detailed JSON Debugging information for transparency

---

## 📦 Installation

### 1. Clone the repository

```bash
git clone https://github.com/your-username/graphrag-streamlit-app.git
cd graphrag-streamlit-app
```

### 2. Set up a Python environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the root directory containing:

```env
NEO4J_URI=bolt://<your-neo4j-host>:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password
OPENAI_API_KEY=sk-...
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
REDIRECT_URI=http://localhost:8501
```

> **Note:** Never commit your `.env` file to version control.

---

## ▶️ Run the App

```bash
streamlit run app.py
```

- Access locally: `http://localhost:8501`
- Access remotely: `http://<your-ec2-ip>:8501` (ensure port 8501 is open in your security group)

You can also disable CORS if needed:

```bash
streamlit run app.py --server.port 8501 --server.enableCORS false
```

---

## 📊 Example Use Cases

- Summarize and explore research topics like COVID-19, Brain-Heart Axis, or Cancer
- Dynamically explore paper-author-abstract relationships
- Visualize specific graph neighborhoods and relationships
- Facilitate knowledge-driven Q&A over complex health and scientific domains

---

## 📁 Project Structure

```
📦 graphrag-streamlit-app
├── app.py                 # Main Streamlit app
├── utils                  # Helper modules
│   ├── auth.py            # OAuth authentication logic
│   ├── neo4j_setup.py     # Neo4j and LLM configuration
│   └── graph_viz.py       # Graph visualization utilities
├── .env                   # API and DB credentials (ignored by Git)
├── requirements.txt       # Python dependencies
└── README.md              # Project documentation
```

---

## 🛡 Security Notes

- Protect your `.env` file from public exposure
- Restrict Neo4j database access appropriately
- Deploy with HTTPS and authentication mechanisms for production environments

---

## 🧠 Built With

- [Neo4j GraphRAG](https://github.com/neo4j/neo4j-graphrag-python)
- [Streamlit](https://streamlit.io/)
- [OpenAI GPT-4o](https://openai.com/)
- [NetworkX](https://networkx.org/)
- [PyVis](https://pyvis.readthedocs.io/)
- [Streamlit OAuth](https://github.com/streamlit/streamlit)

---

## 👤 Author

**Pouria Mortezaagha**  
Data Analyst • AI Researcher • Full-Stack Developer  
[LinkedIn](https://www.linkedin.com/in/pouria-mortezaagha/)  
✉️ pouriamortezaagha7@gmail.com

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

