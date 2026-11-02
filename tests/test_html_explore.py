import networkx as nx
from graphify.exporters.html import to_html
from graphify.exporters.html_explore_data import snapshots

def test_snapshots_are_capped(tmp_path):
    G = nx.star_graph(150)
    G = nx.relabel_nodes(G, {i: str(i) for i in G})
    c = {0: list(G)}
    x = snapshots(G, c, str(tmp_path / 'graph.html'), {0:'Core'})
    assert x == snapshots(G,c,str(tmp_path / 'graph.html'), {0:'Core'})
    assert x["0"]["shown"] == 100
    assert x["0"]["total"] == 151
    assert x["0"]["nodes"][0]["id"] == "0"

def test_aggregate_html_has_drilldown(tmp_path):
    G = nx.path_graph(8)
    G = nx.relabel_nodes(G, {i: str(i) for i in G})
    out = tmp_path / 'graph.html'
    assert to_html(G, {0:['0','1','2','3'],1:['4','5','6','7']}, str(out),
                   node_limit=3)
    page = out.read_text()
    assert 'graphifyOpenCommunity' in page
    assert 'Back to communities' in page
