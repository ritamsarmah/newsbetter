#!/usr/bin/env python3

import abc
import smtplib
import ssl

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from jinja2 import Template


class Newsletter:
    def __init__(self, html_template, sections=[]):
        self.html_template = Template(html_template)
        self.sections = {section.name: section.html() for section in sections}

    def add_section(self, section):
        self.sections[section.name] = section.html()

    def render(self):
        return self.html_template.render(**self.sections)

    def send_email(self, info):
        sender_email = info['sender_email']
        sender_name = info['sender_name']
        sender_password = info['sender_password']
        subject = info['subject']
        recipients = info['recipients']

        # Create message container - the correct MIME type is multipart/alternative.
        message = MIMEMultipart('alternative')
        message['Subject'] = subject
        message['From'] = f"{sender_name} <{sender_email}>"

        message.attach(MIMEText(self.render(), "html"))

        # Create secure connection with server and send email to recipients
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(sender_email, sender_password)

            for recipient in recipients:
                message['To'] = recipient
                server.sendmail(sender_email, recipient, message.as_string())


class Section(metaclass=abc.ABCMeta):
    def __init__(self, name):
        self.name = name    # Variable name used in template HTML

    @abc.abstractmethod
    def html(self):
        """ Return content formatted as HTML """
        pass
