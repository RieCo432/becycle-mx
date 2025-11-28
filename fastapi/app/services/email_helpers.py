import os
import smtplib
import ssl
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
from uuid import UUID
from jinja2 import Environment, FileSystemLoader, select_autoescape

import app.schemas as schemas

GOOGLE_APP_PASSWORD = os.environ['GOOGLE_APP_PASSWORD']
GOOGLE_ACCOUNT = os.environ['GOOGLE_ACCOUNT']
EMAIL_FROM = os.environ['EMAIL_FROM']
SMTP_PORT = int(os.environ['SMTP_PORT'])
SMTP_SERVER = os.environ['SMTP_SERVER']
API_HOST_ADDRESS = os.environ['API_HOST_ADDRESS']
API_HOST_PORT = os.environ['API_HOST_PORT']
PRODUCTION = os.environ['PRODUCTION'] == "true"
SENDER_NAME = os.environ['OFFICIAL_NAME']


env = Environment(
    loader=FileSystemLoader("app/email_templates"),
    autoescape=select_autoescape(["html", "xml"])
)


def send_email(destination: str, subject: str, content: str) -> None:
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = formataddr((SENDER_NAME, EMAIL_FROM))
    message["To"] = destination

    message.attach(MIMEText(content, "html"))

    if PRODUCTION:

        context = ssl.create_default_context()

        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
            server.login(GOOGLE_ACCOUNT, GOOGLE_APP_PASSWORD)
            server.sendmail(GOOGLE_ACCOUNT, destination, message.as_string())

    else:
        print(destination, subject, content)
        
        
def render_template(template_name: str, client: "Client", **kwargs) -> str:
    template = env.get_template(template_name+".html")
    return template.render(env=os.environ, client=client, **kwargs)
