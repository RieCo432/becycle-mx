import app.crud as crud
from app.tests.pytestFixtures import *


def test_get_appointments_for_reminder_email(appointments_soon):
    appointments_for_reminders = crud.get_appointments_for_reminder_email(db=db)

    assert len(appointments_for_reminders) == 1
    assert appointments_for_reminders[0] == appointments_soon[5]


def test_send_appointment_reminders(appointments_soon):
    assert not appointments_soon[5].reminderSent
    crud.send_appointment_reminders(db=db)
    db.refresh(appointments_soon[5])
    assert appointments_soon[5].reminderSent
