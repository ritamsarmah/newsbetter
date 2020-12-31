#!/usr/bin/env python3

import geocoder
import json
import yaml

from datetime import datetime
from newsbetter import Newsletter
from sections.header import HeaderSection
from sections.youtube import YouTubeSection

CONFIG_FILE = "./config.json"

if __name__ == "__main__":
    with open(CONFIG_FILE) as f:
        config = json.load(f)

    with open(config['sources_path']) as file:
        sources = yaml.load(file, Loader=yaml.FullLoader)

    with open(config['template_path']) as file:
        html_template = file.read()

    api_keys = config['api_keys']
    location = geocoder.ip('me').city

    # Create newsletter with an HTML template string and sections
    newsletter = Newsletter(html_template, [
        HeaderSection(location, api_keys['weather']),
        YouTubeSection(sources['youtube'], api_keys['youtube'])
    ])

    # Add subject to email_info
    config['email_info']['subject'] = f"{datetime.now().strftime('%B %d, %Y')}"

    # Send using email info in config
    newsletter.send(**config['email_info'])
