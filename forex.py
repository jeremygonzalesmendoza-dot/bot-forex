import yfinance as yf
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import requests
import ta

NEWS_KEY = "c86852b9b54b499bb1adf65226f2e3f0"
FRED_KEY = "8a37f166be17bbc3250a1f55cf35b101"

PARES = {
    "1": "USD/JPY",
    "2": "CAD/JPY",
    "3": "EUR/USD",
    "4": "GBP/USD"
}

# series de FRED para la tasa de interés de cada país
TASAS = {
    "USD": "FEDFUNDS",
    "JPY": "IRSTCI01JPM156N",
    "CAD": "IRSTCI01CAM156N",
    "EUR": "IRSTCI01EZM156N",
    "GBP": "IRSTCI01GBM156N"
}

def obtener_datos(par):
    ticker = par.replace("/", "") + "=X"
    return yf.Ticker(ticker).history(period="60d", interval="1h")

def precio_en_vivo(data):
    return data["Close"].iloc[-1]

def tecnico_score(data):
    rsi = ta.momentum.RSIIndicator(data["Close"]).rsi().iloc[-1]
    ema50 = ta.trend.EMAIndicator(data["Close"], window=50).ema_indicator().iloc[-1]
    ema200 = ta.trend.EMAIndicator(data["Close"], window=200).ema_indicator().iloc[-1]
    macd = ta.trend.MACD(data["Close"]).macd_diff().iloc[-1]

    score = 50
    if rsi < 30: score += 15
    elif rsi > 70: score -= 15
    if ema50 > ema200: score += 15
    else: score -= 15
    if macd > 0: score += 20
    else: score -= 20
    return max(0, min(100, score))

def sentimiento_par(par):
    query = par.replace("/", " ")
    news = requests.get("https://newsapi.org/v2/everything",
        params={"q": query, "language": "en", "sortBy": "publishedAt",
                "pageSize": 20, "apiKey": NEWS_KEY}).json()
    sia = SentimentIntensityAnalyzer()
    scores = [sia.polarity_scores(a["title"])["compound"] for a in news["articles"]]
    promedio = sum(scores) / len(scores) if scores else 0
    return (promedio + 1) * 50

def tasa_de(moneda):
    base = "https://api.stlouisfed.org/fred/series/observations"
    r = requests.get(base, params={"series_id": TASAS[moneda], "api_key": FRED_KEY, "file_type": "json"}).json()
    return float(r["observations"][-1]["value"])

def fundamental_score(par):
    base_moneda, quote_moneda = par.split("/")
    tasa_base = tasa_de(base_moneda)
    tasa_quote = tasa_de(quote_moneda)
    diff = tasa_base - tasa_quote
    score = min(max((diff + 2) * 25, 0), 100)
    return score, tasa_base, tasa_quote

print("1) USD/JPY  2) CAD/JPY  3) EUR/USD  4) GBP/USD")
opcion = input("Elige un número: ")
par = PARES[opcion]

data = obtener_datos(par)
precio = precio_en_vivo(data)
pct_tecnico = tecnico_score(data)
pct_sentimiento = sentimiento_par(par)
pct_fundamental, tasa_base, tasa_quote = fundamental_score(par)

total = pct_tecnico * 0.5 + pct_sentimiento * 0.3 + pct_fundamental * 0.2
etiqueta = "ALCISTA" if total > 50 else "BAJISTA"

base_moneda, quote_moneda = par.split("/")
print(f"\n{par}: {etiqueta} {round(total)}%")
print(f"(Precio actual: {precio})")
print(f"Técnico: {round(pct_tecnico)}% | Sentimiento: {round(pct_sentimiento)}% | Fundamental: {round(pct_fundamental)}%")
print(f"Tasa {base_moneda}: {tasa_base}% vs Tasa {quote_moneda}: {tasa_quote}%")