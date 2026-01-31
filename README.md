# 🧠 The Smurfing Hunter

A graph-based hackathon prototype to detect **money laundering (smurfing) patterns** in blockchain transactions.

---

## 🚨 Problem Statement
Smurfing is a money laundering technique where large amounts of cryptocurrency are split across many small transactions to hide illicit activity. Detecting such patterns requires analyzing **transaction flow structures**, not just individual transactions.

---

## 💡 Approach
We model blockchain transactions as a **directed graph**:
- **Nodes** → Transactions
- **Edges** → Flow of funds between transactions

Smurfing behavior creates characteristic:
- **Fan-out patterns** (one transaction → many)
- **Fan-in patterns** (many transactions → one)

These patterns are captured using simple, explainable graph metrics.

---

## 🛠️ Current Implementation
- Load Elliptic Bitcoin transaction dataset
- Construct a directed acyclic transaction graph
- Verify graph structure (node count, edge count, DAG property)
- Identify high-risk fan-out transactions using degree-based heuristics

---

## 📊 Dataset
We use the **Elliptic Bitcoin Dataset**.

⚠️ Due to GitHub size limits, the dataset is **not included** in this repository.

Please download from:
https://www.kaggle.com/datasets/ellipticco/elliptic-data-set

Place the following files in the project root:
- `elliptic_txs_features.csv`
- `elliptic_txs_edgelist.csv`

---

## ▶️ How to Run

```bash
pip install pandas networkx
python build_tx_graph.py
