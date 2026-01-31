import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

# Load Elliptic dataset
txs = pd.read_csv(
    "elliptic_txs_features.csv",
    header=None,
    index_col=0
)

edges = pd.read_csv("elliptic_txs_edgelist.csv")

# Build directed transaction graph
G = nx.DiGraph()

for tx_id in txs.index:
    G.add_node(tx_id)

for _, row in edges.iterrows():
    G.add_edge(row["txId1"], row["txId2"])

print("Nodes:", G.number_of_nodes())
print("Edges:", G.number_of_edges())

# FAN-OUT DETECTION (Splitting)
out_degrees = dict(G.out_degree())
fan_out_node = max(out_degrees.items(), key=lambda x: x[1])[0]
print("Max out-degree:", out_degrees[fan_out_node])
print("Fan-out central node:", fan_out_node)

fan_out_neighbors = list(G.successors(fan_out_node))[:15]
fan_out_SG = G.subgraph([fan_out_node] + fan_out_neighbors)

plt.figure(figsize=(7, 7))
pos = nx.spring_layout(fan_out_SG, seed=42)

colors = ["red" if n == fan_out_node else "skyblue" for n in fan_out_SG.nodes()]
nx.draw(
    fan_out_SG,
    pos,
    node_color=colors,
    node_size=800,
    edge_color="gray",
    arrows=True,
    with_labels=False
)

plt.title("Fan-out Pattern (Splitting)")
plt.show()

# FAN-IN DETECTION (Re-aggregation)
in_degrees = dict(G.in_degree())
fan_in_node = max(in_degrees.items(), key=lambda x: x[1])[0]
print("Max in-degree:", in_degrees[fan_in_node])
print("Fan-in central node:", fan_in_node)

fan_in_neighbors = list(G.predecessors(fan_in_node))[:15]
fan_in_SG = G.subgraph([fan_in_node] + fan_in_neighbors)

plt.figure(figsize=(7, 7))
pos = nx.spring_layout(fan_in_SG, seed=42)

colors = ["red" if n == fan_in_node else "skyblue" for n in fan_in_SG.nodes()]
nx.draw(
    fan_in_SG,
    pos,
    node_color=colors,
    node_size=800,
    edge_color="gray",
    arrows=True,
    with_labels=False
)

plt.title("Fan-in Pattern (Re-aggregation)")
plt.show()

# MULTI-HOP PATH TRACING
# Pick most suspicious node overall
suspicious_node = max(G.degree(), key=lambda x: x[1])[0]
print("Node used for path tracing:", suspicious_node)

paths = nx.single_source_shortest_path(G, suspicious_node, cutoff=3)

multi_hop_chain = None
for path in paths.values():
    if len(path) >= 4:
        multi_hop_chain = path
        break

if multi_hop_chain:
    print("Multi-hop transaction chain:")
    print(" → ".join(map(str, multi_hop_chain)))

    chain_edges = list(zip(multi_hop_chain[:-1], multi_hop_chain[1:]))
    chain_G = nx.DiGraph(chain_edges)

    plt.figure(figsize=(8, 4))
    pos = nx.spring_layout(chain_G, seed=42)

    nx.draw(
        chain_G,
        pos,
        node_color="orange",
        node_size=900,
        edge_color="black",
        arrows=True,
        with_labels=False
    )

    plt.title("Multi-hop Blockchain Transaction Flow")
    plt.show()

# SUSPICION SCORING + TOP 5
scores = {
    n: G.in_degree(n) + G.out_degree(n)
    for n in G.nodes()
}

top_5 = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:5]

print("\nTop 5 Suspicious Transactions")
print("Tx_ID | Score")
for tx, score in top_5:
    print(tx, "|", score)
