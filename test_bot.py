import requests
TOKEN = "8669479635:AAFr7RuR-W_K1sjn7XOyDmOHRJp8ughSBMU"  # your corrected token
url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
response = requests.get(url).json()
print(response)
