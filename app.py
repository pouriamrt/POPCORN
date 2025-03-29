import streamlit as st
from utils.auth import handle_authentication
from utils.neo4j_setup import setup_neo4j_and_llm
from utils.graph_viz import draw_filtered_graph
from dotenv import load_dotenv
import os

# ------------------ Page Config ------------------ #
st.set_page_config(page_title="GraphRAG Q&A Interface", layout="wide")

# ------------------ Load Environment ------------------ #
load_dotenv('.env', override=True)

# ------------------ Authentication ------------------ #
user_info = handle_authentication()

# ------------------ Neo4j & LLM Setup ------------------ #
rag = setup_neo4j_and_llm()

# ------------------ Main UI ------------------ #
st.title("🤖 GraphRAG-Powered QA Interface")
st.markdown("Ask natural language questions about your Neo4j knowledge graph.")

with st.sidebar:
    if user_info:
        st.image(user_info.get("picture"), width=100)
        st.write(f"**Welcome, {user_info.get('name')}**")
        st.write(f"📧 {user_info.get('email')}")

    if st.button("🚪 Logout"):
        st.session_state.clear()
        st.rerun()

    st.header("⚙️ Configuration")
    top_k = st.slider("Top K Chunks", min_value=1, max_value=10, value=4)
    use_example = st.checkbox("Use example question", value=True)
    st.header("🧩 Graph Filters")

    edge_type_filter = st.multiselect("Filter by Edge Type", options=st.session_state.get('all_edge_types', []), default=st.session_state.get('all_edge_types', []))
    node_type_filter = st.multiselect("Filter by Node Type", options=st.session_state.get('all_node_types', []), default=st.session_state.get('all_node_types', []))

user_query = st.text_area("📝 Enter your query:", value="Write a summary about COVID and list all the papers." if use_example else "", height=120)
graph_filter = st.text_input("🔎 Filter Graph Nodes/Edges")

if st.button("🔍 Run Query"):
    with st.spinner("Thinking..."):
        try:
            response = rag.search(user_query, retriever_config={"top_k": top_k}, return_context=True)
            st.session_state.raw_record = str(response.retriever_result.items[0].content)
            st.session_state.generated_answer = response.answer
            st.session_state.full_json = response.model_dump()
            st.success("✅ Query processed successfully.")
        except Exception as e:
            st.error(f"❌ An error occurred: {e}")

if st.session_state.get("generated_answer"):
    st.subheader("📌 Answer")
    st.markdown(st.session_state.generated_answer)
    with st.expander("📚 Full Context"):
        st.code(st.session_state.raw_record)
    with st.expander("🧾 Full JSON Response"):
        st.json(st.session_state.full_json)

if st.session_state.get("raw_record"):
    with st.expander("🌐 Graph Visualization"):
        graph_html = draw_filtered_graph(
            st.session_state.raw_record,
            filter_text=graph_filter,
            edge_type_filter=edge_type_filter,
            node_type_filter=node_type_filter
        )
        if graph_html:
            st.components.v1.html(open(graph_html, 'r').read(), height=600, scrolling=True)
