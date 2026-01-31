import pandas as pd
import networkx as nx

# -----------------------------
# Load Elliptic dataset
# NOTE: Dataset is NOT tracked in Git.
# Download from Kaggle and place in project root.
# -----------------------------

txs = pd.read_csv(
    "elliptic_txs_features.csv",
    header=None,
    index_col=0
)

edges = pd.read_csv("elliptic_txs_edgelist.csv")

# -----------------------------
# Create directed graph
# -----------------------------

G = nx.DiGraph()

# Add transaction nodes
for tx_id in txs.index:
    G.add_node(tx_id)

# Add directed edges (fund flow)
for _, row in edges.iterrows():
    G.add_edge(row["txId1"], row["txId2"])

# -----------------------------
# Verification / sanity checks
# -----------------------------

print("Nodes:", G.number_of_nodes())
print("Edges:", G.number_of_edges())

# Sample edge
u, v, attrs = next(iter(G.edges(data=True)))
print(f"Sample edge: {u} → {v}", attrs)

# Degree analysis
degrees = [d for _, d in G.out_degree()]
print("Max out-degree:", max(degrees))

# DAG check
print("Topological sort sample:", list(nx.topological_sort(G))[:10])

# -----------------------------
# Simple smurfing heuristic (fan-out)
# -----------------------------

THRESHOLD = 100  # conservative threshold

suspicious_fan_out = [
    n for n, d in G.out_degree()
    if d > THRESHOLD
]

print("Suspicious fan-out nodes:", len(suspicious_fan_out))

import matplotlib.pyplot as plt

# -----------------------------
# Find most suspicious fan-out node
# -----------------------------

# Get node with highest out-degree
central_node = max(G.out_degree, key=lambda x: x[1])[0]
print("Central suspicious node:", central_node)

# Get its immediate outgoing neighbors
neighbors = list(G.successors(central_node))[:15]  # limit to 10–20

# Create subgraph nodes
subgraph_nodes = [central_node] + neighbors
SG = G.subgraph(subgraph_nodes)

# -----------------------------
# Visualization
# -----------------------------

plt.figure(figsize=(8, 8))

pos = nx.spring_layout(SG, seed=42)

# Color nodes
node_colors = []
for node in SG.nodes():
    if node == central_node:
        node_colors.append("red")
    else:
        node_colors.append("skyblue")

# Draw graph
nx.draw(
    SG,
    pos,
    with_labels=False,
    node_color=node_colors,
    node_size=800,
    edge_color="gray",
    arrows=True
)

plt.title("Smurfing Pattern: Fan-out Transaction Subgraph")
plt.show()
