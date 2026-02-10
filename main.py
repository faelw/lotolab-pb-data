import requests
import json
from datetime import datetime

# URL PLANO B (Link direto do Dataset de NY)
URL = "https://data.ny.gov/resource/d6yy-mqv8.json?$limit=500"
HEADERS = {'User-Agent': 'Mozilla/5.0'}

def process():
    print("📡 Tentando conexão com a API da Powerball...")
    try:
        response = requests.get(URL, headers=HEADERS, timeout=30)
        
        if response.status_code != 200:
            print(f"❌ Erro na API: {response.status_code}")
            # Cria um arquivo vazio para o Git não dar erro de 'pathspec'
            with open("error_log.txt", "w") as f:
                f.write(f"Erro {response.status_code} em {datetime.now()}")
            return

        raw_data = response.json()
        history = []

        for item in raw_data:
            try:
                # Na Powerball de NY, os campos são 'draw_date', 'winning_numbers' e 'powerball'
                date = item.get("draw_date", "").split("T")[0]
                win_nums = item.get("winning_numbers", "")
                pb = item.get("powerball", "")
                
                if not date or not win_nums or not pb:
                    continue

                history.append({
                    "d": date,
                    "w": [int(n) for n in win_nums.split()],
                    "s": int(pb),
                    "m": int(item.get("power_play", 1)),
                    "t": 0
                })
            except:
                continue

        if history:
            # Ordenar por data (mais recente primeiro)
            history.sort(key=lambda x: x["d"], reverse=True)
            
            # Salvar Histórico
            with open("pb_history.json", "w", encoding="utf-8") as f:
                json.dump(history, f, indent=2)
            
            # Salvar Recentes (10 com Payouts)
            payouts = {"5+1": "Jackpot", "5+0": "$1M", "4+1": "$50k", "4+0": "$100"}
            recent = [dict(item, p=payouts) for item in history[:10]]
            with open("pb_recent.json", "w", encoding="utf-8") as f:
                json.dump(recent, f, indent=2)
                
            print(f"✅ Sucesso! {len(history)} resultados processados.")
        
    except Exception as e:
        print(f"💥 Erro fatal: {e}")

if __name__ == "__main__":
    process()
