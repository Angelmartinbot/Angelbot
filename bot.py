import time, requests, yfinance as yf
from datetime import datetime
import pytz
BOT_TOKEN = "8988200465:AAGn-YHiIqKaIK0k188VJhtNurmtGPJk5bA"
CHAT_ID = "934089208"
LIMA = pytz.timezone("America/Lima")
PARES = {"ONDO-USD":"ONDO OTC","DYDX-USD":"DYDX OTC","RAY-USD":"RAY OTC","BTTAO-USD":"TAO OTC","ORDI-USD":"ORDI OTC","SOL-USD":"SOL OTC","ICP-USD":"ICP OTC","TIA-USD":"CELESTIA OTC","^GDAXI":"GER30 OTC"}
HORARIOS = [9,13,16,18]
def enviar(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try: requests.post(url, data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML"}, timeout=10)
    except: pass
def estrategia1(df):
    if len(df)<4: return None
    v1,v2=df.iloc[-3],df.iloc[-2]
    o1,c1,h1,l1=float(v1['Open']),float(v1['Close']),float(v1['High']),float(v1['Low'])
    o2,c2,h2,l2=float(v2['Open']),float(v2['Close']),float(v2['High']),float(v2['Low'])
    indecision=(h1-l1)>0 and abs(c1-o1)<(h1-l1)*0.18
    fuerza=(h2-l2)>0 and abs(c2-o2)>(h2-l2)*0.60
    if indecision and fuerza:
        if c2>o2: return "🟢 COMPRA E1: Indecisión+Fuerza+Continuidad"
        if c2<o2: return "🔴 VENDE E1: Indecisión+Fuerza+Continuidad"
    return None
def estrategia2(df):
    if len(df)<6: return None
    cuerpos=[abs(float(df.iloc[i]['Close'])-float(df.iloc[i]['Open'])) for i in range(-6,-1)]
    promedio=sum(cuerpos)/len(cuerpos) if cuerpos else 0
    if promedio==0: return None
    v=df.iloc[-2]
    o,c=float(v['Open']),float(v['Close'])
    if abs(c-o)>promedio*1.8:
        if c>o: return "🔴 VENDE E2: Vela Verde Grande->Reversión"
        if c<o: return "🟢 COMPRA E2: Vela Roja Grande->Reversión"
    return None
sesion=None; ops=0; perdidas_seg=0
enviar("✅ BOT ANGEL FINAL PRENDIDO\nID:934089208\n✅ E1: Indecisión+Fuerza\n✅ E2: Vela Grande->Reversión AL REVÉS\n✅ Pares: ONDO,DYDX,RAY,TAO,ORDI,SOL,ICP,TIA,GER30\n✅ Horarios: 9,13,16,18 Lima\n✅ Candado: 3 perdidas=OFF | 5 ops | 11 USD FIJO")
while True:
    ahora=datetime.now(LIMA); h=ahora.hour
    if h in HORARIOS:
        if sesion!=h:
            sesion=h; ops=0; perdidas_seg=0
            enviar(f"⏰ SESIÓN {h}:00 INICIADA")
        if perdidas_seg>=3 or ops>=5:
            if ops>=5:
                enviar(f"📊 SESIÓN {h}:00 TERMINADA - {ops} ops")
                sesion=None; time.sleep(3600); continue
            time.sleep(60); continue
        for sym,nombre in PARES.items():
            try:
                df=yf.download(sym, period="1d", interval="5m", progress=False)
                señal=estrategia1(df) or estrategia2(df)
                if señal:
                    enviar(f"{señal}\nPar: {nombre}\nHora: {ahora.strftime('%H:%M')} Lima\n💰 11 USD FIJO sin martingala")
                    ops+=1; time.sleep(300); break
            except: pass
    else: sesion=None
    time.sleep(60)
