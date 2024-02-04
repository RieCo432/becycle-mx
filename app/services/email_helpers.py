import smtplib
import ssl
from uuid import UUID
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import app.schemas as schemas


GOOGLE_APP_PASSWORD = os.environ['GOOGLE_APP_PASSWORD']
GOOGLE_ACCOUNT = os.environ['GOOGLE_ACCOUNT']
SMTP_PORT = os.environ['SMTP_PORT']
SMTP_SERVER = os.environ['SMTP_SERVER']
API_HOST_ADDRESS = os.environ['API_HOST_ADDRESS']
API_HOST_PORT = os.environ['API_HOST_PORT']


def send_email(destination: str, subject: str, content: str) -> None:
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = GOOGLE_ACCOUNT
    message["To"] = destination

    message.attach(MIMEText(content, "html"))

    # TODO: uncomment when production

    print(destination, subject, content)

    # context = ssl.create_default_context()

    # with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
    #     server.login(GOOGLE_ACCOUNT, GOOGLE_APP_PASSWORD)
    #     server.sendmail(GOOGLE_ACCOUNT, destination, message.as_string())


def build_email_verification_html(client_temp_id: UUID, verification_code: str) -> str:
    return ("<html>"
            "   <body>"
            "       <form action='{}:{}/client/temp/verify' method='post'>"
            "           <input type='hidden' id='client_temp_id' name='client_temp_id' value='{}'>"
            "           <input type='hidden' id='verification_code' name='verification_code' value='{}' HIDDEN><br>"
            "           <button type='submit'>Verify</button>"
            "       </form>"
            "   </body>"
            "</html>".format(API_HOST_ADDRESS, API_HOST_PORT, client_temp_id, verification_code))


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
            "       <p>If you wish to add or modify the additional information, cancel or  reschedule your appointment, "
            "please head to <a href='https://becycle.uk/'>becycle.uk</a> and login as a client</p>"
            "   </body>"
            "</html>".format(
                ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"][appointment_start_datetime.weekday()],
                appointment_start_datetime.day,
                ["", "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"][appointment_start_datetime.month],
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
            "       <p>If you wish to add or modify the additional information, cancel or  reschedule your appointment, "
            "please head to <a href='https://becycle.uk/'>becycle.uk</a> and login as a client</p>"
            "   </body>"
            "</html>".format(
                appointment_title,
                ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"][appointment_start_datetime.weekday()],
                appointment_start_datetime.day,
                ["", "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"][appointment_start_datetime.month],
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
            "       <p>If you wish to book a new appointment, please head to <a href='https://becycle.uk/'>becycle.uk</a> and login as a client. From there you can submit a new request.</p>"
            "       <p>We apologise for any inconvenience this may cause.</p>"
            "   </body>"
            "</html>".format(
                appointment_title,
                ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"][appointment_start_datetime.weekday()],
                appointment_start_datetime.day,
                ["", "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"][appointment_start_datetime.month],
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
            "       <p>If you wish to book a new appointment, please head to <a href='https://becycle.uk/'>becycle.uk</a> and login as a client. From there you can submit a new request.</p>"
            "       <p>We apologise for any inconvenience this may cause.</p>"
            "   </body>"
            "</html>".format(
                appointment_title,
                ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"][appointment_start_datetime.weekday()],
                appointment_start_datetime.day,
                ["", "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"][appointment_start_datetime.month],
                appointment_start_datetime.year,
                appointment_start_datetime.hour,
                appointment_start_datetime.minute
            ))


def build_appointment_cancellation_by_client_email(appointment_title: str, appointment_start_datetime: datetime):
    return ("<html>"
            "   <body>"
            "       <h2>Your Appointment has been cancelled!</h2>"
            "       <p>Your {:s} appointment on {:s}, the {:d} {:s} {:d} at {:02d}:{:02d} has been cancelled as per your request.<br></p>"
            "       <p>If you wish to book a new appointment, please head to <a href='https://becycle.uk/'>becycle.uk</a> and login as a client. From there you can submit a new request.</p>"
            "   </body>"
            "</html>".format(
                appointment_title,
                ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"][appointment_start_datetime.weekday()],
                appointment_start_datetime.day,
                ["", "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"][appointment_start_datetime.month],
                appointment_start_datetime.year,
                appointment_start_datetime.hour,
                appointment_start_datetime.minute
            ))


def build_contract_created_email(contract: schemas.Contract):
    return ("<html>"
            "   <body>"
            "       <h2>Your Contract Details</h2>"
            "       <p>{:s} {:s}"
            "           {:s} {:s}"
            "       </p>"
            "   </body>"
            "</html>".format(contract.client.firstName, contract.client.lastName, contract.bike.make, contract.bike.model))


def build_contract_returned_email(contract: schemas.Contract):
    return ("<html>"
            "   <body>"
            "       <h2>Your Contract Details</h2>"
            "       <p>{:s} {:s}"
            "           {:s} {:s}"
            "       </p>"
            "   </body>"
            "</html>".format(contract.client.firstName, contract.client.lastName, contract.bike.make,
                             contract.bike.model))
