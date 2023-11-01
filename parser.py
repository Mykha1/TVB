from bs4 import BeautifulSoup
import requests


def daily_weather():
    url = 'https://weather.com/cs-CZ/weather/today/l/634220104741c219950a0831d75ea95491e6870855b74dc00c0d07f431ced9f6'
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        temperature = soup.find('span', {'data-testid': 'TemperatureValue'}).text
        condition = soup.find('div', {'data-testid': 'wxPhrase'}).text

        return f'{temperature}, {condition}'
    else:
        return 'Unable to parse data'


if __name__ == '__main__':
    weather_info = daily_weather()
    print(weather_info)
