#!/usr/bin/env python3

import os
import pickle

from apiclient.discovery import build
from datetime import datetime, timedelta
from jinja2 import Template
from newsletter import Section


class YouTubeSection(Section):
    def __init__(self, channels, api_key):
        super().__init__("youtube")

        self.api_key = api_key
        self.channels = channels
        self.youtube = build("youtube", "v3", developerKey=self.api_key)

        # Load channel ID cache
        self.cache_file = "./cache.pkl"
        if not os.path.isfile(self.cache_file):
            self.cache = {}
        else:
            with open(self.cache_file, 'rb+') as f:
                self.cache = pickle.load(f)

    def html(self):
        return Template("""
        <h2>Videos</h2>
        <ul>
        {% for video in videos %}
            <li><a href="{{ video['url'] }}">{{ video['title'] }}</a></li>
        {% endfor %}
        </ul>
        """).render(videos=self.videos())

    def videos(self):
        today = datetime.now()
        yesterday = today - timedelta(days=1)
        videos = map(
            lambda channel: self.latest_upload(channel, yesterday),
            self.channels)
        videos = list(filter(None, videos))

        return videos

    def latest_upload(self, channel, since):
       # Search for channel by name and get ID
        if channel in self.cache:
            channel_id = self.cache[channel]
        else:
            request = self.youtube.search().list(
                q=channel, type="channel", part="id", maxResults=1)
            channel_id = request.execute()['items'][0]['id']['channelId']
            self.cache[channel] = channel_id
            with open(self.cache_file, 'wb+') as f:
                pickle.dump(self.cache, f)

        # Get uploads playlist
        request = self.youtube.channels().list(
            part="contentDetails",
            id=channel_id
        )

        response = request.execute()
        uploadsPlaylistId = response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

        # Retrieve uploaded ideos
        request = self.youtube.playlistItems().list(
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
