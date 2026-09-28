import requests, yfinance as yf
from datetime import datetime
import pytz, os

BOT_TOKEN=os.getenv("BOT_TOKEN") or "8988200465:AAGn-YHiIqKaIK0k188VJhtNurmtGPJk5bA"
CHAT_ID=os.getenv("CHAT_ID") or "934089208"
LIMA=pytz.timezone("America/Lima")
# TICKERS CORREGIDOS PARA YAHOO
PARES={"ONDO-USD":"ONDO OTC","DYDX-USD":"DYDX OTC","RAY-USD":"RAY OTC","TAO-USD":"TAO OTC","ORDI-USD":"ORDI OTC","SOL-USD":"SOL OTC","ICP-USD":"ICP OTC","TIA-USD":"CELESTIA OTC","^GDAXI":"GER30 OTC"}
HORARIOS=[9,13,16,18]

def enviar(msg):
 url=f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
 try: requests.post(url,data={"chat_id":CHAT_ID,"text":msg,"parse_mode":"HTML"},timeout=10)
 except: pass

def estrategia1(df):
 if len(df)<4: return None
 v1,v2=df.iloc[-3],df.iloc[-2]
 o1,c1,h1,l1=float(v1['Open']),float(v1['Close']),float(v1['High']),float(v1['Low'])
 o2,c2,h2,l2=float(v2['Open']),float(v2['Close']),float(v2['High']),float(v2['Low'])
 indecision=(h1-l1)>0 and abs(c1-o1)<(h1-l1)*0.18
 fuerza=(h2-l2)>0 and abs(c2-o2)>(h2-l2)*0.60
 if indecision and fuerza:
  if c2>o2: return "🟢 COMPRA E1: Indecisión+Fuerza"
  if c2<o2: return "🔴 VENDE E1: Indecisión+Fuerza"
 return None

def estrategia2(df):
 if len(df)<6: return None
 cuerpos=[abs(float(df.iloc[i]['Close'])-float(df.iloc[i]['Open'])) for i in range(-6,-1)]
 promedio=sum(cuerpos)/len(cuerpos) if cuerpos else 0
 if promedio==0: return None
 v=df.iloc[-2]
 o,c=float(v['Open']),float(v['Close'])
 if abs(c-o)>promedio*1.8:
  if c>o: return "🔴 VENDE E2: Vela Grande->Reversión"
  if c<o: return "🟢 COMPRA E2: Vela Grande->Reversión"
 return None

ahora=datetime.now(LIMA)
h=ahora.hour
print(f"Hora Lima {ahora}")

if h not in HORARIOS:
  enviar(f"⏰ Bot revisó {ahora.strftime('%H:%M')} Lima - Fuera de horario {HORARIOS}")
else:
  enviar(f"⏰ SESIÓN {h}:00 INICIADA - Chequeando 9 pares")
  ops=0
  for sym,nombre in PARES.items():
   try:
    df=yf.download(sym,period="1d",interval="5m",progress=False)
    if df.empty:
     print(f"{sym} vacio")
     continue
    senal=estrategia1(df) or estrategia2(df)
    if senal:
     enviar(f"{senal}\nPar: {nombre}\nHora: {ahora.strftime('%H:%M')} Lima\n💰 11 USD FIJO")
     ops+=1
   except Exception as e:
    print(e)
  enviar(f"📊 Sesión {h}:00 terminada - {ops} señales")
