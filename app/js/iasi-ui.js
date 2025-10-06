import { Spinner, toast, safeFetchJSON, buildAuthHeaders } from "./fetch-helpers.js";

let TH = { observation: 0.50, caution_min: 0.50, caution_max: 0.69, alert: 0.70 };
const COLORS = { iasi:"#72d1ff", A:"#8be989", R:"#ffd36a", D:"#ff9ee5", M:"#c8b6ff", S:"#ffa07a", grid:"#1a2433", text:"#9fb0c0" };
let DATA = { events:{} };
let map, aoiLayer, epicenterMarker, lineChart, barsChart;

function fmt(x,d=2){ return (x??0).toFixed(d); }
function stateFromScore(x){ if(x>=TH.alert) return {name:"Alerta",cls:"alert"}; if(x>=TH.caution_min && x<=TH.caution_max) return {name:"Precaución",cls:"caution"}; return {name:"Observación",cls:"obs"}; }

export function initMap(){
  map = L.map('map', { zoomControl:true, scrollWheelZoom:false });
  const tiles = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { attribution: '&copy; OpenStreetMap' });
  tiles.addTo(map); map.setView([0,-75],3);
}

export async function drawAOI(meta){
  if (aoiLayer){ aoiLayer.remove(); aoiLayer=null; }
  if (epicenterMarker){ epicenterMarker.remove(); epicenterMarker=null; }
  if (typeof meta.lat==='number' && typeof meta.lon==='number'){
    epicenterMarker = L.circleMarker([meta.lat, meta.lon], { radius:6, color:'#ff7b72', weight:2, fillColor:'#ff7b72', fillOpacity:0.8 }).addTo(map).bindTooltip(meta.name||'Evento');
  }
  // Prefer in-memory AOI (meta.aoi_geo) if provided (uploader local)
  if (meta.aoi_geo) {
    try {
      aoiLayer = L.geoJSON(meta.aoi_geo, { style:{color:'#72d1ff', weight:1, fillOpacity:0.1} }).addTo(map);
      map.fitBounds(aoiLayer.getBounds(), { padding:[10,10] });
      return;
    } catch(e){ toast('AOI local inválido','error'); }
  }
  if (meta.aoi_path){
    const gj = await safeFetchJSON(meta.aoi_path, {schema:'geojson'});
    if (gj.ok){
      try {
        aoiLayer = L.geoJSON(gj.data, { style:{color:'#72d1ff', weight:1, fillOpacity:0.1} }).addTo(map);
        map.fitBounds(aoiLayer.getBounds(), { padding:[10,10] });
        return;
      } catch(e){ toast(`AOI inválido: ${meta.aoi_path}`,'error'); }
    } else {
      toast(`No se pudo cargar AOI: ${gj.error}`,'error');
    }
  }
  if (epicenterMarker){ map.setView([meta.lat, meta.lon],5); } else { map.setView([0,-75],3); }
}

export async function loadEvent(name){
  // First try to load from remote server API (useful when the static site is hosted separately).
  try{
    const headers = buildAuthHeaders();
    const apiUrl = `${SERVER_BASE}/get_iasi/${encodeURIComponent(name)}`;
    const r = await fetch(apiUrl, { headers });
    if (r.ok){
      const j = await r.json();
      if (j.ok && j.data) return j.data;
    }
  }catch(e){ /* ignore and fallback to static/demo */ }

  // Fallback: try to load a static copy under outputs/indices (local demo mode)
  const path = `../outputs/indices/${name}/iasi.json`;
  const res = await safeFetchJSON(path, { schema:'iasi.json', requiredKeys:['meta','timeline','metrics'] });
  if (res.ok) return res.data;
  toast(`No se pudo cargar iasi.json de ${name}: ${res.error}. Modo demo.`, 'error');
  const today=new Date(), days=30, tl=[];
  for(let i=days-1;i>=0;i--){
    const d=new Date(today); d.setDate(today.getDate()-i);
    const iso=d.toISOString().slice(0,10);
    const A=0.3+0.2*Math.sin(i/5);
    const R=0.4+0.15*Math.cos(i/6);
    const D=0.2+0.5*Math.max(0,Math.sin(i/9));
    const M=0.2+0.3*Math.random()*0.2;
    const S=0.3+0.2*Math.cos(i/7);
    const IASi=0.25*A+0.20*R+0.25*D+0.15*M+0.15*S;
    tl.push({date:iso,A,R,D,M,S,IASi});
  }
  return { meta:{name,lat:-35.0,lon:-72.5,aoi_path:"../config/aoi.geojson"}, timeline:tl, metrics:{ "7":{auc_pr:0.58,f1:0.50,false_alarm_pm:1.5,lead_time_days:3}, "14":{auc_pr:0.62,f1:0.52,false_alarm_pm:1.4,lead_time_days:3}, "30":{auc_pr:0.55,f1:0.49,false_alarm_pm:1.8,lead_time_days:2} } };
}

// override thresholds from meta if provided
function applyMetaThresholds(meta){
  try{
    if(meta && meta.thresholds){
      const t = meta.thresholds;
      if(typeof t.observation !== 'undefined') TH.observation = +t.observation;
      if(typeof t.caution_min !== 'undefined') TH.caution_min = +t.caution_min;
      if(typeof t.caution_max !== 'undefined') TH.caution_max = +t.caution_max;
      if(typeof t.alert !== 'undefined') TH.alert = +t.alert;
    }
  }catch(e){ console.warn('No se pudieron aplicar thresholds del meta', e); }
}

export function buildLine(ctx, timeline){
  const labels = timeline.map(d=>d.date);
  const data = timeline.map(d=>d.IASi);
  const thObs = Array(labels.length).fill(TH.observation);
  const thAlert = Array(labels.length).fill(TH.alert);
  if (window.lineChart) window.lineChart.destroy();
  window.lineChart = new Chart(ctx, {
    type:'line',
    data: { labels, datasets: [
      { label:'IASi', data, borderColor:COLORS.iasi, backgroundColor:'rgba(114,209,255,0.18)', fill:true, tension:0.25, pointRadius:0 },
      { label:'0.50', data: thObs, borderColor:'#8be989', borderDash:[6,6], pointRadius:0 },
      { label:'0.70', data: thAlert, borderColor:'#ff7b72', borderDash:[6,6], pointRadius:0 }
    ]},
    options:{ responsive:true, scales:{ x:{ grid:{color:COLORS.grid}, ticks:{color:COLORS.text} }, y:{ min:0, max:1, grid:{color:COLORS.grid}, ticks:{color:COLORS.text} } }, plugins:{ legend:{ labels:{ color:COLORS.text } } } }
  });
}

export function buildBars(ctx, last){
  const labels=['A','R','D','M','S'];
  const vals=[last.A,last.R,last.D,last.M,last.S].map(v=>+(v??0));
  const colors=[COLORS.A,COLORS.R,COLORS.D,COLORS.M,COLORS.S];
  if (window.barsChart) window.barsChart.destroy();
  window.barsChart = new Chart(ctx, {
    type:'bar',
    data:{ labels, datasets:[{ label:'Contribución normalizada', data:vals, backgroundColor:colors }] },
    options:{ indexAxis:'y', scales:{ x:{min:0,max:1}, y:{} }, plugins:{ legend:{display:false} } }
  });
}

export async function render(){
  Spinner.show();
  try {
    const eventName = document.getElementById('eventSelect').value;
    const win = document.getElementById('windowSelect').value;
    if (!DATA.events[eventName]) DATA.events[eventName] = await loadEvent(eventName);
    const ev = DATA.events[eventName];
    // apply thresholds from iasi.json meta if present
    applyMetaThresholds(ev.meta||{});
    // apply weights display
    try{
      const w = (ev.meta && ev.meta.weights) || { alpha:0.25,beta:0.2,gamma:0.25,delta:0.15,epsilon:0.15 };
      document.getElementById('w_alpha').textContent = (w.alpha!=null?parseFloat(w.alpha).toFixed(2):'-');
      document.getElementById('w_beta').textContent = (w.beta!=null?parseFloat(w.beta).toFixed(2):'-');
      document.getElementById('w_gamma').textContent = (w.gamma!=null?parseFloat(w.gamma).toFixed(2):'-');
      document.getElementById('w_delta').textContent = (w.delta!=null?parseFloat(w.delta).toFixed(2):'-');
      document.getElementById('w_epsilon').textContent = (w.epsilon!=null?parseFloat(w.epsilon).toFixed(2):'-');
    }catch(e){ /* ignore */ }
    const tl = Array.isArray(ev.timeline) ? ev.timeline : [];
    await drawAOI(ev.meta||{});
    if (!tl.length){ toast('Timeline vacía o inválida.','error'); return; }
    buildLine(document.getElementById('line'), tl);
    const last = tl[tl.length-1];
    buildBars(document.getElementById('bars'), last);
    const st = stateFromScore(last.IASi??0);
    const badge = document.getElementById('stateBadge');
    badge.textContent = st.name; badge.className = `badge ${st.cls}`;
    document.getElementById('kpiScore').textContent = fmt(last.IASi??0,2);
    document.getElementById('kpiState').textContent = st.name;
    document.getElementById('kpiDate').textContent = last.date||'—';
    document.getElementById('kpiWin').textContent = `${win}d`;
    const m = (ev.metrics && ev.metrics[win]) || {};
    document.getElementById('kpiPR').textContent = m.auc_pr!=null?fmt(m.auc_pr,2):'—';
    document.getElementById('kpiF1').textContent = m.f1!=null?fmt(m.f1,2):'—';
    document.getElementById('kpiFA').textContent = m.false_alarm_pm!=null?fmt(m.false_alarm_pm,2):'—';
    document.getElementById('kpiLT').textContent = m.lead_time_days!=null?fmt(m.lead_time_days,0):'—';
  } finally { Spinner.hide(); }
}

export function attachUI(){
  document.getElementById('eventSelect').addEventListener('change', render);
  document.getElementById('windowSelect').addEventListener('change', render);

  // Local uploads already handled by module
  document.getElementById('u_iasi').addEventListener('change', async (ev) => {
    const f = ev.target.files && ev.target.files[0]; if(!f) return;
    try{
      const txt = await f.text(); const data = JSON.parse(txt);
      if(data && data.meta && data.meta.name){ DATA.events[data.meta.name]=data; toast(`Cargado iasi.json local: ${data.meta.name}`,'info'); document.getElementById('eventSelect').value = data.meta.name; await render(); }
      else toast('iasi.json inválido: falta meta.name','error');
    } catch(e){ toast('Error parseando iasi.json: '+e.message,'error'); }
  });

  document.getElementById('u_aoi').addEventListener('change', async (ev) => {
    const f = ev.target.files && ev.target.files[0]; if(!f) return;
    try{
      const txt = await f.text(); const gj = JSON.parse(txt);
      const cur = document.getElementById('eventSelect').value;
      if(!DATA.events[cur]) DATA.events[cur] = { meta:{name:cur}, timeline:[], metrics:{} };
      DATA.events[cur].meta = DATA.events[cur].meta || {};
      DATA.events[cur].meta.aoi_geo = gj;
      toast(`AOI cargado localmente para ${cur}`,'info'); await render();
    } catch(e){ toast('Error parseando AOI GeoJSON: '+e.message,'error'); }
  });

  // Server interactions
  document.getElementById('btnPublish').addEventListener('click', postIasiToServer);
  document.getElementById('btnPublishAOI').addEventListener('click', postAOIToServer);
  document.getElementById('btnListIdx').addEventListener('click', listIndicesFromServer);
  document.getElementById('btnReloadSrv').addEventListener('click', reloadFromServer);
}

// Server helpers: use window.SERVER_BASE if set by the hosting page (see index.html)
const SERVER_BASE = (typeof window !== 'undefined' && window.SERVER_BASE) ? window.SERVER_BASE : 'http://127.0.0.1:5001';

async function postIasiToServer(){
  const cur = document.getElementById('eventSelect').value; const data = DATA.events[cur];
  if(!data){ toast('No hay iasi.json cargado en memoria para publicar','error'); return; }
  try{ Spinner.show(); const headers = Object.assign({'Content-Type':'application/json'}, buildAuthHeaders());
    const res = await fetch(`${SERVER_BASE}/upload_iasi`, { method:'POST', headers, body: JSON.stringify(data) });
    const j = await res.json(); if(j.ok){ toast('Publicado iasi.json en servidor','info'); if(j.name){ const sel=document.getElementById('eventSelect'); if(!Array.from(sel.options).some(o=>o.value===j.name)) sel.add(new Option(j.name,j.name)); } }
    else toast('Error publicando: '+(j.error||res.statusText),'error');
  }catch(e){ toast('Error de red al publicar iasi.json: '+e.message,'error'); }
  finally{ Spinner.hide(); }
}

async function postAOIToServer(){
  const inp = document.getElementById('u_aoi'); const f = inp.files && inp.files[0]; if(!f){ toast('Selecciona un archivo AOI antes de publicar','error'); return; }
  const form = new FormData(); form.append('aoi', f); form.append('name', document.getElementById('eventSelect').value || 'uploaded');
  try{ Spinner.show(); const headers = buildAuthHeaders(); const res = await fetch(`${SERVER_BASE}/upload_aoi`, { method:'POST', body: form, headers }); const j = await res.json(); if(j.ok) toast('AOI publicado en '+j.path,'info'); else toast('Error AOI: '+(j.error||res.statusText),'error'); }
  catch(e){ toast('Error de red al publicar AOI: '+e.message,'error'); }
  finally{ Spinner.hide(); }
}

async function listIndicesFromServer(){
  try{ Spinner.show(); const headers = buildAuthHeaders(); const res = await fetch(`${SERVER_BASE}/list_indices`, { headers }); const j = await res.json(); if(j.ok){ const idx=j.indices||[]; toast('Índices en servidor: '+idx.join(', '),'info',8000); const sel=document.getElementById('eventSelect'); idx.forEach(n=>{ if(!Array.from(sel.options).some(o=>o.value===n)) sel.add(new Option(n,n)); }); } else toast('Error listando índices: '+(j.error||res.statusText),'error'); }
  catch(e){ toast('Error de red listando índices: '+e.message,'error'); }
  finally{ Spinner.hide(); }
}

async function reloadFromServer(){
  const sel = document.getElementById('eventSelect'); const name = sel.value; if(!name) return toast('Seleccione un índice para recargar','error');
  try{ Spinner.show(); const headers = buildAuthHeaders(); const res = await fetch(`${SERVER_BASE}/get_iasi/${encodeURIComponent(name)}`, { headers }); const j = await res.json(); if(j.ok){ DATA.events[name] = j.data || j; toast('Recargado desde servidor: '+name,'info'); await render(); } else toast('Error recargando: '+(j.error||res.statusText),'error'); }
  catch(e){ toast('Error de red recargando índice: '+e.message,'error'); }
  finally{ Spinner.hide(); }
}

// Init on load
window.addEventListener('DOMContentLoaded', async () => { initMap(); attachUI(); await render(); });

// Server status polling
async function pollServerStatus(){
  const base = 'http://127.0.0.1:5001';
  try{
    const h = await fetch(base + '/health');
    if(h.ok){ document.getElementById('serverToken').style.borderColor = '#8be989'; }
    else { document.getElementById('serverToken').style.borderColor = '#ffd36a'; }
  }catch(e){ document.getElementById('serverToken').style.borderColor = '#ff7b72'; }
  try{
    const headers = buildAuthHeaders();
    const s = await fetch(base + '/status', { headers });
    if(s.ok){ const j = await s.json(); if(j.ok && j.status){ const st=j.status; let el=document.getElementById('serverStatus'); if(!el){ el=document.createElement('div'); el.id='serverStatus'; document.querySelector('.toolbar').appendChild(el);} el.textContent = `inbox: processed=${st.processed||0} invalid=${st.invalid||0} queued=${st.queued||0}`; }
    }
  }catch(e){ /* ignore */ }
}
setInterval(pollServerStatus, 10000);
setTimeout(pollServerStatus, 2000);
