"""Shared HTML graph payload contract (2D and future 3D renderers)."""
import json

import networkx as nx

from graphify.exporters.html_data import build_html_payload


def _decode(text):
    return json.loads(text)


def test_payload_preserves_node_edge_and_community_metadata(tmp_path):
    graph = nx.Graph()
    graph.add_node("a", label="Alpha", source_file="a.py", file_type="code")
    graph.add_node("b", label="Beta", source_file="b.py", file_type="code")
    graph.add_edge("a", "b", relation="calls", confidence="INFERRED",
                   _src="b", _tgt="a")
    nodes, edges, legend, hyperedges = build_html_payload(
        graph, {0: ["a", "b"]}, str(tmp_path / "graph.html"),
        community_labels={0: "Core"},
    )
    decoded_nodes = _decode(nodes)
    decoded_edges = _decode(edges)
    assert {n["id"] for n in decoded_nodes} == {"a", "b"}
    assert all(n["community"] == 0 for n in decoded_nodes)
    assert decoded_edges[0]["from"] == "b"
    assert decoded_edges[0]["to"] == "a"
    assert decoded_edges[0]["dashes"] is True
    assert _decode(legend)[0]["label"] == "Core"
    assert _decode(hyperedges) == []


def test_payload_escapes_script_breakout_in_all_data(tmp_path):
    graph = nx.Graph()
    graph.add_node("x", label="x</script><!--", source_file="x.py")
    nodes, edges, legend, hyperedges = build_html_payload(
        graph, {0: ["x"]}, str(tmp_path / "graph.html"),
        community_labels={0: "<script>"},
    )
    assert all("<" not in s for s in (nodes, edges, legend, hyperedges))
    assert _decode(nodes)[0]["label"] == "x</script><!--"
    assert _decode(legend)[0]["label"] == "&lt;script&gt;"
