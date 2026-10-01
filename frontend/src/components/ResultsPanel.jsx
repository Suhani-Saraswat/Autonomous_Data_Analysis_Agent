import {useMemo, useState} from 'react';
import {exportPdfReport, exportReport} from '../services/api';

function downloadBlob(blob, name){
  const u=URL.createObjectURL(blob); const a=document.createElement('a'); a.href=u; a.download=name; document.body.appendChild(a); a.click(); a.remove(); setTimeout(()=>URL.revokeObjectURL(u),1000);
}

function BarChart({labels=[], values=[]}){
  const width=760, height=300, pad={l:58,r:18,t:28,b:62};
  const max=Math.max(...values.map(v=>Math.abs(Number(v)||0)),1);
  const step=(width-pad.l-pad.r)/Math.max(labels.length,1); const bw=Math.max(22,step*.62);
  return <div className="svg-chart-wrap"><svg viewBox={`0 0 ${width} ${height}`} className="analysis-svg" role="img" aria-label="Bar chart">
    {[0,.25,.5,.75,1].map((p,i)=><g key={i}><line x1={pad.l} x2={width-pad.r} y1={pad.t+(height-pad.t-pad.b)*p} y2={pad.t+(height-pad.t-pad.b)*p} className="grid-line"/><text x={pad.l-8} y={pad.t+(height-pad.t-pad.b)*p+3} textAnchor="end" className="axis-text">{(max*(1-p)).toLocaleString(undefined,{notation:'compact',maximumFractionDigits:1})}</text></g>)}
    {labels.map((label,i)=>{const val=Number(values[i])||0;const h=(Math.abs(val)/max)*(height-pad.t-pad.b);const x=pad.l+i*step+(step-bw)/2;const y=height-pad.b-h;return <g key={`${label}-${i}`}><rect x={x} y={y} width={bw} height={h} rx="5" className="chart-bar"/><text x={x+bw/2} y={height-pad.b+18} textAnchor="middle" className="axis-text">{String(label).slice(0,14)}</text><text x={x+bw/2} y={Math.max(15,y-6)} textAnchor="middle" className="value-text">{val.toLocaleString(undefined,{notation:'compact',maximumFractionDigits:1})}</text></g>})}
  </svg></div>
}

function LineChart({labels=[], values=[]}){
  const width=760, height=300, pad={l:58,r:18,t:28,b:62}; const max=Math.max(...values.map(v=>Number(v)||0),1); const min=Math.min(...values.map(v=>Number(v)||0),0); const span=Math.max(max-min,1);
  const pts=values.map((v,i)=>{const x=pad.l+(i/Math.max(values.length-1,1))*(width-pad.l-pad.r);const y=pad.t+(1-(Number(v)-min)/span)*(height-pad.t-pad.b);return [x,y]});
  const path=pts.map((p,i)=>(i?'L':'M')+` ${p[0]} ${p[1]}`).join(' ');
  return <div className="svg-chart-wrap"><svg viewBox={`0 0 ${width} ${height}`} className="analysis-svg" role="img" aria-label="Line chart">
    {[0,.25,.5,.75,1].map((p,i)=><g key={i}><line x1={pad.l} x2={width-pad.r} y1={pad.t+(height-pad.t-pad.b)*p} y2={pad.t+(height-pad.t-pad.b)*p} className="grid-line"/><text x={pad.l-8} y={pad.t+(height-pad.t-pad.b)*p+3} textAnchor="end" className="axis-text">{(max-(max-min)*p).toLocaleString(undefined,{notation:'compact',maximumFractionDigits:1})}</text></g>)}
    <path d={path} className="chart-line" fill="none"/>
    {pts.map((p,i)=><g key={i}><circle cx={p[0]} cy={p[1]} r="4" className="chart-point"/><text x={p[0]} y={height-pad.b+18} textAnchor="middle" className="axis-text">{String(labels[i]).slice(0,11)}</text></g>)}
  </svg></div>
}

function ScatterChart({x=[], y=[]}){
  const width=760, height=300, pad={l:58,r:18,t:28,b:48}; const xs=x.map(Number).filter(Number.isFinite), ys=y.map(Number).filter(Number.isFinite); const xmin=Math.min(...xs,0), xmax=Math.max(...xs,1), ymin=Math.min(...ys,0), ymax=Math.max(...ys,1); const xr=Math.max(xmax-xmin,1), yr=Math.max(ymax-ymin,1);
  return <div className="svg-chart-wrap"><svg viewBox={`0 0 ${width} ${height}`} className="analysis-svg" role="img" aria-label="Scatter chart">
    {[0,.25,.5,.75,1].map((p,i)=><g key={i}><line x1={pad.l} x2={width-pad.r} y1={pad.t+(height-pad.t-pad.b)*p} y2={pad.t+(height-pad.t-pad.b)*p} className="grid-line"/></g>)}
    {x.slice(0,250).map((vx,i)=>{const vy=Number(y[i]);const nx=(Number(vx)-xmin)/xr;const ny=(vy-ymin)/yr;return <circle key={i} cx={pad.l+nx*(width-pad.l-pad.r)} cy={pad.t+(1-ny)*(height-pad.t-pad.b)} r="2.6" className="scatter-point"/>})}
    <text x={pad.l} y={height-12} className="axis-text">{xmin.toLocaleString(undefined,{maximumFractionDigits:2})}</text><text x={width-pad.r} y={height-12} textAnchor="end" className="axis-text">{xmax.toLocaleString(undefined,{maximumFractionDigits:2})}</text>
  </svg></div>
}

function ChartView({chart}){
  if(!chart) return null;
  if(chart.type==='line') return <LineChart labels={chart.labels||[]} values={chart.values||[]}/>;
  if(chart.type==='scatter') return <ScatterChart x={chart.x_labels||[]} y={chart.y_values||[]}/>;
  return <BarChart labels={chart.labels||[]} values={chart.values||[]}/>;
}

function MetricCards({metrics={}}){
  const entries=Object.entries(metrics).filter(([,v])=>typeof v==='number');
  return <div className="metric-cards">{entries.slice(0,5).map(([k,v])=><div className="metric-card" key={k}><span>{k.replaceAll('_',' ')}</span><strong>{Number(v).toLocaleString(undefined,{maximumFractionDigits:2})}</strong></div>)}</div>
}

export default function ResultsPanel({result}){
  const [mode,setMode]=useState('split'); const [busy,setBusy]=useState(false);
  const c=result?.chart||{};
  const chartData=useMemo(()=>c,[c]);
  if(!result) return <section className="panel results empty-results"><div className="empty-results-icon">✦</div><h2>Analysis Results & Synthesis</h2><p>Choose a dataset and click <b>Analyze</b>. The analysis workflow will plan, execute, validate and synthesize the result here.</p></section>;
  async function report(type){setBusy(true);try{const b=type==='pdf'?await exportPdfReport(result.query,result.dataset):await exportReport(result.query,result.dataset);downloadBlob(b,type==='pdf'?'autonomous_analysis_report.pdf':'autonomous_analysis_report.txt')}catch(e){alert(e.message)}finally{setBusy(false)}}
  function print(){window.print()}
  return <section className="panel results">
    <div className="panel-heading compact result-head"><div><div className="result-kicker">ANALYSIS RESULT</div><h2>Analysis Results & Synthesis</h2><p className="query-label">“{result.query}”</p></div><div className="report-actions no-print"><button className="outline-btn" onClick={()=>report('pdf')} disabled={busy}>⇩ PDF Report</button><button className="print-btn" onClick={print}>⎙ Print Summary</button></div></div>
    <div className="result-runtime no-print"><span>✓ Workflow complete</span><span>{result.profile?.rows?.toLocaleString()} rows</span><span>{result.profile?.columns} columns</span><span>{result.profile?.duplicate_rows?.toLocaleString()} duplicates</span></div>
    <div className="tabs result-tabs no-print"><button className={mode==='split'?'active':''} onClick={()=>setMode('split')}>Dashboard</button><button className={mode==='chart'?'active':''} onClick={()=>setMode('chart')}>Charts</button><button className={mode==='summary'?'active':''} onClick={()=>setMode('summary')}>Summary</button><button className={mode==='plan'?'active':''} onClick={()=>setMode('plan')}>Agent Trace</button></div>

    {(mode==='split'||mode==='chart')&&<div className="chart-section"><div className="chart-title-row"><div><h3>{c.title||'Analysis chart'}</h3><p>Computed directly from the selected dataset.</p></div><span className="chart-type">{c.type||'bar'} chart</span></div><ChartView chart={chartData}/><MetricCards metrics={result.metrics}/></div>}

    {(mode==='split'||mode==='summary')&&<div className="insight-box"><div className="section-title"><h3>✦ Evidence-grounded executive summary</h3><span>Based on computed results</span></div>{result.insights?.map((x,i)=><div className="insight" key={i}><span>{i+1}</span><p>{x}</p></div>)}<div className="quality-callout"><b>Data quality:</b> {result.profile?.duplicate_rows?.toLocaleString()} duplicate rows detected; missing-value rates are available in the dataset profile above.</div></div>}

    {(mode==='plan'||mode==='split')&&<div className="agent-trace"><div className="section-title"><h3>⌁ Agent execution trace</h3><span>Planner → Analysis Builder → Execution → Self-Correct → Synthesis</span></div><div className="trace-list">{(result.events||[]).map((e,i)=><div key={i}><b>{i+1}</b><span>{e}</span></div>)}</div><details className="plan"><summary>View generated analysis recipe</summary><pre>{result.generated_code}</pre></details></div>}

    <div className="print-report">
      <h1>Autonomous Data Analysis — Summary Report</h1>
      <p><b>Dataset:</b> {result.dataset}</p><p><b>Question:</b> {result.query}</p>
      <h2>Executive Summary</h2>{result.insights?.map((x,i)=><p key={i}>• {x}</p>)}
      <h2>Key Metrics</h2><table><tbody>{Object.entries(result.metrics||{}).map(([k,v])=><tr key={k}><td>{k.replaceAll('_',' ')}</td><td>{typeof v==='object'?JSON.stringify(v):String(v)}</td></tr>)}</tbody></table>
      <h2>Data Quality</h2><p>Rows: {result.profile?.rows?.toLocaleString()} | Columns: {result.profile?.columns} | Duplicate rows: {result.profile?.duplicate_rows?.toLocaleString()}</p>
      <h2>Autonomous Plan</h2><ol>{result.plan?.map((x,i)=><li key={i}>{x}</li>)}</ol>
      <p className="print-foot">Runtime: {result.runtime}</p>
    </div>
  </section>
}
