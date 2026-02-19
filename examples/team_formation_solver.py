
from typing import Any, List, Set, Tuple, Optional
from packages.graphs.hypergraph import Hypergraph

def solve_team_formation(
    hypergraph: Hypergraph, 
    candidate_costs: dict[Any, float]
) -> Tuple[float, Set[Any]]:
    """
    Вирішує задачу формування команди з мінімальною вартістю (Minimum Weight Hypergraph Transversal).
    
    Знаходить підмножину вершин (кандидатів) з мінімальною сумарною вартістю таку, що
    кожна гіперребро (навичка) покривається принаймні однією вибраною вершиною.
    
    Аргументи:
        hypergraph: Гіперграф, що представляє кандидатів та навички.
                    Вершини = Кандидати.
                    Гіперребра = Навички (множини кандидатів, які володіють цією навичкою).
        candidate_costs: Словник, що зіставляє ID вершини з її вартістю (зарплатою).
        
    Повертає:
        Кортеж, що містить (min_cost, set_of_best_candidates).
        Повертає (нескінченність, порожню множину), якщо рішення не існує.
    """
    
    # Вилучення даних задачі
    candidates = list(hypergraph.vertices())
    # Нам потрібно зіставити кандидатів з їхнім покриттям для ефективності
    # Структура гіперграфа: Гіперребро = множина вершин.
    # Задача: "Гіперребро e_i — це підмножина V, що має навичку i".
    # Умова: Для валідного рішення S, для всіх e в E, перетин S та e не є порожнім.
    # Тобто гіперребро "Java" містить {Alex, Carl, Eve}.
    # Нам потрібно вибрати множину S таку, що S перетинається з кожним гіперребром.
    # Це саме задача про Трансверсаль гіперграфа (Hitting Set).
    
    all_hyperedges = list(hypergraph.edges())
    if not all_hyperedges:
        return 0.0, set()
        
    # Оптимізація: Попередньо обчислити, які ребра покриває кожен кандидат
    # candidate_id -> множина індексів покритих ребер
    candidate_coverage: dict[Any, Set[int]] = {v.id: set() for v in candidates}
    
    for edge_idx, edge in enumerate(all_hyperedges):
        for v_id in edge.vertices:
            if v_id in candidate_coverage:
                candidate_coverage[v_id].add(edge_idx)
                
    sorted_candidates = sorted(candidates, key=lambda v: candidate_costs.get(v.id, float('inf')))
    n_candidates = len(sorted_candidates)
    n_edges = len(all_hyperedges)
    
    best_cost = float('inf')
    best_team: Set[Any] = set()
    
    def backtrack(idx: int, current_team: Set[Any], current_cost: float, covered_edge_indices: Set[int]):
        nonlocal best_cost, best_team
        
        # Відсікання (Pruning)
        if current_cost >= best_cost:
            return
            
        # Базовий випадок: Всі ребра покриті?
        # Примітка: Ми можемо перевіряти це ефективніше, але для даного масштабу перетин множин підійде
        if len(covered_edge_indices) == n_edges:
            best_cost = current_cost
            best_team = set(current_team)
            return

        # Базовий випадок: Більше немає кандидатів
        if idx == n_candidates:
            return
            
        candidate = sorted_candidates[idx]
        c_id = candidate.id
        cost = candidate_costs.get(c_id, float('inf'))
        
        # Варіант 1: Включити кандидата
        # Обчислити нове покриття
        new_covered = covered_edge_indices | candidate_coverage[c_id]
        
        # Рекурсія
        backtrack(idx + 1, current_team | {c_id}, current_cost + cost, new_covered)
        
        # Варіант 2: Виключити кандидата
        backtrack(idx + 1, current_team, current_cost, covered_edge_indices)

    backtrack(0, set(), 0.0, set())
    
    return best_cost, best_team

def main():
    # --- Налаштування іграшкового прикладу ---
    print("=== Задача формування команди (Minimum Weight Hypergraph Transversal) ===")
    
    hg = Hypergraph()
    
    # 1. Додавання кандидатів (Вершини)
    candidates_data = [
        (1, "Alex", 100),
        (2, "Bob", 150),
        (3, "Carl", 250),
        (4, "Dora", 100),
        (5, "Eve", 200),
    ]
    
    costs = {}
    
    print("\nКандидати:")
    label_name = "Ім'я"
    print(f"{'ID':<5} {label_name:<10} {'Вартість':<10}")
    print("-" * 30)
    for cid, name, cost in candidates_data:
        hg.add_vertex(cid, name=name)
        costs[cid] = cost
        print(f"{cid:<5} {name:<10} {cost:<10}")
        
    # 2. Додавання навичок (Гіперребра)
    # Гіперребро = Множина кандидатів, які володіють навичкою
    # Навички: Java, DB, Cloud, ML
    
    # Java: {1, 3, 5} -> {Alex, Carl, Eve}
    hg.add_hyperedge({1, 3, 5}, name="Java")
    
    # DB: {1, 2} -> {Alex, Bob}
    hg.add_hyperedge({1, 2}, name="DB")
    
    # Cloud: {2, 3} -> {Bob, Carl}
    hg.add_hyperedge({2, 3}, name="Cloud")
    
    # ML: {3, 4, 5} -> {Carl, Dora, Eve}
    hg.add_hyperedge({3, 4, 5}, name="ML")
    
    print("\nНавички (Гіперребра):")
    vertex_map = {v.id: v for v in hg.vertices()}
    for edge in hg.edges():
        names = [vertex_map[v].attributes.get('name', str(v)) for v in edge.vertices]
        print(f" - {edge.attributes.get('name')}: {names}")
        
    print("\nРозв'язання...")
    
    # --- Розв'язання ---
    min_cost, best_team_ids = solve_team_formation(hg, costs)
    
    # --- Виведення результатів ---
    print("\n=== Оптимальне рішення ===")
    if min_cost == float('inf'):
        print("Не знайдено рішення, яке б покривало всі навички.")
    else:
        # Повторне отримання мапи вершин для безпеки
        vertex_map = {v.id: v for v in hg.vertices()}
        print(f"Мінімальна загальна вартість: {min_cost}")
        print("Обрана команда:")
        for cid in sorted(best_team_ids):
            name = vertex_map[cid].attributes.get('name', 'Unknown')
            print(f" - ID {cid}: {name} (Вартість: {costs[cid]})")
            
        # Перевірка покриття
        print("\nПеревірка покриття навичок:")
        covered_skills = set()
        for edge in hg.edges():
            skill_name = edge.attributes.get('name')
            # Перевірка перетину
            overlap = edge.vertices.intersection(best_team_ids)
            if overlap:
                who = [vertex_map[v].attributes.get('name') for v in overlap]
                print(f" [x] {skill_name:<10} покрито: {who}")
                covered_skills.add(skill_name)
            else:
                print(f" [ ] {skill_name:<10} НЕ ПОКРИТО")
                
        if len(covered_skills) == hg.hyperedge_count():
            print("\nУСПІХ: Всі навички покрито!")
        else:
            print("\nПОМИЛКА: Деякі навички відсутні!")
    
    print("\nСирий результат:")
    print(f"Вартість: {min_cost}")
    print(f"Команда: {best_team_ids}")

    print("\nКінець роботи.")

if __name__ == "__main__":
    main()
