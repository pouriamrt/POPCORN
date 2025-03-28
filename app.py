import streamlit as st
import neo4j
from neo4j_graphrag.llm import OpenAILLM as LLM
from neo4j_graphrag.embeddings.openai import OpenAIEmbeddings as Embeddings
from neo4j_graphrag.generation.graphrag import GraphRAG
from neo4j_graphrag.generation import RagTemplate
from neo4j_graphrag.retrievers import HybridCypherRetriever
from pyvis.network import Network
import networkx as nx
import tempfile
import os
from dotenv import load_dotenv
import re

# ------------------ Load Environment ------------------ #
load_dotenv('.env', override=True)
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# ------------------ Neo4j & LLM Setup ------------------ #
neo4j_driver = neo4j.GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
embedder = Embeddings()
llm = LLM(model_name="gpt-4o", model_params={"temperature": 0.0})

# ------------------ Cypher Retrieval Query ------------------ #
retrieval_query = """
WITH node AS chunk
MATCH (chunk)<-[:FROM_CHUNK]-()-[rel*1..2]-()
OPTIONAL MATCH ()-[rel0]-()-[:HAS_ABSTRACT]->(chunk)
UNWIND rel AS single_rel
UNWIND rel0 AS single_rel0
WITH 
    [c IN collect(DISTINCT chunk) WHERE c IS NOT NULL] AS chunks,
    [r IN collect(DISTINCT single_rel) WHERE r IS NOT NULL] AS rels,
    [r0 IN collect(DISTINCT single_rel0) WHERE r0 IS NOT NULL] AS rels0
WITH chunks[0..$top_k] AS limited_chunks, rels, rels0
RETURN '=== kg_rels (incoming) ===\n' + 
    apoc.text.join([r0 IN rels0 | 
        coalesce(startNode(r0).name, startNode(r0).title, '') + ' - ' + 
        type(r0) + '(' + coalesce(r0.details, '') + ')' +  
        ' -> ' + coalesce(endNode(r0).name, endNode(r0).title, '')
    ], '\n---\n ********* \n---\n') 
    + '\n\n=== text ===\n' + 
    apoc.text.join([c IN limited_chunks | c.text], '\n---\n') 
    + '\n\n=== kg_rels (outgoing) ===\n' + 
    apoc.text.join([r IN rels | 
        coalesce(startNode(r).name, startNode(r).title, '') + ' - ' + 
        type(r) + '(' + coalesce(r.details, '') + ')' +  
        ' -> ' + coalesce(endNode(r).name, endNode(r).title, '')
    ], '\n---\n ********* \n---\n') 
AS info
"""

# ------------------ Retriever ------------------ #
examples = ["""
USER INPUT: 'Papers and Authors and Abstracts and related nodes and edges.'
QUERY: MATCH (p:Paper)-[r:AUTHORED_BY]->(a:Author), (d)-[r2]-(p)-[r1:HAS_ABSTRACT]->(c:Chunk)-[r3]-(e)
RETURN p, r, r1, a, c, d, r2, r3, e LIMIT 50;

USER INPUT: 'Tell me about Carol Bennett.'
QUERY: MATCH (p:Person {name: 'Carol Bennett'})-[r]-(n)-[r2]-(m) 
RETURN p, r, n, r2, m LIMIT 50;
"""]

hybrid_retriever = HybridCypherRetriever(
    driver=neo4j_driver,
    vector_index_name="text_embeddings",
    fulltext_index_name="paper_fulltext_index",
    retrieval_query=retrieval_query,
    embedder=embedder
)

# ------------------ Prompt Template ------------------ #
rag_template = RagTemplate(
    template='''
Answer the Question using the following Context. Only respond with information mentioned in the Context. Do not inject any speculative information not mentioned.

# Question:
{query_text}

# Context:
{context}

# Answer:
''',
    expected_inputs=['query_text', 'context']
)

rag = GraphRAG(llm=llm, retriever=hybrid_retriever, prompt_template=rag_template)

if 'raw_record' not in st.session_state:
    st.session_state.raw_record = None
    
# ------------------ Streamlit UI ------------------ #
st.set_page_config(page_title="GraphRAG Q&A Interface", layout="wide")
st.title("🤖 GraphRAG-Powered QA Interface")
st.markdown("Ask natural language questions about your Neo4j knowledge graph.")

with st.sidebar:
    st.header("⚙️ Configuration")
    top_k = st.slider("Top K Chunks", min_value=1, max_value=10, value=4)
    use_example = st.checkbox("Use example question", value=True)
    # Place this inside `with st.sidebar:` block
    st.header("🧩 Graph Filters")

    # Edge type filter (initially empty)
    if 'all_edge_types' not in st.session_state:
        st.session_state.all_edge_types = []
    if 'all_node_types' not in st.session_state:
        st.session_state.all_node_types = []

    # Edge filter
    edge_type_filter = st.multiselect(
        "Filter by Edge Type",
        options=st.session_state.all_edge_types,
        default=st.session_state.all_edge_types
    )

    # Node filter
    node_type_filter = st.multiselect(
        "Filter by Node Type",
        options=st.session_state.all_node_types,
        default=st.session_state.all_node_types
    )


default_question = "Write a summary about COVID and list all the papers you are answering based on of."
user_query = st.text_area("📝 Enter your query:", value=default_question if use_example else "", height=120)

# Filter input outside sidebar to dynamically update visualization
graph_filter = st.text_input("🔎 Filter Graph Nodes/Edges")

# ------------------ Graph from Text Parser ------------------ #
def filter_graph(G, filter_text):
    if not filter_text:
        return G

    filtered_G = nx.MultiDiGraph()

    for u, v, data in G.edges(data=True):
        if filter_text.lower() in u.lower() or filter_text.lower() in v.lower() or filter_text.lower() in data.get('label', '').lower():
            filtered_G.add_node(u)
            filtered_G.add_node(v)
            filtered_G.add_edge(u, v, label=data['label'])

    return filtered_G
    
def draw_filtered_graph(raw_record_str, filter_text=None, edge_type_filter=None, node_type_filter=None):
    G = nx.MultiDiGraph()
    edge_types = set()
    node_types = {}

    incoming_match = re.search(r"=== kg_rels \(incoming\) ===\\n(.*?)\\n\\n=== text ===", raw_record_str, re.DOTALL)
    outgoing_match = re.search(r"=== kg_rels \(outgoing\) ===\\n(.*)$", raw_record_str, re.DOTALL)

    def infer_node_type(node_name):
        # Simple heuristics for demo purposes (customize this as needed)
        if re.search(r'\b[A-Z]{2,}\b', node_name):  # Acronym-like
            return 'Paper'
        elif re.search(r'\s', node_name):  # Has space => likely person
            return 'Author'
        elif re.match(r'COVID|Cancer|Heart|Brain', node_name, re.IGNORECASE):
            return 'Topic'
        return 'Entity'

    def parse_edges(block):
        edge_lines = re.split(r"\\n---\\n \*+ \\n---\\n", block)
        for line in edge_lines:
            line = line.strip()
            if not line:
                continue
            match = re.match(r"^(.*?) - ([A-Z_]+)\((.*?)\) -> (.*?)$", line)
            if match:
                source, relation, details, target = match.groups()
                source = source.strip()
                target = target.strip()
                G.add_node(source)
                G.add_node(target)
                G.add_edge(source, target, label=relation.strip(), details=details.strip())
                node_types[source] = infer_node_type(source)
                node_types[target] = infer_node_type(target)
                edge_types.add(relation.strip())

    if incoming_match:
        parse_edges(incoming_match.group(1))
    if outgoing_match:
        parse_edges(outgoing_match.group(1))

    # Update session state
    st.session_state.all_edge_types = sorted(edge_types)
    st.session_state.all_node_types = sorted(set(node_types.values()))

    # Apply filters
    filtered_G = nx.MultiDiGraph()
    for u, v, data in G.edges(data=True):
        if (
            (not filter_text or filter_text.lower() in u.lower() or filter_text.lower() in v.lower() or filter_text.lower() in data.get('label', '').lower()) and
            (not edge_type_filter or data.get("label") in edge_type_filter) and
            (not node_type_filter or (node_types.get(u) in node_type_filter and node_types.get(v) in node_type_filter))
        ):
            filtered_G.add_node(u)
            filtered_G.add_node(v)
            filtered_G.add_edge(u, v, **data)

    net = Network(height="600px", width="100%", directed=True)

    for node in filtered_G.nodes:
        node_label = node
        node_type = node_types.get(node, "Unknown")
        net.add_node(node, label=node_label, title=f"Node: {node_label}<br>Type: {node_type}")

    for source, target, data in filtered_G.edges(data=True):
        label = data.get("label", "")
        details = data.get("details", "")
        net.add_edge(source, target, label=label, title=f"{label}: {details}")

    path = tempfile.NamedTemporaryFile(delete=False, suffix=".html").name
    net.save_graph(path)
    return path



if st.button("🔍 Run Query"):
    with st.spinner("Thinking..."):
        try:
            response = rag.search(user_query, retriever_config={"top_k": top_k}, return_context=True)
            st.success("✅ Query processed successfully.")
            
            st.session_state.raw_record = str(response.retriever_result.items[0].content)
            st.session_state.generated_answer = response.answer
            st.session_state.full_json = response.model_dump()

        except Exception as e:
            st.error(f"❌ An error occurred: {e}")


if st.session_state.get("generated_answer"):
    st.subheader("📌 Answer")
    st.markdown(st.session_state.generated_answer)

    with st.expander("📚 Full Context"):
        st.code(st.session_state.raw_record)

    with st.expander("🧾 Full JSON Response"):
        st.json(st.session_state.full_json)

if st.session_state.raw_record:
    with st.expander("🌐 Graph Visualization"):
        graph_html = draw_filtered_graph(
            st.session_state.raw_record,
            filter_text=graph_filter,
            edge_type_filter=edge_type_filter,
            node_type_filter=node_type_filter
        )
        if graph_html:
            st.components.v1.html(open(graph_html, 'r').read(), height=600, scrolling=True)


