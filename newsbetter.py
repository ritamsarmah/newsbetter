#!/usr/bin/env python3

import abc
import smtplib
import ssl

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Template, Environment, BaseLoader, DebugUndefined


class Newsletter:
    reserved_identifiers = ['_name', '_email']

    def __init__(self, html_template, sections=[]):
        self.html_template = Template(html_template)
        self.sections = set(sections)

    def add_section(self, section):
        if section.identifier in Newsletter.reserved_identifiers:
            raise(NameError(
                f"{section.identifier} is a reserved identifier and cannot be used for {section.__name__}. Please provide a different one."))

        self.sections.add(section)

    def render(self, recipient):
        identifiers = {section.identifier: section.html(recipient)
                       for section in self.sections}

        identifiers['_name'] = recipient['name']
        identifiers['_email'] = recipient['email']

        rendered_email = self.html_template.render(**identifiers)
        return rendered_email

    def send(self, sender_email, sender_name, sender_password, subject, recipients):
        # TODO: add support for other email providers

        # Create secure connection with server and send email to recipients
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(sender_email, sender_password)

            for recipient in recipients:
                # Create message container - the correct MIME type is multipart/alternative.
                message = MIMEMultipart('alternative')
                message['Subject'] = subject
                message['From'] = f"{sender_name} <{sender_email}>"
                message['To'] = recipient["email"]
                message.attach(MIMEText(self.render(recipient), "html"))

                server.sendmail(
                    sender_email, recipient['email'], message.as_string())
                print(f"Sent: {recipient['name']} <{recipient['email']}>")


class Section(metaclass=abc.ABCMeta):
    def __init__(self, identifier):
        self.identifier = identifier    # Identifier used in template HTML

    @abc.abstractmethod
    def html(self, recipient):
        """ Return content formatted as HTML """
        pass
