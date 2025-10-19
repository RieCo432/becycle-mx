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
SMTP_PORT = os.environ['SMTP_PORT']
SMTP_SERVER = os.environ['SMTP_SERVER']
API_HOST_ADDRESS = os.environ['API_HOST_ADDRESS']
API_HOST_PORT = os.environ['API_HOST_PORT']
PRODUCTION = os.environ['PRODUCTION'] == "true"

weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
months = ["", "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]


env = Environment(
    loader=FileSystemLoader("app/email_templates"),
    autoescape=select_autoescape(["html", "xml"])
)


def send_email(destination: str, subject: str, content: str) -> None:
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = formataddr(("BECYCLE", EMAIL_FROM))
    message["To"] = destination

    message.attach(MIMEText(content, "html"))

    if PRODUCTION:

        context = ssl.create_default_context()

        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
            server.login(GOOGLE_ACCOUNT, GOOGLE_APP_PASSWORD)
            server.sendmail(GOOGLE_ACCOUNT, destination, message.as_string())

    else:
        print(destination, subject, content)
        
        
def render_template(template_name: str, **kwargs) -> str:
    template = env.get_template(template_name+".html")
    return template.render(**kwargs)


def build_crime_report_added_email(crime_report: schemas.CrimeReportFull):
    return ("<html>"
            "   <body>"
            "       <p>We have marked your bike as being reported stolen with the following details:</p>"
            "       <h2>Crime Report</h2>"
            "       <p>Crime Number: {:s}</p>"
            "       <p>Created On: {:s}</p>"
            "       <p>If this is a mistake, please contact us as soon as possible.</p>"
            "       <p>Successfully reporting your bike as stolen with a crime number from the police will entitle you to a free replacement bike. "
            "Your deposit will be claimable if the original bike is found and returned to us.</p>"
            "       <h2>Your Details</h2>"
            "       <p>{:s} {:s}</p>"
            "       <h2>Bike Details</h2>"
            "       <p>{:s} {:s}</p>"
            "       <p>Colour: {:s}</p>"
            "       <p>Serial number: {:s}</p>"
            "       <h2>Contract Details</h2>"
            "       <p>Deposit paid: &#163;{:d}"
            "       <p>Valid from: {:02d} {:s} {:04d}</p>"
            "       <p>Valid until: {:02d} {:s} {:04d}</p>"
            "       <p>Notes: {:s}</p>"
            "       <br>"
            "       <h3>Further information</h3>"
            "       <p>You can view your contract at <a href='https://becycle.uk/'>becycle.uk</a> by logging in as a "
            "client with your email address and going to your profile.<br>"
            "</p>"
            "   </body>"
            "</html>".format(crime_report.crimeNumber,
                             crime_report.createdOn.strftime("%d %B %Y"),
        crime_report.contract.client.firstName, crime_report.contract.client.lastName,
                             crime_report.contract.bike.make, crime_report.contract.bike.model,
                             crime_report.contract.bike.colour,
                             crime_report.contract.bike.serialNumber,
                             crime_report.contract.depositAmountCollected,
                             crime_report.contract.startDate.day, months[crime_report.contract.startDate.month], crime_report.contract.startDate.year,
                             crime_report.contract.endDate.day, months[crime_report.contract.endDate.month], crime_report.contract.endDate.year,
                             crime_report.contract.notes if crime_report.contract.notes is not None else ""))


def build_crime_report_closed_email(crime_report: schemas.CrimeReportFull):
    return ("<html>"
            "   <body>"
            "       <p>Your stolen bike case has been closed with the following details:</p>"
            "       <h2>Crime Report</h2>"
            "       <p>Crime Number: {:s}</p>"
            "       <p>Created On: {:s}</p>"
            "       <p>Closed On: {:s}</p>"
            "       <p>If this is a mistake, please contact us as soon as possible.</p>"
            "       <p>If you have the bike in your possession now, you can return it to reclaim your deposit as normal. "
            "If the bike was returned to us by the police, you are still able to visit us as soon as possible to reclaim your deposit.</p>"
            "       <h2>Your Details</h2>"
            "       <p>{:s} {:s}</p>"
            "       <h2>Bike Details</h2>"
            "       <p>{:s} {:s}</p>"
            "       <p>Colour: {:s}</p>"
            "       <p>Serial number: {:s}</p>"
            "       <h2>Contract Details</h2>"
            "       <p>Deposit paid: &#163;{:d}"
            "       <p>Valid from: {:02d} {:s} {:04d}</p>"
            "       <p>Valid until: {:02d} {:s} {:04d}</p>"
            "       <p>Notes: {:s}</p>"
            "       <br>"
            "       <h3>Further information</h3>"
            "       <p>You can view your contract at <a href='https://becycle.uk/'>becycle.uk</a> by logging in as a "
            "client with your email address and going to your profile.<br>"
            "</p>"
            "   </body>"
            "</html>".format(crime_report.crimeNumber,
                             crime_report.createdOn.strftime("%d %B %Y"),
                             crime_report.closedOn.strftime("%d %B %Y"),
        crime_report.contract.client.firstName, crime_report.contract.client.lastName,
                             crime_report.contract.bike.make, crime_report.contract.bike.model,
                             crime_report.contract.bike.colour,
                             crime_report.contract.bike.serialNumber,
                             crime_report.contract.depositAmountCollected,
                             crime_report.contract.startDate.day, months[crime_report.contract.startDate.month], crime_report.contract.startDate.year,
                             crime_report.contract.endDate.day, months[crime_report.contract.endDate.month], crime_report.contract.endDate.year,
                             crime_report.contract.notes if crime_report.contract.notes is not None else ""))

