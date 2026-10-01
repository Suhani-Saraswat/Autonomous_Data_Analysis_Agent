from pathlib import Path
import shutil, uuid, tempfile
import pandas as pd
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from .schema import QueryRequest
from .orchestrator import orchestrator

app=FastAPI(title='Autonomous Data Analysis Agent',version='1.0.0')
app.add_middleware(CORSMiddleware,allow_origins=['*'],allow_credentials=True,allow_methods=['*'],allow_headers=['*'])
ROOT=Path(__file__).resolve().parents[1]; DATASET_DIR=ROOT/'datasets'; DATASET_DIR.mkdir(exist_ok=True)
ALLOWED={'.csv','.xlsx','.xls'}

def resolve_dataset(name:str)->Path:
    safe=Path(name).name
    hits=[p for p in DATASET_DIR.rglob(safe) if p.is_file() and p.suffix.lower() in ALLOWED]
    if not hits: raise HTTPException(404,f'Dataset not found: {safe}')
    return hits[0]

def read_df(path): return pd.read_csv(path) if path.suffix.lower()=='.csv' else pd.read_excel(path)

@app.get('/api/health')
def health(): return {'status':'ok','runtime':'LangGraph StateGraph' if orchestrator.graph is not None else 'LangGraph fallback','agent':'autonomous-data-analysis'}

@app.get('/api/datasets')
def datasets():
    items=[]
    for p in DATASET_DIR.rglob('*'):
        if p.is_file() and p.suffix.lower() in ALLOWED:
            items.append({'name':p.name,'size_kb':round(p.stat().st_size/1024,1),'source':'uploaded' if 'uploads' in p.parts else 'project','kind':'live' if 'live' in p.name.lower() else 'fixed'})
    return {'datasets':sorted(items,key=lambda x:(x['source']!='project',x['name']))}

@app.get('/api/profile')
def profile(dataset:str|None=None):
    path=str(resolve_dataset(dataset)) if dataset else None
    r=orchestrator.analyze('Provide a dataset overview.',path); return r['profile']|{'dataset':r['dataset']}

@app.get('/api/preview')
def preview(dataset:str,rows:int=10):
    df=read_df(resolve_dataset(dataset)).head(max(1,min(rows,50))).fillna('')
    return {'columns':[str(c) for c in df.columns],'rows':df.astype(str).to_dict(orient='records')}

@app.post('/api/analyze')
def analyze(request:QueryRequest):
    path=str(resolve_dataset(request.dataset)) if request.dataset else None
    return orchestrator.analyze(request.query,path)

@app.post('/api/upload')
async def upload(file:UploadFile=File(...)):
    original=Path(file.filename or 'dataset.csv'); suffix=original.suffix.lower()
    if suffix not in ALLOWED: raise HTTPException(400,'Only CSV/XLSX/XLS files are supported')
    d=DATASET_DIR/'uploads'; d.mkdir(exist_ok=True); safe=f'uploaded_{uuid.uuid4().hex[:8]}_{original.name.replace(" ","_")}'; target=d/safe
    with target.open('wb') as b: shutil.copyfileobj(file.file,b)
    try: orchestrator.load(str(target))
    except Exception as e: target.unlink(missing_ok=True); raise HTTPException(400,f'Dataset could not be read: {e}')
    return {'filename':safe,'message':'Dataset uploaded and validated successfully','size_kb':round(target.stat().st_size/1024,1)}

@app.post('/api/live/refresh')
def refresh_live():
    live=DATASET_DIR/'superstore_live_stream_10000plus.csv'
    if not live.exists(): raise HTTPException(404,'Live dataset not found')
    df=pd.read_csv(live); df=df.sample(frac=1,random_state=None).reset_index(drop=True); df.to_csv(live,index=False)
    return {'message':'Live dataset refreshed','filename':live.name,'rows':len(df)}

def _analysis_result(request: QueryRequest):
    path = str(resolve_dataset(request.dataset)) if request.dataset else None
    return orchestrator.analyze(request.query, path)


@app.post('/api/report')
def report(request: QueryRequest):
    result = _analysis_result(request)
    lines = [
        'AUTONOMOUS DATA ANALYSIS REPORT', '=' * 38, '',
        f'Dataset: {result["dataset"]}', f'Question: {result["query"]}', '',
        'EXECUTIVE SUMMARY', '-' * 20,
    ]
    lines += [f'• {x}' for x in result.get('insights', [])]
    lines += ['', 'DATA QUALITY', '-' * 20,
              f'Rows: {result["profile"]["rows"]:,}',
              f'Columns: {result["profile"]["columns"]:,}',
              f'Duplicate rows: {result["profile"]["duplicate_rows"]:,}']
    lines += ['', 'AUTONOMOUS PLAN', '-' * 20] + [f'{i}. {x}' for i, x in enumerate(result.get('plan', []), 1)]
    lines += ['', 'KEY METRICS', '-' * 20]
    for k, v in result.get('metrics', {}).items(): lines.append(f'{k}: {v}')
    lines += ['', 'RUNTIME', '-' * 20, result.get('runtime', 'LangGraph')]
    content = '\n'.join(lines)
    return Response(content=content, media_type='text/plain', headers={'Content-Disposition': 'attachment; filename="autonomous_analysis_report.txt"'})


@app.post('/api/report/pdf')
def report_pdf(request: QueryRequest):
    result = _analysis_result(request)
    import io
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=16*mm, leftMargin=16*mm, topMargin=16*mm, bottomMargin=16*mm)
    styles = getSampleStyleSheet()
    title = ParagraphStyle('ReportTitle', parent=styles['Title'], fontSize=20, leading=24, spaceAfter=10)
    heading = ParagraphStyle('ReportHeading', parent=styles['Heading2'], fontSize=12, leading=15, spaceBefore=10, spaceAfter=6)
    body = ParagraphStyle('ReportBody', parent=styles['BodyText'], fontSize=9, leading=13, spaceAfter=4)
    story = [Paragraph('Autonomous Data Analysis Report', title),
             Paragraph(f'<b>Dataset:</b> {result["dataset"]}', body),
             Paragraph(f'<b>Question:</b> {result["query"]}', body),
             Paragraph('Executive Summary', heading)]
    for item in result.get('insights', []): story.append(Paragraph('• ' + item, body))
    story += [Paragraph('Data Quality', heading)]
    quality = [['Rows', f'{result["profile"]["rows"]:,}'], ['Columns', f'{result["profile"]["columns"]:,}'], ['Duplicate rows', f'{result["profile"]["duplicate_rows"]:,}']]
    table = Table(quality, colWidths=[45*mm, 45*mm])
    table.setStyle(TableStyle([('BACKGROUND',(0,0),(0,-1),colors.HexColor('#eef2ff')),('GRID',(0,0),(-1,-1),0.4,colors.HexColor('#cbd5e1')),('FONTNAME',(0,0),(-1,-1),'Helvetica'),('FONTSIZE',(0,0),(-1,-1),8),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('BOTTOMPADDING',(0,0),(-1,-1),5),('TOPPADDING',(0,0),(-1,-1),5)]))
    story += [table, Paragraph('Autonomous Plan', heading)]
    for i, step in enumerate(result.get('plan', []), 1): story.append(Paragraph(f'{i}. {step}', body))
    story += [Paragraph('Key Metrics', heading)]
    metric_rows = [['Metric', 'Value']]
    for k, v in result.get('metrics', {}).items(): metric_rows.append([str(k), str(v)])
    if len(metric_rows) > 1:
        mt = Table(metric_rows, colWidths=[65*mm, 100*mm], repeatRows=1)
        mt.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#4c1d95')),('TEXTCOLOR',(0,0),(-1,0),colors.white),('GRID',(0,0),(-1,-1),0.35,colors.HexColor('#cbd5e1')),('FONTSIZE',(0,0),(-1,-1),7.5),('VALIGN',(0,0),(-1,-1),'TOP'),('BOTTOMPADDING',(0,0),(-1,-1),4),('TOPPADDING',(0,0),(-1,-1),4)]))
        story.append(mt)
    story += [Paragraph('Runtime', heading), Paragraph(result.get('runtime', 'LangGraph'), body)]
    doc.build(story)
    buffer.seek(0)
    return Response(content=buffer.getvalue(), media_type='application/pdf', headers={'Content-Disposition': 'attachment; filename="autonomous_analysis_report.pdf"'})

@app.get('/')
def home(): return FileResponse(ROOT/'backend'/'templates'/'index.html')
