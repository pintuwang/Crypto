import os
import json
import requests
from datetime import datetime, timezone, timedelta

SGT = timezone(timedelta(hours=8))

API_KEY  = os.environ.get('COINGECKO_API_KEY', '').strip()
BASE_URL = 'https://pro-api.coingecko.com/api/v3' if API_KEY else 'https://api.coingecko.com/api/v3'
HEADERS  = {'x-cg-pro-api-key': API_KEY} if API_KEY else {}

def get(path, **params):
    url = f"{BASE_URL}{path}"
    r = requests.get(url, headers=HEADERS, params=params, timeout=15)
    r.raise_for_status()
    return r.json()

def run():
    tier = "Pro" if API_KEY else "Free (public)"
    print(f"CoinGecko tier: {tier}")

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
