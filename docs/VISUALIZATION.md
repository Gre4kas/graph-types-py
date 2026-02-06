# Graph Visualization Guide

This guide covers visualization capabilities using graph-tool integration.

## Installation

graph-tool requires conda for installation:

```bash
conda install -c conda-forge graph-tool
```

Quick Start
Basic Visualization

```python
from packages.graphs.simple_graph import SimpleGraph
from packages.integrations.graph_tool_adapter import GraphToolAdapter

# Create graph
graph = SimpleGraph()
graph.add_vertex("A")
graph.add_vertex("B")
graph.add_vertex("C")
graph.add_edge("A", "B", weight=5.0)
graph.add_edge("B", "C", weight=3.0)
```
# Visualize
GraphToolAdapter.visualize(graph, output="graph.pdf")

Using GraphToolVisualizer

```python
from packages.integrations.graph_tool_adapter import GraphToolVisualizer

# Create visualizer
viz = GraphToolVisualizer(graph)

# Generate different visualizations
viz.basic_plot("basic.pdf")
viz.degree_colored_plot("degree.pdf")
viz.weighted_plot("weighted.pdf")
viz.community_plot("communities.pdf")
```

Layout Algorithms
Available Layouts
- sfdp: Scalable force-directed layout (default, good for most graphs)
- fr: Fruchterman-Reingold layout (classic force-directed)
- arf: ARF layout (force-directed with angle restrictions)
- radial: Radial tree layout (good for hierarchical graphs)
- random: Random layout

Usage

```python
# Try different layouts
for layout in ["sfdp", "fr", "arf", "radial"]:
    GraphToolAdapter.visualize(
        graph,
        output=f"graph_{layout}.pdf",
        layout=layout,
    )
```
Styling Options
Vertex Styling

```python
GraphToolAdapter.visualize(
    graph,
    output="styled.pdf",
    vertex_size=30,
    vertex_fill_color="lightblue", 
    vertex_text=True,
    vertex_font_size=12,
)
```
Using Vertex Attributes

```python
# Add color attribute to vertices
graph.add_vertex("A", color="red")
graph.add_vertex("B", color="blue")

# Use attribute for coloring
GraphToolAdapter.visualize(
    graph,
    output="colored.pdf",
    vertex_fill_color="color",
)
```
Edge Styling

```python
GraphToolAdapter.visualize(
    graph,
    output="styled_edges.pdf",
    edge_pen_width=3.0,
    edge_color="gray",
)
```

Weight-Based Edge Width

```python
# Automatically scale edge width by weight
GraphToolAdapter.visualize(
    graph,
    output="weighted.pdf",
    edge_pen_width=None,
)
```
Output Formats

Supported formats:
- PDF: output="graph.pdf"
- SVG: output="graph.svg"
- PNG: output="graph.png"

Advanced Examples
Community Detection Visualization

```python
viz = GraphToolVisualizer(graph)
viz.community_plot("communities.pdf")
```

Large Graphs

For large graphs (100+ vertices):

```python
GraphToolAdapter.visualize(
    large_graph,
    output="large.pdf",
    layout="sfdp",
    vertex_size=5,
    vertex_text=False,  # Hide labels
    edge_pen_width=0.5,
)
```

Interactive Visualization

```python
# Don't specify output for interactive window
# (or inline display in Jupyter)
GraphToolAdapter.visualize(graph)
```

Tips

- Layout Choice: Use sfdp for most graphs, radial for trees
- Large Graphs: Disable vertex labels and use smaller sizes
- Edge Weights: Set edge_pen_width=None to visualize by weight
- Communities: Use GraphToolVisualizer.community_plot() for community structure
- Consistency: Reuse layout positions for multiple visualizations of same graph

Examples

See examples/graph_tool_visualization_demo.py for complete examples.

## Запуск

```bash
conda install -c conda-forge graph-tool

uv run pytest tests/unit/test_graph_tool_adapter.py -v

python examples/graph_tool_visualization_demo.py