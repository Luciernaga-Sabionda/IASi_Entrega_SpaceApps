export const Spinner = {
  show(){ document.getElementById('spinner').hidden = false; },
  hide(){ document.getElementById('spinner').hidden = true; }
};

export function toast(msg, type='info', timeout=4500){
  const box = document.getElementById('toasts');
  const el = document.createElement('div');
  el.className = `toast ${type}`;
  el.textContent = msg;
  box.appendChild(el);
  setTimeout(()=> el.remove(), timeout);
}

export async function safeFetchJSON(url, {schema='unknown', requiredKeys=[]} = {}) {
  try {
    const res = await fetch(url, {cache:'no-store'});
    if (!res.ok) throw new Error(`HTTP ${res.status} en ${url}`);
    const data = await res.json();
    if (requiredKeys.length) {
      const missing = requiredKeys.filter(k => !(k in data));
      if (missing.length) throw new Error(`Esquema ${schema} inválido. Faltan: ${missing.join(', ')}`);
    }
    return { ok:true, data };
  } catch (err) {
    return { ok:false, error: err instanceof Error ? err.message : String(err) };
  }
}

// Helper to build headers including Authorization token if present
export function buildAuthHeaders(extra = {}) {
  const tokenInput = document.getElementById('serverToken')
  const headers = Object.assign({}, extra)
  if (tokenInput && tokenInput.value && tokenInput.value.trim() !== '') {
    headers['Authorization'] = `Bearer ${tokenInput.value.trim()}`
  }
  return headers
}
