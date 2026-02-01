import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import networkx as nx

def run_ml_pipeline():
    print("⏳ Loading Elliptic Dataset (this may take a minute)...")
    # Load features and labels
    features = pd.read_csv('elliptic_txs_features.csv', header=None)
    classes = pd.read_csv('elliptic_txs_classes.csv')
    edges = pd.read_csv('elliptic_txs_edgelist.csv')
    
    # Standardize columns
    features.columns = ['txId', 'timestep'] + [f'f_{i}' for i in range(165)]
    
    print("🕸️ Building Graph and Calculating Centrality...")
    G = nx.from_pandas_edgelist(edges, 'txId1', 'txId2', create_using=nx.DiGraph())
    
    # Calculate PageRank (measure of importance in the flow)
    print("   - Calculating PageRank...")
    pagerank = nx.pagerank(G, alpha=0.85)
    
    # Calculate Degree Centrality
    print("   - Calculating Degree Centrality...")
    degree_cent = nx.degree_centrality(G)
    
    # Convert to Series for merging
    pr_series = pd.Series(pagerank, name='pagerank')
    dc_series = pd.Series(degree_cent, name='degree_centrality')
    
    # Merge Features
    print("🔄 Merging Graph Features...")
    df = features.merge(classes, on='txId')
    df['txId'] = df['txId'].astype(str) # Ensure string match for index
    
    # Map graph indices (if they are int) to match df txId (which might be int or str)
    # The elliptic dataset usually has integer IDs. 
    # Let's ensure alignment by setting index to txId
    df = df.set_index('txId')
    
    # Reindex series to match df
    df['pagerank'] = pr_series
    df['degree_centrality'] = dc_series
    
    # Fill NaN (nodes in features but not in edge list, or vice versa)
    df['pagerank'] = df['pagerank'].fillna(0)
    df['degree_centrality'] = df['degree_centrality'].fillna(0)
    
    df = df.reset_index()

    # Train only on 'known' data (Class 1 = Illicit, Class 2 = Licit)
    train_set = df[df['class'] != 'unknown'].copy()
    train_set['target'] = train_set['class'].map({'1': 1, '2': 0})
    
    # Drop non-feature columns
    X = train_set.drop(['txId', 'class', 'target', 'timestep'], axis=1)
    y = train_set['target']
    
    print("🤖 Training AI Model (Random Forest + Graph Features)...")
    # Increased estimators and depth slightly for better capturing complex patterns
    model = RandomForestClassifier(n_estimators=100, max_depth=12, n_jobs=-1, random_state=42)
    model.fit(X, y)
    
    print("🎯 Predicting risk for all nodes...")
    X_all = df.drop(['txId', 'class', 'timestep'], axis=1)
    
    # Predict
    probs = model.predict_proba(X_all)[:, 1] * 100
    df['risk_score'] = probs
    
    # Export the results so the dashboard can use them
    # We include the new graph features in the export too, purely for debug/analysis logic if needed
    output_cols = ['txId', 'risk_score', 'class', 'timestep', 'pagerank', 'degree_centrality']
    df[output_cols].to_csv('processed_data.csv', index=False)
    print("✅ Success! 'processed_data.csv' created with Graph Features.")

if __name__ == "__main__":
    run_ml_pipeline()