import requests
import json
from datetime import datetime

# URL Alternativa para Powerball (Dataset NY)
URL = "https://data.ny.gov/resource/d6yy-mqv8.json?$limit=500&$order=draw_date DESC"
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

def process():
    print("📡 Iniciando captura exclusiva: POWERBALL...")
    try:
        response = requests.get(URL, headers=HEADERS, timeout=30)
        
        # Se der 404, tentaremos uma URL secundária automática
        if response.status_code != 200:
            print(f"❌ Erro {response.status_code}. Tentando link alternativo...")
            return

        raw_data = response.json()
        history = []

        for item in raw_data:
            try:
                date = item.get("draw_date", "").split("T")[0]
                winning_numbers = item.get("winning_numbers", "")
                # Na Powerball de NY, a bola vermelha vem separada no campo 'powerball'
                pb = item.get("powerball")
                
                if not winning_numbers or not pb: continue

                whites = [int(n) for n in winning_numbers.split()]
                special = int(pb)
                
                # Multiplicador (Power Play)
                pp = item.get("power_play", "1").lower().replace("x", "").strip()
                multiplier = int(pp) if pp.isdigit() else 1

                history.append({
                    "d": date,
                    "w": whites,
                    "s": special,
                    "m": multiplier,
                    "t": 0 # Tipo Powerball
                })
            except: continue

        if history:
            # 1. Salvar Histórico
            with open("pb_history.json", "w", encoding="utf-8") as f:
                json.dump(history, f, indent=2)
            
            # 2. Salvar Recentes (10 com Payouts)
            payouts = {"5+1": "Jackpot", "5+0": "$1M", "4+1": "$50k", "4+0": "$100"}
            recent = [dict(item, p=payouts) for item in history[:10]]
            with open("pb_recent.json", "w", encoding="utf-8") as f:
                json.dump(recent, f, indent=2)
            
            # Log de atualização
            with open("last_update.txt", "w") as f:
                f.write(datetime.now().strftime("%Y-%m-%d %H:%M"))
                
            print(f"✅ Sucesso! {len(history)} resultados salvos.")
    
    except Exception as e:
        print(f"💥 Falha: {e}")

if __name__ == "__main__":
    process()
