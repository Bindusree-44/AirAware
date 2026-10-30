"""Create a SYNTHETIC demo dataset. Never represent these values as CPCB measurements."""
import csv
from datetime import date, timedelta
from pathlib import Path

path=Path('data/delhi_pilot.csv')
path.parent.mkdir(parents=True, exist_ok=True)
stations=[('Anand Vihar',104,183,46),('R K Puram',78,142,39),('Punjabi Bagh',95,168,43)]
with path.open('w',newline='',encoding='utf-8') as f:
    writer=csv.writer(f)
    writer.writerow(['date','city','station','pm25','pm10','no2'])
    for day in range(30):
        d=date(2025,1,1)+timedelta(days=day)
        for index,(station,p25,p10,no2) in enumerate(stations):
            writer.writerow([d.isoformat(),'Delhi',station,p25+(day*7+index*3)%31-15,p10+(day*11+index*5)%43-21,no2+(day*5+index*2)%17-8])
print(f'Created {path}: 90 synthetic rows (3 Delhi stations x 30 days). NOT actual CPCB data.')
