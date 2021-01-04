#!/usr/bin/env python3

import feedparser

from jinja2 import Template
from newsbetter import Section


class RSSSection(Section):
    def __init__(self, feeds):
        super().__init__("rss")
        self.feeds = feeds

    def html(self, recipient):
        links = self.latest_entries()

        if len(links) == 0:
            return ""
        else:
            return Template("""
            <h2>News</h2>
            {% for (title, entries) in feeds.items() %}
                <h3>{{ title }}</h3>
                <ul>
                {% for entry in entries %}
                    <li>
                        <a href="{{ entry['link'] }}">{{ entry['title'] }}</a>
                    </li>
                {% endfor %}
                </ul>
            {% endfor %}
            """).render(feeds=links)

    def latest_entries(self):
        entries = {}
        number_of_entries = 3
        for feed in self.feeds:
            d = feedparser.parse(feed)
            entries[d.feed.title] = d.entries[:number_of_entries]

        return entries
