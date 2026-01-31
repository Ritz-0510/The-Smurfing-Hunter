import pandas as pd
import networkx as nx
import streamlit as st
from pyvis.network import Network
import streamlit.components.v1 as components

# --- 1. UI CONFIGURATION ---
st.set_page_config(layout="wide", page_title="Smurfing Hunter Forensic Tool")
st.title("🛡️ The Smurfing Hunter: Crypto-Forensics Dashboard")
st.markdown("Detecting **Fan-out/Fan-in** structures and **Peeling Chains**.")

# --- 2. DATA LOADING & SCORING ---
@st.cache_data
def load_and_process():
    # Load Elliptic dataset files (Ensure these are in your local directory)
    txs = pd.read_csv("elliptic_bitcoin_dataset/elliptic_txs_features.csv", header=None, index_col=0)
    txs["wallet_id"] = txs.iloc[:, 1]
    edges = pd.read_csv("elliptic_bitcoin_dataset/elliptic_txs_edgelist.csv")
    classes = pd.read_csv("elliptic_bitcoin_dataset/elliptic_txs_classes.csv")
    
    # REQUIREMENT: Identify Seed Nodes (Class 1 = Known Illicit)
    illicit_tx_ids = classes[classes['class'] == '1']['txId']
    seed_nodes = set(txs.loc[txs.index.intersection(illicit_tx_ids), 'wallet_id'].unique())

    W = nx.DiGraph()
    for _, row in edges.iterrows():
        if row["txId1"] in txs.index and row["txId2"] in txs.index:
            w1, w2 = txs.loc[row["txId1"], "wallet_id"], txs.loc[row["txId2"], "wallet_id"]
            if w1 != w2:
                W.add_edge(w1, w2)

    # --- SUSPICION SCORING FOR EVERY WALLET ---
    # Based on centrality and proximity to illicit seeds
    centrality = nx.degree_centrality(W)
    scores = {}
    for n in W.nodes():
        # Topology Factor: Fan-out/Fan-in structures
        base = (0.3 * W.out_degree(n)) + (0.3 * W.in_degree(n)) + (0.4 * centrality.get(n, 0))
        
        # Seed Proximity: Boost if connected to known illicit node
        seed_boost = 100 if n in seed_nodes else 0
        for neighbor in W.neighbors(n):
            if neighbor in seed_nodes:
                seed_boost += 50
        
        scores[n] = base + seed_boost

    return W, scores, seed_nodes

W, all_scores, seed_nodes = load_and_process()

# --- 3. SIDEBAR: SEARCH & DOWNLOAD ---
st.sidebar.header("🔍 Global Search")
search_id = st.sidebar.text_input("Enter Wallet ID to Search:")

# Full report generation for all 195k+ wallets
full_report = pd.DataFrame(list(all_scores.items()), columns=["Wallet_ID", "Risk_Score"]).sort_values(by="Risk_Score", ascending=False)
st.sidebar.download_button("📥 Download Full Risk Report (CSV)", full_report.to_csv(index=False), "risk_report.csv")

# --- 4. TOP RISK DISPLAY ---
st.subheader("🚩 Highest Risk Entities Detected")
top_5 = full_report.head(5).reset_index(drop=True)
st.table(top_5) # First column is now just a clean index (Rank)

# --- 5. FORENSIC TRACE VISUALIZATION ---
def draw_forensic_graph(G, center_node):
    # Filter by Hops: Show only immediate neighborhood to fix clutter
    nodes = {center_node} | set(G.successors(center_node)) | set(G.predecessors(center_node))
    sub = G.subgraph(nodes)
    
    net = Network(height="600px", width="100%", directed=True, bgcolor="#f8f9fa")
    for n in sub.nodes():
        node_id = str(n)
        if n in seed_nodes:
            color, label = "#ff4b4b", "ILLICIT SEED"
        elif n == center_node:
            color, label = "#ffa500", "TARGET SUSPECT"
        elif G.out_degree(n) > G.in_degree(n):
            color, label = "#1c83e1", "MULE (Fan-out)"
        else:
            color, label = "#2eb086", "SINK (Fan-in)"
            
        net.add_node(node_id, label=f"{label}\n{node_id}", color=color, size=25 if n == center_node else 15)

    for e in sub.edges():
        net.add_edge(str(e[0]), str(e[1]), color="#808080")

    net.save_graph("forensic_trace.html")
    components.html(open("forensic_trace.html", 'r').read(), height=650)

# --- SEARCH EXECUTION WITH TYPE FIX ---
if search_id:
    try:
        # FIX: Convert string input to float to match dataset format
        query_id = float(search_id)
        
        if query_id in all_scores:
            st.subheader(f"Analysis for Wallet: {search_id}")
            col1, col2 = st.columns(2)
            col1.metric("Suspicion Score", f"{all_scores[query_id]:.2f}")
            col2.metric("Connections", W.degree(query_id))
            
            draw_forensic_graph(W, query_id)
        else:
            st.error(f"Wallet ID {search_id} not found. Check the Top Risk table for valid IDs.")
    except ValueError:
        st.error("Please enter a numeric ID (e.g., -0.1605).")
else:
    # Default view for the Top Suspect
    st.info("Searching for the #1 highest risk wallet by default.")
    draw_forensic_graph(W, full_report.iloc[0]["Wallet_ID"])