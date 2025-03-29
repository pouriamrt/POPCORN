import tempfile, re, networkx as nx
from pyvis.network import Network
import streamlit as st

def draw_filtered_graph(raw_record_str, filter_text=None, edge_type_filter=None, node_type_filter=None):
    G = nx.MultiDiGraph()
    edge_types = set()
    node_types = {}

    newline = r"(?:\\n|\n)"
    separator = rf"{newline}---{newline} \*+ {newline}---{newline}"

    incoming_match = re.search(rf"=== kg_rels \(incoming\) ==={newline}(.*?){newline}{newline}=== text ===", raw_record_str, re.DOTALL)
    outgoing_match = re.search(rf"=== kg_rels \(outgoing\) ==={newline}(.*)$", raw_record_str, re.DOTALL)

    def infer_node_type(name):
        if re.search(r'\b[A-Z]{2,}\b', name): return 'Paper'
        if re.search(r'\s', name): return 'Author'
        if re.match(r'COVID|Cancer|Heart|Brain', name, re.IGNORECASE): return 'Topic'
        return 'Entity'

    def parse_edges(block):
        for line in re.split(separator, block):
            line = line.strip()
            if not line: continue
            match = re.match(r"^(.*?) - ([A-Z_]+)\((.*?)\) -> (.*?)$", line)
            if match:
                src, rel, det, tgt = match.groups()
                G.add_node(src)
                G.add_node(tgt)
                G.add_edge(src, tgt, label=rel.strip(), details=det.strip())
                node_types[src] = infer_node_type(src)
                node_types[tgt] = infer_node_type(tgt)
                edge_types.add(rel.strip())

    if incoming_match: parse_edges(incoming_match.group(1))
    if outgoing_match: parse_edges(outgoing_match.group(1))

    st.session_state.all_edge_types = sorted(edge_types)
    st.session_state.all_node_types = sorted(set(node_types.values()))

    FG = nx.MultiDiGraph()
    for u, v, d in G.edges(data=True):
        if ((not filter_text or filter_text.lower() in u.lower() or filter_text.lower() in v.lower() or filter_text.lower() in d.get('label', '').lower()) and
            (not edge_type_filter or d.get("label") in edge_type_filter) and
            (not node_type_filter or (node_types.get(u) in node_type_filter and node_types.get(v) in node_type_filter))):
            FG.add_node(u)
            FG.add_node(v)
            FG.add_edge(u, v, **d)

    net = Network(height="600px", width="100%", directed=True)
    for node in FG.nodes:
        net.add_node(node, label=node, title=f"Node: {node}<br>Type: {node_types.get(node, 'Unknown')}")
    for s, t, d in FG.edges(data=True):
        net.add_edge(s, t, label=d.get("label", ""), title=f"{d.get('label', '')}: {d.get('details', '')}")

    path = tempfile.NamedTemporaryFile(delete=False, suffix=".html").name
    net.save_graph(path)
    return path
