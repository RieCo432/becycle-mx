from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.tests.pytestFixtures import *
from app.main import app
import app.crud as crud


test_client = TestClient(app)


def test_get_admin_duplicates_clients(detected_potential_client_duplicates, admin_user_auth_header):
    response = test_client.get("/admin/duplicates/clients", headers=admin_user_auth_header)

    assert response.status_code == 200

    response_json = response.json()

    for response_duplicate in response_json:
        assert {
            "id": response_duplicate.get("id"),
            "client1Id": response_duplicate.get("client1").get("id"),
            "client2Id": response_duplicate.get("client2").get("id"),
            "similarityScore": response_duplicate.get("similarityScore"),
            "ignore": response_duplicate.get("ignore")
        } in detected_potential_client_duplicates


def test_admin_duplicates_clients_refresh(clients_with_duplicates, admin_user_auth_header):
    response = test_client.get("/admin/duplicates/clients/refresh", headers=admin_user_auth_header)

    assert response.status_code == 200


    db.query(models.DetectedPotentialClientDuplicates).delete()
    db.commit()


def test_admin_duplicates_client_resolve_keep_number_1(detected_potential_client_duplicates, clients_with_duplicates, client_logins_with_duplicate_clients, admin_user_auth_header, contracts_with_duplicate_clients_and_bikes, appointments_with_client_duplicates):
    for duplicate_index, duplicate_id in enumerate([d.id for d in detected_potential_client_duplicates]):

        # the duplicate at index 1 will discard client index 1, which leads to deletion of duplicate index 2
        if duplicate_index in [2]:
            assert crud.get_potential_client_duplicate(db=db, potential_client_duplicate_id=duplicate_id) is None
            continue
        else:
            duplicate = crud.get_potential_client_duplicate(db=db, potential_client_duplicate_id=duplicate_id)

            keep_id = duplicate.client1Id
            discard_id = duplicate.client2Id

            affected_contracts = [c for c in contracts_with_duplicate_clients_and_bikes if c.clientId == discard_id or c.clientId == keep_id]
            affected_appointments = [a for a in appointments_with_client_duplicates if a.clientId == discard_id or a.clientId == keep_id]

            if duplicate_index == 1:
                assert db.scalar(
                    select(models.ClientLogin)
                    .where(models.ClientLogin.clientId == clients_with_duplicates[1].id)
                ) is not None

            response = test_client.put("/admin/duplicates/clients/{duplicateId}/resolve".format(duplicateId=duplicate.id), json={
                "discard_client_id": str(discard_id),
                "keep_client_id": str(keep_id)
            }, headers=admin_user_auth_header)

            assert response.status_code == 200

            for c in affected_contracts:
                db.refresh(c)
            for a in affected_appointments:
                db.refresh(a)

            assert all([c.clientId == keep_id for c in affected_contracts])
            assert all([a.clientId == keep_id for a in affected_appointments])

            if duplicate_index == 1:
                assert db.scalar(
                    select(models.ClientLogin)
                    .where(models.ClientLogin.clientId == clients_with_duplicates[1].id)
                ) is None

            assert crud.get_client(db=db, client_id=discard_id) is None
            assert crud.get_potential_client_duplicate(db=db, potential_client_duplicate_id=duplicate.id) is None


def test_admin_duplicates_client_resolve_keep_number_2(detected_potential_client_duplicates, clients_with_duplicates, client_logins_with_duplicate_clients, admin_user_auth_header, contracts_with_duplicate_clients_and_bikes, appointments_with_client_duplicates):
    for duplicate_index, duplicate_id in enumerate([d.id for d in detected_potential_client_duplicates]):

        # the duplicate at index 1 will discard client index 3, which leads to deletion of duplicate index 3
        if duplicate_index in [3]:
            assert crud.get_potential_client_duplicate(db=db, potential_client_duplicate_id=duplicate_id) is None
            continue
        else:
            duplicate = crud.get_potential_client_duplicate(db=db, potential_client_duplicate_id=duplicate_id)

            keep_id = duplicate.client2Id
            discard_id = duplicate.client1Id

            affected_contracts = [c for c in contracts_with_duplicate_clients_and_bikes if c.clientId == discard_id or c.clientId == keep_id]
            affected_appointments = [a for a in appointments_with_client_duplicates if a.clientId == discard_id or a.clientId == keep_id]

            if duplicate_index == 1:
                assert db.scalar(
                    select(models.ClientLogin)
                    .where(models.ClientLogin.clientId == clients_with_duplicates[3].id)
                ) is not None

            response = test_client.put("/admin/duplicates/clients/{duplicateId}/resolve".format(duplicateId=duplicate.id), json={
                "discard_client_id": str(discard_id),
                "keep_client_id": str(keep_id)
            }, headers=admin_user_auth_header)

            assert response.status_code == 200

            for c in affected_contracts:
                db.refresh(c)
            for a in affected_appointments:
                db.refresh(a)

            assert all([c.clientId == keep_id for c in affected_contracts])
            assert all([a.clientId == keep_id for a in affected_appointments])

            if duplicate_index == 1:
                assert db.scalar(
                    select(models.ClientLogin)
                    .where(models.ClientLogin.clientId == clients_with_duplicates[3].id)
                ) is None

            assert crud.get_client(db=db, client_id=discard_id) is None
            assert crud.get_potential_client_duplicate(db=db, potential_client_duplicate_id=duplicate.id) is None


def test_admin_duplicates_client_resolve_same_id(detected_potential_client_duplicates, admin_user_auth_header):
    response = test_client.put("/admin/duplicates/clients/{duplicateId}/resolve".format(duplicateId=detected_potential_client_duplicates[0].id),
                               json={
                                   "discard_client_id": str(detected_potential_client_duplicates[0].client1Id),
                                   "keep_client_id": str(detected_potential_client_duplicates[0].client1Id)
                               }, headers=admin_user_auth_header)

    assert response.status_code == 400
    assert response.json().get("detail").get("description") == "Both IDs are identical"


def test_admin_duplicates_client_resolve_not_found(detected_potential_client_duplicates, admin_user_auth_header):
    response = test_client.put("/admin/duplicates/clients/{duplicateId}/resolve".format(duplicateId=uuid4()),
                               json={
                                   "discard_client_id": str(detected_potential_client_duplicates[0].client1Id),
                                   "keep_client_id": str(detected_potential_client_duplicates[0].client2Id)
                               }, headers=admin_user_auth_header)

    assert response.status_code == 404
    assert response.json().get("detail").get("description") == "Potential client duplicate not found"


def test_admin_duplicates_client_resolve_client_1_not_in_this_duplicate(detected_potential_client_duplicates, admin_user_auth_header):
    response = test_client.put("/admin/duplicates/clients/{duplicateId}/resolve".format(duplicateId=detected_potential_client_duplicates[0].id),
                               json={
                                   "discard_client_id": str(detected_potential_client_duplicates[1].client1Id),
                                   "keep_client_id": str(detected_potential_client_duplicates[0].client2Id)
                               }, headers=admin_user_auth_header)

    assert response.status_code == 400
    assert response.json().get("detail").get("description") == "One of the clients is not part of this potential duplicate"


def test_admin_duplicates_client_resolve_client_2_not_in_this_duplicate(detected_potential_client_duplicates, admin_user_auth_header):
    response = test_client.put("/admin/duplicates/clients/{duplicateId}/resolve".format(duplicateId=detected_potential_client_duplicates[0].id),
                               json={
                                   "discard_client_id": str(detected_potential_client_duplicates[0].client1Id),
                                   "keep_client_id": str(detected_potential_client_duplicates[1].client2Id)
                               }, headers=admin_user_auth_header)

    assert response.status_code == 400
    assert response.json().get("detail").get("description") == "One of the clients is not part of this potential duplicate"


def test_admin_duplicates_client_ignore(detected_potential_client_duplicates, admin_user_auth_header):
    for duplicate in detected_potential_client_duplicates:
        response = test_client.patch("/admin/duplicates/clients/{duplicateId}/ignore".format(duplicateId=duplicate.id), headers=admin_user_auth_header)

        assert response.status_code == 200
        response_duplicate = response.json()
        db.refresh(duplicate)
        assert duplicate == {
            "id": response_duplicate.get("id"),
            "client1Id": response_duplicate.get("client1").get("id"),
            "client2Id": response_duplicate.get("client2").get("id"),
            "similarityScore": response_duplicate.get("similarityScore"),
            "ignore": response_duplicate.get("ignore")
        }
        assert duplicate.ignore


def test_admin_duplicates_client_ignore_not_found(detected_potential_client_duplicates, admin_user_auth_header):
    response = test_client.patch("/admin/duplicates/clients/{duplicateId}/ignore".format(duplicateId=uuid4()), headers=admin_user_auth_header)

    assert response.status_code == 404
    assert response.json().get("detail").get("description") == "Potential client duplicate not found"


def test_get_admin_duplicates_bikes(detected_potential_bike_duplicates, admin_user_auth_header):
    response = test_client.get("/admin/duplicates/bikes", headers=admin_user_auth_header)

    assert response.status_code == 200

    response_json = response.json()

    for response_duplicate in response_json:
        assert {
            "id": response_duplicate.get("id"),
            "bike1Id": response_duplicate.get("bike1").get("id"),
            "bike2Id": response_duplicate.get("bike2").get("id"),
            "similarityScore": response_duplicate.get("similarityScore"),
            "ignore": response_duplicate.get("ignore")
        } in detected_potential_bike_duplicates


def test_admin_duplicates_bikes_refresh(bikes_with_duplicates, admin_user_auth_header):
    response = test_client.get("/admin/duplicates/bikes/refresh", headers=admin_user_auth_header)

    assert response.status_code == 200

    db.query(models.DetectedPotentialBikeDuplicates).delete()
    db.commit()


def test_admin_duplicates_bike_resolve_keep_number_1(detected_potential_bike_duplicates, bikes_with_duplicates, admin_user_auth_header, contracts_with_duplicate_clients_and_bikes):
    for duplicate_index, duplicate_id in enumerate([d.id for d in detected_potential_bike_duplicates]):

        # the duplicate at index 1 will discard bike index 6, which leads to deletion of duplicate index 3
        if duplicate_index in [3]:
            assert crud.get_potential_bike_duplicate(db=db, potential_bike_duplicate_id=duplicate_id) is None
            continue
        else:
            duplicate = crud.get_potential_bike_duplicate(db=db, potential_bike_duplicate_id=duplicate_id)

            keep_id = duplicate.bike1Id
            discard_id = duplicate.bike2Id

            affected_contracts = [c for c in contracts_with_duplicate_clients_and_bikes if c.bikeId == discard_id or c.bikeId == keep_id]

            response = test_client.put("/admin/duplicates/bikes/{duplicateId}/resolve".format(duplicateId=duplicate.id), json={
                "discard_bike_id": str(discard_id),
                "keep_bike_id": str(keep_id)
            }, headers=admin_user_auth_header)

            assert response.status_code == 200

            for c in affected_contracts:
                db.refresh(c)

            assert all([c.bikeId == keep_id for c in affected_contracts])

            assert crud.get_bike(db=db, bike_id=discard_id) is None
            assert crud.get_potential_bike_duplicate(db=db, potential_bike_duplicate_id=duplicate.id) is None


def test_admin_duplicates_bike_resolve_keep_number_2(detected_potential_bike_duplicates, bikes_with_duplicates, admin_user_auth_header, contracts_with_duplicate_clients_and_bikes):
    for duplicate_index, duplicate_id in enumerate([d.id for d in detected_potential_bike_duplicates]):

        # the duplicate at index 0 will discard bike index 0, which leads to deletion of duplicate index 3
        if duplicate_index in [3]:
            assert crud.get_potential_bike_duplicate(db=db, potential_bike_duplicate_id=duplicate_id) is None
            continue
        else:
            duplicate = crud.get_potential_bike_duplicate(db=db, potential_bike_duplicate_id=duplicate_id)

            keep_id = duplicate.bike1Id
            discard_id = duplicate.bike2Id

            affected_contracts = [c for c in contracts_with_duplicate_clients_and_bikes if c.bikeId == discard_id or c.bikeId == keep_id]

            response = test_client.put("/admin/duplicates/bikes/{duplicateId}/resolve".format(duplicateId=duplicate.id), json={
                "discard_bike_id": str(discard_id),
                "keep_bike_id": str(keep_id)
            }, headers=admin_user_auth_header)

            assert response.status_code == 200

            for c in affected_contracts:
                db.refresh(c)

            assert all([c.bikeId == keep_id for c in affected_contracts])

            assert crud.get_bike(db=db, bike_id=discard_id) is None
            assert crud.get_potential_bike_duplicate(db=db, potential_bike_duplicate_id=duplicate.id) is None


def test_admin_duplicates_bike_resolve_same_id(detected_potential_bike_duplicates, admin_user_auth_header):
    response = test_client.put("/admin/duplicates/bikes/{duplicateId}/resolve".format(duplicateId=detected_potential_bike_duplicates[0].id),
                               json={
                                   "discard_bike_id": str(detected_potential_bike_duplicates[0].bike1Id),
                                   "keep_bike_id": str(detected_potential_bike_duplicates[0].bike1Id)
                               }, headers=admin_user_auth_header)

    assert response.status_code == 400
    assert response.json().get("detail").get("description") == "Both IDs are identical"


def test_admin_duplicates_bike_resolve_not_found(detected_potential_bike_duplicates, admin_user_auth_header):
    response = test_client.put("/admin/duplicates/bikes/{duplicateId}/resolve".format(duplicateId=uuid4()),
                               json={
                                   "discard_bike_id": str(detected_potential_bike_duplicates[0].bike1Id),
                                   "keep_bike_id": str(detected_potential_bike_duplicates[0].bike2Id)
                               }, headers=admin_user_auth_header)

    assert response.status_code == 404
    assert response.json().get("detail").get("description") == "Potential bike duplicate not found"


def test_admin_duplicates_bike_resolve_bike_1_not_in_duplicate(detected_potential_bike_duplicates, admin_user_auth_header):
    response = test_client.put("/admin/duplicates/bikes/{duplicateId}/resolve".format(duplicateId=detected_potential_bike_duplicates[0].id),
                               json={
                                   "discard_bike_id": str(detected_potential_bike_duplicates[1].bike1Id),
                                   "keep_bike_id": str(detected_potential_bike_duplicates[0].bike2Id)
                               }, headers=admin_user_auth_header)

    assert response.status_code == 400
    assert response.json().get("detail").get("description") == "One of the bikes is not part of this potential duplicate"


def test_admin_duplicates_bike_resolve_bike_2_not_in_duplicate(detected_potential_bike_duplicates, admin_user_auth_header):
    response = test_client.put("/admin/duplicates/bikes/{duplicateId}/resolve".format(duplicateId=detected_potential_bike_duplicates[0].id),
                               json={
                                   "discard_bike_id": str(detected_potential_bike_duplicates[0].bike1Id),
                                   "keep_bike_id": str(detected_potential_bike_duplicates[1].bike2Id)
                               }, headers=admin_user_auth_header)

    assert response.status_code == 400
    assert response.json().get("detail").get("description") == "One of the bikes is not part of this potential duplicate"


def test_admin_duplicates_bike_ignore(detected_potential_bike_duplicates, admin_user_auth_header):
    for duplicate in detected_potential_bike_duplicates:
        response = test_client.patch("/admin/duplicates/bikes/{duplicateId}/ignore".format(duplicateId=duplicate.id), headers=admin_user_auth_header)

        assert response.status_code == 200
        response_duplicate = response.json()
        db.refresh(duplicate)
        assert duplicate == {
            "id": response_duplicate.get("id"),
            "bike1Id": response_duplicate.get("bike1").get("id"),
            "bike2Id": response_duplicate.get("bike2").get("id"),
            "similarityScore": response_duplicate.get("similarityScore"),
            "ignore": response_duplicate.get("ignore")
        }
        assert duplicate.ignore


def test_admin_duplicates_bike_ignore_not_found(detected_potential_client_duplicates, admin_user_auth_header):
    response = test_client.patch("/admin/duplicates/bikes/{duplicateId}/ignore".format(duplicateId=uuid4()), headers=admin_user_auth_header)

    assert response.status_code == 404
    assert response.json().get("detail").get("description") == "Potential bike duplicate not found"


def test_get_contracts_takeout_excel(contracts, admin_user_auth_header):
    response = test_client.get("/admin/takeout/contracts.xlsx", headers=admin_user_auth_header)

    assert response.status_code == 200

    current_directory = os.path.dirname(__file__)
    tests_directory = os.path.dirname(current_directory)
    photos_directory = os.path.join(tests_directory, "photos")
    excel_filepath = os.path.join(photos_directory, "contracts.xlsx")
    with open(excel_filepath, "wb") as fout:
        fout.write(response.content)

    import pandas as pd

    df = pd.read_excel(excel_filepath, sheet_name="contracts")

    for contract in contracts:
        df_filtered = df[(df["Name"] == f"{contract.client.firstName} {contract.client.lastName}") & (df["Make"] == contract.bike.make) & (df["Serial Number"] == contract.bike.serialNumber)].reset_index()
        assert len(df_filtered) == 1
        assert df_filtered["Email Address"][0] == contract.client.emailAddress
        assert df_filtered["Start Date"][0].date() == contract.startDate
        assert df_filtered["End Date"][0].date() == contract.endDate
        assert df_filtered["Model"][0] == contract.bike.model
        assert df_filtered["Colour"][0] == contract.bike.colour
        assert df_filtered["Decals"][0] == contract.bike.decals if contract.bike.decals is not None else pd.isnull(df_filtered["Decals"][0])
        assert df_filtered["Condition"][0] == contract.conditionOfBike
        assert df_filtered["Notes"][0] == contract.notes
        assert df_filtered["Contract Type"][0] == contract.contractType
        assert df_filtered["Working Volunteer"][0] == contract.workingUser.username
        assert df_filtered["Checking Volunteer"][0] == contract.checkingUser.username
        assert df_filtered["Deposit Amount Collected"][0] == contract.depositAmountCollected
        assert df_filtered["Deposit Collected By"][0] == contract.depositCollectingUser.username
        assert df_filtered["Returned Date"][0].date() == contract.returnedDate if contract.returnedDate is not None else pd.isnull(df_filtered["Returned Date"][0])
        assert df_filtered["Deposit Amount Returned"][0] == contract.depositAmountReturned if contract.depositAmountReturned is not None else pd.isnull(df_filtered["Deposit Amount Returned"][0])
        assert df_filtered["Deposit Returned By"][0] == contract.depositReturningUser.username if contract.depositReturningUser is not None else pd.isnull(df_filtered["Deposit Returned By"][0])
        assert df_filtered["Return Received By"][0] == contract.returnAcceptingUser.username if contract.returnAcceptingUser is not None else pd.isnull(df_filtered["Return Received By"][0])


def test_get_contracts_takeout_pdf(contracts, admin_user_auth_header):
    response = test_client.get("/admin/takeout/contracts.pdf", headers=admin_user_auth_header)
    assert response.status_code == 200

    assert b"Pages\n/Count " + bytes(str(len(contracts)), encoding='utf-8') in response.content
