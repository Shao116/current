"""Cached public weather for fixed regional points; never forwards a customer's exact location."""
import json,time,urllib.request,urllib.parse,threading,datetime
from pathlib import Path
ROOT=Path(__file__).resolve().parent
CACHE=ROOT/'private/weather-region.json'
LOCK=threading.Lock()
POINTS=[(37.27,-79.94),(37.12,-80.17),(37.30,-80.18),(37.43,-80.08),(37.43,-79.78),(37.25,-79.73),(37.07,-79.82)]
def weather():
 with LOCK:
  saved=None
  if CACHE.exists():
   try:saved=json.loads(CACHE.read_text())
   except Exception:pass
  if saved and time.time()-saved.get('fetchedEpoch',0)<1200 and all('wind_direction_10m' in p.get('hourly',{}) for p in saved.get('points',[])):return saved
  params={'latitude':','.join(str(p[0]) for p in POINTS),'longitude':','.join(str(p[1]) for p in POINTS),'current':'temperature_2m,weather_code,wind_speed_10m,wind_gusts_10m','hourly':'temperature_2m,precipitation_probability,wind_speed_10m,wind_direction_10m,wind_gusts_10m,precipitation,rain,snowfall,snow_depth,weather_code','daily':'weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max,wind_gusts_10m_max','temperature_unit':'fahrenheit','wind_speed_unit':'mph','timezone':'America/New_York','forecast_days':5}
  url='https://api.open-meteo.com/v1/forecast?'+urllib.parse.urlencode(params)
  try:
   req=urllib.request.Request(url,headers={'User-Agent':'current-HackOHIO-educational-prototype/2.0'})
   with urllib.request.urlopen(req,timeout=18) as f:data=json.load(f)
   if not isinstance(data,list):data=[data]
   out={'fetchedEpoch':time.time(),'fetchedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source':'Open-Meteo','sourceUrl':'https://open-meteo.com/','license':'CC BY 4.0; free API for non-commercial prototypes','stale':False,'points':data}
   CACHE.write_text(json.dumps(out));return out
  except Exception as e:
   if saved:return dict(saved,stale=True,error='Weather refresh unavailable; showing saved forecast')
   initial=ROOT/'private/weather-initial.json'
   if initial.exists():return {'source':'Open-Meteo','sourceUrl':'https://open-meteo.com/','fetchedAt':None,'stale':True,'points':[json.loads(initial.read_text())],'error':'Regional refresh unavailable; showing downloaded Roanoke forecast'}
   return {'source':'Open-Meteo','stale':True,'points':[],'error':'Weather unavailable'}
