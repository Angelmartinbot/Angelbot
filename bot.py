import os
import requests
import pytz
import yfinance as yf
from datetime import datetime

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
LIMA = pytz.timezone("America/Lima")

PARES = {
    "ONDO-USD": "ONDO/USD",
    "DYDX-USD": "DYDX/USD",
    "RAY-USD": "RAY/USD",
    "TAO-USD": "TAO/USD",
    "ORDI-USD": "ORDI/USD",
    "SOL-USD": "SOL/USD",
    "ICP-USD": "ICP/USD",
    "TIA-USD": "CELESTIA/USD",
    "^GDAXI": "GER30 (DAX)"
}

HORARIOS = [9, 13, 16, 18]

def enviar(msg):
    if not BOT_TOKEN or not CHAT_ID:
        print("Error: BOT_TOKEN o CHAT_ID no configurados.")
        return
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "HTML"}, timeout=10)
    except Exception as e:
        print(f"Error enviando mensaje: {e}")

def estrategia1(df):
    if len(df) < 3:
        return None
    
    v1 = df.iloc[-3]
    v2 = df.iloc[-2]

    o1 = float(v1['Open'].iloc[0] if hasattr(v1['Open'], 'iloc') else v1['Open'])
    c1 = float(v1['Close'].iloc[0] if hasattr(v1['Close'], 'iloc') else v1['Close'])
    h1 = float(v1['High'].iloc[0] if hasattr(v1['High'], 'iloc') else v1['High'])
    l1 = float(v1['Low'].iloc[0] if hasattr(v1['Low'], 'iloc') else v1['Low'])

    o2 = float(v2['Open'].iloc[0] if hasattr(v2['Open'], 'iloc') else v2['Open'])
    c2 = float(v2['Close'].iloc[0] if hasattr(v2['Close'], 'iloc') else v2['Close'])
    h2 = float(v2['High'].iloc[0] if hasattr(v2['High'], 'iloc') else v2['High'])
    l2 = float(v2['Low'].iloc[0] if hasattr(v2['Low'], 'iloc') else v2['Low'])

    indecision = (h1 - l1) > 0 and abs(c1 - o1) < (h1 - l1) * 0.18
    fuerza = (h2 - l2) > 0 and abs(c2 - o2) > (h2 - l2) * 0.60

    if indecision and fuerza:
        if c2 > o2:
            return "🟢 COMPRA E1: Indecisión + Fuerza"
        if c2 < o2:
            return "🔴 VENDE E1: Indecisión + Fuerza"
    return None

def estrategia2(df):
    if len(df) < 7:
        return None
    
    cuerpos = []
    for i in range(-7, -2):
        row = df.iloc[i]
        o = float(row['Open'].iloc[0] if hasattr(row['Open'], 'iloc') else row['Open'])
        c = float(row['Close'].iloc[0] if hasattr(row['Close'], 'iloc') else row['Close'])
        cuerpos.append(abs(c - o))
        
    promedio = sum(cuerpos) / len(cuerpos) if cuerpos else 0
    if promedio == 0:
        return None

    v = df.iloc[-2]
    o = float(v['Open'].iloc[0] if hasattr(v['Open'], 'iloc') else v['Open'])
    c = float(v['Close'].iloc[0] if hasattr(v['Close'], 'iloc') else v['Close'])

    if abs(c - o) > promedio * 1.8:
        if c > o:
            return "🔴 VENDE E2: Agotamiento -> Reversión"
        if c < o:
            return "🟢 COMPRA E2: Agotamiento -> Reversión"
    return None

ahora = datetime.now(LIMA)
h = ahora.hour

if h not in HORARIOS:
    enviar(f"⏰ Bot revisó {ahora.strftime('%H:%M')} Lima - Fuera de horario {HORARIOS}")
else:
    enviar(f"⏰ <b>SESIÓN {h}:00 INICIADA</b> - Chequeando {len(PARES)} pares")
    ops = 0
    for sym, nombre in PARES.items():
        try:
            df = yf.download(sym, period="1d", interval="5m", progress=False)
            df = df.dropna()
            
            if df.empty or len(df) < 10:
                continue

            senal = estrategia1(df) or estrategia2(df)
            if senal:
                enviar(f"{senal}\nPar: <b>{nombre}</b>\nHora: {ahora.strftime('%H:%M')} Lima\n💰 11 USD FIJO")
                ops += 1
        except Exception as e:
            print(f"Error procesando {sym}: {e}")

    enviar(f"📊 Sesión {h}:00 terminada - {ops} señales sent")
