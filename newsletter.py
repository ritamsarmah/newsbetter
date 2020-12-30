#!/usr/bin/env python3

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from apiclient.discovery import build
from datetime import datetime, timedelta

import feedparser
import geocoder
import json
import os
import pickle
import smtplib
import ssl
import requests
import yaml

CACHE_FILE = "./cache.pkl"
CONFIG_FILE = "./config.json"
SOURCES_FILE = "./sources.yaml"


def get_weather():
    location = geocoder.ip('me')

    url = f'https://api.openweathermap.org/data/2.5/weather?q={location.city}&units=imperial&appid={weather_api_key}'
    response = requests.get(url).json()
    description = response["weather"][0]["main"]
    low = int(response["main"]["temp_min"])
    high = int(response["main"]["temp_max"])

    return f"{description}, H: {high}&deg; L: {low}&deg;"


def get_quote():
    url = 'https://quotes.rest/qod?category=inspire'
    headers = {'content-type': 'application/json'}
    response = requests.get(url, headers=headers).json()
    quote = response['contents']['quotes'][0]
    return f"{quote['quote']} &mdash;{quote['author']}"


def get_latest_video(channel, since, cache):
    # Search for channel by name and get ID
    if channel in cache:
        channel_id = cache[channel]
    else:
        request = youtube.search().list(q=channel, type="channel", part="id", maxResults=1)
        channel_id = request.execute()['items'][0]['id']['channelId']
        cache[channel] = channel_id
        with open(CACHE_FILE, 'wb+') as f:
            pickle.dump(cache, f)

    # Get uploads playlist
    request = youtube.channels().list(
        part="contentDetails",
        id=channel_id
    )

    response = request.execute()
    uploadsPlaylistId = response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

    # Retrieve uploaded ideos
    request = youtube.playlistItems().list(
        part="snippet,contentDetails",
        playlistId=uploadsPlaylistId,
        maxResults=1
    )

    response = request.execute()
    latest_video = response['items'][0]
    publish_date = datetime.strptime(
        latest_video['contentDetails']['videoPublishedAt'], "%Y-%m-%dT%H:%M:%SZ")

    # Return only if video has been published after "since" date
    if publish_date > since:
        # Retrieve and return metadata or video
        return {
            "title": f"{latest_video['snippet']['title']}",
            "subtitle": channel,
            "url": f"https://www.youtube.com/embed/{latest_video['contentDetails']['videoId']}"
        }
    else:
        return None


def build_newsletter(today, sections):
    content = ""
    for (section, links) in sections.items():
        content += f"<h2>{section}</h2>"
        content += "<ul>"
        for link in links:
            content += f"<li><a href={link['url']}>{link['title']}</a></li>"
        content += "</ul>"

    return f"""\
    <html>
        <style>
        body {{ font-family: "Helvetica", sans-serif; }}
        </style>
        <body>
            <h1>The Daily Brief</h1>
            <p>
                {today.strftime("%A, %B %d, %Y")}
                <br>
                {get_weather()}
            </p>
            <em>{get_quote()}</em>
            {content}
        </body>
    </html>"""


if __name__ == "__main__":
    if not os.path.isfile(CACHE_FILE):
        yt_cache = {}
    else:
        with open(CACHE_FILE, 'rb+') as f:
            yt_cache = pickle.load(f)

    with open(CONFIG_FILE) as f:
        config = json.load(f)
        weather_api_key = config['weather_api_key']
        youtube_api_key = config['youtube_api_key']

    with open(SOURCES_FILE) as file:
        sources = yaml.load(file, Loader=yaml.FullLoader)

    today = datetime.now()
    yesterday = today - timedelta(days=1)

    # Get RSS links
    # rss = {}

    # for feed in sources['rss']:
    #     d = feedparser.parse(feed)
    #     title = d['feed']['title']
    #     links = list(map(feed[:5]))
    #     rss[title] = {

    #     }

    # Get YouTube video links
    youtube = build("youtube", "v3", developerKey=youtube_api_key)
    videos = map(
        lambda channel: get_latest_video(
            channel, since=yesterday, cache=yt_cache),
        sources['youtube'])
    videos = list(filter(None, videos))

    newsletter = build_newsletter(today, {
        "Videos": videos
    })

    # # Create message container - the correct MIME type is multipart/alternative.
    message = MIMEMultipart('alternative')
    message['Subject'] = f"{today.strftime('%B %d, %Y')}"
    message['From'] = f"Daily Brief <{config['from']}>"
    message['To'] = config['to']

    message.attach(MIMEText(newsletter, "html"))

    # Create secure connection with server and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(config['from'], config['password'])
        server.sendmail(
            config['from'], config['to'], message.as_string()
        )
