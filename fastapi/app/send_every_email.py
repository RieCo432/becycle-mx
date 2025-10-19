import datetime
import datetime
import os
import bcrypt
from dateutil.relativedelta import relativedelta
from fastapi.routing import APIRoute
from scipy.signal import cascade
from sqlalchemy import select

import app.models as models
from sqlalchemy.orm import Session
import app.crud as crud
from app.database.db import Base, engine, SessionLocal
from app.models import *

Base.metadata.create_all(bind=engine)
db = SessionLocal()



target_email = "colin.ries@gmail.com"
target_client = crud.get_client_by_email(db, target_email)

if __name__ == "__main__":
    contract = target_client.contracts[0]

    contract.send_creation_email()
    contract.send_expiry_reminder_email()
    contract.send_return_email()
    
    appointment = target_client.appointments[0]
    appointment.send_request_received_email()
    appointment.send_confirmation_email()
    appointment.send_request_denied_email()
    appointment.send_cancellation_email()
    appointment.send_client_cancellation_email()
    appointment.send_reminder_email()
    
    crime_report = contract.crimeReports[0]
    crime_report.send_crime_report_added_email()
    crime_report.send_crime_report_closed_email()
    