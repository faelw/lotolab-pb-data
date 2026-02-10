import requests
import json
import os
from datetime import datetime

# ==========================================
# LISTA DE FONTES (Plano A, B e C)
# ==========================================
URLS_FONTE = [
    # 1. API Socrata (Endpoint JSON Oficial)
    "https://data.ny.gov/resource/d6yy-mqv8.json?$limit=500&$order=draw_date DESC",
    
    # 2. API Socrata (Endpoint Alternativo / Catálogo)
    "https://data.ny.gov/resource/82fy-idv3.json?$limit=500&$order=draw_date DESC",
    
    # 3. Backup Estático (Caso tudo falhe, usa um espelho raw do GitHub)
    "https://raw.githubusercontent.com/faelw/lotolab-data-server/main/pb_history.json"
]

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json'
}

def fetch_data():
    """Tenta baixar de várias fontes até conseguir"""
    for i, url in enumerate(URLS_FONTE):
        print(f"📡 Tentativa {i+1}: Conectando a {url[:40]}...")
        try:
            response = requests.get(url, headers=HEADERS, timeout=20)
            if response.status_code == 200:
                print(f"✅ Conexão BEM SUCEDIDA na fonte {i+1}!")
                return response.json()
            else:
                print(f"❌ Falha na fonte {i+1}: Erro {response.status_code}")
        except Exception as e:
            print(f"⚠️ Erro de conexão na fonte {i+1}: {e}")
    return None

def process():
    print("🚀 Iniciando Motor LotoLab (Multi-Source)...")
    
    raw_data = fetch_data()
    
    if not raw_data:
        print("💥 ERRO CRÍTICO: Todas as APIs falharam.")
        # Salva log de erro para o Git
        with open("error_log.txt", "w") as f:
            f.write(f"Falha total em {datetime.now()}")
        return

    history = []
    seen_dates = set()

    print("⚙️ Processando dados...")
    for item in raw_data:
        try:
            # Normaliza Data (algumas APIs usam 'd', outras 'draw_date')
            date = item.get("draw_date") or item.get("d") or ""
            date = str(date).split("T")[0]
            
            if not date or date in seen_dates: continue

            # Normaliza Números
            # Tenta ler como string "10 20 30" ou lista [10, 20, 30]
            win_val = item.get("winning_numbers") or item.get("w")
            if not win_val: continue
            
            if isinstance(win_val, list):
                whites = [int(n) for n in win_val]
            else:
                whites = [int(n) for n in str(win_val).split()]

            # Normaliza Powerball
            pb_val = item.get("powerball") or item.get("s")
            if pb_val is None: continue
            special = int(pb_val)

            # Normaliza Multiplicador
            m_val = item.get("power_play") or item.get("m") or "1"
            multiplier = int(str(m_val).lower().replace("x", "").strip()) if str(m_val).isdigit() else 1

            history.append({
                "d": date,
                "w": whites,
                "s": special,
                "m": multiplier,
                "t": 0
            })
            seen_dates.add(date)

        except Exception:
            continue

    if history:
        # Ordenar e Salvar
        history.sort(key=lambda x: x["d"], reverse=True)
        
        with open("pb_history.json", "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2)
            
        payouts = {"5+1": "Jackpot", "5+0": "$1M", "4+1": "$50k", "4+0": "$100"}
        recent = [dict(item, p=payouts) for item in history[:10]]
        
        with open("pb_recent.json", "w", encoding="utf-8") as f:
            json.dump(recent, f, indent=2)
            
        with open("last_update.txt", "w") as f:
            f.write(f"Atualizado via Multi-API em {datetime.now()}")

        # Remove log de erro antigo se existir
        if os.path.exists("error_log.txt"): os.remove("error_log.txt")
        
        print(f"🏆 SUCESSO! {len(history)} resultados gerados.")
    else:
        print("⚠️ Dados baixados mas nenhum válido encontrado.")

if __name__ == "__main__":
    process()
