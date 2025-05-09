from .appointments import Appointment
from .client import Client
from .settings import AppointmentType

class AppointmentFull(Appointment):
    client: Client
    type: AppointmentType