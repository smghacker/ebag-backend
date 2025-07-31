import json
from collections import deque, defaultdict

from catalog.models import SimilarCategory, Category


def build_similarity_graph():
    graph = defaultdict(set)
    for rel in SimilarCategory.objects.select_related("category_a", "category_b"):
        graph[rel.category_a_id].add(rel.category_b_id)
        graph[rel.category_b_id].add(rel.category_a_id)
    return graph


def find_rabbit_islands(graph, all_categories):
    visited = set()
    islands = []

    def bfs(start):
        queue = deque([start])
        component = {start}
        visited.add(start)

        while queue:
            node = queue.popleft()
            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    component.add(neighbor)
                    queue.append(neighbor)
        return component

    for node in all_categories:
        if node not in visited:
            islands.append(bfs(node))

    return islands



def find_diameter_of_island(graph, island):
    def bfs_longest_path(start):
        queue = deque([[start]])
        seen = {start}
        longest_path = []

        while queue:
            path = queue.popleft()
            node = path[-1]
            for neighbor in graph[node]:
                if neighbor not in seen:
                    seen.add(neighbor)
                    new_path = path + [neighbor]
                    queue.append(new_path)
                    if len(new_path) > len(longest_path):
                        longest_path = new_path
        return longest_path

    any_node = next(iter(island))
    first_extreme = bfs_longest_path(any_node)
    if not first_extreme:
        return []

    second_extreme = bfs_longest_path(first_extreme[-1])
    return second_extreme


def format_category_path(category_ids):
    id_to_name = dict(Category.objects.values_list("id", "name"))
    return [{"id": cid, "name": id_to_name.get(cid, f"[Unknown:{cid}]")} for cid in category_ids]


def export_graph_analysis_to_json(path="graph_report.json"):
    graph = build_similarity_graph()
    all_categories = list(Category.objects.values_list('id', flat=True))
    islands = find_rabbit_islands(graph, all_categories)

    longest_path = []
    for island in islands:
        curr_path = find_diameter_of_island(graph, island)
        if len(curr_path) > len(longest_path):
            longest_path = curr_path

    report = {
        "longest_rabbit_hole": {
            "length": max(len(longest_path) - 1, 0),
            "path": format_category_path(longest_path),
        },
        "rabbit_islands": [
            format_category_path(sorted(island)) for island in islands
        ],
    }

    with open(path, "w") as f:
        json.dump(report, f, indent=2)

    return path, report
