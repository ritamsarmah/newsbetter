# Newsbetter

A simple library for generating and sending personalized newsletters using [Jinja](https://jinja.palletsprojects.com/en/2.11.x/) templates.

## Getting Started

- Add `newsbetter.py` to your project
- Install Jinja using `pip install jinja2`

### Sending a Newsletter

```python
from newsletter import Newsletter, Section

# A section to be included in the newsletter
class HelloSection(Section):
	def __init__(self):
        # "hello" is identifier in template identifier
		super().__init__("hello")
        
	def html(self, recipient):
        return f"<p>Hello, {recipient["name"]}!</p>"

if __name__ == "__main__":
    # Specify layout of sections using Jinja template syntax
    html_template = """
    <html lang="en">
      <body>
        {{ hello }} <!-- Replaced by result of HelloSection.html() -->
      </body>
    </html>
    """

    newsletter = Newsletter(html_template)

    # Include the section in the newsletter
    newsletter.add_section(HelloSection())

    email_info = {
        "sender_email": "sender@gmail.com", # Only supports Gmail for now
        "sender_name": "Sender",
        "sender_password": "sender_password",
        "subject": "Hello there!"
        "recipients": [
            {
                "name": "First Recipient"
                "email": "recipient1@email.com"
            },
            {
                "name": "Second Recipient"
                "email": "recipient2@email.com"
            }
        ]
    }

    # Send newsletter to recipients
    newsletter.send(**email_info)
```

### Sample Newsletter Template

A newsletter template for a "Daily Briefing"  is included in the `example` directory with sections that includes weather info, RSS feeds, and latest YouTube channel uploads. Run the example using `main.py` after running `pip install requirements.txt` and creating the following two configuration files in the same directory:

1. `config.json`

    ```json
    {
      "sources_path": "/path/to/sources.yaml",
      "template_path": "/path/to/template.html",
      "email_info": {
        "sender_email": "SENDER@gmail.com",
        "sender_name": "SENDER",
        "sender_password": "PASSWORD",
        "recipients": [
          {
            "name": "RECIPIENT NAME",
            "email": "RECIPIENT@EMAIL.TLD"
          }
        ]
      },
      "api_keys": {
        "youtube": "YOUTUBE_DATA_API_KEY",
        "weather": "OPEN_WEATHER_API_KEY"
      }
    }
    ```

2. `sources.yaml` (with example sources)

    ```
    rss:
    	- https://news.ycombinator.com/rss
    	- https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml
    youtube:
    	- TED-Ed
        - Verge Science
        - Vox
    ```

    