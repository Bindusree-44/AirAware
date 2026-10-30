from backend.agent import fallback_plan
from backend.db import initialize, options, query_frame

def test_sample_and_query():
    import subprocess,sys
    subprocess.run([sys.executable,'generate_sample.py'],check=True)
    assert initialize()==90
    assert options()['records']==90
    assert len(query_frame())==90

def test_intent():
    assert fallback_plan('Delhi lo PM10 trend graph chupinchu').intent=='trend'
    assert fallback_plan('What is highest NO2?').intent=='maximum'
    assert fallback_plan('Compare PM2.5 stations').intent=='compare'
