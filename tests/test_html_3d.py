"""Tests for the optional HTML 3D view without requiring a WebGL runner."""
import networkx as nx

from graphify.exporters.html import to_html


def test_3d_view_markup_and_lazy_loader(tmp_path):
    graph = nx.Graph()
    graph.add_node("x", label="Node", source_file="x.py")
    graph.add_node("y", label="Other", source_file="y.py")
    graph.add_edge("x", "y", relation="calls", confidence="EXTRACTED")
    dest = tmp_path / "graph.html"
    assert to_html(graph, {0: ["x", "y"]}, str(dest), community_labels={0: "Core"})
    html = dest.read_text(encoding="utf-8")
    assert 'id="graphify-view-2d"' in html
    assert 'id="graphify-view-3d"' in html
    assert 'id="graph3d"' in html
    assert 'aria-pressed="true">2D' in html
    assert "3d-force-graph@1.80.0" in html
    assert "document.createElement('script')" in html
    assert "window.graphifyFocus3d" in html
    assert ".filter(n => !n.hidden)" in html
    assert "focusNode(n.id)" in html
    assert "esc(n.label)" in html


def test_3d_disabled_by_default(tmp_path):
    graph = nx.Graph()
    graph.add_node("a", label="A")
    dest = tmp_path / "graph.html"
    assert to_html(graph, {0: ["a"]}, str(dest))
    html = dest.read_text(encoding="utf-8")
    assert '#graph3d { flex: 1; min-width: 0; display: none; }' in html
    assert 'aria-pressed="false">3D' in html
