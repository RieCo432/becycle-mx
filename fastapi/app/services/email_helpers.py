import os
import smtplib
import socket
import ssl
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
from uuid import UUID
from jinja2 import Environment, FileSystemLoader, select_autoescape
import inspect

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


def send_email(destination: str, subject: str, content: str) -> bool:
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = formataddr((SENDER_NAME, EMAIL_FROM))
    message["To"] = destination

    message.attach(MIMEText(content, "html"))

    if PRODUCTION:
        try:
            context = ssl.create_default_context()
    
            with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
                server.login(GOOGLE_ACCOUNT, GOOGLE_APP_PASSWORD)
                server.sendmail(GOOGLE_ACCOUNT, destination, message.as_string())
                
            return True
        except smtplib.SMTPRecipientsRefused:
            current_frame = inspect.currentframe()
            caller_frame = inspect.getouterframes(current_frame, 2)
            print(f"Failed to send email to {destination} for {caller_frame[1][3]}: Recipients refused")
            return False
        except smtplib.SMTPAuthenticationError:
            current_frame = inspect.currentframe()
            caller_frame = inspect.getouterframes(current_frame, 2)
            print(f"Failed to send email to {destination} for {caller_frame[1][3]}: Authentication error")
            return False
        except smtplib.SMTPServerDisconnected:
            current_frame = inspect.currentframe()
            caller_frame = inspect.getouterframes(current_frame, 2)
            print(f"Failed to send email to {destination} for {caller_frame[1][3]}: Server disconnected")
            return False
        except socket.gaierror:
            current_frame = inspect.currentframe()
            caller_frame = inspect.getouterframes(current_frame, 2)
            print(f"Failed to send email to {destination} for {caller_frame[1][3]}: DNS error")
            return False
        except Exception as e:
            current_frame = inspect.currentframe()
            caller_frame = inspect.getouterframes(current_frame, 2)
            print(f"Failed to send email to {destination} for {caller_frame[1][3]}: {e}")
            return False
    else:
        print(destination, subject, content)
        return True
        
        
def render_template(template_name: str, client: "Client", **kwargs) -> str:
    template = env.get_template(template_name+".html")
    return template.render(env=os.environ, client=client, **kwargs)


def email_task(entity_model, entity_id, method_name: str, related: "tuple" = ()):
    """Run ``entity_model``'s ``send_*`` email method as a FastAPI background task.

    Background tasks run *after* the request's get_db session has been closed, and
    expire_on_commit=True has expired the row's attributes — so calling the method
    on the request-scoped instance would lazy-load a detached object and raise
    DetachedInstanceError (e.g. reading ``.client``). Instead, re-fetch the entity
    (and any related instances given in ``related``) in a fresh session and call
    the method while that session is open, so lazy relationships resolve.

    ``entity_id`` and each ``related`` id must be captured by the caller *before*
    the session closes (i.e. at the call site). ``related`` is a sequence of
    ``(model, id)`` pairs, passed to the method as positional args in order.
    """
    # Imported here to avoid any import cycle between services and the db module.
    from app.database.db import SessionLocal

    db = SessionLocal()
    try:
        entity = db.get(entity_model, entity_id)
        if entity is None:
            return
        related_entities = [db.get(model, id) for (model, id) in related]
        getattr(entity, method_name)(*related_entities)
    finally:
        db.close()
