import smtplib
import ssl
from uuid import UUID
from app.config import GOOGLE_APP_PASSWORD, GOOGLE_ACCOUNT, SMTP_PORT, SMTP_SERVER, API_HOST_ADDRESS, API_HOST_PORT
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


# TODO: should probably make this run as a background task to speed up API responses
def send_email(destination: str, subject: str, content: str) -> None:
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = GOOGLE_ACCOUNT
    message["To"] = destination

    message.attach(MIMEText(content, "html"))

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
        server.login(GOOGLE_ACCOUNT, GOOGLE_APP_PASSWORD)
        server.sendmail(GOOGLE_ACCOUNT, destination, message.as_string())


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

