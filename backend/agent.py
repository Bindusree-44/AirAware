"""LLM parses intent into strict structured parameters; it never writes SQL."""
import json
import os
import re
from datetime import date
from pydantic import BaseModel, Field
from typing import Literal

class Plan(BaseModel):
    intent: Literal['summary','trend','compare','maximum','help'] = 'summary'
    city: str = 'Delhi'
    pollutant: Literal['pm25','pm10','no2'] = 'pm25'
    start_date: str | None = None
    end_date: str | None = None
    station: str | None = None
    response_language: Literal['english','telugu','mixed'] = 'mixed'
    model_used: str = 'fallback'

SYSTEM = """You extract a data-query plan for a SMALL DELHI AIR POLLUTION database.
Understand English, Telugu script and Romanized Telugu (e.g. 'Delhi lo PM2.5 entha?').
Return structured fields according to the supplied schema. Choose intent:
summary = average or general query; trend = graph/by day; compare = comparing stations or pollutants;
maximum = highest/peak; help = unrelated/unsupported request.
Only available city: Delhi. Pollutants: pm25, pm10, no2. Optional station filter.
Dates if explicitly present must be YYYY-MM-DD. No guessing dates. Choose response_language appropriately.
Never invent pollution values or try to answer the question: the database does that.
"""

def fallback_plan(question: str) -> Plan:
    q=question.lower()
    pollutant='pm25'
    if 'pm10' in q or 'pm 10' in q: pollutant='pm10'
    elif 'no2' in q or 'nitrogen' in q: pollutant='no2'
    intent='summary'
    if any(s in q for s in ('graph','trend','plot','chart','రోజు','చూపించు')): intent='trend'
    elif any(s in q for s in ('compare','comparison','versus','vs','difference','పోల్చ')): intent='compare'
    elif any(s in q for s in ('highest','maximum','max','peak','ఎక్కువ')): intent='maximum'
    dates=re.findall(r'\b\d{4}-\d{2}-\d{2}\b',q)
    station=next((n for n in ['Anand Vihar','R K Puram','Punjabi Bagh'] if n.lower() in q),None)
    lang='telugu' if any('\u0c00' <= c <= '\u0c7f' for c in question) else ('mixed' if any(s in q for s in [' lo ',' entha',' chupinchu',' ela ',' undhi',' ekkuva']) else 'english')
    return Plan(intent=intent,pollutant=pollutant,start_date=dates[0] if dates else None,end_date=dates[1] if len(dates)>1 else (dates[0] if dates else None),station=station,response_language=lang)

def make_plan(question: str, metadata: dict) -> Plan:
    key=os.getenv('GEMINI_API_KEY','').strip()
    if not key:
        return fallback_plan(question)
    from google import genai
    from google.genai import types
    model=os.getenv('GEMINI_MODEL','gemini-2.5-flash')
    client=genai.Client(api_key=key)
    result=client.models.generate_content(
        model=model,
        contents=f'Available database: {json.dumps(metadata)}\nUser question: {question}',
        config=types.GenerateContentConfig(system_instruction=SYSTEM,response_mime_type='application/json',response_schema=Plan,temperature=0)
    )
    plan=Plan.model_validate_json(result.text)
    plan.model_used=model
    return plan
