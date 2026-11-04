import yfinance as yf

def precio_en_vivo(par="JPY=X"):  # USD/JPY en yfinance se escribe así
    data = yf.Ticker(par).history(period="1d", interval="1m")
    return data["Close"].iloc[-1]

precio = precio_en_vivo()
print(f"Precio actual USD/JPY: {precio}")