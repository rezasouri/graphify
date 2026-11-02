"""HTML controls for interactive community exploration."""
import json

def script_for(snapshots):
    serialized = json.dumps(snapshots).replace("<", "\\u003c")
    return """<script>
(() => {
const details = """ + serialized + """;
const startNodes = RAW_NODES.slice(), startEdges = RAW_EDGES.slice();
const back = document.getElementById('explore-back');
const status = document.getElementById('explore-status');
let expanded = false;
window.graphifyDrilldown = false;
function setGraph(nodes, edges) {
  RAW_NODES.splice(0, RAW_NODES.length, ...nodes);
  RAW_EDGES.splice(0, RAW_EDGES.length, ...edges);
  nodesDS.clear(); edgesDS.clear();
  nodesDS.add(nodes.map((n,i) => ({...n,
    x: 30*Math.sqrt(i)*Math.cos(i*2.4),
    y: 30*Math.sqrt(i)*Math.sin(i*2.4)})));
  edgesDS.add(edges.map((e,i) => ({
    id:i,from:e.from,to:e.to,label:'',title:e.title,color:e.color,
    width:e.width,dashes:e.dashes,
    arrows:{to:{enabled:true,scaleFactor:0.5}}
  })));
  network.fit({animation:false});
  document.getElementById('search-results').style.display = 'none';
  document.getElementById('search').value = '';
}
function openCommunity(id) {
  if (expanded) return false;
  const info = details[String(id)];
  if (!info) return false;
  expanded = true;
  window.graphifyDrilldown = true;
  back.hidden = false;
  status.textContent = 'Community ' + id + ': ' + info.shown + ' of ' +
      info.total + ' nodes shown (highest degree)';
  setGraph(info.nodes, info.edges);
  return true;
}
back.addEventListener('click', () => {
  expanded = false;
  window.graphifyDrilldown = false;
  back.hidden = true;
  status.textContent = 'Double-click a community to explore';
  setGraph(startNodes, startEdges);
});
network.on('doubleClick', p => {
  if (p.nodes.length) openCommunity(p.nodes[0]);
});
window.graphifyOpenCommunity = openCommunity;
})();
</script>"""
