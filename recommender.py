import requests
from bs4 import BeautifulSoup

import requests
from bs4 import BeautifulSoup

def get_stockrecommendations():
    url = "https://indian-stock-exchange-api2.p.rapidapi.com/trending"

    headers = {
        "x-rapidapi-key": "f7000d1082msh86835a1eeeb4a73p15c316jsn35159586df39",
        "x-rapidapi-host": "indian-stock-exchange-api2.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers)
    recommendations = []
    # print(response.json())
    if response.status_code == 200:
        response = response.json()
        trending_stocks = response['trending_stocks']
        list = trending_stocks["top_gainers"]
        for i in list:
            stock = i['company_name']
            recommendations.append(stock)
        
    # # return response['trending_stocks']
    # # print(response.json())'
    # print(recommendations)
    return recommendations

def get_sellrecommendations():
    url = "https://indian-stock-exchange-api2.p.rapidapi.com/trending"

    headers = {
        "x-rapidapi-key": "f7000d1082msh86835a1eeeb4a73p15c316jsn35159586df39",
        "x-rapidapi-host": "indian-stock-exchange-api2.p.rapidapi.com"
    }


    response = requests.get(url, headers=headers)
    recommendations = []
    # print(response.json())
    if response.status_code == 200:
        response = response.json()
        trending_stocks = response['trending_stocks']
        list = trending_stocks["top_losers"]
        # print(response.json())
        for i in list:
            stock = i['company_name']
            recommendations.append(stock)
    # # return response['trending_stocks']
    # # print(response.json())'
    # print(recommendations)
    return recommendations