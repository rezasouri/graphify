"""Create capped subgraph payloads for each aggregated community."""
import json
from graphify.exporters.html_data import build_html_payload

def snapshots(G, communities, output_path, labels, cap=100):
    result = {}
    for cid, members in sorted(communities.items()):
        available = [n for n in members if n in G]
        chosen = sorted(available, key=lambda n: (-G.degree[n], str(n)))[:cap]
        n, e, _, _ = build_html_payload(G.subgraph(chosen).copy(), {cid: chosen},
                                        output_path, labels, learning_overlay={})
        result[str(cid)] = {"nodes": json.loads(n), "edges": json.loads(e),
                            "shown": len(chosen), "total": len(available)}
    return result
