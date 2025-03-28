# 🤖 GraphRAG POPCORN Q&A Interface
Population Health Modelling Consensus Reporting Network (POPCORN)

A powerful question-answering interface powered by [Neo4j](https://neo4j.com/), [OpenAI](https://openai.com/), and [Streamlit](https://streamlit.io/), built using the [`neo4j-graphrag`](https://github.com/neo4j/graph-rag) framework. This app enables natural language queries over a Neo4j knowledge graph and provides contextual answers with an interactive graph visualization.

---

## 🚀 Features

- 🔍 Natural Language Querying over a Neo4j graph using OpenAI's GPT-4o
- 🧠 GraphRAG Retrieval with both full-text and vector search (HybridCypherRetriever)
- 📎 Contextual Answers generated via templated RAG prompt
- 🌐 Graph Visualization using PyVis + NetworkX
- 🎛 Filter Controls to refine visualization by node and edge type
- 📚 Expandable Context + JSON Debug Info for transparency

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

### 4. Create your `.env` file

In the root directory, create a `.env` file containing:

```env
NEO4J_URI=bolt://<your-neo4j-host>:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password
OPENAI_API_KEY=sk-...
```

> **Note:** Be sure not to commit `.env` to version control.

---

## ▶️ Run the App

```bash
streamlit run your_app.py
```

- Access locally: `http://localhost:8501`
- Access remotely: `http://<your-ec2-ip>:8501` (make sure port 8501 is open in your security group)

You can also run it with additional flags to disable CORS or enable production configs:

```bash
streamlit run your_app.py --server.port 8501 --server.enableCORS false
```

---

## 📊 Example Use Cases

- Summarize research topics like COVID, Brain-Heart Axis, or Cancer
- Explore paper-author-abstract relationships dynamically
- Visualize graph neighborhoods and query paths
- Enable knowledge-driven Q&A over complex domains

---

## 📁 Project Structure

```
📦 graphrag-streamlit-app
├── your_app.py            # Main Streamlit app
├── .env                   # API and DB credentials (ignored by Git)
├── requirements.txt       # Python dependencies
└── README.md              # Project documentation
```

---

## 🛡 Security Notes

- Never expose your `.env` file publicly
- Restrict Neo4j access to specific IPs or via secure tunnel
- For production, consider using HTTPS + authentication (e.g., with Nginx and Certbot)

---

## 🧠 Built With

- [Neo4j GraphRAG](https://github.com/neo4j/neo4j-graphrag-python)
- [Streamlit](https://streamlit.io/)
- [OpenAI GPT-4o](https://openai.com/)
- [NetworkX](https://networkx.org/)
- [PyVis](https://pyvis.readthedocs.io/)

---

## 👤 Author

**Pouria Mortezaagha**  
Data Analyst • AI Researcher • Full-Stack Developer  
[LinkedIn](https://www.linkedin.com/in/pouria-mortezaagha/)  
✉️ pouriamortezaagha7@gmail.com

---

## 📄 License

This project is licensed under the MIT License. See `LICENSE` file for details.
