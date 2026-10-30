import os
import sqlite3
from pathlib import Path
import pandas as pd

COLUMNS = ['date','city','station','pm25','pm10','no2']

def db_path():
    return Path(os.getenv('DATABASE_PATH', 'data/airaware.db'))

def initialize(csv_file='data/delhi_pilot.csv'):
    path = db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    src = Path(csv_file)
    if not src.exists():
        raise FileNotFoundError(f'{src} is missing. Run python generate_sample.py or import a real CSV.')
    frame = pd.read_csv(src)
    missing = set(COLUMNS) - set(frame.columns)
    if missing:
        raise ValueError(f'Missing required columns: {sorted(missing)}')
    frame = frame[COLUMNS].copy()
    frame['date'] = pd.to_datetime(frame['date'], errors='raise').dt.strftime('%Y-%m-%d')
    for key in ['pm25','pm10','no2']:
        frame[key] = pd.to_numeric(frame[key], errors='coerce')
        frame.loc[frame[key] < 0, key] = float('nan')
    frame.drop_duplicates(subset=['date','city','station'], keep='last', inplace=True)
    with sqlite3.connect(path) as conn:
        frame.to_sql('pollution', conn, if_exists='replace', index=False)
        conn.execute('CREATE INDEX IF NOT EXISTS idx_pollution_date_city ON pollution(city,date)')
    return len(frame)

def query_frame(city='Delhi', pollutant='pm25', start=None, end=None, station=None):
    if pollutant not in ('pm25','pm10','no2'):
        raise ValueError('Unsupported pollutant')
    clauses = ['LOWER(city) = LOWER(?)']
    params = [city]
    if start:
        clauses.append('date >= ?'); params.append(start)
    if end:
        clauses.append('date <= ?'); params.append(end)
    if station:
        clauses.append('LOWER(station) = LOWER(?)'); params.append(station)
    sql = 'SELECT date,city,station,"' + pollutant + '" AS value FROM pollution WHERE ' + ' AND '.join(clauses) + ' ORDER BY date,station'
    with sqlite3.connect(db_path()) as conn:
        return pd.read_sql_query(sql, conn, params=params)

def options():
    with sqlite3.connect(db_path()) as conn:
        cities = [x[0] for x in conn.execute('SELECT DISTINCT city FROM pollution ORDER BY city')]
        dates = conn.execute('SELECT MIN(date), MAX(date), COUNT(*) FROM pollution').fetchone()
        stations = [x[0] for x in conn.execute('SELECT DISTINCT station FROM pollution ORDER BY station')]
    return {'cities': cities, 'stations': stations, 'date_start': dates[0], 'date_end': dates[1], 'records': dates[2], 'pollutants':['pm25','pm10','no2']}
