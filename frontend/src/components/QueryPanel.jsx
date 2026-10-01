const suggestions = [
  "Break down total sales and profit margins across regions",
  "Identify correlation between discount rates and sales volume",
  "Find top 5 customer segments generating highest profit",
  "Detect unusual sales and quantity values",
  "Show monthly sales trend by time"
];

export default function QueryPanel({query,setQuery,onAnalyze,loading}) {
  return <section className="panel query-panel">
    <div className="panel-heading compact">
      <div><h2>✦ &nbsp;Autonomous Analytical Query</h2><p>Ask a business question in plain English. The analysis workflow selects and executes the required steps automatically.</p></div>
      <div className="model-selects"><span>⌁ Adaptive Workflow</span><span>Local Analysis Engine</span></div>
    </div>
    <div className="query-row">
      <input value={query} onChange={e=>setQuery(e.target.value)} onKeyDown={e=>e.key==='Enter'&&!loading&&onAnalyze()} placeholder="e.g. Compare sales and profit by region" />
      <button onClick={onAnalyze} disabled={loading}>{loading ? 'Running…' : 'Analyze ➤'}</button>
    </div>
    <div className="suggestions"><small>Try:</small>{suggestions.map(s=><button key={s} onClick={()=>setQuery(s)}>{s}</button>)}</div>
  </section>
}
