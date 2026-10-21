"""Optional 3D HTML viewer. Lazy-loads the WebGL renderer on first use."""

def html_3d_script() -> str:
    return """<script>
(function () {
  'use strict';
  const btn2d = document.getElementById('graphify-view-2d');
  const btn3d = document.getElementById('graphify-view-3d');
  const panel3d = document.getElementById('graph3d');
  const panel2d = document.getElementById('graph');
  let viewer = null;
  let mode = '2d';
  let loading = false;
  let chosen = null;
  let refreshTimer = null;

  function renderData() {
    const nodes = nodesDS.get().filter(n => !n.hidden).map(n => ({
      id: n.id, label: n.label, community: n.community,
      color: n.color.background, val: Math.max(1, n.size / 8)
    }));
    const visible = new Set(nodes.map(n => n.id));
    const links = RAW_EDGES.filter(e => visible.has(e.from) && visible.has(e.to))
      .map(e => ({ source: e.from, target: e.to, title: e.title,
                    confidence: e.confidence, width: e.width }));
    return { nodes, links };
  }

  function refresh() {
    if (!viewer || mode !== '3d') return;
    // Coalesce vis DataSet batch updates triggered by theme/community controls.
    clearTimeout(refreshTimer);
    refreshTimer = setTimeout(() => viewer.graphData(renderData()), 40);
  }
  nodesDS.on('update', refresh);

  function focus3d(id) {
    if (!viewer) return;
    const n = viewer.graphData().nodes.find(n => n.id === id);
    if (!n) return;
    chosen = id;
    const dist = Math.hypot(n.x || 0, n.y || 0, n.z || 0);
    const ratio = dist > 0 ? 160 / dist : 1;
    viewer.cameraPosition(
      { x: (n.x || 0) * (1 + ratio), y: (n.y || 0) * (1 + ratio),
        z: (n.z || 0) * (1 + ratio) },
      { x: n.x || 0, y: n.y || 0, z: n.z || 0 }, 700
    );
    showInfo(id);
  }

  window.graphifyFocus3d = focus3d;
  window.graphifyIs3d = () => mode === '3d';

  function resize3d() {
    if (viewer) viewer.width(panel3d.clientWidth).height(panel3d.clientHeight);
  }
  window.addEventListener('resize', resize3d);

  function activate(which) {
    if (which === '3d' && !viewer) return;
    mode = which;
    panel2d.style.display = which === '2d' ? '' : 'none';
    panel3d.style.display = which === '3d' ? 'block' : 'none';
    btn2d.setAttribute('aria-pressed', String(which === '2d'));
    btn3d.setAttribute('aria-pressed', String(which === '3d'));
    if (which === '3d') {
      network.setOptions({ physics: { enabled: false } });
      resize3d();
      viewer.resumeAnimation();
      refresh();
    } else {
      viewer && viewer.pauseAnimation();
      network.redraw();
      if (chosen !== null) {
        network.selectNodes([chosen]);
        showInfo(chosen);
      }
    }
  }

  function init3d() {
    if (!window.ForceGraph3D) throw new Error('3D graph library unavailable');
    viewer = ForceGraph3D({ controlType: 'orbit' })(panel3d)
      .backgroundColor(getComputedStyle(document.documentElement).getPropertyValue('--bg').trim() || '#0f0f1a')
      .nodeId('id').nodeColor(n => n.color).nodeVal(n => n.val)
      // Labels are data, never trusted HTML. The 3D library interprets the
      // nodeLabel return value as HTML; escape before passing it in.
      .nodeLabel(n => esc(n.label)).linkLabel(e => esc(e.title || ''))
      .linkWidth(e => e.width || 1)
      .linkOpacity(0.32)
      .onNodeClick(n => { chosen = n.id; showInfo(n.id); })
      .onBackgroundClick(() => {
        document.getElementById('info-content').innerHTML =
          '<span class="empty">Click a node to inspect it</span>';
      })
      .showNavInfo(true)
      .graphData(renderData());
    const themeObserver = new MutationObserver(() => {
      if (viewer) viewer.backgroundColor(
        getComputedStyle(document.documentElement).getPropertyValue('--bg').trim() || '#0f0f1a');
    });
    themeObserver.observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });
    activate('3d');
  }

  btn2d.addEventListener('click', () => {
    if (mode === '3d') activate('2d');
  });
  btn3d.addEventListener('click', () => {
    if (loading || mode === '3d') return;
    if (viewer) { activate('3d'); return; }
    // WebGL capability check avoids blank panels on unsupported devices.
    const canvas = document.createElement('canvas');
    if (!window.WebGLRenderingContext ||
        !(canvas.getContext('webgl') || canvas.getContext('experimental-webgl'))) {
      btn3d.title = '3D requires WebGL support';
      btn3d.disabled = true;
      return;
    }
    loading = true;
    btn3d.textContent = 'Loading 3D…';
    const done = () => { loading = false; btn3d.textContent = '3D'; };
    const fail = () => { done(); btn3d.title = '3D could not load; 2D remains available'; };
    const start = () => { try { init3d(); done(); } catch (_) { fail(); } };
    if (window.ForceGraph3D) { start(); return; }
    const script = document.createElement('script');
    script.src = 'https://unpkg.com/3d-force-graph@1.80.0/dist/3d-force-graph.min.js';
    script.onload = start;
    script.onerror = fail;
    document.head.appendChild(script);
  });
})();
</script>"""
