import yfinance as yf
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import requests

NEWS_KEY = "c86852b9b54b499bb1adf65226f2e3f0"
FRED_KEY = "8a37f166be17bbc3250a1f55cf35b101"

PARES = {
    "1": "USD/JPY",
    "2": "CAD/JPY",
    "3": "EUR/USD",
    "4": "GBP/USD"
}

def precio_en_vivo(par):
    ticker = par.replace("/", "") + "=X"
    data = yf.Ticker(ticker).history(period="1d", interval="1m")
    return data["Close"].iloc[-1]

def sentimiento_par(par):
    query = par.replace("/", " ")
    news = requests.get("https://newsapi.org/v2/everything",
        params={"q": query, "language": "en", "sortBy": "publishedAt",
                "pageSize": 20, "apiKey": NEWS_KEY}).json()
    sia = SentimentIntensityAnalyzer()
    scores = [sia.polarity_scores(a["title"])["compound"] for a in news["articles"]]
    promedio = sum(scores) / len(scores) if scores else 0
    return (promedio + 1) * 50

def fundamental_fed_boj():
    base = "https://api.stlouisfed.org/fred/series/observations"
    fed = requests.get(base, params={"series_id": "FEDFUNDS", "api_key": FRED_KEY, "file_type": "json"}).json()
    fed_rate = float(fed["observations"][-1]["value"])
    return fed_rate

print("1) USD/JPY  2) CAD/JPY  3) EUR/USD  4) GBP/USD")
opcion = input("Elige un número: ")
par = PARES[opcion]

precio = precio_en_vivo(par)
sentimiento = sentimiento_par(par)
fed_rate = fundamental_fed_boj()

print(f"Precio {par}: {precio}")
print(f"Sentimiento: {sentimiento}%")
print(f"Tasa Fed actual: {fed_rate}%")