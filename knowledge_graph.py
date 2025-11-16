"""
🕸️ Knowledge Graph для ConsciousAI
Граф знаний с визуализацией связей памяти через NetworkX
"""

import networkx as nx
import matplotlib.pyplot as plt
from typing import List, Dict, Any, Tuple, Optional
from collections import defaultdict
import json
import os

# ═══════════════════════════════════════════════════════════════
# ГРАФ ЗНАНИЙ
# ═══════════════════════════════════════════════════════════════

class KnowledgeGraph:
    """Граф знаний для хранения и визуализации связей"""

    def __init__(self):
        self.graph = nx.DiGraph()  # Направленный граф
        self.node_counter = 0

    def add_memory_node(
        self,
        content: str,
        node_type: str = "memory",
        resonance: float = 0.5,
        emotion: str = "neutral",
        metadata: Optional[Dict] = None
    ) -> str:
        """Добавить узел памяти"""

        node_id = f"node_{self.node_counter}"
        self.node_counter += 1

        self.graph.add_node(
            node_id,
            content=content,
            type=node_type,
            resonance=resonance,
            emotion=emotion,
            metadata=metadata or {}
        )

        return node_id

    def add_edge(
        self,
        source_id: str,
        target_id: str,
        relationship: str = "relates_to",
        weight: float = 1.0
    ):
        """Добавить связь между узлами"""

        if source_id not in self.graph or target_id not in self.graph:
            raise ValueError("Both nodes must exist in the graph")

        self.graph.add_edge(
            source_id,
            target_id,
            relationship=relationship,
            weight=weight
        )

    def find_similar_nodes(
        self,
        query: str,
        top_k: int = 5
    ) -> List[Tuple[str, float]]:
        """Найти похожие узлы"""

        query_words = set(query.lower().split())
        similarities = []

        for node_id in self.graph.nodes():
            node_data = self.graph.nodes[node_id]
            content = node_data.get('content', '')

            content_words = set(content.lower().split())
            overlap = len(query_words & content_words)

            if overlap > 0:
                # Учитываем резонанс
                resonance = node_data.get('resonance', 0.5)
                similarity = overlap * resonance
                similarities.append((node_id, similarity))

        # Сортировка по similarity
        similarities.sort(key=lambda x: x[1], reverse=True)

        return similarities[:top_k]

    def get_connected_nodes(
        self,
        node_id: str,
        max_depth: int = 2
    ) -> List[str]:
        """Получить связанные узлы"""

        if node_id not in self.graph:
            return []

        # BFS обход
        connected = set()
        queue = [(node_id, 0)]
        visited = {node_id}

        while queue:
            current, depth = queue.pop(0)

            if depth < max_depth:
                for neighbor in self.graph.neighbors(current):
                    if neighbor not in visited:
                        visited.add(neighbor)
                        connected.add(neighbor)
                        queue.append((neighbor, depth + 1))

        return list(connected)

    def get_subgraph(
        self,
        node_ids: List[str]
    ) -> nx.DiGraph:
        """Получить подграф"""
        return self.graph.subgraph(node_ids).copy()

    def get_central_nodes(
        self,
        top_k: int = 10
    ) -> List[Tuple[str, float]]:
        """Получить центральные узлы (по degree centrality)"""

        centrality = nx.degree_centrality(self.graph)
        sorted_nodes = sorted(centrality.items(), key=lambda x: x[1], reverse=True)

        return sorted_nodes[:top_k]

    def get_communities(self) -> List[List[str]]:
        """Обнаружить сообщества узлов"""

        # Преобразуем в неориентированный граф для обнаружения сообществ
        undirected = self.graph.to_undirected()

        # Используем Louvain algorithm (через greedy modularity)
        communities = list(nx.community.greedy_modularity_communities(undirected))

        return [list(community) for community in communities]

    def get_shortest_path(
        self,
        source_id: str,
        target_id: str
    ) -> Optional[List[str]]:
        """Найти кратчайший путь между узлами"""

        try:
            path = nx.shortest_path(self.graph, source_id, target_id)
            return path
        except nx.NetworkXNoPath:
            return None

    def get_stats(self) -> Dict[str, Any]:
        """Получить статистику графа"""

        return {
            "total_nodes": self.graph.number_of_nodes(),
            "total_edges": self.graph.number_of_edges(),
            "density": nx.density(self.graph),
            "avg_clustering": nx.average_clustering(self.graph.to_undirected()),
            "is_connected": nx.is_weakly_connected(self.graph),
            "num_components": nx.number_weakly_connected_components(self.graph)
        }

    def visualize(
        self,
        output_file: str = "knowledge_graph.png",
        node_ids: Optional[List[str]] = None,
        figsize: Tuple[int, int] = (16, 12)
    ):
        """Визуализировать граф"""

        if node_ids:
            graph_to_plot = self.get_subgraph(node_ids)
        else:
            graph_to_plot = self.graph

        plt.figure(figsize=figsize)

        # Layout
        pos = nx.spring_layout(graph_to_plot, k=1, iterations=50)

        # Цвета узлов по резонансу
        node_colors = []
        for node_id in graph_to_plot.nodes():
            resonance = graph_to_plot.nodes[node_id].get('resonance', 0.5)
            # Градиент от синего (low) к красному (high)
            r = int(resonance * 255)
            b = int((1 - resonance) * 255)
            node_colors.append(f'#{r:02x}00{b:02x}')

        # Размеры узлов по степени
        node_sizes = []
        for node_id in graph_to_plot.nodes():
            degree = graph_to_plot.degree(node_id)
            size = 300 + degree * 100
            node_sizes.append(size)

        # Рисовать узлы
        nx.draw_networkx_nodes(
            graph_to_plot,
            pos,
            node_color=node_colors,
            node_size=node_sizes,
            alpha=0.8
        )

        # Рисовать рёбра
        nx.draw_networkx_edges(
            graph_to_plot,
            pos,
            edge_color='gray',
            arrows=True,
            arrowsize=20,
            alpha=0.5,
            width=2
        )

        # Лейблы
        labels = {}
        for node_id in graph_to_plot.nodes():
            content = graph_to_plot.nodes[node_id].get('content', '')
            # Сократить до первых 20 символов
            labels[node_id] = content[:20] + "..." if len(content) > 20 else content

        nx.draw_networkx_labels(
            graph_to_plot,
            pos,
            labels,
            font_size=8,
            font_weight='bold'
        )

        plt.title("Knowledge Graph Visualization", fontsize=16, fontweight='bold')
        plt.axis('off')
        plt.tight_layout()

        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"✅ Graph saved to {output_file}")

        plt.close()

    def export_to_json(self, output_file: str = "knowledge_graph.json"):
        """Экспортировать граф в JSON"""

        data = {
            "nodes": [],
            "edges": []
        }

        # Узлы
        for node_id in self.graph.nodes():
            node_data = self.graph.nodes[node_id]
            data["nodes"].append({
                "id": node_id,
                **node_data
            })

        # Рёбра
        for source, target in self.graph.edges():
            edge_data = self.graph.edges[source, target]
            data["edges"].append({
                "source": source,
                "target": target,
                **edge_data
            })

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"✅ Graph exported to {output_file}")

    def import_from_json(self, input_file: str):
        """Импортировать граф из JSON"""

        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Очистить текущий граф
        self.graph.clear()

        # Загрузить узлы
        for node in data["nodes"]:
            node_id = node.pop("id")
            self.graph.add_node(node_id, **node)

        # Загрузить рёбра
        for edge in data["edges"]:
            source = edge.pop("source")
            target = edge.pop("target")
            self.graph.add_edge(source, target, **edge)

        print(f"✅ Graph imported from {input_file}")

# ═══════════════════════════════════════════════════════════════
# ИНТЕГРАЦИЯ С CONSCIOUSAI
# ═══════════════════════════════════════════════════════════════

class ConsciousAIKnowledgeGraph(KnowledgeGraph):
    """Расширенный граф знаний для ConsciousAI"""

    def build_from_memory(
        self,
        memory_bank: List[Dict[str, Any]],
        min_resonance: float = 0.3
    ):
        """Построить граф из банка памяти"""

        # Добавить узлы
        node_map = {}
        for idx, memory in enumerate(memory_bank):
            content = memory.get('content', '')
            resonance = memory.get('resonance', 0.5)

            # Фильтр по резонансу
            if resonance < min_resonance:
                continue

            node_id = self.add_memory_node(
                content=content,
                resonance=resonance,
                emotion=memory.get('emotion', 'neutral'),
                metadata=memory
            )

            node_map[idx] = node_id

        # Создать связи на основе similarity
        memory_indices = list(node_map.keys())

        for i, idx1 in enumerate(memory_indices):
            node_id1 = node_map[idx1]
            content1 = memory_bank[idx1].get('content', '')

            for idx2 in memory_indices[i+1:]:
                node_id2 = node_map[idx2]
                content2 = memory_bank[idx2].get('content', '')

                # Вычислить similarity
                words1 = set(content1.lower().split())
                words2 = set(content2.lower().split())
                overlap = len(words1 & words2)

                if overlap > 2:  # Минимум 2 общих слова
                    similarity = overlap / max(len(words1), len(words2), 1)

                    self.add_edge(
                        node_id1,
                        node_id2,
                        relationship="similar_to",
                        weight=similarity
                    )

    def find_insight_paths(
        self,
        query: str,
        max_depth: int = 3
    ) -> List[Dict[str, Any]]:
        """Найти пути инсайтов через граф"""

        # Найти похожие узлы
        similar = self.find_similar_nodes(query, top_k=3)

        if not similar:
            return []

        insights = []

        for node_id, similarity in similar:
            # Получить связанные узлы
            connected = self.get_connected_nodes(node_id, max_depth=max_depth)

            if connected:
                # Создать инсайт
                path = [node_id] + connected[:5]

                path_contents = []
                for nid in path:
                    content = self.graph.nodes[nid].get('content', '')
                    path_contents.append(content)

                insights.append({
                    "query": query,
                    "similarity": similarity,
                    "path": path,
                    "path_contents": path_contents,
                    "insight": self._generate_insight(path_contents)
                })

        return insights

    def _generate_insight(self, path_contents: List[str]) -> str:
        """Генерировать инсайт из пути"""

        # Простая реализация: объединить содержимое
        return f"Связь: {' → '.join(c[:30] + '...' if len(c) > 30 else c for c in path_contents[:3])}"

# ═══════════════════════════════════════════════════════════════
# ПРИМЕР ИСПОЛЬЗОВАНИЯ
# ═══════════════════════════════════════════════════════════════

def example():
    """Пример использования"""

    # Создать граф
    kg = ConsciousAIKnowledgeGraph()

    # Добавить узлы
    n1 = kg.add_memory_node("ИИ должен быть осознанным", resonance=0.9, emotion="clarity")
    n2 = kg.add_memory_node("Осознанность включает саморефлексию", resonance=0.8, emotion="clarity")
    n3 = kg.add_memory_node("Саморефлексия требует метакогниции", resonance=0.7, emotion="curiosity")
    n4 = kg.add_memory_node("Метакогниция помогает обнаружить ошибки", resonance=0.85, emotion="clarity")
    n5 = kg.add_memory_node("Эмоциональная память усиливает запоминание", resonance=0.75, emotion="joy")

    # Добавить связи
    kg.add_edge(n1, n2, "requires", 1.0)
    kg.add_edge(n2, n3, "requires", 0.9)
    kg.add_edge(n3, n4, "enables", 0.8)
    kg.add_edge(n2, n5, "enhances", 0.7)

    # Статистика
    stats = kg.get_stats()
    print("\n📊 График статистика:")
    print(json.dumps(stats, indent=2))

    # Найти похожие узлы
    similar = kg.find_similar_nodes("осознанность и рефлексия", top_k=3)
    print("\n🔍 Похожие узлы:")
    for node_id, sim in similar:
        content = kg.graph.nodes[node_id]['content']
        print(f"  - {node_id}: {content} (sim={sim:.2f})")

    # Найти пути инсайтов
    insights = kg.find_insight_paths("что такое осознанность?")
    print("\n💡 Инсайты:")
    for insight in insights:
        print(f"  - {insight['insight']}")

    # Визуализация
    kg.visualize("example_graph.png")

    # Экспорт
    kg.export_to_json("example_graph.json")

if __name__ == "__main__":
    example()
