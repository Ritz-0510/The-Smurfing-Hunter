
import networkx as nx
import unittest
from lib.detectors import detect_smurfing_topology, detect_peeling_chain

class TestSmurfingDetectors(unittest.TestCase):
    
    def test_fan_out(self):
        G = nx.DiGraph()
        # A sends to B, C, D, E, F (Fan Out > 5)
        edges = [('A', 'B'), ('A', 'C'), ('A', 'D'), ('A', 'E'), ('A', 'F')]
        G.add_edges_from(edges)
        
        result = detect_smurfing_topology(G, 'A')
        self.assertIsNotNone(result)
        self.assertEqual(result['type'], 'Fan-Out (Source)')

    def test_fan_in(self):
        G = nx.DiGraph()
        edges = [('B', 'A'), ('C', 'A'), ('D', 'A'), ('E', 'A'), ('F', 'A')]
        G.add_edges_from(edges)
        
        result = detect_smurfing_topology(G, 'A')
        self.assertIsNotNone(result)
        self.assertEqual(result['type'], 'Fan-In (Destination)')

    def test_smurfing_diamond(self):
        # A -> B -> D
        # A -> C -> D
        # Target is B. B is part of the loop A->{B,C}->D
        G = nx.DiGraph()
        edges = [
            ('Source', 'Mule1'), ('Source', 'Mule2'),
            ('Mule1', 'Dest'), ('Mule2', 'Dest')
        ]
        G.add_edges_from(edges)
        
        # Test checking Mule1
        result = detect_smurfing_topology(G, 'Mule1', search_depth=2)
        self.assertIsNotNone(result)
        self.assertEqual(result['type'], 'Smurf/Layering Mules')
        
    def test_peeling_chain(self):
        # A -> B -> C -> D -> E
        # With small side outputs usually, but simplified here to linear chain
        G = nx.DiGraph()
        edges = [('A', 'B'), ('B', 'C'), ('C', 'D'), ('D', 'E')]
        G.add_edges_from(edges)
        
        # Add some noise (side payments) to make it realistic 
        # A -> Payment1
        # B -> Payment2
        edges_noise = [('A', 'p1'), ('B', 'p2'), ('C', 'p3'), ('D', 'p4')]
        G.add_edges_from(edges_noise)
        
        result = detect_peeling_chain(G, 'A')
        self.assertIsNotNone(result)
        self.assertEqual(result['type'], 'Peeling Chain')
        self.assertEqual(len(result['nodes']), 5)

if __name__ == '__main__':
    unittest.main()
