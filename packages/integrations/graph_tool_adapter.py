"""
graph-tool integration adapter with visualization support.

Provides conversion and advanced visualization capabilities using graph-tool.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from packages.core.base_graph import BaseGraph

try:
    import graph_tool.all as gt

    GRAPH_TOOL_AVAILABLE = True
except ImportError:
    GRAPH_TOOL_AVAILABLE = False
    gt = None  # type: ignore


class GraphToolAdapter:
    """
    Adapter for converting between graph-library and graph-tool.

    graph-tool is a high-performance C++ library with Python bindings,
    offering advanced visualization and analysis capabilities.

    Examples:
        >>> from packages.graphs.simple_graph import SimpleGraph
        >>> 
        >>> # Convert our graph to graph-tool
        >>> graph = SimpleGraph()
        >>> graph.add_vertex("A", color="red", size=10)
        >>> graph.add_edge("A", "B", weight=5.0)
        >>> gt_graph = GraphToolAdapter.to_graph_tool(graph)
        >>> 
        >>> # Visualize with graph-tool
        >>> GraphToolAdapter.visualize(graph, output="graph.pdf")
    """

    @staticmethod
    def _check_graph_tool_available() -> None:
        """Check if graph-tool is available."""
        if not GRAPH_TOOL_AVAILABLE:
            msg = (
                "graph-tool is not installed. "
                "Install it with: conda install -c conda-forge graph-tool"
            )
            raise ImportError(msg)

    @staticmethod
    def to_graph_tool(graph: BaseGraph) -> Any:
        """
        Convert our graph to graph-tool Graph.

        Args:
            graph: Graph to convert

        Returns:
            graph-tool Graph instance

        Raises:
            ImportError: If graph-tool is not installed

        Examples:
            >>> graph = SimpleGraph()
            >>> graph.add_vertex("A")
            >>> graph.add_vertex("B")
            >>> graph.add_edge("A", "B", weight=5.0)
            >>> gt_graph = GraphToolAdapter.to_graph_tool(graph)
            >>> gt_graph.num_vertices()
            2
        """
        GraphToolAdapter._check_graph_tool_available()

        # Create graph-tool Graph with matching directedness
        gt_graph = gt.Graph(directed=graph._directed)

        # Create vertex ID mapping (our ID -> graph-tool vertex)
        vertex_map = {}
        
        # Create internal property map for storing our original vertex IDs
        # This is crucial - graph-tool uses integer indices internally
        vertex_id_prop = gt_graph.new_vertex_property("string")
        
        # Add all vertices first
        for vertex in graph.vertices():
            # add_vertex() returns a vertex descriptor
            gt_vertex = gt_graph.add_vertex()
            vertex_map[vertex.id] = gt_vertex
            # Store original ID
            vertex_id_prop[gt_vertex] = str(vertex.id)

        # Make the ID property internal so it's saved with the graph
        gt_graph.vp["original_id"] = vertex_id_prop

        # Copy vertex attributes as property maps
        # First, collect all unique attribute keys
        vertex_attrs: dict[str, set[type]] = {}
        for vertex in graph.vertices():
            for key, value in vertex.attributes.items():
                if key not in vertex_attrs:
                    vertex_attrs[key] = set()
                vertex_attrs[key].add(type(value))

        # Create property maps for each attribute
        for attr_name, types in vertex_attrs.items():
            # Determine property type based on Python type
            if len(types) == 1:
                py_type = list(types)[0]
                prop_type = GraphToolAdapter._python_type_to_graph_tool(py_type)
            else:
                # Mixed types - use object
                prop_type = "object"

            # Create the property map
            vprop = gt_graph.new_vertex_property(prop_type)
            
            # Fill values
            for vertex in graph.vertices():
                gt_vertex = vertex_map[vertex.id]
                value = vertex.attributes.get(attr_name)
                if value is not None:
                    vprop[gt_vertex] = value

            # Make it internal
            gt_graph.vp[attr_name] = vprop

        # Add all edges
        edge_weight_prop = gt_graph.new_edge_property("double")
        
        for edge in graph.edges():
            gt_source = vertex_map[edge.source]
            gt_target = vertex_map[edge.target]
            
            # add_edge() returns edge descriptor
            gt_edge = gt_graph.add_edge(gt_source, gt_target)
            
            # Store weight
            edge_weight_prop[gt_edge] = edge.weight

        # Make weight internal
        gt_graph.ep["weight"] = edge_weight_prop

        # Copy edge attributes
        edge_attrs: dict[str, set[type]] = {}
        for edge in graph.edges():
            for key, value in edge.attributes.items():
                if key not in edge_attrs:
                    edge_attrs[key] = set()
                edge_attrs[key].add(type(value))

        for attr_name, types in edge_attrs.items():
            if len(types) == 1:
                py_type = list(types)[0]
                prop_type = GraphToolAdapter._python_type_to_graph_tool(py_type)
            else:
                prop_type = "object"

            eprop = gt_graph.new_edge_property(prop_type)
            
            for edge in graph.edges():
                gt_source = vertex_map[edge.source]
                gt_target = vertex_map[edge.target]
                # Get edge descriptor using edge() method
                gt_edge = gt_graph.edge(gt_source, gt_target)
                if gt_edge is not None:
                    value = edge.attributes.get(attr_name)
                    if value is not None:
                        eprop[gt_edge] = value

            gt_graph.ep[attr_name] = eprop

        return gt_graph

    @staticmethod
    def _python_type_to_graph_tool(py_type: type) -> str:
        """
        Map Python type to graph-tool property type.

        Args:
            py_type: Python type

        Returns:
            graph-tool property type string
        """
        type_map = {
            bool: "bool",
            int: "int",
            float: "double",
            str: "string",
            list: "vector<double>",  # Default to double vector
            tuple: "vector<double>",
        }
        return type_map.get(py_type, "object")

    @staticmethod
    def from_graph_tool(gt_graph: Any, graph_type: str = "simple") -> BaseGraph:
        """
        Convert graph-tool Graph to our graph.

        Args:
            gt_graph: graph-tool Graph instance
            graph_type: Type of graph to create ("simple", "multi", "pseudo")

        Returns:
            Our graph instance

        Raises:
            ImportError: If graph-tool is not installed
            ValueError: If graph_type is not supported

        Examples:
            >>> # Assuming gt_graph is a graph-tool Graph
            >>> graph = GraphToolAdapter.from_graph_tool(gt_graph)
            >>> graph.vertex_count()
            10
        """
        GraphToolAdapter._check_graph_tool_available()

        from packages.graphs.multigraph import Multigraph
        from packages.graphs.pseudograph import Pseudograph
        from packages.graphs.simple_graph import SimpleGraph

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

        # Create our graph with matching directedness
        directed = gt_graph.is_directed()
        graph = graph_class(directed=directed)

        # Check if we have original_id property
        has_original_id = "original_id" in gt_graph.vp

        # Map graph-tool vertices to our vertex IDs
        vertex_map = {}

        # Add vertices
        for v in gt_graph.vertices():
            # Use original ID if available, otherwise use integer index
            if has_original_id:
                vertex_id = gt_graph.vp.original_id[v]
                # Try to convert to int if possible
                try:
                    vertex_id = int(vertex_id)
                except ValueError:
                    pass  # Keep as string
            else:
                vertex_id = int(v)

            vertex_map[int(v)] = vertex_id

            # Collect vertex attributes
            attrs = {}
            for prop_name in gt_graph.vp.keys():
                if prop_name != "original_id":  # Skip our internal ID
                    attrs[prop_name] = gt_graph.vp[prop_name][v]

            graph.add_vertex(vertex_id, **attrs)

        # Add edges
        for e in gt_graph.edges():
            source = vertex_map[int(e.source())]
            target = vertex_map[int(e.target())]
            
            # Get weight if available
            weight = 1.0
            if "weight" in gt_graph.ep:
                weight = float(gt_graph.ep.weight[e])

            # Collect edge attributes
            attrs = {}
            for prop_name in gt_graph.ep.keys():
                if prop_name != "weight":  # Skip weight (handled separately)
                    attrs[prop_name] = gt_graph.ep[prop_name][e]

            graph.add_edge(source, target, weight=weight, **attrs)

        return graph

    @staticmethod
    def visualize(
        graph: BaseGraph,
        output: str | Path | None = None,
        layout: str = "sfdp",
        vertex_size: float | None = 15,
        vertex_fill_color: str | None = None,
        vertex_text: bool | str = True,
        vertex_font_size: int = 12,
        edge_pen_width: float | None = 2.0,
        edge_color: str | None = None,
        **kwargs: Any,
    ) -> Any:
        """
        Visualize graph using graph-tool's drawing capabilities.

        Args:
            graph: Graph to visualize
            output: Output file path (None = interactive window, or inline in Jupyter)
            layout: Layout algorithm ("sfdp", "fr", "arf", "radial", "random")
            vertex_size: Vertex size (None = use degree-based sizing)
            vertex_fill_color: Vertex color (None = use default, or attribute name)
            vertex_text: Show vertex labels (True/False or attribute name)
            vertex_font_size: Font size for vertex labels
            edge_pen_width: Edge width (None = use weight-based)
            edge_color: Edge color (None = use default)
            **kwargs: Additional arguments passed to graph_draw()

        Returns:
            Position property map (can be reused for consistent layouts)

        Examples:
            >>> # Basic visualization
            >>> GraphToolAdapter.visualize(graph, output="graph.pdf")
            >>> 
            >>> # Interactive (no output specified)
            >>> GraphToolAdapter.visualize(graph)
            >>> 
            >>> # Custom styling
            >>> GraphToolAdapter.visualize(
            ...     graph,
            ...     output="styled.pdf",
            ...     layout="fr",
            ...     vertex_size=25,
            ...     vertex_fill_color="lightblue",
            ...     edge_pen_width=3.0
            ... )
            >>> 
            >>> # Use vertex attribute for color
            >>> GraphToolAdapter.visualize(
            ...     graph,
            ...     output="colored.pdf",
            ...     vertex_fill_color="color"  # Use "color" attribute
            ... )
        """
        GraphToolAdapter._check_graph_tool_available()

        # Convert to graph-tool
        gt_graph = GraphToolAdapter.to_graph_tool(graph)

        # Calculate layout
        layout_funcs = {
            "sfdp": gt.sfdp_layout,
            "fr": gt.fruchterman_reingold_layout,
            "arf": gt.arf_layout,
            "random": gt.random_layout,
        }

        if layout == "radial":
            # Radial layout needs a root vertex
            root = gt_graph.vertex(0)  # Use first vertex as root
            pos = gt.radial_tree_layout(gt_graph, root)
        elif layout in layout_funcs:
            pos = layout_funcs[layout](gt_graph)
        else:
            supported = ", ".join(list(layout_funcs.keys()) + ["radial"])
            msg = f"Unsupported layout: {layout!r}. Supported: {supported}"
            raise ValueError(msg)

        # Prepare vertex properties
        
        # Vertex size
        if vertex_size is None:
            # Size based on degree
            deg = gt_graph.degree_property_map("total")
            # Normalize to reasonable range (5-30)
            vertex_size_prop = gt.prop_to_size(deg, mi=5, ma=30)
        else:
            vertex_size_prop = vertex_size

        # Vertex fill color
        if vertex_fill_color is not None and isinstance(vertex_fill_color, str):
            # Check if it's an attribute name
            if vertex_fill_color in gt_graph.vp:
                vertex_fill_color_prop = gt_graph.vp[vertex_fill_color]
            else:
                # It's a color string
                vertex_fill_color_prop = vertex_fill_color
        else:
            vertex_fill_color_prop = vertex_fill_color

        # Vertex text
        if vertex_text is True:
            # Use original IDs if available
            if "original_id" in gt_graph.vp:
                vertex_text_prop = gt_graph.vp.original_id
            else:
                vertex_text_prop = gt_graph.vertex_index
        elif vertex_text is False or vertex_text is None:
            vertex_text_prop = None
        elif isinstance(vertex_text, str):
            # It's an attribute name
            if vertex_text in gt_graph.vp:
                vertex_text_prop = gt_graph.vp[vertex_text]
            else:
                vertex_text_prop = None
        else:
            vertex_text_prop = vertex_text

        # Edge pen width
        if edge_pen_width is None:
            # Width based on weight
            if "weight" in gt_graph.ep:
                edge_pen_width_prop = gt.prop_to_size(
                    gt_graph.ep.weight,
                    mi=1,
                    ma=10,
                )
            else:
                edge_pen_width_prop = 2.0
        else:
            edge_pen_width_prop = edge_pen_width

        # Edge color
        if edge_color is not None and isinstance(edge_color, str):
            if edge_color in gt_graph.ep:
                edge_color_prop = gt_graph.ep[edge_color]
            else:
                edge_color_prop = edge_color
        else:
            edge_color_prop = edge_color

        # Draw the graph
        result = gt.graph_draw(
            gt_graph,
            pos=pos,
            vertex_size=vertex_size_prop,
            vertex_fill_color=vertex_fill_color_prop,
            vertex_text=vertex_text_prop,
            vertex_font_size=vertex_font_size,
            edge_pen_width=edge_pen_width_prop,
            edge_color=edge_color_prop,
            output=str(output) if output is not None else None,
            **kwargs,
        )

        return pos


class GraphToolVisualizer:
    """
    High-level visualization interface using graph-tool.

    Provides convenient methods for common visualization tasks.

    Examples:
        >>> viz = GraphToolVisualizer(graph)
        >>> viz.basic_plot("output.pdf")
        >>> viz.degree_colored_plot("degree.pdf")
        >>> viz.weighted_plot("weighted.pdf")
    """

    def __init__(self, graph: BaseGraph) -> None:
        """
        Initialize visualizer.

        Args:
            graph: Graph to visualize
        """
        GraphToolAdapter._check_graph_tool_available()
        self.graph = graph
        self.gt_graph = GraphToolAdapter.to_graph_tool(graph)
        self.pos: Any = None

    def basic_plot(
        self,
        output: str | Path | None = None,
        layout: str = "sfdp",
    ) -> None:
        """
        Create basic visualization with default styling.

        Args:
            output: Output file path
            layout: Layout algorithm

        Examples:
            >>> viz.basic_plot("basic.pdf")
        """
        self.pos = GraphToolAdapter.visualize(
            self.graph,
            output=output,
            layout=layout,
        )

    def degree_colored_plot(
        self,
        output: str | Path | None = None,
        layout: str = "sfdp",
    ) -> None:
        """
        Visualization with vertices colored by degree.

        Args:
            output: Output file path
            layout: Layout algorithm

        Examples:
            >>> viz.degree_colored_plot("degree.pdf")
        """
        # Calculate degree
        deg = self.gt_graph.degree_property_map("total")
        
        # Normalize to color range
        deg_array = deg.fa
        if deg_array.max() > deg_array.min():
            normalized = (deg_array - deg_array.min()) / (deg_array.max() - deg_array.min())
        else:
            normalized = deg_array * 0  # All zeros if constant

        # Create color property map using colormap
        color_prop = self.gt_graph.new_vertex_property("vector<double>")
        for v in self.gt_graph.vertices():
            # Use a simple red-to-blue gradient
            value = normalized[int(v)]
            # RGB: blue (low degree) to red (high degree)
            color_prop[v] = [value, 0, 1 - value, 0.8]  # RGBA

        # Draw
        gt.graph_draw(
            self.gt_graph,
            pos=self._get_layout(layout),
            vertex_fill_color=color_prop,
            vertex_text=self.gt_graph.vp.get("original_id", self.gt_graph.vertex_index),
            output=str(output) if output is not None else None,
        )

    def weighted_plot(
        self,
        output: str | Path | None = None,
        layout: str = "sfdp",
    ) -> None:
        """
        Visualization with edge width based on weights.

        Args:
            output: Output file path
            layout: Layout algorithm

        Examples:
            >>> viz.weighted_plot("weighted.pdf")
        """
        if "weight" not in self.gt_graph.ep:
            msg = "Graph has no edge weights"
            raise ValueError(msg)

        # Normalize edge weights to pen width
        edge_width = gt.prop_to_size(
            self.gt_graph.ep.weight,
            mi=1,
            ma=10,
        )

        gt.graph_draw(
            self.gt_graph,
            pos=self._get_layout(layout),
            vertex_text=self.gt_graph.vp.get("original_id", self.gt_graph.vertex_index),
            edge_pen_width=edge_width,
            output=str(output) if output is not None else None,
        )

    def community_plot(
        self,
        output: str | Path | None = None,
        layout: str = "sfdp",
    ) -> None:
        """
        Visualization with community detection coloring.

        Uses graph-tool's built-in community detection.

        Args:
            output: Output file path
            layout: Layout algorithm

        Examples:
            >>> viz.community_plot("communities.pdf")
        """
        # Detect communities using stochastic block model
        state = gt.minimize_blockmodel_dl(self.gt_graph)
        
        # Get block membership
        blocks = state.get_blocks()

        # Draw with community colors
        gt.graph_draw(
            self.gt_graph,
            pos=self._get_layout(layout),
            vertex_fill_color=blocks,
            vertex_text=self.gt_graph.vp.get("original_id", self.gt_graph.vertex_index),
            output=str(output) if output is not None else None,
        )

    def _get_layout(self, layout: str) -> Any:
        """Get or compute layout positions."""
        if self.pos is None:
            layout_funcs = {
                "sfdp": gt.sfdp_layout,
                "fr": gt.fruchterman_reingold_layout,
                "arf": gt.arf_layout,
                "random": gt.random_layout,
            }
            
            if layout in layout_funcs:
                self.pos = layout_funcs[layout](self.gt_graph)
            elif layout == "radial":
                root = self.gt_graph.vertex(0)
                self.pos = gt.radial_tree_layout(self.gt_graph, root)
            else:
                self.pos = gt.sfdp_layout(self.gt_graph)
        
        return self.pos


def requires_graph_tool(func):
    """
    Decorator to check graph-tool availability.

    Examples:
        >>> @requires_graph_tool
        ... def my_function(graph):
        ...     return GraphToolAdapter.to_graph_tool(graph)
    """

    def wrapper(*args, **kwargs):
        if not GRAPH_TOOL_AVAILABLE:
            msg = (
                f"{func.__name__} requires graph-tool. "
                "Install it with: conda install -c conda-forge graph-tool"
            )
            raise ImportError(msg)
        return func(*args, **kwargs)

    return wrapper
