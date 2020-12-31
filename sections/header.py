#!/usr/bin/env python3

import requests

from datetime import datetime
from newsbetter import Section
from jinja2 import Template


class HeaderSection(Section):
    def __init__(self, location, weather_key):
        super().__init__("header")
        self.location = location
        self.weather_key = weather_key

    def html(self, recipient):
        return Template("""
        <h1>Daily Briefing</h1>
        <p>
            {{ date }}
            <br>
            {{ forecast }}
        </p>
        <em>{{ quote }}</em>
        """).render(
            name=recipient["name"],
            date=datetime.now().strftime("%A, %B %d, %Y"),
            forecast=self.weather_forecast(),
            quote=self.daily_quote()
        )

    def weather_forecast(self):
        url = f'https://api.openweathermap.org/data/2.5/weather?q={self.location}&units=imperial&appid={self.weather_key}'
        response = requests.get(url).json()
        description = response["weather"][0]["main"]
        low = int(response["main"]["temp_min"])
        high = int(response["main"]["temp_max"])

        return f"{description} | H: {high}&deg; L: {low}&deg;"

    def daily_quote(self):
        url = 'https://quotes.rest/qod?category=inspire'
        headers = {'content-type': 'application/json'}
        response = requests.get(url, headers=headers).json()
        quote = response['contents']['quotes'][0]
        return f"{quote['quote']} &mdash;{quote['author']}"
