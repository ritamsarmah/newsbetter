#!/usr/bin/env python3

import json
import yaml

from datetime import datetime
from newsletter import Newsletter
from sections.header import HeaderSection
from sections.youtube import YouTubeSection

CONFIG_FILE = "./config.json"

if __name__ == "__main__":
    with open(CONFIG_FILE) as f:
        config = json.load(f)

    sources_file = config['sources_path']
    with open(sources_file) as file:
        sources = yaml.load(file, Loader=yaml.FullLoader)

    template_file = config['template_path']
    with open(template_file) as file:
        html_template = file.read()

    api_keys = config['api_keys']

    newsletter = Newsletter(html_template, [
        HeaderSection(api_keys['weather']),
        YouTubeSection(sources['youtube'], api_keys['youtube'])
    ])

    # Add subject to email_info
    config['email_info']['subject'] = f"{datetime.now().strftime('%B %d, %Y')}"

    # Send email using email info in config
    newsletter.send_email(config['email_info'])
