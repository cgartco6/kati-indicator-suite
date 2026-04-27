# test_telegram.py
import requests

TOKEN = "8669479635:AARfr7RuR-W_K1sjn7XOyDmOHRjP8ughSBMU"   # your token
url = f"https://api.telegram.org/bot{TOKEN}/getMe"
r = requests.get(url).json()
print(r)
