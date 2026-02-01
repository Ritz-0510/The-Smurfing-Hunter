import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import networkx as nx

def run_ml_pipeline():
    print("⏳ Loading Elliptic Dataset (this may take a minute)...")

    features = pd.read_csv('elliptic_txs_features.csv', header=None)
    classes = pd.read_csv('elliptic_txs_classes.csv')
    edges = pd.read_csv('elliptic_txs_edgelist.csv')

    # Standardize columns
    features.columns = ['txId', 'timestep'] + [f'f_{i}' for i in range(165)]

    # 🔑 FORCE txId to string EVERYWHERE
    features['txId'] = features['txId'].astype(str)
    classes['txId'] = classes['txId'].astype(str)
    edges['txId1'] = edges['txId1'].astype(str)
    edges['txId2'] = edges['txId2'].astype(str)

    print("🕸️ Building Graph and Calculating Centrality...")
    G = nx.from_pandas_edgelist(
        edges, 'txId1', 'txId2', create_using=nx.DiGraph()
    )

    print("   - Calculating PageRank...")
    pagerank = nx.pagerank(G, alpha=0.85)

    print("   - Calculating Degree Centrality...")
    degree_cent = nx.degree_centrality(G)

    # Convert to Series (indices are now strings ✔)
    pr_series = pd.Series(pagerank, name='pagerank')
    dc_series = pd.Series(degree_cent, name='degree_centrality')

    print("🔄 Merging Graph Features...")
    df = features.merge(classes, on='txId')
    df = df.set_index('txId')

    # Correct alignment
    df['pagerank'] = pr_series
    df['degree_centrality'] = dc_series

    # Fill missing values safely
    df[['pagerank', 'degree_centrality']] = df[['pagerank', 'degree_centrality']].fillna(0)

    df = df.reset_index()

    # Train only on known labels
    train_set = df[df['class'] != 'unknown'].copy()
    train_set['target'] = train_set['class'].map({'1': 1, '2': 0})

    X = train_set.drop(['txId', 'class', 'target', 'timestep'], axis=1)
    y = train_set['target']

    print("🤖 Training AI Model (Random Forest + Graph Features)...")
    model = RandomForestClassifier(
        n_estimators=100, max_depth=12, n_jobs=-1, random_state=42
    )
    model.fit(X, y)

    print("🎯 Predicting risk for all nodes...")
    X_all = df.drop(['txId', 'class', 'timestep'], axis=1)
    probs = model.predict_proba(X_all)[:, 1] * 100
    df['risk_score'] = probs

    output_cols = [
        'txId', 'risk_score', 'class', 'timestep',
        'pagerank', 'degree_centrality'
    ]
    df[output_cols].to_csv('processed_data.csv', index=False)

    print("✅ Success! 'processed_data.csv' created with correct PageRank values.")

if __name__ == "__main__":
    run_ml_pipeline()
