import {useMemo, useState} from 'react';

const fallbackNodes = [
  {id:'input', title:'Dataset Input', status:'idle', input:'Selected dataset', operation:'load_dataframe(path)', output:'Waiting for dataset'},
  {id:'planner', title:'Planner', status:'idle', input:'User query + profile', operation:'infer_plan(query, dataframe)', output:'Waiting for analysis'},
  {id:'codegen', title:'Analysis Builder', status:'idle', input:'Planner output', operation:'_code_template(query, plan)', output:'Waiting for plan'},
  {id:'execution', title:'Execution', status:'idle', input:'Dataframe + plan', operation:'execute_plan(dataframe, query)', output:'Waiting for execution'},
  {id:'self_correct', title:'Self-Correct', status:'idle', input:'Metrics + chart evidence', operation:'validate_results(metrics)', output:'Waiting for validation'},
  {id:'synthesis', title:'Synthesis', status:'idle', input:'Validated evidence', operation:'evidence-grounded synthesis', output:'Waiting for insights'},
];

export default function AgentPipeline({pipeline=[],events=[],nodeDetails=[],plan=[],generatedCode='',runtime=''}) {
  const [tab,setTab]=useState('graph');
  const [selected,setSelected]=useState('execution');
  const pipelineMap=useMemo(()=>Object.fromEntries((pipeline||[]).map(x=>[x.id,x])),[pipeline]);
  const nodes=(nodeDetails?.length?nodeDetails:fallbackNodes).map(n=>({...n,...(pipelineMap[n.id]||{})}));
  const active=nodes.find(n=>n.id===selected)||nodes[0];

  return <section className="runtime-card">
    <div className="runtime-top">
      <span className="dot red"></span><span className="dot yellow"></span><span className="dot green"></span>
      <span>⌁ Analytical Execution Runtime</span>
      <span className="runtime-badge">Workflow active</span>
    </div>

    <div className="lg-explainer"><b>Execution flow:</b> each node receives state, transforms it, and passes the updated state to the next node. Click a node to inspect its input, operation and output.</div>

    <div className="pipeline-tabs">
      <button className={tab==='graph'?'active':''} onClick={()=>setTab('graph')}>⌁ Flow</button>
      <button className={tab==='stream'?'active':''} onClick={()=>setTab('stream')}>↯ Stream ({events.length})</button>
      <button className={tab==='state'?'active':''} onClick={()=>setTab('state')}>◉ State</button>
      <button className={tab==='code'?'active':''} onClick={()=>setTab('code')}>〈/〉 Code</button>
      <button className={tab==='plan'?'active':''} onClick={()=>setTab('plan')}>⚙ Plan</button>
    </div>

    {tab==='graph'&&<div className="langgraph-canvas">
      <div className="graph-flow">
        {nodes.map((n,i)=><div className="graph-step" key={n.id}>
          <button className={`graph-node ${n.status||'idle'} ${selected===n.id?'selected':''}`} onClick={()=>setSelected(n.id)}>
            <span className="node-number">{i}</span>
            <span className="node-copy"><b>{n.title}</b><small>{n.status==='complete'?'✓ completed':n.status==='warning'?'⚠ validation issue':'waiting'}</small></span>
            <span className="node-arrow">›</span>
          </button>
          {i<nodes.length-1&&<div className="graph-connector"><i></i><span>state</span></div>}
        </div>)}
      </div>
      <div className="node-inspector">
        <div className="inspector-head"><div><small>SELECTED NODE</small><h3>{active?.title||'Node'}</h3></div><span className={`node-status ${active?.status||'idle'}`}>{active?.status||'idle'}</span></div>
        <div className="inspector-grid">
          <div><small>INPUT STATE</small><p>{active?.input||'—'}</p></div>
          <div><small>OPERATION</small><code>{active?.operation||'—'}</code></div>
          <div className="inspector-output"><small>OUTPUT STATE</small><p>{active?.output||'—'}</p></div>
        </div>
      </div>
    </div>}

    {tab==='stream'&&<div className="runtime-log large-log">{events.length?events.map((e,i)=><div className="event-row" key={i}><b>{String(i+1).padStart(2,'0')}</b><span className="event-node">{nodes[Math.min(i+1,nodes.length-1)]?.title||'Graph'}</span><span>{e}</span></div>):<span>Run an analysis to stream workflow node events here.</span>}</div>}

    {tab==='state'&&<div className="state-view">
      <div className="state-row"><span>query</span><code>{events.length?'user question received':'waiting'}</code></div>
      <div className="state-row"><span>profile</span><code>{pipeline.length?'rows × columns profiled':'waiting'}</code></div>
      <div className="state-row"><span>plan</span><code>{plan.length?`${plan.length} analysis operations selected`:'waiting'}</code></div>
      <div className="state-row"><span>metrics</span><code>{pipelineMap.execution?'computed':'waiting'}</code></div>
      <div className="state-row"><span>validation</span><code>{pipelineMap.self_correct?.status==='complete'?'passed':'waiting'}</code></div>
      <div className="state-row"><span>insights</span><code>{pipelineMap.synthesis?'synthesized':'waiting'}</code></div>
    </div>}

    {tab==='code'&&<div className="code-panel"><div className="code-caption">Generated analysis recipe <span>safe execution boundary</span></div><pre>{generatedCode||'# Run Analyze to generate the planner recipe.'}</pre></div>}

    {tab==='plan'&&<div className="plan-panel"><div className="plan-caption">Planner selected these operations from the question</div>{plan.length?<ol>{plan.map((x,i)=><li key={i}>{x}</li>)}</ol>:<p>Run Analyze to populate the autonomous plan.</p>}</div>}
  </section>
}
