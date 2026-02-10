from packages.graphs.multigraph import Multigraph

multi = Multigraph()
multi.add_vertex("A")
multi.add_vertex("B")
multi.add_vertex("C")
multi.add_vertex("D")

# Додавання кількох ребер між одними й тими самими вершинами
multi.add_edge("A", "B", weight=15.0, label="Денний рейс")
multi.add_edge("A", "B", weight=5.0, label="Нічний рейс")
multi.add_edge("A", "C", weight=7.0, label="Ранковий рейс")
multi.add_edge("B", "D", weight=12.0, label="Вечірній рейс")

print(f"Кількість ребер між A та B: {multi.edge_multiplicity('A', 'B')}")
print(f"Кількість ребер між A та C: {multi.edge_multiplicity('A', 'C', 'B', 'D')}")
print(f"Кількість ребер між B та C: {multi.edge_multiplicity('B', 'C', 'A', 'D')}")
print(f"Кількість ребер між B та D: {multi.edge_multiplicity('B', 'D')}")
print(f"Кількість ребер між C та D: {multi.edge_multiplicity('C', 'D', 'B', 'A')}")