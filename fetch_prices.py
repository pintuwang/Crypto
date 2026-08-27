import os
import json
import requests
from datetime import datetime, timezone, timedelta

SGT = timezone(timedelta(hours=8))

# ---------------------------------------------------------------------------
# CoinGecko API key routing
#   Demo keys (free) start with "CG-" → api.coingecko.com + x-cg-demo-api-key
#   Paid keys (Analyst/Lite/Pro/Pro+) → pro-api.coingecko.com + x-cg-pro-api-key
#   No key at all                     → api.coingecko.com, no header (keyless)
# ---------------------------------------------------------------------------
API_KEY = os.environ.get('COINGECKO_API_KEY', '').strip()

if API_KEY and not API_KEY.startswith('CG-'):
    BASE_URL = 'https://pro-api.coingecko.com/api/v3'
    HEADERS  = {'x-cg-pro-api-key': API_KEY}
    TIER     = 'Pro (paid)'
elif API_KEY:
    BASE_URL = 'https://api.coingecko.com/api/v3'
    HEADERS  = {'x-cg-demo-api-key': API_KEY}
    TIER     = 'Demo (free)'
else:
    BASE_URL = 'https://api.coingecko.com/api/v3'
    HEADERS  = {}
    TIER     = 'Keyless (public)'

def get(path, **params):
    url = f"{BASE_URL}{path}"
    r = requests.get(url, headers=HEADERS, params=params, timeout=15)
    r.raise_for_status()
    return r.json()

def run():
    print(f"CoinGecko tier: {TIER}")

    prices    = get('/simple/price', ids='bitcoin,ripple', vs_currencies='usd,sgd')
    btc_chart = get('/coins/bitcoin/market_chart', vs_currency='usd', days=1)
    xrp_chart = get('/coins/ripple/market_chart',   vs_currency='usd', days=1)

    payload = {
        "last_update": datetime.now(SGT).strftime("%Y-%m-%d %H:%M SGT"),
        "prices": {
            "bitcoin": prices.get("bitcoin", {}),
            "ripple":  prices.get("ripple",  {})
        },
        "charts": {
            "bitcoin": btc_chart.get("prices", []),
            "ripple":  xrp_chart.get("prices", [])
        }
    }

    os.makedirs('data', exist_ok=True)
    with open('data/prices.json', 'w') as f:
        json.dump(payload, f)

    btc = prices['bitcoin']['usd']
    xrp = prices['ripple']['usd']
    print(f"✓ BTC ${btc:,.2f} | XRP ${xrp:.4f} — saved to data/prices.json")

if __name__ == '__main__':
    run()
