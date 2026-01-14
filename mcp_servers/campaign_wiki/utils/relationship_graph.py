"""Relationship graph using networkx"""

import networkx as nx
from typing import List, Dict, Any
import matplotlib.pyplot as plt
from pathlib import Path


class RelationshipGraph:
    """Manage NPC/PC relationship graphs"""
    
    def __init__(self):
        self.graph = nx.DiGraph()
    
    def add_entity(self, entity_id: str, entity_data: Dict[str, Any]):
        """Add an entity (NPC or PC) to the graph"""
        self.graph.add_node(entity_id, **entity_data)
    
    def add_relationship(self, from_id: str, to_id: str, relationship_type: str, strength: int = 5, **kwargs):
        """Add a relationship between entities"""
        self.graph.add_edge(from_id, to_id, relationship_type=relationship_type, strength=strength, **kwargs)
    
    def get_relationships(self, entity_id: str) -> Dict[str, List]:
        """Get all relationships for an entity"""
        outgoing = list(self.graph.successors(entity_id))
        incoming = list(self.graph.predecessors(entity_id))
        
        return {
            "outgoing": [
                {
                    "target": target,
                    **self.graph[entity_id][target]
                }
                for target in outgoing
            ],
            "incoming": [
                {
                    "source": source,
                    **self.graph[source][entity_id]
                }
                for source in incoming
            ]
        }
    
    def find_connections(self, entity1_id: str, entity2_id: str) -> List[List[str]]:
        """Find all paths between two entities"""
        try:
            paths = list(nx.all_simple_paths(self.graph, entity1_id, entity2_id, cutoff=4))
            return paths
        except nx.NetworkXNoPath:
            return []
    
    def export_graphviz(self, output_path: str):
        """Export graph to Graphviz DOT format"""
        nx.drawing.nx_pydot.write_dot(self.graph, output_path)
    
    def visualize(self, output_path: str, figsize=(12, 8)):
        """Create a visualization of the relationship graph"""
        plt.figure(figsize=figsize)
        pos = nx.spring_layout(self.graph, k=0.5, iterations=50)
        
        # Draw nodes
        nx.draw_networkx_nodes(self.graph, pos, node_size=500, node_color='lightblue')
        
        # Draw edges with different colors for relationship types
        edges = self.graph.edges(data=True)
        edge_colors = {
            'friend': 'green',
            'enemy': 'red',
            'family': 'purple',
            'neutral': 'gray',
            'ally': 'blue',
            'rival': 'orange',
        }
        
        for edge in edges:
            rel_type = edge[2].get('relationship_type', 'neutral')
            color = edge_colors.get(rel_type, 'gray')
            nx.draw_networkx_edges(self.graph, pos, [(edge[0], edge[1])], edge_color=color, arrows=True)
        
        # Draw labels
        nx.draw_networkx_labels(self.graph, pos, font_size=8)
        
        plt.axis('off')
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()




