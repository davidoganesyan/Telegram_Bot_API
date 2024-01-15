import requests

# Запрос текущего курса доллара

data = requests.get('https://www.cbr-xml-daily.ru/daily_json.js').json()
USD = data['Valute']['USD']['Value']
