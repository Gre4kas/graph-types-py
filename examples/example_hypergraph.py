"""
Hypergraph Example for graph-types-py

Demonstrates:
- Creating a hypergraph (hyperedges connect 3+ vertices)
- Modeling collaborative networks (teams, projects, events)
- Hyperedge operations (edges connecting multiple vertices simultaneously)
- Converting to incidence matrix representation
"""

from packages.graphs.hypergraph import Hypergraph
from packages.representations.adjacency_list import to_adjacency_list
from packages.representations.incidence_matrix import to_incidence_matrix


def main():
    # Create a hypergraph representing cities connected by regional projects
    graph = Hypergraph()
    
    # Add vertices (cities participating in projects)
    cities = ["Kyiv", "Lviv", "Odesa", "Kharkiv", "Dnipro", "Zaporizhzhia", "Vinnytsia"]
    for city in cities:
        graph.add_vertex(city)
    
    # Add hyperedges (each represents a regional cooperation project)
    # Hyperedge connects multiple cities simultaneously
    projects = [
        {
            "name": "Western Development",
            "vertices": ["Kyiv", "Lviv", "Vinnytsia"],
            "budget": 1000000
        },
        {
            "name": "Southern Infrastructure",
            "vertices": ["Odesa", "Kharkiv", "Zaporizhzhia"],
            "budget": 1500000
        },
        {
            "name": "Central Hub Project",
            "vertices": ["Kyiv", "Dnipro", "Kharkiv", "Zaporizhzhia"],
            "budget": 2000000
        },
        {
            "name": "Tourism Initiative",
            "vertices": ["Lviv", "Odesa", "Vinnytsia"],
            "budget": 800000
        },
        {
            "name": "Tech Corridor",
            "vertices": ["Kyiv", "Lviv", "Kharkiv"],
            "budget": 1200000
        },
    ]
    
    print("=== Hypergraph Structure ===")
    for project in projects:
        hyperedge_id = graph.add_hyperedge(
            vertices=project["vertices"],
            name=project["name"],
            budget=project["budget"]
        )
        print(f"Added hyperedge '{project['name']}': {project['vertices']}")
    
    print(f"\nTotal vertices: {len(graph.get_vertices())}")
    print(f"Total hyperedges: {graph.hyperedge_count()}\n")
    
    # Analyze vertex participation
    print("=== City Participation in Projects ===")
    for city in cities:
        hyperedges = graph.get_hyperedges_containing(city)
        print(f"{city}: {len(hyperedges)} projects")
        for he in hyperedges:
            print(f"  - {he['name']} (budget: ${he['budget']:,})")
        print()
    
    # Find cities that share hyperedges (collaborate on projects)
    print("=== Collaboration Analysis ===")
    kyiv_neighbors = graph.get_neighbors("Kyiv")
    print(f"Cities collaborating with Kyiv: {', '.join(kyiv_neighbors)}\n")
    
    # Convert to adjacency list (shows which cities are connected via hyperedges)
    print("=== Adjacency List Representation ===")
    adj_list = to_adjacency_list(graph)
    for city, neighbors in list(adj_list.items())[:3]:  # Show first 3
        print(f"{city}: {neighbors}")
    print("...\n")
    
    # Convert to incidence matrix (rows=vertices, cols=hyperedges)
    print("=== Incidence Matrix ===")
    incidence_matrix = to_incidence_matrix(graph)
    print(f"Shape: {incidence_matrix.shape} (cities × projects)")
    print("Matrix (1 indicates city participates in project):")
    print(incidence_matrix)


if __name__ == "__main__":
    main()
