from fastapi.testclient import TestClient
from app.tests.pytestFixtures import *
from app.main import app
import app.crud as crud
from sqlalchemy import select
import app.dependencies as dep
from random import random

client = TestClient(app)


def test_post_pre_becycle_survey(clients: list[models], client_auth_headers):
    for app_client, client_auth_header in zip(clients, client_auth_headers):

        answers = {
            "hurdleSafety": random() > 0.5,
            "hurdleMoney": random() > 0.5,
            "hurdleTime": random() > 0.5,
            "hurdleSweating": random() > 0.5,
            "hurdleComfort": random() > 0.5,
            "hurdleDistance": random() > 0.5,
            "hurdleOther": "somethingElse" if random() > 0.5 else None,
            "motivationMoney": random() > 0.5,
            "motivationHealth": random() > 0.5,
            "motivationEnvironmental": random() > 0.5,
            "motivationOther": "somethingElse" if random() > 0.5 else None,
            "consideredNewOnline": random() > 0.5,
            "consideredNewShop": random() > 0.5,
            "consideredUsed": random() > 0.5,
            "consideredLendingPrivate": random() > 0.5,
            "consideredLendingBecycle": random() > 0.5,
            "consideredOther": "somethingElse" if random() > 0.5 else None,
            "trainingExperienceMonths": int(random() * 10),
            "trainingFormal": random() > 0.5,
            "trainingConfidence": int(random() * 10),
            "trainingRules": random() > 0.5,
            "trainingDriver": random() > 0.5,
            "interestMaintenanceDesired": int(random() * 10),
            "interestMaintenanceCurrent": int(random() * 10)
        }

        response = client.post("/surveys/pre-becycle", json=answers, headers=client_auth_header)

        if not app_client.preBecycleSurveyCompleted:
            assert response.status_code == 200
        else:
            assert response.status_code == 403
            assert response.json().get("detail").get("description") == "You have already completed this survey"

        db.refresh(app_client)

        assert app_client.preBecycleSurveyCompleted


def test_post_peri_becycle_survey(clients: list[models], client_auth_headers):
    for app_client, client_auth_header in zip(clients, client_auth_headers):

        answers = {
            "serviceSatisfactionGetBike": int(random() * 10),
            "serviceSatisfactionFixBike": int(random() * 10),
            "serviceSatisfactionLearn": int(random() * 10),
            "roadsGreat": random() > 0.5,
            "roadsLight": random() > 0.5,
            "roadsPotholes": random() > 0.5,
            "roadsRubbish": random() > 0.5,
            "roadsParking": random() > 0.5,
            "roadsDark": random() > 0.5,
            "usersSafe": random() > 0.5,
            "usersBusesUnsafe": random() > 0.5,
            "usersCarsUnsafe": random() > 0.5,
            "usersTrucksUnsafe": random() > 0.5,
            "usersTaxisUnsafe": random() > 0.5,
            "usersCyclistsUnsafe": random() > 0.5,
            "usersPedestriansUnsafe": random() > 0.5,
            "routesRoads": random() > 0.5,
            "routesPavements": random() > 0.5,
            "routesOffroad": random() > 0.5,
            "accidentsNearMisses": int(random() * 10),
            "accidentsContact": int(random() * 10),
            "harassmentExperienced": random() > 0.5,
            "harassmentSuggestions": "somethingElse" if random() > 0.5 else None,
        }

        response = client.post("/surveys/peri-becycle", json=answers, headers=client_auth_header)

        if not app_client.periBecycleSurveyCompleted:
            assert response.status_code == 200
        else:
            assert response.status_code == 403
            assert response.json().get("detail").get("description") == "You have already completed this survey"

        db.refresh(app_client)

        assert app_client.periBecycleSurveyCompleted


def test_post_post_becycle_survey(clients: list[models], client_auth_headers):
    for app_client, client_auth_header in zip(clients, client_auth_headers):

        answers = {
            "serviceSatisfactionGetBike": int(random() * 10),
            "serviceSatisfactionFixBike": int(random() * 10),
            "serviceSatisfactionLearn": int(random() * 10),
            "reasonStoppedCycling": random() > 0.5,
            "reasonLeavingAberdeen": random() > 0.5,
            "issueSafety": random() > 0.5,
            "issueMoney": random() > 0.5,
            "issueTime": random() > 0.5,
            "issueSweating": random() > 0.5,
            "issueComfort": random() > 0.5,
            "issueDistance": random() > 0.5,
            "issueOther": "somethingElse" if random() > 0.5 else None,
            "improvementNone": random() > 0.5,
            "improvementCyclingPaths": random() > 0.5,
            "improvementLights": random() > 0.5,
            "improvementSurface": random() > 0.5,
            "improvementCleaner": random() > 0.5,
            "improvementOther": "somethingElse" if random() > 0.5 else None,
            "alternativeOwnBike": random() > 0.5,
            "alternativeShareFriendsFamily": random() > 0.5,
            "alternativeAnotherBecycle": random() > 0.5,
            "alternativeOtherRental": random() > 0.5,
        }

        response = client.post("/surveys/post-becycle", json=answers, headers=client_auth_header)

        if not app_client.postBecycleSurveyCompleted:
            assert response.status_code == 200
        else:
            assert response.status_code == 403
            assert response.json().get("detail").get("description") == "You have already completed this survey"

        db.refresh(app_client)

        assert app_client.postBecycleSurveyCompleted
