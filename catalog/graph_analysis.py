import json
from collections import deque, defaultdict

from catalog.models import SimilarCategory, Category


def build_similarity_graph():
    graph = defaultdict(set)
    for rel in SimilarCategory.objects.all().select_related("category_a", "category_b"):
        graph[rel.category_a_id].add(rel.category_b_id)
        graph[rel.category_b_id].add(rel.category_a_id)
    return graph


def find_rabbit_islands_and_longest_path(graph):
    visited = set()
    islands = []
    longest_path = []

    def bfs(start):
        queue = deque([[start]])
        seen = {start}
        component = {start}
        max_path = []

        while queue:
            path = queue.popleft()
            node = path[-1]

            for neighbor in graph[node]:
                if neighbor not in seen:
                    seen.add(neighbor)
                    queue.append(path + [neighbor])
                    component.add(neighbor)
                    if len(path) + 1 > len(max_path):
                        max_path = path + [neighbor]

        return component, max_path

    for node in graph:
        if node not in visited:
            component, path = bfs(node)
            islands.append(component)
            visited.update(component)
            if len(path) > len(longest_path):
                longest_path = path

    return islands, longest_path


def export_graph_analysis_to_json(path="graph_report.json"):
    graph = build_similarity_graph()
    islands, longest_path_ids = find_rabbit_islands_and_longest_path(graph)
    id_to_name = dict(Category.objects.values_list("id", "name"))

    data = {
        "longest_rabbit_hole": {
            "length": len(longest_path_ids) - 1,
            "path": [
                {"id": cid, "name": id_to_name.get(cid, f"[Unknown:{cid}]")}
                for cid in longest_path_ids
            ],
        },
        "rabbit_islands": [
            [
                {"id": cid, "name": id_to_name.get(cid, f"[Unknown:{cid}]")}
                for cid in sorted(island)
            ]
            for island in islands
        ],
    }

    with open(path, "w") as f:
        json.dump(data, f, indent=2)

    return path, data
