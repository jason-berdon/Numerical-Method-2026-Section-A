"""
structural_solver.py
Structural Solver style mock structural app with interactive joint-load editor.
Real JS stiffness solver embedded; results update when you add/remove loads.
Supports material selection, metric/imperial units, and per-member sections.

Run:
    python structural_solver.py               # native window if pywebview, else browser
    python structural_solver.py --browser     # force browser
"""

import os
import sys
import tempfile
import webbrowser


HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<title>Structural Solver  ·  rev3.r3d</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  html, body { height: 100%; overflow: hidden; font-family: 'Segoe UI', Tahoma, sans-serif; }
  body { background: #e9e9ef; color: #1b1b1f; display: flex; flex-direction: column; font-size: 12px; }
  button { font-family: inherit; cursor: pointer; }

  .titlebar {
    height: 30px;
    background: linear-gradient(180deg, #6b3fa0 0%, #4a2472 100%);
    color: #fff; display: flex; align-items: center; padding: 0 12px;
    font-weight: 600; font-size: 12px;
  }
  .titlebar .logo {
    width: 18px; height: 18px; margin-right: 8px; background: #fff;
    border-radius: 3px; display: inline-flex; align-items: center;
    justify-content: center; color: #4a2472; font-weight: 900; font-size: 10px;
  }
  .titlebar .filename { opacity: .85; font-weight: 400; margin-left: 8px; }
  .titlebar .winctrl { margin-left: auto; display: flex; gap: 16px; opacity: .8; }

  .menubar {
    height: 26px; background: #f4f4f8; border-bottom: 1px solid #c8c8d2;
    display: flex; align-items: center; padding: 0 8px; font-size: 12px;
  }
  .menubar span { padding: 3px 10px; border-radius: 3px; cursor: default; }
  .menubar span:hover { background: #e2dff0; }

  .ribbon { background: #f4f4f8; border-bottom: 1px solid #c8c8d2; display: flex; flex-direction: column; }
  .ribbon-tabs {
    display: flex; align-items: flex-end; height: 28px; padding-left: 6px;
    background: #e8e6f2; border-bottom: 1px solid #d0cee0;
  }
  .ribbon-tabs button {
    background: transparent; border: none; padding: 6px 16px; font-size: 12px;
    color: #3a3a3a; border-radius: 6px 6px 0 0; margin-right: 2px; font-weight: 500;
  }
  .ribbon-tabs button.active {
    background: #f4f4f8; color: #4a2472; font-weight: 700;
    border: 1px solid #d0cee0; border-bottom-color: #f4f4f8;
    position: relative; top: 1px;
  }
  .ribbon-body {
    height: 72px; display: flex; align-items: stretch; padding: 4px 6px;
    gap: 6px; overflow-x: auto;
  }
  .rgroup {
    display: flex; flex-direction: column; align-items: center;
    padding: 0 8px; border-right: 1px solid #ddd; min-width: 60px;
  }
  .rgroup:last-child { border-right: none; }
  .rgroup .row { display: flex; gap: 3px; flex: 1; align-items: center; }
  .rgroup .lbl { font-size: 10px; color: #666; margin-top: 2px; letter-spacing: .3px; }
  .ricon {
    width: 46px; height: 46px; background: #fff; border: 1px solid #d0cee0;
    border-radius: 4px; display: flex; flex-direction: column;
    align-items: center; justify-content: center; font-size: 9px;
    color: #4a2472; gap: 2px; padding: 2px;
  }
  .ricon:hover { background: #f3effa; border-color: #a48bcf; }
  .ricon .sym {
    width: 20px; height: 20px; background: #e2dff0; border-radius: 4px;
    display: flex; align-items: center; justify-content: center;
    color: #4a2472; font-weight: 700; font-size: 11px;
  }
  .ribbon-select {
    height: 22px; background: #fff; border: 1px solid #c8c8d2;
    border-radius: 3px; padding: 0 6px; font-size: 11px; color: #333;
  }
  .mini-btn {
    height: 20px; font-size: 10px; padding: 0 6px;
    background: #fff; border: 1px solid #d0cee0; border-radius: 3px;
    color: #4a2472; font-weight: 600;
  }
  .mini-btn:hover { background: #f3effa; border-color: #a48bcf; }

  .main { flex: 1; display: flex; min-height: 0; }

  .left-panel {
    width: 250px; background: #f7f7fb; border-right: 1px solid #c8c8d2;
    display: flex; flex-direction: column; overflow: hidden;
  }
  .panel-header {
    height: 26px;
    background: linear-gradient(180deg, #6b3fa0 0%, #4a2472 100%);
    color: #fff; display: flex; align-items: center; padding: 0 10px;
    font-size: 11px; font-weight: 700;
  }
  .panel-subtabs { display: flex; background: #ebe9f5; border-bottom: 1px solid #d0cee0; }
  .panel-subtabs button {
    flex: 1; background: transparent; border: none; padding: 6px 4px;
    font-size: 11px; color: #555;
  }
  .panel-subtabs button.active {
    background: #fff; color: #4a2472; font-weight: 700;
    border-bottom: 2px solid #6b3fa0;
  }

  .tree { flex: 1; overflow-y: auto; padding: 4px 0; font-size: 12px; }
  .tree .node {
    padding: 3px 8px 3px 20px; position: relative; cursor: pointer;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis; color: #333;
  }
  .tree .node:hover { background: #ede9f7; }
  .tree .node.sel { background: #d9cff0; color: #2a0f52; font-weight: 600; }
  .tree .node::before {
    content: '▸'; position: absolute; left: 6px; color: #6b3fa0; font-size: 10px;
  }
  .tree .node.open::before { content: '▾'; }
  .tree .node.leaf::before { content: '•'; color: #999; }
  .tree .child { display: none; }
  .tree .child.open { display: block; }
  .tree .child .node { padding-left: 34px; }

  .viewport-wrap { flex: 1; display: flex; flex-direction: column; min-width: 0; background: #fff; }
  .view-tabs {
    height: 26px; background: #ebe9f5; border-bottom: 1px solid #d0cee0;
    display: flex; align-items: flex-end; padding-left: 4px; gap: 2px;
  }
  .view-tabs button {
    background: #dedaf0; border: 1px solid #c8c8d2; border-bottom: none;
    border-radius: 5px 5px 0 0; padding: 5px 14px; font-size: 11px; color: #444;
  }
  .view-tabs button.active {
    background: #fff; color: #4a2472; font-weight: 700;
    border-bottom: 1px solid #fff; position: relative; top: 1px;
  }

  .viewport { flex: 1; position: relative; background: #fff; overflow: hidden; }
  #three-canvas { display: block; width: 100%; height: 100%; }
  .view-overlay {
    position: absolute; top: 8px; left: 8px;
    background: rgba(255,255,255,0.9); border: 1px solid #d0cee0;
    border-radius: 4px; padding: 6px 10px; font-size: 11px; color: #333;
    line-height: 1.5; box-shadow: 0 1px 4px rgba(0,0,0,.08);
  }
  .view-overlay b { color: #4a2472; }
  .view-overlay .hint {
    display: block; margin-top: 4px; color: #666; font-size: 10px;
    border-top: 1px dashed #ddd; padding-top: 4px;
  }
  .view-toolbar { position: absolute; top: 8px; right: 8px; display: flex; gap: 4px; }
  .view-toolbar button {
    width: 28px; height: 28px; background: #fff; border: 1px solid #d0cee0;
    border-radius: 4px; font-size: 13px; color: #4a2472;
  }
  .view-toolbar button:hover { background: #f3effa; }
  .view-status {
    position: absolute; bottom: 8px; left: 8px;
    background: rgba(255,255,255,0.92); border: 1px solid #d0cee0;
    border-radius: 4px; padding: 4px 10px; font-size: 11px;
    font-family: 'Consolas', monospace; color: #4a2472;
  }

  .dock {
    height: 240px; background: #f7f7fb; border-top: 1px solid #c8c8d2;
    display: flex; flex-direction: column;
  }
  .dock-tabs {
    height: 26px; background: #ebe9f5; border-bottom: 1px solid #d0cee0;
    display: flex; align-items: flex-end; padding-left: 6px; gap: 2px;
    overflow-x: auto;
  }
  .dock-tabs button {
    background: #dedaf0; border: 1px solid #c8c8d2; border-bottom: none;
    border-radius: 5px 5px 0 0; padding: 5px 14px; font-size: 11px;
    color: #444; white-space: nowrap;
  }
  .dock-tabs button.active {
    background: #fff; color: #4a2472; font-weight: 700;
    border-bottom: 1px solid #fff; position: relative; top: 1px;
  }
  .sheet-wrap { flex: 1; overflow: auto; background: #fff; }
  table.sheet {
    border-collapse: collapse; width: 100%; font-size: 11px;
    font-family: 'Consolas', 'Courier New', monospace;
  }
  table.sheet thead th {
    position: sticky; top: 0;
    background: linear-gradient(180deg, #6b3fa0 0%, #4a2472 100%);
    color: #fff; padding: 4px 10px; text-align: left; font-weight: 600;
    border-right: 1px solid #3a1d58; white-space: nowrap;
  }
  table.sheet tbody td {
    padding: 3px 10px; border-bottom: 1px solid #eee;
    border-right: 1px solid #f2f2f2; color: #222; white-space: nowrap;
  }
  table.sheet tbody tr:nth-child(even) { background: #faf9fd; }
  table.sheet tbody tr:hover { background: #f0ebfa; }
  table.sheet tbody td.num { text-align: right; font-variant-numeric: tabular-nums; }
  table.sheet tbody td.sel {
    background: #e8dcf7; box-shadow: inset 0 0 0 2px #6b3fa0;
  }
  table.sheet tbody td.del {
    color: #b00; font-weight: 700; cursor: pointer; text-align: center;
  }
  table.sheet tbody td.del:hover { background: #ffe5e5; }

  .statusbar {
    height: 24px; background: #e8e6f2; border-top: 1px solid #c8c8d2;
    display: flex; align-items: center; padding: 0 12px; font-size: 11px;
    color: #333; gap: 24px;
  }
  .statusbar .dot { width: 8px; height: 8px; border-radius: 50%;
                    background: #2fa84f; margin-right: 6px; }
  .statusbar .right { margin-left: auto; display: flex; gap: 18px; }
  .statusbar b { color: #4a2472; }

  /* ---------------- MODAL ---------------- */
  .modal-overlay {
    position: fixed; inset: 0; background: rgba(30, 20, 60, .35);
    display: flex; align-items: center; justify-content: center;
    z-index: 1000;
  }
  .modal-box {
    background: #fff; border-radius: 6px; min-width: 380px;
    box-shadow: 0 12px 40px rgba(0,0,0,.3);
    border-top: 4px solid #6b3fa0;
    font-size: 12px;
  }
  .modal-header {
    padding: 10px 16px; font-weight: 700; color: #4a2472;
    font-size: 13px; border-bottom: 1px solid #ebe9f5;
  }
  .modal-body {
    padding: 12px 16px;
    display: grid;
    grid-template-columns: 120px 1fr 120px 1fr;
    gap: 8px 10px;
    align-items: center;
  }
  .modal-body label { color: #333; }
  .modal-body input[type=number] {
    width: 100%; height: 24px; border: 1px solid #c8c8d2;
    border-radius: 3px; padding: 0 6px; font-family: 'Consolas', monospace;
    font-size: 12px;
  }
  .modal-body input[type=number]:focus {
    outline: none; border-color: #6b3fa0;
    box-shadow: 0 0 0 2px #e2dff0;
  }
  .modal-footer {
    padding: 10px 16px; border-top: 1px solid #ebe9f5;
    display: flex; gap: 8px; justify-content: flex-end;
  }
  .modal-footer button {
    min-width: 90px; height: 28px;
    border-radius: 3px; border: 1px solid #c8c8d2; background: #f4f4f8;
    font-size: 12px;
  }
  .modal-footer button.primary {
    background: #6b3fa0; border-color: #4a2472; color: #fff;
    font-weight: 700;
  }
  .modal-footer button.primary:hover { background: #7c4cb8; }
</style>
</head>
<body>

<div class="titlebar">
  <div class="logo">S</div>
  Structural Solver
  <span class="filename">— rev3.r3d — 6m × 6m × 6m Cube, Rev. 3</span>
  <span class="winctrl"><span>—</span><span>❐</span><span>✕</span></span>
</div>

<div class="menubar">
  <span>File</span><span>Edit</span><span>View</span><span>Insert</span>
  <span>Modify</span><span>Tools</span><span>Window</span><span>Help</span>
</div>

<div class="ribbon">
  <div class="ribbon-tabs" id="ribbon-tabs">
    <button class="active">Home</button>
    <button>Model</button>
    <button>Loads</button>
    <button>Analysis</button>
    <button>Results</button>
    <button>Reports</button>
  </div>
  <div class="ribbon-body">

    <div class="rgroup">
      <div class="row">
        <button class="ricon" onclick="alert('New model')"><span class="sym">N</span>New</button>
        <button class="ricon" onclick="alert('Open model')"><span class="sym">O</span>Open</button>
        <button class="ricon" onclick="alert('Save')"><span class="sym">S</span>Save</button>
      </div>
      <div class="lbl">File</div>
    </div>

    <div class="rgroup">
      <div class="row">
        <button class="ricon" onclick="focusSheet('nodes')"><span class="sym">●</span>Nodes</button>
        <button class="ricon" onclick="focusSheet('members')"><span class="sym">—</span>Members</button>
        <button class="ricon" onclick="focusSheet('supports')"><span class="sym">▲</span>Supports</button>
      </div>
      <div class="lbl">Model</div>
    </div>

    <div class="rgroup">
      <div class="row" style="flex-direction:column; align-items:stretch; gap:3px; padding:2px 0;">
        <select class="ribbon-select" id="section-select"
                onchange="onSectionChange(this.value)"
                style="width:150px;" title="Member Section"></select>
        <div style="display:flex; gap:3px;">
          <button class="mini-btn" style="flex:1;" onclick="applySectionToSelected()"
                  title="Apply chosen section to selected member(s)">Apply Sel</button>
          <button class="mini-btn" style="flex:1;" onclick="applySectionToAll()"
                  title="Apply chosen section to ALL members">All</button>
        </div>
      </div>
      <div class="lbl">Section</div>
    </div>

    <div class="rgroup">
      <div class="row">
        <button class="ricon" onclick="openLoadDialog()"><span class="sym">＋</span>Add Load</button>
        <button class="ricon" onclick="clearLoads()"><span class="sym">×</span>Clear</button>
        <button class="ricon" onclick="focusSheet('loads')"><span class="sym">↓</span>List</button>
      </div>
      <div class="lbl">Loads</div>
    </div>

    <div class="rgroup">
      <div class="row">
        <button class="ricon" onclick="runAnalysis()"><span class="sym">▶</span>Run</button>
      </div>
      <div class="lbl">Solve</div>
    </div>

    <div class="rgroup">
      <div class="row">
        <button class="ricon" onclick="focusSheet('disp')"><span class="sym">↗</span>Disp</button>
        <button class="ricon" onclick="focusSheet('react')"><span class="sym">↑</span>React</button>
        <button class="ricon" onclick="focusSheet('forces')"><span class="sym">F</span>Forces</button>
      </div>
      <div class="lbl">Results</div>
    </div>

    <div class="rgroup">
      <div class="row" style="flex-direction:column; align-items:stretch; gap:3px; padding:2px 0;">
        <select class="ribbon-select" id="mat-select"
                onchange="onMaterialChange(this.value)"
                style="width:150px;" title="Material"></select>
        <select class="ribbon-select" id="unit-select"
                onchange="onUnitsChange(this.value)"
                style="width:150px;" title="Units">
          <option value="metric">Metric (kN, m, MPa)</option>
          <option value="imperial">Imperial (kip, ft, ksi)</option>
        </select>
      </div>
      <div class="lbl">Material / Units</div>
    </div>

    <div class="rgroup" style="margin-left:auto;">
      <div class="row">
        <button class="ricon" onclick="toggleDeformed()"><span class="sym">≈</span>Deformed</button>
        <button class="ricon" onclick="toggleArrows()"><span class="sym">⇣</span>Arrows</button>
      </div>
      <div class="lbl">Display</div>
    </div>
  </div>
</div>

<div class="main">
  <div class="left-panel">
    <div class="panel-header">MODEL NAVIGATOR</div>
    <div class="panel-subtabs">
      <button class="active">Model</button>
      <button>Properties</button>
      <button>Results</button>
    </div>
    <div class="tree" id="tree">
      <div class="node open" onclick="toggleGroup('g-geom', this)">Geometry</div>
      <div class="child open" id="g-geom">
        <div class="node leaf sel" onclick="focusSheet('nodes')">Nodes (8)</div>
        <div class="node leaf" onclick="focusSheet('members')">Members (12)</div>
      </div>

      <div class="node open" onclick="toggleGroup('g-supp', this)">Supports</div>
      <div class="child open" id="g-supp">
        <div class="node leaf" onclick="focusSheet('supports')">Pinned (4)</div>
      </div>

      <div class="node open" onclick="toggleGroup('g-mat', this)">Materials</div>
      <div class="child open" id="g-mat">
        <div class="node leaf" onclick="focusSheet('materials')" id="tree-mat">A992</div>
      </div>

      <div class="node open" onclick="toggleGroup('g-sec', this)">Sections</div>
      <div class="child open" id="g-sec">
        <div class="node leaf" onclick="focusSheet('sections')" id="tree-sec">Section Library</div>
      </div>

      <div class="node open" onclick="toggleGroup('g-load', this)">Loads</div>
      <div class="child open" id="g-load">
        <div class="node leaf" onclick="focusSheet('loads')" id="tree-loads">Joint Loads</div>
      </div>

      <div class="node open" onclick="toggleGroup('g-res', this)">Results</div>
      <div class="child open" id="g-res">
        <div class="node leaf" onclick="focusSheet('disp')">Joint Displacements</div>
        <div class="node leaf" onclick="focusSheet('react')">Support Reactions</div>
        <div class="node leaf" onclick="focusSheet('forces')">Member Forces</div>
      </div>
    </div>
  </div>

  <div class="viewport-wrap">
    <div class="view-tabs">
      <button class="active">3D View</button>
      <button>Spreadsheet</button>
      <button>Results View</button>
    </div>
    <div class="viewport">
      <div id="three-canvas"></div>

      <div class="view-overlay">
        <div><b>Material:</b> <span id="ov-mat">A992 (199,948 MPa)</span></div>
        <div><b>Nodes:</b> 8 &nbsp; <b>Members:</b> 12 &nbsp; <b>DOFs:</b> 48</div>
        <div><b>Loads:</b> <span id="ov-loads">4</span> &nbsp;
             <b>Selected:</b> <span id="ov-sel">—</span></div>
        <span class="hint">Click a <b>node</b> or <b>member</b> to select,
             then use the ribbon to add loads or change section.
             <b>Shift+Click</b> for multi-select.</span>
      </div>

      <div class="view-toolbar">
        <button title="Zoom in"  onclick="zoomView(1.15)">+</button>
        <button title="Zoom out" onclick="zoomView(0.87)">−</button>
        <button title="Reset"    onclick="resetView()">⟲</button>
      </div>

      <div class="view-status" id="view-status">
        Ready.
      </div>
    </div>
  </div>
</div>

<div class="dock">
  <div class="dock-tabs" id="dock-tabs">
    <button data-sheet="nodes">Nodes</button>
    <button data-sheet="members">Members</button>
    <button data-sheet="sections">Sections</button>
    <button data-sheet="supports">Supports</button>
    <button data-sheet="materials">Materials</button>
    <button class="active" data-sheet="loads">Loads</button>
    <button data-sheet="disp">Displacements</button>
    <button data-sheet="react">Reactions</button>
    <button data-sheet="forces">Member Forces</button>
  </div>
  <div class="sheet-wrap">
    <table class="sheet" id="sheet">
      <thead></thead>
      <tbody></tbody>
    </table>
  </div>
</div>

<div class="statusbar">
  <span><span class="dot" id="status-dot"></span><b id="status-msg">Ready</b></span>
  <span>Units: <b id="sb-units">Metric (kN, m)</b></span>
  <span>Solve: <b>Direct Stiffness (JS)</b></span>
  <span class="right">
    <span>Nodes: <b>8</b></span>
    <span>Members: <b>12</b></span>
    <span>Supports: <b>4</b></span>
    <span>Loads: <b id="sb-loads">4</b></span>
    <span>Material: <b id="sb-mat">A992</b></span>
  </span>
</div>

<!-- ================ LOAD DIALOG ================ -->
<div class="modal-overlay" id="load-dialog" style="display:none;">
  <div class="modal-box">
    <div class="modal-header" id="dlg-title">Add Joint Load</div>
    <div class="modal-body">
      <label>Node:</label>
      <input type="number" id="dlg-node" min="1" max="8" step="1" value="5"/>
      <label id="lbl-fx">FX (kN):</label>
      <input type="number" id="dlg-fx" value="0" step="1"/>

      <label id="lbl-fy">FY (kN):</label>
      <input type="number" id="dlg-fy" value="-100" step="1"/>
      <label id="lbl-fz">FZ (kN):</label>
      <input type="number" id="dlg-fz" value="0" step="1"/>

      <label id="lbl-mx">MX (kNm):</label>
      <input type="number" id="dlg-mx" value="0" step="1"/>
      <label id="lbl-my">MY (kNm):</label>
      <input type="number" id="dlg-my" value="0" step="1"/>

      <label id="lbl-mz">MZ (kNm):</label>
      <input type="number" id="dlg-mz" value="0" step="1"/>
      <span></span><span></span>
    </div>
    <div class="modal-footer">
      <button onclick="closeLoadDialog()">Cancel</button>
      <button class="primary" onclick="confirmLoadDialog()">Add Load</button>
    </div>
  </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/build/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>

<script>
/* ==================================================================
   0. UNITS  (internal solver stays SI: N, m, Pa)
   ================================================================== */
let units = 'metric';   // 'metric' | 'imperial'

const UC = {
  metric: {
    kN: 1, kNm: 1, len: 1, disp: 1, stress: 1 / 1e6,
    area: 1, inertia: 1,
    labForce: 'kN', labMoment: 'kN·m', labLen: 'm', labDisp: 'm',
    labStress: 'MPa', labArea: 'm²', labInertia: 'm⁴',
    name: 'Metric (kN, m)',
  },
  imperial: {
    kN:    0.2248089431,
    kNm:   0.7375621493,
    len:   3.280839895,
    disp:  3.280839895,
    stress: 0.1450377377 / 1e6,
    area: 10.76391042,
    inertia: 115.8615395,
    labForce: 'kip', labMoment: 'kip·ft', labLen: 'ft', labDisp: 'ft',
    labStress: 'ksi', labArea: 'ft²', labInertia: 'ft⁴',
    name: 'Imperial (kip, ft)',
  }
};

function dF(kN)   { return kN  * UC[units].kN; }
function dM(kNm)  { return kNm * UC[units].kNm; }
function dL(m)    { return m   * UC[units].len; }
function dD(m)    { return m   * UC[units].disp; }
function dS(Pa)   { return Pa  * UC[units].stress; }
function dA(m2)   { return m2  * UC[units].area; }
function dI(m4)   { return m4  * UC[units].inertia; }
function iF(v)    { return v / UC[units].kN; }
function iM(v)    { return v / UC[units].kNm; }

function labF() { return UC[units].labForce; }
function labM() { return UC[units].labMoment; }
function labL() { return UC[units].labLen; }
function labD() { return UC[units].labDisp; }
function labS() { return UC[units].labStress; }
function labA() { return UC[units].labArea; }
function labI() { return UC[units].labInertia; }

/* ==================================================================
   1. BASE MODEL
   ================================================================== */
const NODES = {
  1: [0, 0, 0], 2: [6, 0, 0], 3: [6, 0, 6], 4: [0, 0, 6],
  5: [0, 6, 0], 6: [6, 6, 0], 7: [6, 6, 6], 8: [0, 6, 6]
};

// [n1, n2, beta_deg, release_start, release_end]
const MEMBERS = [
  [1, 2, 0, null, null], [2, 3, 0, null, null],
  [3, 4, 0, null, null], [4, 1, 0, null, null],
  [5, 6, 0, null, null], [6, 7, 0, null, null],
  [7, 8, 0, null, null], [8, 5, 0, null, null],
  [1, 5, 90, 'rz', null], [2, 6, 90, 'rz', null],
  [3, 7, 90, 'rz', null], [4, 8, 90, 'rz', null]
];

const SUPPORTS = {
  1: 'Pinned', 2: 'Pinned', 3: 'Pinned', 4: 'Pinned',
  5: 'Free', 6: 'Free', 7: 'Free', 8: 'Free'
};

// ---- Section library (internal SI: m², m⁴, m) ----
const SECTIONS = [
  { name: 'W8×31',       type: 'W',    A: 5.87e-3, Iy: 4.79e-5, Iz: 1.53e-6, J: 2.03e-7, d: 0.203 },
  { name: 'W10×49',      type: 'W',    A: 9.29e-3, Iy: 1.16e-4, Iz: 3.92e-6, J: 5.19e-7, d: 0.253 },
  { name: 'W12×65',      type: 'W',    A: 1.23e-2, Iy: 2.19e-4, Iz: 7.74e-6, J: 9.79e-7, d: 0.308 },
  { name: 'W14×90',      type: 'W',    A: 1.71e-2, Iy: 4.30e-4, Iz: 1.50e-5, J: 2.03e-6, d: 0.356 },
  { name: 'W16×100',     type: 'W',    A: 1.90e-2, Iy: 6.19e-4, Iz: 1.94e-5, J: 2.65e-6, d: 0.406 },
  { name: 'HSS6×6×½',    type: 'HSS',  A: 6.70e-3, Iy: 3.81e-5, Iz: 3.81e-5, J: 6.36e-5, d: 0.152 },
  { name: 'HSS8×8×½',    type: 'HSS',  A: 9.10e-3, Iy: 9.47e-5, Iz: 9.47e-5, J: 1.58e-4, d: 0.203 },
  { name: 'HSS10×10×½',  type: 'HSS',  A: 1.16e-2, Iy: 1.90e-4, Iz: 1.90e-4, J: 3.16e-4, d: 0.254 },
  { name: 'Custom-1',    type: 'Custom', A: 1.00e-2, Iy: 1.00e-6, Iz: 1.00e-6, J: 1.00e-6, d: 0.180 },
];

// Default section per member (parallel to MEMBERS)
let MEMBER_SECTIONS = MEMBERS.map(() => 'W10×49');
let currentSection = 'W10×49';

function getSection(name) {
  return SECTIONS.find(s => s.name === name) || SECTIONS[1];
}

// Material (global - applied to all members)
const SEC_BASE = { E: 199948e6, G: 76904e6 };   // Pa - overwritten by material selector
const MATERIALS = [
  ['Hot Rolled','A36 Gr.36',   199948, 76904, 0.30, 11.7, 76.97, 248.2, 399.9],
  ['Hot Rolled','A572 Gr.50',  199948, 76904, 0.30, 11.7, 76.97, 344.7, 399.9],
  ['Hot Rolled','A992',        199948, 76904, 0.30, 11.7, 76.97, 344.7, 399.9],
  ['Hot Rolled','A500 Gr.42',  199948, 76904, 0.30, 11.7, 76.97, 289.6, 399.9],
  ['Hot Rolled','A500 Gr.46',  199948, 76904, 0.30, 11.7, 76.97, 317.2, 399.9],
  ['Cold Formed','A570_33',    203395, 78228, 0.30, 11.7, 76.97, 227.5, 358.5],
  ['Cold Formed','A607_C1_55', 203395, 78228, 0.30, 11.7, 76.97, 379.2, 482.6],
  ['Concrete','Conc3000NW',    21760, 9460, 0.15, 10.8, 22.78, 20.7, 0],
  ['Concrete','Conc3500NW',    23504, 10218, 0.15, 10.8, 22.78, 24.1, 0],
  ['Concrete','Conc4000NW',    25124, 10921, 0.15, 10.8, 22.78, 27.6, 0],
  ['Aluminum','6061-T6',       69637, 26114, 0.33, 23.4, 27.18, 241.3, 262.0],
];

let currentMaterial = 'A992';

function applyMaterial(label) {
  const m = MATERIALS.find(row => row[1] === label);
  if (!m) return;
  SEC_BASE.E = m[2] * 1e6;
  SEC_BASE.G = m[3] * 1e6;
  currentMaterial = label;
  updateMaterialLabels();
}

function updateMaterialLabels() {
  const m = MATERIALS.find(row => row[1] === currentMaterial);
  if (!m) return;
  const E_disp = dS(m[2] * 1e6);
  const txt = `${currentMaterial} (${E_disp.toLocaleString(undefined, {maximumFractionDigits: 0})} ${labS()})`;
  document.getElementById('ov-mat').textContent = txt;
  document.getElementById('sb-mat').textContent = currentMaterial;
  const tree = document.getElementById('tree-mat');
  if (tree) tree.textContent = currentMaterial + ' (steel)';
}

/* ==================================================================
   2. LOADS  (internal: kN, kN·m)
   ================================================================== */
let LOADS = [
  { id: 1, node: 5, fx: 0, fy: -100, fz: 0, mx: 0, my: 0, mz: 0 },
  { id: 2, node: 6, fx: 0, fy: -100, fz: 0, mx: 0, my: 0, mz: 0 },
  { id: 3, node: 7, fx: 0, fy: -100, fz: 0, mx: 0, my: 0, mz: 0 },
  { id: 4, node: 8, fx: 0, fy: -100, fz: 0, mx: 0, my: 0, mz: 0 },
];
let nextLoadId = 5;

function getNodalLoads() {
  const map = {};
  for (const L of LOADS) {
    if (!map[L.node]) map[L.node] = [0, 0, 0, 0, 0, 0];
    map[L.node][0] += L.fx;
    map[L.node][1] += L.fy;
    map[L.node][2] += L.fz;
    map[L.node][3] += L.mx;
    map[L.node][4] += L.my;
    map[L.node][5] += L.mz;
  }
  return map;
}

/* ==================================================================
   3. LINEAR ALGEBRA HELPERS
   ================================================================== */
function zeros(n, m) {
  const a = new Array(n);
  for (let i = 0; i < n; i++) a[i] = new Float64Array(m);
  return a;
}
function matMul(A, B) {
  const n = A.length, p = B.length, m = B[0].length;
  const C = zeros(n, m);
  for (let i = 0; i < n; i++) {
    const Ai = A[i];
    for (let k = 0; k < p; k++) {
      const a = Ai[k];
      if (!a) continue;
      const Bk = B[k];
      for (let j = 0; j < m; j++) C[i][j] += a * Bk[j];
    }
  }
  return C;
}
function matT(A) {
  const n = A.length, m = A[0].length;
  const B = zeros(m, n);
  for (let i = 0; i < n; i++)
    for (let j = 0; j < m; j++) B[j][i] = A[i][j];
  return B;
}
function cross(a, b) {
  return [a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0]];
}
function dot(a, b) { return a[0]*b[0]+a[1]*b[1]+a[2]*b[2]; }
function norm(a)   { return Math.hypot(a[0], a[1], a[2]); }

function solveLinear(A, b) {
  const n = A.length;
  const M = A.map(row => Float64Array.from(row));
  const x = Float64Array.from(b);
  for (let k = 0; k < n; k++) {
    let maxRow = k, maxVal = Math.abs(M[k][k]);
    for (let i = k + 1; i < n; i++) {
      if (Math.abs(M[i][k]) > maxVal) { maxVal = Math.abs(M[i][k]); maxRow = i; }
    }
    if (maxRow !== k) {
      const tmp = M[k]; M[k] = M[maxRow]; M[maxRow] = tmp;
      const t = x[k]; x[k] = x[maxRow]; x[maxRow] = t;
    }
    const pivot = M[k][k];
    if (Math.abs(pivot) < 1e-20) continue;
    for (let i = k + 1; i < n; i++) {
      const f = M[i][k] / pivot;
      if (!f) continue;
      for (let j = k; j < n; j++) M[i][j] -= f * M[k][j];
      x[i] -= f * x[k];
    }
  }
  for (let i = n - 1; i >= 0; i--) {
    let s = x[i];
    for (let j = i + 1; j < n; j++) s -= M[i][j] * x[j];
    x[i] = s / M[i][i];
  }
  return x;
}

/* ==================================================================
   4. SOLVER  (SI internally; per-member section)
   ================================================================== */
function memberTransform(n1, n2, betaDeg) {
  const p1 = NODES[n1], p2 = NODES[n2];
  const dx = p2[0]-p1[0], dy = p2[1]-p1[1], dz = p2[2]-p1[2];
  const L = Math.hypot(dx, dy, dz);
  const ex = [dx/L, dy/L, dz/L];
  const ref = Math.abs(ex[1]) < 0.9 ? [0, 1, 0] : [0, 0, 1];
  let ey = cross(ex, ref);
  const ney = norm(ey);
  if (ney < 1e-12) { ey = [0, 0, 1]; }
  else             { ey = [ey[0]/ney, ey[1]/ney, ey[2]/ney]; }

  const beta = betaDeg * Math.PI / 180;
  const cb = Math.cos(beta), sb = Math.sin(beta);
  const kxv = cross(ex, ey);
  const kdv = dot(ex, ey);
  const eyRot = [
    ey[0]*cb + kxv[0]*sb + ex[0]*kdv*(1-cb),
    ey[1]*cb + kxv[1]*sb + ex[1]*kdv*(1-cb),
    ey[2]*cb + kxv[2]*sb + ex[2]*kdv*(1-cb),
  ];
  const nr = norm(eyRot);
  const eyF = [eyRot[0]/nr, eyRot[1]/nr, eyRot[2]/nr];
  const ezF = cross(ex, eyF);

  const T = [
    [ex[0], eyF[0], ezF[0]],
    [ex[1], eyF[1], ezF[1]],
    [ex[2], eyF[2], ezF[2]],
  ];
  return { L, T };
}

function buildTmat(T) {
  const Tm = zeros(12, 12);
  for (let b = 0; b < 4; b++)
    for (let i = 0; i < 3; i++)
      for (let j = 0; j < 3; j++)
        Tm[b*3+i][b*3+j] = T[i][j];
  return Tm;
}

function beamStiff(L, rel_s, rel_e, section) {
  const E = SEC_BASE.E, G = SEC_BASE.G;
  const A  = section.A;
  const Iy = section.Iy;
  const Iz = section.Iz;
  const J  = section.J;

  const k = zeros(12, 12);
  k[0][0] = k[6][6] = E*A/L;
  k[0][6] = k[6][0] = -E*A/L;

  k[3][3] = k[9][9] = G*J/L;
  k[3][9] = k[9][3] = -G*J/L;

  k[1][1] = 12*E*Iz/Math.pow(L,3);
  k[1][5] = 6*E*Iz/Math.pow(L,2);
  k[1][7] = -12*E*Iz/Math.pow(L,3);
  k[1][11] = 6*E*Iz/Math.pow(L,2);
  k[5][1] = k[1][5]; k[5][5] = 4*E*Iz/L;
  k[5][7] = -6*E*Iz/Math.pow(L,2); k[5][11] = 2*E*Iz/L;
  k[7][1] = k[1][7]; k[7][5] = k[5][7];
  k[7][7] = 12*E*Iz/Math.pow(L,3); k[7][11] = -6*E*Iz/Math.pow(L,2);
  k[11][1] = k[1][11]; k[11][5] = k[5][11];
  k[11][7] = k[7][11]; k[11][11] = 4*E*Iz/L;

  k[2][2] = 12*E*Iy/Math.pow(L,3);
  k[2][4] = -6*E*Iy/Math.pow(L,2);
  k[2][8] = -12*E*Iy/Math.pow(L,3);
  k[2][10] = -6*E*Iy/Math.pow(L,2);
  k[4][2] = k[2][4]; k[4][4] = 4*E*Iy/L;
  k[4][8] = 6*E*Iy/Math.pow(L,2); k[4][10] = 2*E*Iy/L;
  k[8][2] = k[2][8]; k[8][4] = k[4][8];
  k[8][8] = 12*E*Iy/Math.pow(L,3); k[8][10] = 6*E*Iy/Math.pow(L,2);
  k[10][2] = k[2][10]; k[10][4] = k[4][10];
  k[10][8] = k[8][10]; k[10][10] = 4*E*Iy/L;

  const dofMap = {ux: 0, uy: 1, uz: 2, rx: 3, ry: 4, rz: 5};
  const rel = [];
  if (rel_s && rel_s in dofMap) rel.push(dofMap[rel_s]);
  if (rel_e && rel_e in dofMap) rel.push(dofMap[rel_e] + 6);
  const small = 1e-6 * E * A / L;
  for (const idx of rel) {
    for (let j = 0; j < 12; j++) k[idx][j] = 0;
    for (let i = 0; i < 12; i++) k[i][idx] = 0;
    k[idx][idx] = small;
  }
  return k;
}

function solveModel() {
  const nodeIds = Object.keys(NODES).map(Number).sort((a, b) => a - b);
  const idxMap = {};
  nodeIds.forEach((n, i) => idxMap[n] = i);
  const ndof = nodeIds.length * 6;

  const fixed = new Set();
  for (const [nid, t] of Object.entries(SUPPORTS)) {
    if (t === 'Pinned') {
      const i = idxMap[nid];
      for (let d = 0; d < 3; d++) fixed.add(i * 6 + d);
    }
  }
  const free = [];
  for (let d = 0; d < ndof; d++) if (!fixed.has(d)) free.push(d);
  const nFree = free.length;

  const K = zeros(ndof, ndof);
  for (let mi = 0; mi < MEMBERS.length; mi++) {
    const [n1, n2, beta, rs, re] = MEMBERS[mi];
    const sec = getSection(MEMBER_SECTIONS[mi]);
    const { L, T } = memberTransform(n1, n2, beta);
    if (L < 1e-12) continue;
    const kL = beamStiff(L, rs, re, sec);
    const Tm = buildTmat(T);
    const kG = matMul(matMul(matT(Tm), kL), Tm);
    const i1 = idxMap[n1], i2 = idxMap[n2];
    const dofs = [];
    for (let d = 0; d < 6; d++) dofs.push(i1 * 6 + d);
    for (let d = 0; d < 6; d++) dofs.push(i2 * 6 + d);
    for (let a = 0; a < 12; a++)
      for (let b = 0; b < 12; b++)
        K[dofs[a]][dofs[b]] += kG[a][b];
  }

  const F = new Float64Array(ndof);
  const nl = getNodalLoads();
  for (const [nid, forces] of Object.entries(nl)) {
    const i = idxMap[nid];
    for (let d = 0; d < 6; d++) F[i * 6 + d] += forces[d] * 1000; // kN -> N
  }

  const Kred = zeros(nFree, nFree);
  const Fred = new Float64Array(nFree);
  for (let a = 0; a < nFree; a++) {
    Fred[a] = F[free[a]];
    for (let b = 0; b < nFree; b++) Kred[a][b] = K[free[a]][free[b]];
  }
  const Ufree = solveLinear(Kred, Fred);
  const U = new Float64Array(ndof);
  for (let a = 0; a < nFree; a++) U[free[a]] = Ufree[a];

  const R = new Float64Array(ndof);
  for (let i = 0; i < ndof; i++) {
    let s = -F[i];
    for (let j = 0; j < ndof; j++) s += K[i][j] * U[j];
    R[i] = s;
  }

  const members = [];
  for (let mid = 0; mid < MEMBERS.length; mid++) {
    const [n1, n2, beta, rs, re] = MEMBERS[mid];
    const sec = getSection(MEMBER_SECTIONS[mid]);
    const { L, T } = memberTransform(n1, n2, beta);
    const Tm = buildTmat(T);
    const i1 = idxMap[n1], i2 = idxMap[n2];
    const dofs = [];
    for (let d = 0; d < 6; d++) dofs.push(i1 * 6 + d);
    for (let d = 0; d < 6; d++) dofs.push(i2 * 6 + d);

    const uG = new Float64Array(12);
    for (let a = 0; a < 12; a++) uG[a] = U[dofs[a]];
    const uL = new Float64Array(12);
    for (let i = 0; i < 12; i++) {
      let s = 0;
      for (let j = 0; j < 12; j++) s += Tm[i][j] * uG[j];
      uL[i] = s;
    }
    const kL = beamStiff(L, rs, re, sec);
    const fL = new Float64Array(12);
    for (let i = 0; i < 12; i++) {
      let s = 0;
      for (let j = 0; j < 12; j++) s += kL[i][j] * uL[j];
      fL[i] = s;
    }
    members.push({
      mid: mid + 1, n1, n2, L,
      section: MEMBER_SECTIONS[mid],
      Fi: Array.from(fL.slice(0, 6)),
      Fj: Array.from(fL.slice(6, 12)),
    });
  }
  return { nodeIds, idxMap, U, R, members, fixed, free, ndof };
}

/* ==================================================================
   5. SPREADSHEET
   ================================================================== */
function formatNum(v) {
  if (typeof v !== 'number') return v;
  if (!isFinite(v)) return v.toString();
  if (Number.isInteger(v)) return v.toString();
  if (Math.abs(v) >= 1e-3 && Math.abs(v) < 1e6) return v.toFixed(4);
  return v.toExponential(4);
}

let RESULTS = null;

function materialRowDisp(m) {
  if (units === 'imperial') {
    const ksi = 0.1450377377;
    return [m[0], m[1],
      m[2] * ksi, m[3] * ksi, m[4],
      m[5] * 5/9,
      m[6] * 0.2248089431 / 35.3146667,
      m[7] * ksi, m[8] * ksi];
  }
  return m;
}

function setSheet(sheet) {
  const thead = document.querySelector('#sheet thead');
  const tbody = document.querySelector('#sheet tbody');
  thead.innerHTML = '';
  tbody.innerHTML = '';

  let headers = [];
  let rows = [];

  if (sheet === 'nodes') {
    headers = ['Node', `X (${labL()})`, `Y (${labL()})`, `Z (${labL()})`,
               'Support Type', 'DOF Range'];
    Object.entries(NODES).forEach(([id, c]) => {
      const s = SUPPORTS[id] || 'Free';
      const st = (Number(id) - 1) * 6 + 1, en = Number(id) * 6;
      rows.push([id, dL(c[0]), dL(c[1]), dL(c[2]), s, `${st} - ${en}`]);
    });
  } else if (sheet === 'members') {
    headers = ['Member', 'Node i', 'Node j', 'Type',
               `Length (${labL()})`, 'Beta (deg)', 'Section'];
    MEMBERS.forEach((m, i) => {
      const L = Math.hypot(
        NODES[m[1]][0] - NODES[m[0]][0],
        NODES[m[1]][1] - NODES[m[0]][1],
        NODES[m[1]][2] - NODES[m[0]][2]);
      const y1 = NODES[m[0]][1], y2 = NODES[m[1]][1];
      let t = 'Column';
      if (y1 === 0 && y2 === 0) t = 'Base Beam';
      else if (y1 === 6 && y2 === 6) t = 'Roof Beam';
      rows.push([i + 1, m[0], m[1], t, dL(L), m[2], MEMBER_SECTIONS[i]]);
    });
  } else if (sheet === 'sections') {
    headers = ['Name', 'Type',
               `A (${labA()})`, `Iy (${labI()})`, `Iz (${labI()})`, `J (${labI()})`,
               `Depth (${labL()})`, 'In Use'];
    const usage = {};
    MEMBER_SECTIONS.forEach(n => usage[n] = (usage[n] || 0) + 1);
    SECTIONS.forEach(s => {
      rows.push([s.name, s.type,
                 dA(s.A), dI(s.Iy), dI(s.Iz), dI(s.J), dL(s.d),
                 usage[s.name] || 0]);
    });
  } else if (sheet === 'supports') {
    headers = ['Node', 'Type', 'UX', 'UY', 'UZ', 'RX', 'RY', 'RZ'];
    Object.entries(SUPPORTS).forEach(([n, t]) => {
      const p = t === 'Pinned';
      rows.push([n, t, p ? 'R' : 'F', p ? 'R' : 'F', p ? 'R' : 'F', 'F', 'F', 'F']);
    });
  } else if (sheet === 'materials') {
    if (units === 'imperial') {
      headers = ['Category', 'Label', 'E (ksi)', 'G (ksi)', 'ν',
                 'α (1e-6/°F)', 'ρ (kip/ft³)', 'Fy (ksi)', 'Fu (ksi)'];
    } else {
      headers = ['Category', 'Label', 'E (MPa)', 'G (MPa)', 'ν',
                 'α (1e-6/°C)', 'ρ (kN/m³)', 'Fy (MPa)', 'Fu (MPa)'];
    }
    MATERIALS.forEach(m => rows.push(materialRowDisp(m)));
  } else if (sheet === 'loads') {
    headers = ['#', 'Node',
               `FX (${labF()})`, `FY (${labF()})`, `FZ (${labF()})`,
               `MX (${labM()})`, `MY (${labM()})`, `MZ (${labM()})`,
               'Delete'];
    LOADS.forEach(L => {
      rows.push({
        cells: [L.id, L.node,
                dF(L.fx), dF(L.fy), dF(L.fz),
                dM(L.mx), dM(L.my), dM(L.mz),
                '✕'],
        delId: L.id,
      });
    });
  } else if (sheet === 'disp') {
    headers = ['Node', 'DOF', `Value (${labD()} or rad)`];
    if (!RESULTS) rows.push(['—', '—', 'run analysis']);
    else {
      const dofNames = ['UX', 'UY', 'UZ', 'RX', 'RY', 'RZ'];
      for (const nid of RESULTS.nodeIds) {
        const i = RESULTS.idxMap[nid];
        for (let k = 0; k < 6; k++) {
          const v = (k < 3) ? dD(RESULTS.U[i * 6 + k]) : RESULTS.U[i * 6 + k];
          rows.push([nid, dofNames[k], v]);
        }
      }
    }
  } else if (sheet === 'react') {
    headers = ['Node',
               `FX (${labF()})`, `FY (${labF()})`, `FZ (${labF()})`,
               `MX (${labM()})`, `MY (${labM()})`, `MZ (${labM()})`];
    if (!RESULTS) rows.push(['—','—','—','—','—','—','—']);
    else {
      for (const nid of RESULTS.nodeIds) {
        const i = RESULTS.idxMap[nid];
        if (SUPPORTS[nid] === 'Free') continue;
        const R = [RESULTS.R[i*6],   RESULTS.R[i*6+1], RESULTS.R[i*6+2],
                   RESULTS.R[i*6+3], RESULTS.R[i*6+4], RESULTS.R[i*6+5]];
        rows.push([nid, dF(R[0]/1000), dF(R[1]/1000), dF(R[2]/1000),
                        dM(R[3]/1000), dM(R[4]/1000), dM(R[5]/1000)]);
      }
    }
  } else if (sheet === 'forces') {
    headers = ['Member', 'Node i', 'Node j', 'Section', 'End',
               `FX (${labF()})`, `FY (${labF()})`, `FZ (${labF()})`,
               `MX (${labM()})`, `MY (${labM()})`, `MZ (${labM()})`];
    if (!RESULTS) rows.push(['—','—','—','—','—','—','—','—','—','—','—']);
    else {
      for (const mr of RESULTS.members) {
        const Fi = mr.Fi.map(v => dF(v / 1000));
        const Fj = mr.Fj.map(v => dF(v / 1000));
        rows.push([mr.mid, mr.n1, mr.n2, mr.section, 'i', ...Fi]);
        rows.push([mr.mid, mr.n1, mr.n2, mr.section, 'j', ...Fj]);
      }
    }
  }

  const trh = document.createElement('tr');
  headers.forEach(h => {
    const th = document.createElement('th');
    th.textContent = h;
    trh.appendChild(th);
  });
  thead.appendChild(trh);

  rows.forEach((entry, ri) => {
    const row = entry && entry.cells ? entry.cells : entry;
    const delId = entry && entry.delId;
    const tr = document.createElement('tr');
    row.forEach((c, ci) => {
      const td = document.createElement('td');
      td.textContent = (typeof c === 'number') ? formatNum(c) : c;
      if (typeof c === 'number') td.classList.add('num');
      if (ri === 0 && ci === 0) td.classList.add('sel');
      if (headers[ci] === 'Delete') {
        td.classList.add('del');
        td.onclick = () => deleteLoad(delId);
      } else {
        td.onclick = () => {
          document.querySelectorAll('#sheet td.sel')
            .forEach(t => t.classList.remove('sel'));
          td.classList.add('sel');
        };
      }
      tr.appendChild(td);
    });
    tbody.appendChild(tr);
  });

  document.querySelectorAll('#dock-tabs button').forEach(b => {
    b.classList.toggle('active', b.dataset.sheet === sheet);
  });
}

document.querySelectorAll('#dock-tabs button').forEach(b => {
  b.onclick = () => setSheet(b.dataset.sheet);
});

function focusSheet(name) { setSheet(name); }

document.querySelectorAll('#ribbon-tabs button').forEach(b => {
  b.onclick = () => {
    document.querySelectorAll('#ribbon-tabs button')
      .forEach(x => x.classList.remove('active'));
    b.classList.add('active');
  };
});

function toggleGroup(id, el) {
  el.classList.toggle('open');
  const g = document.getElementById(id);
  if (g) g.classList.toggle('open');
}
document.querySelectorAll('#tree .node.leaf').forEach(n => {
  n.onclick = () => {
    document.querySelectorAll('#tree .node.sel')
      .forEach(x => x.classList.remove('sel'));
    n.classList.add('sel');
  };
});

/* ==================================================================
   6. THREE.JS VIEWER
   ================================================================== */
let scene, camera, renderer, controls;
let nodeMeshes = {};
let memberGroup, memberMeshes = [];
let loadGroup, deformedGroup;
let selectedNode = null;
let selectedMembers = new Set();
let showArrows = true;
let showDeformed = true;
const DEFORM_SCALE = 200;

function initViewer() {
  const container = document.getElementById('three-canvas');
  const w = container.clientWidth;
  const h = container.clientHeight;

  scene = new THREE.Scene();
  scene.background = new THREE.Color(0xffffff);

  camera = new THREE.PerspectiveCamera(45, w / h, 0.1, 200);
  camera.position.set(12, 11, 14);

  renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setPixelRatio(window.devicePixelRatio);
  renderer.setSize(w, h);
  container.appendChild(renderer.domElement);

  controls = new THREE.OrbitControls(camera, renderer.domElement);
  controls.target.set(3, 3, 3);
  controls.update();

  scene.add(new THREE.AmbientLight(0xffffff, 0.85));
  const d1 = new THREE.DirectionalLight(0xffffff, 0.6);
  d1.position.set(10, 15, 8); scene.add(d1);
  const d2 = new THREE.DirectionalLight(0xffffff, 0.35);
  d2.position.set(-8, -6, -10); scene.add(d2);

  const grid = new THREE.GridHelper(14, 28, 0xdddddd, 0xf0f0f0);
  grid.position.set(3, -0.01, 3);
  scene.add(grid);

  addGlobalAxes();

  memberGroup = new THREE.Group();
  scene.add(memberGroup);
  buildMemberTubes();

  Object.entries(NODES).forEach(([id, c]) => {
    const geo = new THREE.SphereGeometry(0.13, 20, 20);
    const mat = new THREE.MeshPhongMaterial({ color: 0xc00000 });
    const mesh = new THREE.Mesh(geo, mat);
    mesh.position.set(c[0], c[1], c[2]);
    mesh.userData.node = Number(id);
    scene.add(mesh);
    nodeMeshes[id] = mesh;
  });

  Object.entries(SUPPORTS).forEach(([id, t]) => {
    if (t !== 'Pinned') return;
    const [x, y, z] = NODES[id];
    const geo = new THREE.ConeGeometry(0.3, 0.5, 4);
    const mat = new THREE.MeshPhongMaterial({ color: 0x1e8b3a });
    const cone = new THREE.Mesh(geo, mat);
    cone.position.set(x, y - 0.35, z);
    cone.rotation.y = Math.PI / 4;
    scene.add(cone);
  });

  Object.entries(NODES).forEach(([id, c]) => {
    if (id === '8') return;
    const canvas = document.createElement('canvas');
    canvas.width = 64; canvas.height = 64;
    const ctx = canvas.getContext('2d');
    ctx.font = 'bold 40px Segoe UI';
    ctx.fillStyle = '#1b1b1f';
    ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
    ctx.fillText(id, 32, 32);
    const tex = new THREE.CanvasTexture(canvas);
    const mat = new THREE.SpriteMaterial({ map: tex, transparent: true });
    const sp = new THREE.Sprite(mat);
    sp.position.set(c[0] + 0.35, c[1] + 0.35, c[2] + 0.35);
    sp.scale.set(0.6, 0.6, 1);
    scene.add(sp);
  });

  loadGroup = new THREE.Group(); scene.add(loadGroup);
  deformedGroup = new THREE.Group(); scene.add(deformedGroup);

  renderer.domElement.addEventListener('click', onCanvasClick);

  window.addEventListener('resize', onResize);
  animate();
}

function buildMemberTubes() {
  while (memberGroup.children.length) {
    const c = memberGroup.children.pop();
    c.geometry?.dispose?.();
    c.material?.dispose?.();
  }
  memberMeshes = [];

  MEMBERS.forEach((mem, idx) => {
    const p1 = new THREE.Vector3(...NODES[mem[0]]);
    const p2 = new THREE.Vector3(...NODES[mem[1]]);
    const dir = new THREE.Vector3().subVectors(p2, p1);
    const len = dir.length();
    const isColumn = mem[2] === 90;
    const sec = getSection(MEMBER_SECTIONS[idx]);
    const radius = Math.max(0.02, sec.d / 4);

    const geo = new THREE.CylinderGeometry(radius, radius, len, 14, 1);
    const mat = new THREE.MeshPhongMaterial({
      color: isColumn ? 0x6b3fa0 : 0x3060c0, shininess: 40,
    });
    const tube = new THREE.Mesh(geo, mat);
    tube.position.copy(p1).add(dir.clone().multiplyScalar(0.5));
    tube.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0),
                                       dir.clone().normalize());
    tube.userData.member = idx;
    memberGroup.add(tube);
    memberMeshes.push(tube);
  });
  updateMemberHighlight();
}

function updateMemberHighlight() {
  memberMeshes.forEach((mesh, idx) => {
    const isCol = MEMBERS[idx][2] === 90;
    if (selectedMembers.has(idx)) {
      mesh.material.color.setHex(0xf0c000);
    } else {
      mesh.material.color.setHex(isCol ? 0x6b3fa0 : 0x3060c0);
    }
  });
}

function addGlobalAxes() {
  const alen = 7.5;
  const ax = new THREE.ArrowHelper(new THREE.Vector3(1, 0, 0),
                                   new THREE.Vector3(0, 0, 0), alen,
                                   0x000000, 0.35, 0.2);
  const ay = new THREE.ArrowHelper(new THREE.Vector3(0, 1, 0),
                                   new THREE.Vector3(0, 0, 0), alen,
                                   0x000000, 0.35, 0.2);
  const az = new THREE.ArrowHelper(new THREE.Vector3(0, 0, 1),
                                   new THREE.Vector3(0, 0, 0), alen,
                                   0x000000, 0.35, 0.2);
  scene.add(ax, ay, az);
}

function onResize() {
  const container = document.getElementById('three-canvas');
  const w = container.clientWidth, h = container.clientHeight;
  if (!w || !h) return;
  camera.aspect = w / h;
  camera.updateProjectionMatrix();
  renderer.setSize(w, h);
}

function animate() {
  requestAnimationFrame(animate);
  controls.update();
  renderer.render(scene, camera);
}

function zoomView(factor) {
  const dir = new THREE.Vector3().subVectors(camera.position, controls.target);
  dir.multiplyScalar(1 / factor);
  camera.position.copy(controls.target).add(dir);
  controls.update();
}
function resetView() {
  camera.position.set(12, 11, 14);
  controls.target.set(3, 3, 3);
  controls.update();
}

function onCanvasClick(ev) {
  const rect = renderer.domElement.getBoundingClientRect();
  const mouse = new THREE.Vector2(
    ((ev.clientX - rect.left) / rect.width) * 2 - 1,
    -((ev.clientY - rect.top) / rect.height) * 2 + 1,
  );
  const ray = new THREE.Raycaster();
  ray.setFromCamera(mouse, camera);

  const nodeHits = ray.intersectObjects(Object.values(nodeMeshes));
  if (nodeHits.length) {
    selectedMembers.clear();
    updateMemberHighlight();
    selectNode(nodeHits[0].object.userData.node);
    return;
  }

  const memHits = ray.intersectObjects(memberMeshes);
  if (memHits.length) {
    const idx = memHits[0].object.userData.member;
    if (ev.shiftKey) {
      if (selectedMembers.has(idx)) selectedMembers.delete(idx);
      else                          selectedMembers.add(idx);
    } else {
      selectedMembers.clear();
      selectedMembers.add(idx);
    }
    selectNode(null);
    updateMemberHighlight();
    syncSectionDropdown();
    updateSelectionOverlay();
    return;
  }

  selectedMembers.clear();
  selectNode(null);
  updateMemberHighlight();
  updateSelectionOverlay();
}

function selectNode(nid) {
  selectedNode = nid;
  Object.entries(nodeMeshes).forEach(([id, mesh]) => {
    const sel = Number(id) === nid;
    mesh.material.color.setHex(sel ? 0xf0c000 : 0xc00000);
    mesh.scale.setScalar(sel ? 1.35 : 1);
  });
  updateSelectionOverlay();
}

function updateSelectionOverlay() {
  const el = document.getElementById('ov-sel');
  if (selectedNode) {
    el.textContent = `Node ${selectedNode}`;
    return;
  }
  if (selectedMembers.size === 0) {
    el.textContent = '—';
  } else if (selectedMembers.size === 1) {
    const idx = [...selectedMembers][0];
    el.textContent = `Member ${idx + 1}`;
  } else {
    const list = [...selectedMembers].map(i => i + 1).sort((a,b)=>a-b).join(', ');
    el.textContent = `Members ${list}`;
  }
}

function syncSectionDropdown() {
  if (selectedMembers.size === 1) {
    const idx = [...selectedMembers][0];
    currentSection = MEMBER_SECTIONS[idx];
    document.getElementById('section-select').value = currentSection;
  }
}

function drawLoads() {
  while (loadGroup.children.length) {
    const c = loadGroup.children.pop();
    c.geometry?.dispose?.();
    c.material?.dispose?.();
  }
  const nl = getNodalLoads();
  for (const [nid, forces] of Object.entries(nl)) {
    const [fx, fy, fz] = forces;
    const mag = Math.hypot(fx, fy, fz);
    if (mag < 1e-9) continue;
    const dir = new THREE.Vector3(fx, fy, fz).normalize();
    const len = Math.min(2.5, 0.9 + Math.log10(mag + 1) * 0.7);
    const anchor = new THREE.Vector3(...NODES[nid]);
    const origin = anchor.clone().sub(dir.clone().multiplyScalar(len));
    const color = fy < 0 ? 0xd02020 : (mag > 0 ? 0xe08000 : 0xd02020);
    const arrow = new THREE.ArrowHelper(dir, origin, len, color, 0.28, 0.17);
    loadGroup.add(arrow);
  }
  loadGroup.visible = showArrows;
}

function drawDeformed() {
  while (deformedGroup.children.length) {
    const c = deformedGroup.children.pop();
    c.geometry?.dispose?.();
    c.material?.dispose?.();
  }
  if (!RESULTS) return;
  const U = RESULTS.U;
  const idxMap = RESULTS.idxMap;
  MEMBERS.forEach(mem => {
    const n1 = mem[0], n2 = mem[1];
    const p1 = new THREE.Vector3(...NODES[n1]);
    const p2 = new THREE.Vector3(...NODES[n2]);
    const i1 = idxMap[n1], i2 = idxMap[n2];
    const d1 = new THREE.Vector3(U[i1*6], U[i1*6+1], U[i1*6+2]).multiplyScalar(DEFORM_SCALE);
    const d2 = new THREE.Vector3(U[i2*6], U[i2*6+1], U[i2*6+2]).multiplyScalar(DEFORM_SCALE);
    const q1 = p1.clone().add(d1);
    const q2 = p2.clone().add(d2);

    const geo = new THREE.BufferGeometry().setFromPoints([q1, q2]);
    const mat = new THREE.LineDashedMaterial({
      color: 0xe06020, dashSize: 0.22, gapSize: 0.14, linewidth: 2,
    });
    const line = new THREE.Line(geo, mat);
    line.computeLineDistances();
    deformedGroup.add(line);
  });
  deformedGroup.visible = showDeformed;
}

function toggleArrows() { showArrows = !showArrows; loadGroup.visible = showArrows; }
function toggleDeformed() { showDeformed = !showDeformed; deformedGroup.visible = showDeformed; }

/* ==================================================================
   7. ANALYSIS + UI WIRING
   ================================================================== */
function runAnalysis() {
  const s = document.getElementById('view-status');
  const sm = document.getElementById('status-msg');
  s.textContent = 'Solving …';
  sm.textContent = 'Solving …';
  try {
    RESULTS = solveModel();
  } catch (e) {
    s.textContent = 'Solve failed: ' + e.message;
    sm.textContent = 'Analysis failed';
    return;
  }

  let maxU = 0;
  for (const v of RESULTS.U) if (Math.abs(v) > maxU) maxU = Math.abs(v);
  let maxReact = 0;
  for (const v of RESULTS.R) if (Math.abs(v) > maxReact) maxReact = Math.abs(v);

  const maxUdisp = dD(maxU).toExponential(3);
  const maxRdisp = dF(maxReact / 1000).toFixed(3);
  s.textContent = `Solved ✓  ·  max |U| = ${maxUdisp} ${labD()}  ·  max |R| = ${maxRdisp} ${labF()}`;
  sm.textContent = 'Analysis complete — no errors';

  drawLoads();
  drawDeformed();
  updateOverlay();
  refreshCurrentSheet();
}

function refreshCurrentSheet() {
  const active = document.querySelector('#dock-tabs button.active');
  if (active) setSheet(active.dataset.sheet);
}

function updateOverlay() {
  document.getElementById('ov-loads').textContent = LOADS.length;
  document.getElementById('sb-loads').textContent = LOADS.length;
  document.getElementById('tree-loads').textContent = `Joint Loads (${LOADS.length})`;
  updateMaterialLabels();
  updateSelectionOverlay();
}

/* ---------- Load dialog ---------- */
function openLoadDialog() {
  const node = selectedNode || 5;
  const defFy = units === 'imperial' ? -22.48 : -100;
  document.getElementById('dlg-node').value = node;
  document.getElementById('dlg-fx').value = 0;
  document.getElementById('dlg-fy').value = defFy;
  document.getElementById('dlg-fz').value = 0;
  document.getElementById('dlg-mx').value = 0;
  document.getElementById('dlg-my').value = 0;
  document.getElementById('dlg-mz').value = 0;
  refreshUnitLabels();
  document.getElementById('load-dialog').style.display = 'flex';
}

function refreshUnitLabels() {
  const f = labF(), m = labM();
  document.getElementById('lbl-fx').textContent = `FX (${f}):`;
  document.getElementById('lbl-fy').textContent = `FY (${f}):`;
  document.getElementById('lbl-fz').textContent = `FZ (${f}):`;
  document.getElementById('lbl-mx').textContent = `MX (${m}):`;
  document.getElementById('lbl-my').textContent = `MY (${m}):`;
  document.getElementById('lbl-mz').textContent = `MZ (${m}):`;
}

function closeLoadDialog() {
  document.getElementById('load-dialog').style.display = 'none';
}

function confirmLoadDialog() {
  const n = parseInt(document.getElementById('dlg-node').value, 10);
  if (!(n >= 1 && n <= 8)) { alert('Node must be between 1 and 8.'); return; }
  const fx = iF(parseFloat(document.getElementById('dlg-fx').value) || 0);
  const fy = iF(parseFloat(document.getElementById('dlg-fy').value) || 0);
  const fz = iF(parseFloat(document.getElementById('dlg-fz').value) || 0);
  const mx = iM(parseFloat(document.getElementById('dlg-mx').value) || 0);
  const my = iM(parseFloat(document.getElementById('dlg-my').value) || 0);
  const mz = iM(parseFloat(document.getElementById('dlg-mz').value) || 0);

  LOADS.push({ id: nextLoadId++, node: n, fx, fy, fz, mx, my, mz });
  closeLoadDialog();
  focusSheet('loads');
  runAnalysis();
}

function deleteLoad(id) {
  LOADS = LOADS.filter(L => L.id !== id);
  refreshCurrentSheet();
  runAnalysis();
}

function clearLoads() {
  if (!confirm('Remove all joint loads?')) return;
  LOADS = [];
  refreshCurrentSheet();
  runAnalysis();
}

/* ==================================================================
   8. MATERIAL + UNITS + SECTION SWITCHING
   ================================================================== */
function populateMaterialSelect() {
  const sel = document.getElementById('mat-select');
  sel.innerHTML = '';
  MATERIALS.forEach(m => {
    const opt = document.createElement('option');
    opt.value = m[1];
    opt.textContent = `${m[1]}  ·  ${m[0]}`;
    sel.appendChild(opt);
  });
  sel.value = currentMaterial;
}

function populateSectionSelect() {
  const sel = document.getElementById('section-select');
  sel.innerHTML = '';
  SECTIONS.forEach(s => {
    const opt = document.createElement('option');
    opt.value = s.name;
    opt.textContent = s.name + '  ·  ' + s.type;
    sel.appendChild(opt);
  });
  sel.value = currentSection;
}

function onMaterialChange(label) {
  applyMaterial(label);
  runAnalysis();
}

function onSectionChange(name) {
  currentSection = name;
  const sec = getSection(name);
  document.getElementById('tree-sec').textContent =
    `${name}  (A=${dA(sec.A).toExponential(2)} ${labA()})`;
}

function applySectionToSelected() {
  if (selectedMembers.size === 0) {
    alert('No members selected. Click a member in the 3D view to select it,\n' +
          'or use "All" to apply to every member.');
    return;
  }
  const idxs = [...selectedMembers];
  idxs.forEach(i => MEMBER_SECTIONS[i] = currentSection);
  buildMemberTubes();
  refreshCurrentSheet();
  runAnalysis();
}

function applySectionToAll() {
  const sec = getSection(currentSection);
  if (!confirm(`Apply section ${currentSection} to ALL 12 members?`)) return;
  MEMBER_SECTIONS = MEMBERS.map(() => currentSection);
  buildMemberTubes();
  refreshCurrentSheet();
  runAnalysis();
}

function onUnitsChange(val) {
  units = val;
  document.getElementById('unit-select').value = units;
  document.getElementById('sb-units').textContent = UC[units].name;
  updateMaterialLabels();
  refreshUnitLabels();
  refreshCurrentSheet();
  updateOverlay();
  if (RESULTS) {
    let maxU = 0, maxReact = 0;
    for (const v of RESULTS.U) if (Math.abs(v) > maxU) maxU = Math.abs(v);
    for (const v of RESULTS.R) if (Math.abs(v) > maxReact) maxReact = Math.abs(v);
    const maxUdisp = dD(maxU).toExponential(3);
    const maxRdisp = dF(maxReact / 1000).toFixed(3);
    document.getElementById('view-status').textContent =
      `Solved ✓  ·  max |U| = ${maxUdisp} ${labD()}  ·  max |R| = ${maxRdisp} ${labF()}`;
  }
}

/* ==================================================================
   9. BOOT
   ================================================================== */
window.addEventListener('load', () => {
  initViewer();
  populateMaterialSelect();
  populateSectionSelect();
  applyMaterial(currentMaterial);
  onSectionChange(currentSection);
  document.getElementById('unit-select').value = units;
  document.getElementById('sb-units').textContent = UC[units].name;
  refreshUnitLabels();
  setSheet('loads');
  runAnalysis();
  updateOverlay();
});
</script>
</body>
</html>
"""


# ============================================================================
# LAUNCHER
# ============================================================================
def write_html_to_disk():
    folder = os.path.join(tempfile.gettempdir(), "structural_solver")
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, "structural_solver.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(HTML)
    return path


def launch_native_window(html_path):
    try:
        import webview  # noqa
    except ImportError:
        return False
    try:
        webview.create_window(
            "Structural Solver  ·  rev3.r3d",
            url=f"file:///{html_path.replace(os.sep, '/')}",
            width=1420, height=900, resizable=True,
        )
        webview.start()
        return True
    except Exception as e:
        print(f"[pywebview] failed: {e}")
        return False


def launch_browser(html_path):
    url = f"file:///{html_path.replace(os.sep, '/')}"
    print(f"Opening Structural Solver mock in default browser:\n  {url}")
    webbrowser.open(url)


def main():
    html_path = write_html_to_disk()
    print(f"HTML written to: {html_path}")
    if "--browser" in sys.argv:
        launch_browser(html_path)
        return
    if not launch_native_window(html_path):
        print("pywebview not available – falling back to default browser.")
        print("(Install for native window: pip install pywebview)")
        launch_browser(html_path)


if __name__ == "__main__":
    main()