"""
NetworkX integration adapter.

Provides bidirectional conversion between graph-library and NetworkX graphs.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from packages.core.base_graph import BaseGraph

try:
    import networkx as nx

    NETWORKX_AVAILABLE = True
except ImportError:
    NETWORKX_AVAILABLE = False
    nx = None  # type: ignore


class NetworkXAdapter:
    """
    Adapter for converting between graph-library and NetworkX.

    Supports bidirectional conversion with attribute preservation.

    Examples:
        >>> import networkx as nx
        >>> from packages.graphs.simple_graph import SimpleGraph
        >>> 
        >>> # Our graph -> NetworkX
        >>> graph = SimpleGraph()
        >>> graph.add_vertex("A", color="red")
        >>> graph.add_edge("A", "B", weight=5.0)
        >>> nx_graph = NetworkXAdapter.to_networkx(graph)
        >>> 
        >>> # NetworkX -> Our graph
        >>> nx_g = nx.karate_club_graph()
        >>> our_graph = NetworkXAdapter.from_networkx(nx_g)
    """

    @staticmethod
    def _check_networkx_available() -> None:
        """Check if NetworkX is available."""
        if not NETWORKX_AVAILABLE:
            msg = (
                "NetworkX is not installed. "
                "Install it with: pip install networkx"
            )
            raise ImportError(msg)

    @staticmethod
    def to_networkx(graph: BaseGraph) -> Any:
        """
        Convert our graph to NetworkX graph.

        Args:
            graph: Graph to convert

        Returns:
            NetworkX Graph, DiGraph, MultiGraph, or MultiDiGraph

        Raises:
            ImportError: If NetworkX is not installed

        Examples:
            >>> graph = SimpleGraph()
            >>> graph.add_vertex("A")
            >>> graph.add_vertex("B")
            >>> graph.add_edge("A", "B", weight=5.0)
            >>> nx_graph = NetworkXAdapter.to_networkx(graph)
            >>> nx_graph.number_of_nodes()
            2
        """
        NetworkXAdapter._check_networkx_available()

        # Handle Hypergraph via bipartite representation
        from packages.graphs.hypergraph import Hypergraph
        if isinstance(graph, Hypergraph):
            bipartite = graph.to_bipartite_graph()
            return NetworkXAdapter.to_networkx(bipartite)

        # Detect Multigraph/Pseudograph
        from packages.graphs.multigraph import Multigraph
        is_multi = isinstance(graph, Multigraph)

        # Create appropriate NetworkX graph type
        if graph._directed:
            nx_graph = nx.MultiDiGraph() if is_multi else nx.DiGraph()
        else:
            nx_graph = nx.MultiGraph() if is_multi else nx.Graph()

        # Add vertices with attributes
        for vertex in graph.vertices():
            nx_graph.add_node(vertex.id, **vertex.attributes)

        # Add edges with attributes
        for edge in graph.edges():
            nx_graph.add_edge(
                edge.source,
                edge.target,
                weight=edge.weight,
                **edge.attributes,
            )

        return nx_graph

    @staticmethod
    def from_networkx(
        nx_graph: Any,
        graph_type: str = "simple",
    ) -> BaseGraph:
        """
        Convert NetworkX graph to our graph.

        Args:
            nx_graph: NetworkX graph to convert
            graph_type: Type of graph to create ("simple", "multi", "pseudo")

        Returns:
            Our graph instance

        Raises:
            ImportError: If NetworkX is not installed
            ValueError: If graph_type is not supported

        Examples:
            >>> import networkx as nx
            >>> nx_g = nx.karate_club_graph()
            >>> graph = NetworkXAdapter.from_networkx(nx_g)
            >>> graph.vertex_count()
            34
        """
        NetworkXAdapter._check_networkx_available()

        from packages.graphs.multigraph import Multigraph
        from packages.graphs.pseudograph import Pseudograph
        from packages.graphs.simple_graph import SimpleGraph

        # Select graph class
        graph_classes = {
            "simple": SimpleGraph,
            "multi": Multigraph,
            "pseudo": Pseudograph,
        }

        if graph_type not in graph_classes:
            supported = ", ".join(graph_classes.keys())
            msg = f"Unsupported graph type: {graph_type!r}. Supported: {supported}"
            raise ValueError(msg)

        graph_class = graph_classes[graph_type]

        # Check if directed
        directed = nx_graph.is_directed()

        # Create graph
        graph = graph_class(directed=directed)

        # Add vertices with attributes
        for node in nx_graph.nodes():
            attrs = nx_graph.nodes[node].copy()
            graph.add_vertex(node, **attrs)

        # Add edges with attributes
        for source, target in nx_graph.edges():
            edge_data = nx_graph.edges[source, target].copy()
            weight = edge_data.pop("weight", 1.0)
            graph.add_edge(source, target, weight=weight, **edge_data)

        return graph

    @staticmethod
    def apply_networkx_algorithm(
        graph: BaseGraph,
        algorithm_func: Any,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Apply NetworkX algorithm to our graph.

        Temporarily converts to NetworkX, applies algorithm, returns result.

        Args:
            graph: Our graph instance
            algorithm_func: NetworkX algorithm function
            *args: Positional arguments for algorithm
            **kwargs: Keyword arguments for algorithm

        Returns:
            Algorithm result

        Examples:
            >>> import networkx as nx
            >>> graph = SimpleGraph()
            >>> # ... add vertices and edges ...
            >>> 
            >>> # Apply PageRank
            >>> pagerank = NetworkXAdapter.apply_networkx_algorithm(
            ...     graph,
            ...     nx.pagerank
            ... )
            >>> 
            >>> # Apply community detection
            >>> communities = NetworkXAdapter.apply_networkx_algorithm(
            ...     graph,
            ...     nx.community.greedy_modularity_communities
            ... )
        """
        NetworkXAdapter._check_networkx_available()

        nx_graph = NetworkXAdapter.to_networkx(graph)
        return algorithm_func(nx_graph, *args, **kwargs)


class NetworkXAlgorithms:
    """
    Wrapper for common NetworkX algorithms.

    Provides convenient access to NetworkX algorithms for our graphs.

    Examples:
        >>> graph = SimpleGraph()
        >>> # ... build graph ...
        >>> 
        >>> # Centrality measures
        >>> betweenness = NetworkXAlgorithms.betweenness_centrality(graph)
        >>> pagerank = NetworkXAlgorithms.pagerank(graph)
        >>> 
        >>> # Community detection
        >>> communities = NetworkXAlgorithms.detect_communities(graph)
        >>> 
        >>> # Shortest paths
        >>> paths = NetworkXAlgorithms.all_pairs_shortest_path(graph)
    """

    @staticmethod
    def _check_networkx_available() -> None:
        """Check if NetworkX is available."""
        if not NETWORKX_AVAILABLE:
            msg = (
                "NetworkX is not installed. "
                "Install it with: pip install networkx"
            )
            raise ImportError(msg)

    @staticmethod
    def betweenness_centrality(graph: BaseGraph, **kwargs: Any) -> dict[Any, float]:
        """
        Calculate betweenness centrality using NetworkX.

        Args:
            graph: Graph to analyze
            **kwargs: Additional arguments for nx.betweenness_centrality

        Returns:
            Dictionary mapping vertex_id -> centrality score

        Examples:
            >>> centrality = NetworkXAlgorithms.betweenness_centrality(graph)
            >>> most_central = max(centrality, key=centrality.get)
        """
        NetworkXAlgorithms._check_networkx_available()
        return NetworkXAdapter.apply_networkx_algorithm(
            graph,
            nx.betweenness_centrality,
            **kwargs,
        )

    @staticmethod
    def closeness_centrality(graph: BaseGraph, **kwargs: Any) -> dict[Any, float]:
        """
        Calculate closeness centrality using NetworkX.

        Args:
            graph: Graph to analyze
            **kwargs: Additional arguments for nx.closeness_centrality

        Returns:
            Dictionary mapping vertex_id -> centrality score

        Examples:
            >>> centrality = NetworkXAlgorithms.closeness_centrality(graph)
        """
        NetworkXAlgorithms._check_networkx_available()
        return NetworkXAdapter.apply_networkx_algorithm(
            graph,
            nx.closeness_centrality,
            **kwargs,
        )

    @staticmethod
    def pagerank(graph: BaseGraph, **kwargs: Any) -> dict[Any, float]:
        """
        Calculate PageRank using NetworkX.

        Args:
            graph: Graph to analyze
            **kwargs: Additional arguments for nx.pagerank

        Returns:
            Dictionary mapping vertex_id -> PageRank score

        Examples:
            >>> ranks = NetworkXAlgorithms.pagerank(graph, alpha=0.85)
            >>> top_ranked = sorted(ranks.items(), key=lambda x: x[1], reverse=True)[:5]
        """
        NetworkXAlgorithms._check_networkx_available()
        return NetworkXAdapter.apply_networkx_algorithm(
            graph,
            nx.pagerank,
            **kwargs,
        )

    @staticmethod
    def detect_communities(graph: BaseGraph, method: str = "greedy") -> list[set[Any]]:
        """
        Detect communities using NetworkX algorithms.

        Args:
            graph: Graph to analyze
            method: Community detection method ("greedy", "louvain")

        Returns:
            List of communities (sets of vertex IDs)

        Examples:
            >>> communities = NetworkXAlgorithms.detect_communities(graph)
            >>> print(f"Found {len(communities)} communities")
        """
        NetworkXAlgorithms._check_networkx_available()

        if method == "greedy":
            result = NetworkXAdapter.apply_networkx_algorithm(
                graph,
                nx.community.greedy_modularity_communities,
            )
            return [set(community) for community in result]
        elif method == "louvain":
            try:
                # Louvain requires python-louvain package
                result = NetworkXAdapter.apply_networkx_algorithm(
                    graph,
                    nx.community.louvain_communities,
                )
                return [set(community) for community in result]
            except AttributeError:
                msg = "Louvain method requires NetworkX >= 2.7"
                raise ValueError(msg) from None
        else:
            msg = f"Unsupported method: {method!r}. Use 'greedy' or 'louvain'"
            raise ValueError(msg)

    @staticmethod
    def all_pairs_shortest_path(
        graph: BaseGraph,
        weight: str = "weight",
    ) -> dict[Any, dict[Any, list[Any]]]:
        """
        Calculate all pairs shortest paths using NetworkX.

        Args:
            graph: Graph to analyze
            weight: Edge attribute to use as weight

        Returns:
            Nested dictionary with paths

        Examples:
            >>> paths = NetworkXAlgorithms.all_pairs_shortest_path(graph)
            >>> path_a_to_c = paths["A"]["C"]
        """
        NetworkXAlgorithms._check_networkx_available()
        return dict(
            NetworkXAdapter.apply_networkx_algorithm(
                graph,
                nx.all_pairs_dijkstra_path,
                weight=weight,
            )
        )

    @staticmethod
    def minimum_spanning_tree(graph: BaseGraph, **kwargs: Any) -> BaseGraph:
        """
        Calculate minimum spanning tree using NetworkX.

        Args:
            graph: Graph to analyze
            **kwargs: Additional arguments for nx.minimum_spanning_tree

        Returns:
            New graph containing only MST edges

        Examples:
            >>> mst = NetworkXAlgorithms.minimum_spanning_tree(graph)
            >>> print(f"MST has {mst.edge_count()} edges")
        """
        NetworkXAlgorithms._check_networkx_available()

        nx_graph = NetworkXAdapter.to_networkx(graph)
        mst_nx = nx.minimum_spanning_tree(nx_graph, **kwargs)

        # Convert back to our graph type
        return NetworkXAdapter.from_networkx(
            mst_nx,
            graph_type="simple",
        )

    @staticmethod
    def is_connected(graph: BaseGraph) -> bool:
        """
        Check if graph is connected using NetworkX.

        Args:
            graph: Graph to check

        Returns:
            True if graph is connected

        Examples:
            >>> if NetworkXAlgorithms.is_connected(graph):
            ...     print("Graph is connected")
        """
        NetworkXAlgorithms._check_networkx_available()
        return NetworkXAdapter.apply_networkx_algorithm(
            graph,
            nx.is_connected if not graph._directed else nx.is_strongly_connected,
        )

    @staticmethod
    def clustering_coefficient(graph: BaseGraph, **kwargs: Any) -> dict[Any, float]:
        """
        Calculate clustering coefficient using NetworkX.

        Args:
            graph: Graph to analyze
            **kwargs: Additional arguments for nx.clustering

        Returns:
            Dictionary mapping vertex_id -> clustering coefficient

        Examples:
            >>> clustering = NetworkXAlgorithms.clustering_coefficient(graph)
            >>> avg_clustering = sum(clustering.values()) / len(clustering)
        """
        NetworkXAlgorithms._check_networkx_available()
        return NetworkXAdapter.apply_networkx_algorithm(
            graph,
            nx.clustering,
            **kwargs,
        )


def requires_networkx(func):
    """
    Decorator to check NetworkX availability.

    Examples:
        >>> @requires_networkx
        ... def my_function(graph):
        ...     return NetworkXAdapter.to_networkx(graph)
    """

    def wrapper(*args, **kwargs):
        if not NETWORKX_AVAILABLE:
            msg = (
                f"{func.__name__} requires NetworkX. "
                "Install it with: pip install networkx"
            )
            raise ImportError(msg)
        return func(*args, **kwargs)

    return wrapper
