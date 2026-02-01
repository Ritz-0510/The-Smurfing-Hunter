# 🕵️‍♂️ Smurfing Hunter AI  
**Graph-Based Blockchain Forensics Dashboard**

Smurfing Hunter AI is an **interactive blockchain forensics platform** designed to identify and analyze **money laundering patterns** in large-scale cryptocurrency transaction networks. The system combines **graph-based machine learning**, **network topology analysis**, and **explainable visualizations** to assist investigators in detecting suspicious financial behavior.

Built on real-world blockchain data from the **Elliptic dataset**, the platform focuses on uncovering complex laundering strategies such as **smurfing rings** (coordinated fund splitting across multiple wallets) and **peeling chains** (gradual fund transfer across sequential hops). By integrating **AI-generated risk scores**, **centrality measures**, and **structural pattern detectors**, the dashboard enables both **automated risk assessment** and **human-in-the-loop investigation**.

The application is implemented using **Streamlit** for rapid interactive analysis and **NetworkX + PyVis** for forensic graph visualization, making it suitable for **academic research, AML analysis, and hackathon demonstrations**.

---

## 🚀 Features

- 🔍 **Transaction-Level Investigation**
- 🧠 **AI Risk Scoring Integration**
- 🕸️ **Graph-Based Pattern Detection**
  - Smurfing Topology Detection
  - Peeling Chain Detection
- 📊 **Interactive Network Visualization (PyVis)**
- 📈 **PageRank & Degree Centrality Analysis**
- 📥 **Exportable Forensic Investigation Report**

---

## 🛠️ Tech Stack

- Python 3.8+
- Streamlit (interactive dashboard)
- Pandas (data manipulation)
- NetworkX (graph construction & analysis)
- PyVis (interactive network visualization)
- Vis.js (graph rendering engine)
- scikit-learn (model training & evaluation)

**Development Tools**
- Git & GitHub
- Kaggle (dataset hosting)
 
---

## 🧱 Project Structure
The-Smurfing-Hunter-main/
  - elliptic_txs_classes.csv # Ground-truth transaction labels
  - elliptic_txs_edgelist.csv # Blockchain transaction edges
  - elliptic_txs_features.csv # Raw transaction features (Elliptic dataset)
  - processed_data.csv # Generated risk scores & graph features
  - smurfing_hunter_dashboard.py # Streamlit forensic dashboard
  - trainer.py # Feature engineering & risk scoring
  - test_detectors.py # Detector validation tests
  - lib/
    - init.py
    - detectors.py # Smurfing & peeling detection logic
  - README.md
  
---

## ⚙️ Requirements

Install dependencies using:

```bash
pip install streamlit pandas networkx pyvis
streamlit run smurfing_hunter_dashboard.py
```
---

## 📦 Dataset (External Download Required)

Due to GitHub file size limitations, the original Elliptic dataset files are **not included in this repository**.

### 🔗 Dataset Source
Download the dataset from Kaggle:

https://www.kaggle.com/datasets/ellipticco/elliptic-data-set

### 📁 Required Files
After downloading, place the following files in the project root directory:

- `elliptic_txs_features.csv`
- `elliptic_txs_edgelist.csv`
- `elliptic_txs_classes.csv`

### ⚠️ Note
- `elliptic_txs_features.csv` is ~700MB and cannot be pushed to GitHub
- `processed_data.csv` is generated locally by running `trainer.py`
- All experiments and visualizations are fully reproducible once the dataset is downloaded

---
