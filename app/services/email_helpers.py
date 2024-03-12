import smtplib
import ssl
from uuid import UUID
import os
from email.utils import formataddr
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
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


def build_email_verification_html(client_temp_id: UUID, verification_code: str) -> str:
    return ("<html>"
            "   <body>"
            "       <h2>Enter this code on the website to verify your email address.</h2><br>"
            "       <h2>{}</h2>"
            "   </body>"
            "</html>".format(verification_code))


def build_client_login_code_html(login_code: str):
    return ("<html>"
            "   <body>"
            "       <h2>Enter this code on the website to log in</h2><br>"
            "       <h2>{}</h2>"
            "   </body>"
            "</html>".format(login_code))


def build_appointment_confirmation_email(appointment_title: str, appointment_start_datetime: datetime):
    return ("<html>"
            "   <body>"
            "       <h2>Your Appointment is confirmed!</h2>"
            "       <p>We are looking forward to seeing on {:s}, the {:d} {:s} {:d} at {:02d}:{:02d} for your appointment: {}!</p>"
            "       <p>If you wish to cancel your appointment, "
            "please head to <a href='https://becycle.uk/'>becycle.uk</a>, login as a client and go to your profile.</p>"
            "   </body>"
            "</html>".format(
                weekdays[appointment_start_datetime.weekday()],
                appointment_start_datetime.day,
                months[appointment_start_datetime.month],
                appointment_start_datetime.year,
                appointment_start_datetime.hour,
                appointment_start_datetime.minute,
                appointment_title
            ))


def build_appointment_request_received_email(appointment_title: str, appointment_start_datetime: datetime):
    return ("<html>"
            "   <body>"
            "       <h2>We have received your appointment request!</h2>"
            "       <p>You have requested a {} appointment for {:s}, the {:d} {:s} {:d} at {:02d}:{:02d}.</p>"
            "       <p>If you wish to cancel your appointment, "
            "please head to <a href='https://becycle.uk/'>becycle.uk</a>, login as a client and go to your profile.</p>"
            "   </body>"
            "</html>".format(
                appointment_title,
                weekdays[appointment_start_datetime.weekday()],
                appointment_start_datetime.day,
                months[appointment_start_datetime.month],
                appointment_start_datetime.year,
                appointment_start_datetime.hour,
                appointment_start_datetime.minute,
            ))


def build_appointment_cancellation_email(appointment_title: str, appointment_start_datetime: datetime):
    return ("<html>"
            "   <body>"
            "       <h2>Your Appointment has been cancelled!</h2>"
            "       <p>We are sorry to inform you that your {:s} appointment on {:s}, the {:d} {:s} {:d} at {:02d}:{:02d} has been cancelled.<br>"
            "This is usually due to an unexpected shortage of volunteers.</p>"
            "       <p>If you wish to book a new appointment, please head to <a href='https://becycle.uk/'>becycle.uk</a> and book a new appointment.</p>"
            "       <p>We apologise for any inconvenience this may cause.</p>"
            "   </body>"
            "</html>".format(
                appointment_title,
                weekdays[appointment_start_datetime.weekday()],
                appointment_start_datetime.day,
                months[appointment_start_datetime.month],
                appointment_start_datetime.year,
                appointment_start_datetime.hour,
                appointment_start_datetime.minute
            ))


def build_appointment_request_denied_email(appointment_title: str, appointment_start_datetime: datetime):
    return ("<html>"
            "   <body>"
            "       <h2>Your Appointment request has been denied!</h2>"
            "       <p>We are sorry to inform you that we could not accept your request for a {:s} appointment on {:s}, the {:d} {:s} {:d} at {:02d}:{:02d}.<br>"
            "This is usually due to us expecting a lower number of volunteers than usual for the day in question.</p>"
            "       <p>If you wish to book a new appointment, please head to <a href='https://becycle.uk/'>becycle.uk</a> and book a new appointment.</p>"
            "       <p>We apologise for any inconvenience this may cause.</p>"
            "   </body>"
            "</html>".format(
                appointment_title,
                weekdays[appointment_start_datetime.weekday()],
                appointment_start_datetime.day,
                months[appointment_start_datetime.month],
                appointment_start_datetime.year,
                appointment_start_datetime.hour,
                appointment_start_datetime.minute
            ))


def build_appointment_cancellation_by_client_email(appointment_title: str, appointment_start_datetime: datetime):
    return ("<html>"
            "   <body>"
            "       <h2>Your Appointment has been cancelled!</h2>"
            "       <p>Your {:s} appointment on {:s}, the {:d} {:s} {:d} at {:02d}:{:02d} has been cancelled as per your request.<br></p>"
            "       <p>If you wish to book a new appointment, please head to <a href='https://becycle.uk/'>becycle.uk</a> and book a new appointment.</p>"
            "   </body>"
            "</html>".format(
                appointment_title,
                weekdays[appointment_start_datetime.weekday()],
                appointment_start_datetime.day,
                months[appointment_start_datetime.month],
                appointment_start_datetime.year,
                appointment_start_datetime.hour,
                appointment_start_datetime.minute
            ))


def build_contract_created_email(contract: schemas.Contract):
    return ("<html>"
            "   <body>"
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
            "To retain your deposit, please keep the bike in working condition and return it before the expiry date."
            "If there are any problems with the bike, please book a repair appointment and we will assist you with "
            "repairs.<br>"
            "If you wish to keep the bike for longer, you can extend your contract by another 6 months.<br>"
            "To return the bike or extend the contract, please come to the workshop during our opening hours."
            "No appointment is needed for this.<br>"
            "In the case of returning the bike, we will assess the condition of the bike to determine if the full"
            "deposit can be paid back. In the case of extending the contract, we will check the bike for safety-related"
            "problems.</p>"
            "       <h4>Terms of Loan</h4>"
            "       <p>"
            "Bicycle (Bike) Release Form: Terms of Loan) The agreed deposit is made and kept as a retainer against the value"
            "of the bike and released back to You (Keeper) upon the return of the borrowed bike – in satisfactory condition."
            "BeCYCLE Workshop reserves the right to deduct money from the deposit if and when any damage or excessive"
            "wear and tear occurs to the bike – and/or the bike was kept by You over the agreed rental period. The bike, when"
            "loaned is the full and sole responsibility of You (Keeper) therefore You are entrusted with the burden of"
            "ownership, maintenance, and upkeep. It is completely at your own risk that the bike is maintained and operated"
            "within reasonable use – to ensure Your personal safety."
            "       </p>"
            "   </body>"
            "</html>".format(contract.client.firstName, contract.client.lastName,
                             contract.bike.make, contract.bike.model,
                             contract.bike.colour,
                             contract.bike.serialNumber,
                             contract.depositAmountCollected,
                             contract.startDate.day, months[contract.startDate.month], contract.startDate.year,
                             contract.endDate.day, months[contract.endDate.month], contract.endDate.year,
                             contract.notes if contract.notes is not None else ""))


def build_contract_returned_email(contract: schemas.Contract):
    return ("<html>"
            "   <body>"
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
            "       <p>Deposit returned: &#163;{:d}</p>"
            "       <p>Returned on: {:02d} {:s} {:04d}</p>"
            "       <br>"
            "       <h3>Further information</h3>"
            "       <p>You can view your contract at <a href='https://becycle.uk/'>becycle.uk</a> by logging in as a "
            "client with your email address and going to your profile.<br>Should you want another bike in the future,"
            "please feel free to book another appointment.</p>"
            "   </body>"
            "</html>".format(contract.client.firstName, contract.client.lastName,
                             contract.bike.make, contract.bike.model,
                             contract.bike.colour,
                             contract.bike.serialNumber,
                             contract.depositAmountCollected,
                             contract.startDate.day, months[contract.startDate.month], contract.startDate.year,
                             contract.endDate.day, months[contract.endDate.month], contract.endDate.year,
                             contract.notes if contract.notes is not None else "",
                             contract.depositAmountReturned,
                             contract.returnedDate.day, months[contract.returnedDate.month], contract.returnedDate.year))
