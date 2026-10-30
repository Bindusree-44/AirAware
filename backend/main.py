import os
import re
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from backend.agent import Plan, make_plan
from backend.db import initialize, options, query_frame

load_dotenv()

@asynccontextmanager
async def lifespan(app):
    initialize()
    yield

app=FastAPI(title='AirAware Agentic Pollution Analytics', lifespan=lifespan)

class Question(BaseModel):
    question: str

class Execution(BaseModel):
    plan: Plan
    question: str = ''

def validate_date(d):
    if d is None: return None
    if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', d):
        raise HTTPException(400, f'Invalid date: {d}')
    from datetime import date
    try: date.fromisoformat(d)
    except ValueError: raise HTTPException(400, f'Invalid date: {d}')
    return d

@app.get('/health')
def health():
    return {'status':'ok','dataset':options(),'source':'demo synthetic unless replaced with verified CPCB CSV'}

@app.post('/plan')
def plan_question(body:Question):
    if not body.question.strip() or len(body.question)>1000:
        raise HTTPException(400,'Question must be 1-1000 characters')
    try:
        plan=make_plan(body.question,options())
        return {'question':body.question,'plan':plan.model_dump()}
    except Exception as e:
        raise HTTPException(502,f'Gemini query planning failed: {type(e).__name__}: {e}')

@app.post('/execute')
def execute(body:Execution):
    p=body.plan
    meta=options()
    if p.city.lower() not in [s.lower() for s in meta['cities']]:
        return {'answer':f'Only {", ".join(meta["cities"])} data are available in this pilot.','rows':[],'intent':p.intent,'model_used':p.model_used}
    if p.station and p.station.lower() not in [s.lower() for s in meta['stations']]:
        return {'answer':'Station not found in this dataset. Available: '+', '.join(meta['stations']),'rows':[],'intent':p.intent,'model_used':p.model_used}
    start=validate_date(p.start_date); end=validate_date(p.end_date)
    if start and end and start>end: raise HTTPException(400,'Start date occurs after end date')
    if p.intent=='help':
        return {'answer':'Ask about PM2.5, PM10, or NO2 averages, highest days, station comparisons, or daily graphs for Delhi.','rows':[],'intent':'help','model_used':p.model_used}
    df=query_frame(city=p.city,pollutant=p.pollutant,start=start,end=end,station=p.station)
    df=df.dropna(subset=['value'])
    if df.empty:
        return {'answer':'No measurements are available for that filter. Try another date or station.','rows':[],'intent':p.intent,'model_used':p.model_used}
    units='µg/m³'  # Ensure real CPCB source is in these units before importing
    date_range=f'{df.date.min()} to {df.date.max()}'
    count=len(df)
    station_info=f' at {p.station}' if p.station else ' across the available stations'
    if p.intent=='maximum':
        highest=df.loc[df.value.idxmax()]
        answer=f'The highest {p.pollutant.upper()} reading was {highest.value:.1f} {units} at {highest.station} on {highest.date}.'
        chart=df.groupby('date',as_index=False).value.max().round(2)
    elif p.intent=='compare':
        groups=df.groupby('station',as_index=False).value.mean().round(2).sort_values('value',ascending=False)
        answer=f'{p.pollutant.upper()} station comparison ({date_range}): '+ '; '.join(f'{r.station}: {r.value:.1f} {units}' for r in groups.itertuples())+'.'
        chart=groups
    else:
        avg=df.value.mean()
        answer=f'Average {p.pollutant.upper()}{station_info} from {date_range}: {avg:.1f} {units}, based on {count} valid station-day observations.'
        chart=df.groupby('date',as_index=False).value.mean().round(2)
    if p.response_language=='mixed':
        answer='Delhi pollution data prakaram: '+answer
    elif p.response_language=='telugu':
        answer='ఢిల్లీ వాయు కాలుష్య డేటా ప్రకారం: '+answer
    return {'answer':answer,'rows':chart.to_dict(orient='records'),'intent':p.intent,'pollutant':p.pollutant,'units':units,'count':count,'source_label':'SYNTHETIC DEMO DATA — replace with actual CPCB data before presenting findings','model_used':p.model_used,'range':date_range}

@app.post('/process')
def process(question:Question):
    """Direct fallback endpoint, when n8n is not yet configured."""
    planned=plan_question(question)
    return execute(Execution(**planned))
