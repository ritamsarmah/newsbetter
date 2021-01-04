#!/usr/bin/env python3

import abc
import smtplib
import ssl

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Template


class Newsletter:
    def __init__(self, html_template, sections=[]):
        self.html_template = Template(html_template)
        self.sections = {
            section.identifier: section for section in sections}

    def add_section(self, section):
        self.sections[section.identifier] = section

    def render(self, recipient):
        identifiers = {identifier: section.html(recipient)
                       for (identifier, section) in self.sections.items()}

        rendered_email = self.html_template.render(**identifiers)
        return rendered_email

    def send(self, sender, subject, recipients):
        DEFAULT_SMTP_PORT = 25

        # Create secure connection with server and send email to recipients
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(sender["smtp"], sender.get("port", DEFAULT_SMTP_PORT), context=context) as server:
            server.login(sender["email"], sender["password"])

            for recipient in recipients:
                message = MIMEMultipart('alternative')
                message['Subject'] = subject
                message['From'] = f"{sender['name']} <{sender['email']}>"
                message['To'] = recipient["email"]
                message.attach(MIMEText(self.render(recipient), "html"))

                server.sendmail(sender['email'],
                                recipient['email'],
                                message.as_string())

                print(f"Sent: {recipient['name']} <{recipient['email']}>")


class Section(metaclass=abc.ABCMeta):
    def __init__(self, identifier):
        self.identifier = identifier    # Identifier used in template HTML

    @abc.abstractmethod
    def html(self, recipient):
        """ Return content formatted as HTML """
        pass
