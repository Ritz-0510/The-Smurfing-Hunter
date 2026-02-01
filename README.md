##The Smurfing Hunter
Blockchain Transaction Smurfing Detection System

---

##Overview
The Smurfing Hunter is a blockchain forensic analysis project designed to detect smurfing activities, a common money laundering technique where large transactions are intentionally split into multiple smaller ones to avoid detection. This system analyzes wallet transaction behavior to identify suspicious patterns and provides explainable forensic insights using transaction graphs.

The project is intended for academic use, hackathons, and blockchain forensics demonstrations.

---

##Problem Statement
Smurfing on blockchains makes illicit fund movement difficult to identify using traditional monitoring methods. Criminals distribute funds across multiple transactions and wallets, reducing visibility and traceability. The goal of this project is to automatically detect such behavior by analyzing transaction frequency, amount distribution, and wallet interaction patterns.

---

##Key Features

Detection of smurfing patterns in blockchain transaction data
Wallet-level risk scoring
Identification of abnormal transaction frequency and low-value transfers
Graph-based visualization of suspicious fund flows
Explainable reasons for each flagged wallet

---

##Approach
The system processes blockchain transaction data and aggregates activity at the wallet level. It applies rule-based heuristics such as frequent small-value transactions, rapid transaction timing, and repeated intermediary wallet usage. Suspicious wallets are scored and visualized using transaction graphs to support forensic analysis.

---

##Tech Stack
Python
Pandas
NetworkX
Matplotlib
Streamlit

---

##Project Structure
The-Smurfing-Hunter/
data/ – blockchain transaction datasets
smurfing_detection.py – core detection logic
graph_analysis.py – transaction graph construction
utils.py – helper functions
reports/ – generated forensic outputs

---

##How to Run

Clone the repository
git clone https://github.com/Ritz-0510/The-Smurfing-Hunter.git

Navigate to the project directory
cd The-Smurfing-Hunter

Install dependencies
pip install pandas networkx streamlit pyvis empfile os sys

Run the detection script
streamlit run smurfing_hunter_dashboard.py

---

##Output
The system produces a list of suspicious wallets, smurfing risk scores, explainable detection reasons, and visual transaction graphs for forensic inspection.
Integration of machine learning-based anomaly detection
Real-time blockchain data ingestion
Multi-blockchain support
Interactive web dashboard for visualization
