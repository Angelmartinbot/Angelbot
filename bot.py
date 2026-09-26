import os, time, requests
from datetime import datetime
import pytz

TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
LIMA = pytz.timezone("America/Lima")

def enviar(msg):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}, timeout=15)

def obtener_respuesta(last_id):
    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
    r = requests.get(url, params={"offset": last_id+1, "timeout": 30}, timeout=35).json()
    for upd in r.get("result", []):
        if "message" in upd and str(upd["message"]["chat"]["id"]) == str(CHAT_ID):
            txt = upd["message"].get("text","").strip().upper()
            if txt in ["G", "P", "G✅", "P❌"]:
                return txt[0], upd["update_id"]
    return None, last_id

# --- INICIO SESION ---
ahora = datetime.now(LIMA)
sesion = f"{ahora.hour}:00"
enviar(f"🟢 *SESION {sesion} LIMA INICIADA*\nPar: EUR/USD OTC (Exnova)\nInversion: $11\nEstrategias:\n1️⃣ CONTINUIDAD: Doji/Martillo + fuerza\n2️⃣ REVERSION: Vela gigante agotamiento\n\nMax 5 ops | Candado 3 P seguidas\n\nEscribe G si ganaste, P si perdiste")

ops = 0
ganadas = 0
perdidas_seg = 0
perdidas_total = 0
last_id = 0

# obtener ultimo update_id
try:
    r = requests.get(f"https://api.telegram.org/bot{TOKEN}/getUpdates", timeout=10).json()
    if r.get("result"): last_id = r["result"][-1]["update_id"]
except: pass

while ops < 5:
    ops += 1
    enviar(f"⏰ *SEÑAL {ops}/5* - {datetime.now(LIMA).strftime('%H:%M')} LIMA\nBusca tu estrategia y opera.\nResponde G o P")

    # Esperar respuesta G/P (max 10 min por op)
    espera = 0
    while espera < 600:
        res, last_id = obtener_respuesta(last_id)
        if res:
            if res == "G":
                ganadas += 1
                perdidas_seg = 0
                enviar(f"✅ G registrada | Marcador {ganadas}-{perdidas_total+ (1 if res=='P' else 0)} | Racha P: {perdidas_seg}")
            else:
                perdidas_total += 1
                perdidas_seg += 1
                enviar(f"❌ P registrada | Marcador {ganadas}-{perdidas_total} | Racha P: {perdidas_seg}")
                if perdidas_seg >= 3:
                    enviar(f"🔴 *CANDADO ACTIVADO* - 3 P seguidas. Sesion {sesion} cerrada por seguridad.\nFinal: {ganadas}-{perdidas_total}")
                    exit()
            break
        time.sleep(5)
        espera += 5
    else:
        enviar(f"⚠️ Sin respuesta en 10min, paso a siguiente")

    if ops < 5:
        time.sleep(10)

enviar(f"🔴 *FIN SESION {sesion}* | Resultado final: {ganadas}-{perdidas_total} ({'5-0' if perdidas_total==0 else '4-1' if perdidas_total==1 else '3-2' if perdidas_total==2 else f'{ganadas}-{perdidas_total}'})")
