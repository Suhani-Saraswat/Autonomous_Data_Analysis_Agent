async function req(url, opts) {
  const r = await fetch(url, opts);
  if (!r.ok) {
    let message = `Request failed (${r.status})`;
    try { message = (await r.json()).detail || message; } catch { try { message = await r.text(); } catch {} }
    throw new Error(message);
  }
  return r;
}
export async function getDatasets(){return (await req('/api/datasets')).json()}
export async function getProfile(dataset){return (await req('/api/profile?dataset='+encodeURIComponent(dataset))).json()}
export async function getPreview(dataset){return (await req('/api/preview?dataset='+encodeURIComponent(dataset)+'&rows=12')).json()}
export async function analyze(query,dataset){return (await req('/api/analyze',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({query,dataset})})).json()}
export async function uploadDataset(file){const f=new FormData();f.append('file',file);return (await req('/api/upload',{method:'POST',body:f})).json()}
export async function refreshLive(){return (await req('/api/live/refresh',{method:'POST'})).json()}
export async function exportReport(query,dataset){const r=await req('/api/report',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({query,dataset})});return r.blob()}
export async function exportPdfReport(query,dataset){const r=await req('/api/report/pdf',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({query,dataset})});return r.blob()}
