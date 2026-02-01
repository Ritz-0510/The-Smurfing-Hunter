import networkx as nx

def detect_smurfing_topology(G, target_node, search_depth=2, max_paths=100):
    """
    Detects 'Fan-out -> Fan-in' patterns typical of Smurfing/Layering.
    
    Structure:
    Source (Fan-out) -> [Intermediaries] -> Destination (Fan-in)
    
    We look for loops starting and ending at 'target_node' or passing through it significantly.
    However, the classic smurf pattern is: 
       A -> {B, C, D} -> E
    where 'target_node' might be any of these.
    
    If 'target_node' is an intermediary (B), we look for A (predecessor) and E (successor).
    If 'prev' splits to multiple, and 'next' receives from multiple, it's suspicious.
    """
    if target_node not in G:
        return None, "Node not found"

    suspicion_details = {}
    is_suspicious = False
    
    # 1. Check for Fan-Out / Fan-In around the node
    predecessors = list(G.predecessors(target_node))
    successors = list(G.successors(target_node))
    
    in_degree = len(predecessors)
    out_degree = len(successors)
    
    # Heuristic 1: High Fan-Out (Structuring placement)
    if out_degree >= 5:
        suspicion_details['type'] = 'Fan-Out (Source)'
        suspicion_details['confidence'] = min(out_degree * 5, 100) # Cap at 100
        is_suspicious = True
        
    # Heuristic 2: High Fan-In (Aggregation/Collection)
    elif in_degree >= 5:
        suspicion_details['type'] = 'Fan-In (Destination)'
        suspicion_details['confidence'] = min(in_degree * 5, 100)
        is_suspicious = True
        
    # Heuristic 3: The Intermediary (Smurf)
    # Checks if this node is part of a diamond/circle: Prev -> Me -> Next, and Prev -> Other -> Next
    elif in_degree > 0 and out_degree > 0:
        # Check simple cycles or diamonds
        for p in predecessors:
            for s in successors:
                # Find all paths from P to S
                try:
                    paths = list(nx.all_simple_paths(G, source=p, target=s, cutoff=search_depth))
                    # If there are multiple paths from my predecessor to my successor, 
                    # it means funds are taking multiple routes (Layering).
                    if len(paths) >= 2:
                        suspicion_details['type'] = 'Smurf/Layering Mules'
                        suspicion_details['confidence'] = 85
                        suspicion_details['paths'] = paths
                        is_suspicious = True
                        break
                except nx.NetworkXNoPath:
                    continue
            if is_suspicious: break

    if is_suspicious:
        return suspicion_details
    return None

def detect_peeling_chain(G, target_node):
    """
    Detects Peeling Chains: One main output (change) and one small output (payment/fee), repeated.
    A -> B (large)
      -> C (small)
    B -> D (large)
      -> E (small)
      
    For this simplified version without amounts, we look for long linear chains 
    where nodes have consistently Low Out-Degree (approx 2).
    """
    if target_node not in G: 
        return None

    # Walk forward
    current = target_node
    chain = [current]
    
    for _ in range(5): # Check for chain length 5
        succ = list(G.successors(current))
        if len(succ) == 2: # Classic peeling: 1 change, 1 payment
            # Heuristic: Follow the path. 
            # In a real scenario with amounts, we'd follow the larger amount.
            # Here, we just pick the first neighbor for structural check.
            current = succ[0] 
            chain.append(current)
        elif len(succ) == 1:
            current = succ[0]
            chain.append(current)
        else:
            break
            
    if len(chain) >= 4:
        return {
            'type': 'Peeling Chain',
            'confidence': len(chain) * 15,
            'nodes': chain
        }
    return None
