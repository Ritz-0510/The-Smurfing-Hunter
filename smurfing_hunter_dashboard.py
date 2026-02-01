import streamlit as st
import pandas as pd
import networkx as nx
from pyvis.network import Network
import tempfile
import os
import sys

# Ensure we can import from lib
sys.path.append(os.getcwd())
from lib.detectors import detect_smurfing_topology, detect_peeling_chain

# 1. Page Setup
st.set_page_config(page_title="Smurfing Hunter AI", layout="wide", page_icon="🕵️‍♂️")

st.markdown("""
<style>
    .reportview-container {
        background: #f0f2f6;
    }
    .metric-box {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# 2. Load Data (The pre-processed results)
@st.cache_data
def load_data():
    try:
        # Check if processed data exists, if not warn user
        if not os.path.exists('processed_data.csv'):
            return None, None
            
        df = pd.read_csv('processed_data.csv')
        edges = pd.read_csv('elliptic_txs_edgelist.csv')
        df['txId'] = df['txId'].astype(str)
        edges['txId1'] = edges['txId1'].astype(str)
        edges['txId2'] = edges['txId2'].astype(str)
        return df, edges
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None, None

df, edges = load_data()

if df is None:
    st.warning("⚠️ Data not found. Please run `python trainer.py` first to generate the models and graph features.")
    st.stop()

risk_dict = dict(zip(df['txId'], df['risk_score']))
class_dict = dict(zip(df['txId'], df['class']))
# Load new graph features if available
if 'pagerank' in df.columns:
    pagerank_dict = dict(zip(df['txId'], df['pagerank']))
else:
    pagerank_dict = {}

# 3. Build the Network Graph (Global)
@st.cache_resource
def build_network(_edges):
    G = nx.DiGraph()
    G.add_edges_from(zip(_edges['txId1'], _edges['txId2']))
    return G

G = build_network(edges)

# 4. Sidebar & Summary Dashboard
with st.sidebar:
    st.title("🛡️ Network Health")
    
    # Calculate global stats for Summary Dashboard
    high_risk_total = len(df[df['risk_score'] > 80])
    unknown_flagged = len(df[(df['class'] == 'unknown') & (df['risk_score'] > 75)])
    
    col_a, col_b = st.columns(2)
    col_a.metric("High Risk", high_risk_total)
    col_b.metric("AI Flagged Unknowns", unknown_flagged)
    
    st.divider()
    st.header("Investigation Panel")
    
    default_target = "230425876"
    if default_target not in G:
        # Fallback to a node that exists if default is missing
        default_target = list(G.nodes())[0]
        
    target_id = st.text_input("Enter Transaction ID", default_target)
    hops = st.slider("Neighborhood Depth", 1, 3, 2, help="How many hops away from the target to visualize.")
    
    st.divider()
    st.info("AI classifies risk based on node features, PageRank, and structural topology.")

# 5. Dashboard Logic & Pattern Labeling
st.title("🔍 Smurfing Hunter: Graph ML Forensics")

if target_id in G:
    # --- 5.1 Run Detectors ---
    smurf_alert = detect_smurfing_topology(G, target_id, search_depth=hops)
    peeling_alert = detect_peeling_chain(G, target_id)
    
    # Logic to prioritize alerts
    pattern_label = "Standard Transaction"
    pattern_color = "green"
    alert_details = None
    
    if smurf_alert:
        pattern_label = f"🚨 {smurf_alert['type']}"
        pattern_color = "red"
        alert_details = smurf_alert
    elif peeling_alert:
        pattern_label = f"⚠️ {peeling_alert['type']}"
        pattern_color = "orange"
        alert_details = peeling_alert

    # --- 5.2 Metrics Display ---
    c1, c2, c3, c4 = st.columns(4)
    score = risk_dict.get(target_id, 0)
    
    # Determine Risk Level
    risk_level = "LOW"
    risk_delta_color = "normal"
    if score > 75: 
        risk_level = "CRITICAL"
        risk_delta_color = "inverse"
    elif score > 50: 
        risk_level = "HIGH"
        risk_delta_color = "off"
        
    c1.metric("AI Risk Score", f"{score:.1f}%", delta=risk_level, delta_color=risk_delta_color)
    c2.metric("PageRank Centrality", f"{pagerank_dict.get(target_id, 0):.6f}")
    c3.metric("Structure Type", pattern_label)
    
    # In/Out Degree
    in_d = G.in_degree(target_id)
    out_d = G.out_degree(target_id)
    c4.metric("In/Out Degree", f"{in_d} / {out_d}")

    # --- 5.3 Alert Box ---
    if alert_details:
        st.error(f"**Topology Alert:** {pattern_label} detected with **{alert_details['confidence']}% Confidence**.")
        if 'paths' in alert_details:
            st.write(f"Found {len(alert_details['paths'])} distinct paths in this circle.")

    # --- 5.4 Graph Visualization ---
    st.subheader("Forensic Subgraph")
    
    # Create Subgraph
    nodes = {target_id}
    for _ in range(hops):
        new_nodes = set()
        for n in nodes:
            new_nodes.update(G.predecessors(n))
            new_nodes.update(G.successors(n))
        nodes.update(new_nodes)
    sub = G.subgraph(nodes)
    
    net = Network(height='600px', width='100%', directed=True, bgcolor="#ffffff")
    
    # Layout optimization
    net.force_atlas_2based()
    
    # Identify nodes to highlight (from detectors)
    highlight_nodes = set()
    if smurf_alert and 'paths' in smurf_alert:
        for p in smurf_alert['paths']:
            highlight_nodes.update(p)
    if peeling_alert and 'nodes' in peeling_alert:
        highlight_nodes.update(peeling_alert['nodes'])
            
    for n in sub.nodes():
        r = risk_dict.get(n, 0)
        
        # Color Logic
        color = "#2ecc71" # Green
        if r > 40: color = "#f1c40f" # Orange
        if r > 70: color = "#e74c3c" # Red
        
        border_width = 1
        if n == target_id: 
            color = "#8e44ad" # Purple
            border_width = 3
        elif n in highlight_nodes:
            color = "#e67e22" # Dark Orange for pattern participants
            border_width = 2
            
        net.add_node(n, label=str(n)[:6], title=f"ID: {n}\nRisk: {r:.1f}%\nPageRank: {pagerank_dict.get(n,0):.5f}", color=color, borderWidth=border_width)
    
    for e in sub.edges():
        color = "#dddddd"
        width = 1
        # Highlight pattern edges
        if e[0] in highlight_nodes and e[1] in highlight_nodes:
            color = "#e67e22"
            width = 2
            
        net.add_edge(e[0], e[1], color=color, width=width)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as f:
        net.save_graph(f.name)
        st.components.v1.html(open(f.name, 'r').read(), height=650)
else:
    st.warning("Transaction ID not found in the transaction graph.")

# 6. Analysis Tables
st.divider()
c_left, c_right = st.columns(2)

with c_left:
    st.subheader("🚩 Top Suspicious Wallets")
    st.dataframe(df[['txId', 'risk_score', 'pagerank']].sort_values('risk_score', ascending=False).head(10), use_container_width=True)

with c_right:
    st.subheader("🧐 High PageRank Nodes (Hubs)")
    st.dataframe(df[['txId', 'pagerank', 'risk_score']].sort_values('pagerank', ascending=False).head(10), use_container_width=True)

# 7. Final CSV Export
@st.cache_data
def convert_df_to_csv(df_to_convert):
    return df_to_convert.to_csv(index=False).encode('utf-8')

st.divider()
csv_binary = convert_df_to_csv(df)
st.download_button(
    label="📥 Download Full Investigation Report",
    data=csv_binary,
    file_name='smurfing_investigation_report.csv',
    mime='text/csv',
)