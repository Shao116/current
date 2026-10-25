"""Stable API adapter for the v2 evidence-gated algorithms."""
import math
STAGES={'pre':'Pre-storm','outage':'Outage scenario','update':'Estimate updated','restored':'Restoration scenario'}
RATES={'pole':(2.50295207667732,.9274888178913726),'transformer':(1.2445957446808502,.890893617021277),'fuse':(.256,.128),'switch':(1.7579459459459466,1.0097297297297296),'wire':None}
def number(s,k,default,lo,hi):
 try:v=float(s.get(k,default))
 except (TypeError,ValueError):raise ValueError(f'{k} must be numeric')
 if not math.isfinite(v) or v<lo or v>hi:raise ValueError(f'{k} must be between {lo} and {hi}')
 return v

def normalize(s):
 if not isinstance(s,dict):raise ValueError('Scenario must be an object')
 x={k:number(s,k,d,lo,hi) for k,d,lo,hi in [('wind',55,0,120),('crews',3,1,20),('quantity',3,0,50),('accessDelay',1,0,48),('upstream',1,0,10),('lat',37.27,36.95,37.53),('lng',-79.94,-80.32,-79.58)]}
 for k in ['crews','quantity','upstream']:
  if x[k]!=int(x[k]):raise ValueError(f'{k} must be a whole number')
  x[k]=int(x[k])
 x.update({'asset':s.get('asset','pole'),'stage':s.get('stage','pre'),'contextType':s.get('contextType','map'),'contextId':str(s.get('contextId',''))[:24],'access':s.get('access') is True,'step':s.get('step') is True,'medical':s.get('medical') is True,'accessible':s.get('accessible') is True,'critical':s.get('critical') is True,'channel':s.get('channel','SMS'),'optIn':s.get('optIn') is True,'size':s.get('size','medium')})
 if x['asset'] not in RATES:raise ValueError('Unknown asset category')
 if x['stage'] not in STAGES:raise ValueError('Unknown scenario stage')
 if x['contextType'] not in ['map','premise','circuit']:raise ValueError('Unknown location type')
 if x['size'] not in ['small','medium','large']:raise ValueError('Unknown pole size')
 if x['channel'] not in ['SMS','Email','In-app']:raise ValueError('Unknown channel')
 return x

def distance(a,b):
 return math.hypot((a['lat']-b['lat'])*111,(a['lng']-b['lng'])*88.5)

def evaluate(raw,data):
 from algorithms.service import get_service
 s=normalize(raw);premise=None
 if s['contextType']=='premise':
  premise=data['premiseIndex'].get(s['contextId'])
  if not premise:raise ValueError('Choose a valid anonymized premise')
  s.update({k:premise[k] for k in ['lat','lng']})
  from pyproj import Transformer
  xy=get_service().d['customers'][int(s['contextId'].split('-')[1])-1]['xy']
  s['lng'],s['lat']=Transformer.from_crs(26917,4326,always_xy=True).transform(*xy)
 elif s['contextType']=='circuit':
  circuit=data['circuitIndex'].get(s['contextId'])
  if not circuit:raise ValueError('Choose a valid circuit')
  s.update({k:circuit[k] for k in ['lat','lng']})
 result=get_service().run(s,raw);impact=result['impact'];ert=result['ert'];circuit=data['circuitIndex'][result['scopeCircuit']]
 path=premise['path'] if premise else [];work=ert['workload'];available=ert['low'] is not None;lo=ert['low'];hi=ert['high'];duration=f'{lo:.1f}–{hi:.1f} hours' if available else 'unavailable because a verified task rate is missing'
 restoration={'low':lo,'high':hi,'directHours':work.get('directHours'),'indirectMultiplier':4.5,'crewHours':ert.get('meanCrewHours',work.get('taskHours',0)*(ert.get('taskCount') or 0) if work['available'] else None),'predecessorHours':None,'parallelHours':hi,'accessDelay':s['accessDelay'],'firstRestoration':ert.get('firstRestoration') if s['step'] else None,'rate':{'install':work.get('components',[{}])[0].get('installHours') if work.get('components') else None,'remove':work.get('components',[{}])[0].get('removeHours') if work.get('components') else None,'source':work.get('source','Supplied AEP workbook component rates; default transformer 50 kVA.')},'formula':'Workbook component work × ILM 4.5 → resource-constrained discrete-event schedule → latest completed failed ancestor on each customer source path.','note':ert.get('rangeMeaning',ert.get('reason'))}
 from algorithms.customer_view import customer_estimate
 selected_customer=customer_estimate(result,get_service().d['customers'][int(s['contextId'][2:])-1] if premise else None)
 if selected_customer is not None and hasattr(get_service(),'physics') and 'riskAssessment' in result:selected_customer['modeledSupportCount']=len(get_service().physics.by_customer[int(s['contextId'][2:])-1])
 from algorithms.customer_guidance import guidance,messages as communication_messages
 actions,alert_result=guidance(s,result);messages=communication_messages(s,selected_customer,impact,duration)
 extra_keys=['date','historicalWeather','windDirection','rainMm','snowfallCm','snowDepthM','freezingRain','failedNodes','trials','seed','correlation','components','crewSize','laborBasis','crewRange','accessDelayRange','repairHours','scope','drawingPage','predictionMode','restorationModel','repairCV','hazardHoldHours','damageDetails','facilityLinks','fallCorridorM','iceAccretionMm','backup','laborAdders']
 s.update({k:raw[k] for k in extra_keys if k in raw})
 return {'customerRisk':selected_customer,'scenario':s,'location':{'label':premise['id'] if premise else circuit['id'],'lat':s['lat'],'lng':s['lng'],'circuit':circuit['id'],'circuitCustomers':circuit['count'],'path':path,'topologyAvailable':bool(path),'nearbyReports':result.get('riskAssessment',{}).get('historicalDamage',{}).get('priorReportsWithin3km'),'nearbyCustomers':impact['scopeCustomers']},'risk':{'score':None,'band':'Winter hazard · partial model' if result.get('riskAssessment',{}).get('status')=='partial_winter_hazard' else 'Engineering scenario' if result.get('riskAssessment') else 'Unknown','confidence':'Unvalidated','label':'Published-parameter wind/tree engineering estimate; uncalibrated' if result.get('riskAssessment') else 'Conditional damage scenario; uncalibrated','factors':[{'name':'Dynamic wind pressure','value':round(result['physicsFeatures']['dynamicPressurePa'],1),'max':None,'detail':'Pascals, from selected gust and stated air-density assumption. Physical feature, not risk points.'},{'name':'Verified topology candidates','value':impact['candidateDevices'],'max':None,'detail':'Devices connected through supplied customer upstream paths; no spatially invented connectivity.'}]},'restoration':restoration,'alerts':alert_result,'actions':actions,'messages':messages,'message':messages[s['stage']],'limitations':result['model']['reasons']+impact['warnings']+['Range is a conditional scenario, not verified utility ERT.','Exact GIS and critical-customer attributes remain private.'],'confirmedFacts':['117,642 customers and 32,600 source-path nodes in Roanoke, Virginia.','113 supplied LS Life Support flags; facility-to-customer links unverified.','Workbook ILM 4.5 includes drive/safety/setup time.'],'assumptions':['Quantity, crew availability, access delay and component damage are explicit scenario assumptions.','Wind direction/rain/snow defaults are scenario assumptions if not supplied.','No forced GNN training, fabricated negatives or unverified backup feed. Published reference fragility is explicitly transferred, not locally calibrated.'],**result}
