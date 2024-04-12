import os
from uuid import UUID
import pandas as pd
from fastapi import HTTPException, status

import app.schemas as schemas
import app.models as models
from Levenshtein import distance as levenshtein_distance
from sqlalchemy import select
from sqlalchemy.orm import Session
from .clients import get_all_clients, get_client, get_client_logins
from .bikes import get_all_bikes, get_bike
from .contracts import get_contracts
from .appointments import get_appointments
from .finances import get_deposit_balances_book


def get_potential_client_duplicates_detected(db: Session) -> list[models.DetectedPotentialClientDuplicates]:
    return [_ for _ in db.scalars(
        select(models.DetectedPotentialClientDuplicates)
        .order_by(models.DetectedPotentialClientDuplicates.similarityScore)
    )]


def is_potential_client_duplicate_detected_before(db: Session, client1: models.Client, client2: models.Client) -> bool:
    if not str(client1.id) < str(client2.id):
        temp = client1
        client1 = client2
        client2 = temp

    return len([_ for _ in db.scalars(
        select(models.DetectedPotentialClientDuplicates)
        .where(
            (models.DetectedPotentialClientDuplicates.client1Id == client1.id)
            & (models.DetectedPotentialClientDuplicates.client2Id == client2.id)
        )
    )]) > 0


def find_potential_client_duplicates(db: Session) -> None:
    clients = get_all_clients(db=db)

    for i in range(len(clients)):

        client1 = clients[i]

        if client1.firstName.lower() == "notprovided" and client1.lastName.lower() == "notprovided":
            continue

        for j in range(i+1, len(clients)):

            client2 = clients[j]

            if client2.firstName.lower() == "notprovided" and client2.lastName.lower() == "notprovided":
                continue

            if client1.id == client2.id:
                continue

            if is_potential_client_duplicate_detected_before(db=db, client1=client1, client2=client2):
                continue

            similarity_score = 0

            client_1_all_names = [n.strip().lower() for n in client1.firstName.split(" ") + client1.lastName.split(" ")]
            client_2_all_names = [n.strip().lower() for n in client2.firstName.split(" ") + client2.lastName.split(" ")]

            for client_1_name in client_1_all_names:
                if len(client_1_name) < 3:
                    continue
                for client_2_name in client_2_all_names:
                    if len(client_2_name) < 3:
                        continue
                    if client_1_name == client_2_name:
                        similarity_score += 2
                    elif levenshtein_distance(client_1_name, client_2_name) < 4:
                        similarity_score += 1

            client_1_email = client1.emailAddress.lower().replace(" ", "")
            client_2_email = client2.emailAddress.lower().replace(" ", "")

            if client_1_email == client_2_email:
                similarity_score += 2
            elif levenshtein_distance(client_1_email, client_2_email) < 4:
                similarity_score += 1

            if similarity_score >= 2:
                c1_id = client1.id
                c2_id = client2.id
                if str(c2_id) < str(c1_id):
                    temp = c1_id
                    c1_id = c2_id
                    c2_id = temp
                potential_duplicate = models.DetectedPotentialClientDuplicates(
                    client1Id=c1_id,
                    client2Id=c2_id,
                    similarityScore=similarity_score
                )
                db.add(potential_duplicate)
                db.commit()


def get_potential_client_duplicate(db: Session, potential_client_duplicate_id: UUID) -> models.DetectedPotentialClientDuplicates:
    return db.scalar(
        select(models.DetectedPotentialClientDuplicates)
        .where(models.DetectedPotentialClientDuplicates.id == potential_client_duplicate_id)
    )


def get_potential_client_duplicates_for_client(db: Session, client_id: UUID) -> list[models.DetectedPotentialClientDuplicates]:
    return [_ for _ in db.scalars(
        select(models.DetectedPotentialClientDuplicates)
        .where(
            (models.DetectedPotentialClientDuplicates.client1Id == client_id)
            | (models.DetectedPotentialClientDuplicates.client2Id == client_id)
        )
    )]


def resolve_client_duplicate(db: Session, potential_client_duplicate_id: UUID, discard_client_id: UUID, keep_client_id: UUID) -> None:
    potential_client_duplicate = get_potential_client_duplicate(db=db, potential_client_duplicate_id=potential_client_duplicate_id)

    if potential_client_duplicate is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"description": "Potential client duplicate not found"})

    if (
            (potential_client_duplicate.client1Id != discard_client_id and potential_client_duplicate.client1Id != keep_client_id)
            or (potential_client_duplicate.client2Id != discard_client_id and potential_client_duplicate.client2Id != keep_client_id)):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"description": "One of the clients is not part of this potential duplicate"})

    discard_client = get_client(db=db, client_id=discard_client_id)
    keep_client = get_client(db=db, client_id=keep_client_id)

    if discard_client is None or keep_client is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"description": "One or more clients not found!"})

    discard_client_contracts = get_contracts(db=db, client_id=discard_client_id)

    for contract in discard_client_contracts:
        contract.clientId = keep_client_id

    discard_client_appointments = get_appointments(db=db, client_id=discard_client_id)

    for appointment in discard_client_appointments:
        appointment.clientId = keep_client_id

    discard_client_logins = get_client_logins(db=db, client_id=discard_client_id)

    for login in discard_client_logins:
        db.delete(login)

    db.commit()

    keep_client.preBecycleSurveyCompleted |= discard_client.preBecycleSurveyCompleted
    keep_client.periBecycleSurveyCompleted |= discard_client.periBecycleSurveyCompleted
    keep_client.postBecycleSurveyCompleted |= discard_client.postBecycleSurveyCompleted

    db.delete(potential_client_duplicate)
    db.commit()

    for potential_client_duplicate_other in get_potential_client_duplicates_for_client(db=db, client_id=discard_client_id):
        db.delete(potential_client_duplicate_other)
    db.commit()

    db.delete(discard_client)

    db.commit()


def ignore_potential_client_duplicate(db: Session, potential_client_duplicate_id: UUID) -> models.DetectedPotentialClientDuplicates:
    potential_client_duplicate = get_potential_client_duplicate(db=db, potential_client_duplicate_id=potential_client_duplicate_id)
    if potential_client_duplicate is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"description": "Potential client duplicate not found"})

    potential_client_duplicate.ignore = True

    db.commit()

    return potential_client_duplicate




def get_potential_bike_duplicates_detected(db: Session) -> list[models.DetectedPotentialBikeDuplicates]:
    return [_ for _ in db.scalars(
        select(models.DetectedPotentialBikeDuplicates)
        .order_by(models.DetectedPotentialBikeDuplicates.similarityScore)
    )]


def is_potential_bike_duplicate_detected_before(db: Session, bike1: models.Bike, bike2: models.Bike) -> bool:
    if not str(bike1.id) < str(bike2.id):
        temp = bike1
        bike1 = bike2
        bike2 = temp

    return len([_ for _ in db.scalars(
        select(models.DetectedPotentialBikeDuplicates)
        .where(
            (models.DetectedPotentialBikeDuplicates.bike1Id == bike1.id)
            & (models.DetectedPotentialBikeDuplicates.bike2Id == bike2.id)
        )
    )]) > 0


def find_potential_bike_duplicates(db: Session) -> None:
    bikes = get_all_bikes(db=db)

    for i in range(len(bikes)):

        bike1 = bikes[i]

        if bike1.make.lower() == "notprovided" and bike1.model.lower() == "notprovided":
            continue

        for j in range(i+1, len(bikes)):

            bike2 = bikes[j]

            if bike2.make.lower() == "notprovided" and bike2.model.lower() == "notprovided":
                continue

            if bike1.id == bike2.id:
                continue

            if is_potential_bike_duplicate_detected_before(db=db, bike1=bike1, bike2=bike2):
                continue

            similarity_score = 0

            bike_1_all_names = [n.strip().lower() for n in bike1.make.split(" ") + bike1.model.split(" ")]
            bike_2_all_names = [n.strip().lower() for n in bike2.make.split(" ") + bike2.model.split(" ")]

            for bike_1_name in bike_1_all_names:
                if len(bike_1_name) < 3:
                    continue
                for bike_2_name in bike_2_all_names:
                    if len(bike_2_name) < 3:
                        continue
                    if bike_1_name == bike_2_name:
                        similarity_score += 2
                    elif levenshtein_distance(bike_1_name, bike_2_name) < 4:
                        similarity_score += 1

            bike_1_all_design = [n.strip().lower() for n in bike1.colour.split(" ") + (bike1.decals.split(" ") if bike1.decals is not None else [])]
            bike_2_all_design = [n.strip().lower() for n in bike2.colour.split(" ") + (bike2.decals.split(" ") if bike2.decals is not None else [])]

            except_tokens = ["and", "with"]

            for bike_1_design in bike_1_all_design:
                if len(bike_1_design) < 3:
                    continue
                if bike_1_design in except_tokens:
                    continue
                for bike_2_design in bike_2_all_design:
                    if len(bike_2_design) < 3:
                        continue
                    if bike_2_design in except_tokens:
                        continue
                    if bike_1_design == bike_2_design:
                        similarity_score += 2
                    elif levenshtein_distance(bike_1_design, bike_2_design) < 4:
                        similarity_score += 1

            bike_1_serial_number = bike1.serialNumber.lower().replace(" ", "")
            bike_2_serial_number = bike2.serialNumber.lower().replace(" ", "")

            if bike_1_serial_number == bike_2_serial_number:
                similarity_score += 2
            elif levenshtein_distance(bike_1_serial_number, bike_2_serial_number) < 4:
                similarity_score += 1

            if similarity_score >= 4:
                b1_id = bike1.id
                b2_id = bike2.id
                if str(b2_id) < str(b1_id):
                    temp = b1_id
                    b1_id = b2_id
                    b2_id = temp
                potential_duplicate = models.DetectedPotentialBikeDuplicates(
                    bike1Id=b1_id,
                    bike2Id=b2_id,
                    similarityScore=similarity_score
                )
                db.add(potential_duplicate)
                db.commit()


def get_potential_bike_duplicate(db: Session, potential_bike_duplicate_id: UUID) -> models.DetectedPotentialBikeDuplicates:
    return db.scalar(
        select(models.DetectedPotentialBikeDuplicates)
        .where(models.DetectedPotentialBikeDuplicates.id == potential_bike_duplicate_id)
    )


def get_potential_bike_duplicates_for_bike(db: Session, bike_id: UUID) -> list[models.DetectedPotentialBikeDuplicates]:
    return [_ for _ in db.scalars(
        select(models.DetectedPotentialBikeDuplicates)
        .where(
            (models.DetectedPotentialBikeDuplicates.bike1Id == bike_id)
            | (models.DetectedPotentialBikeDuplicates.bike2Id == bike_id)
        )
    )]


def resolve_bike_duplicate(db: Session, potential_bike_duplicate_id: UUID, discard_bike_id: UUID, keep_bike_id: UUID) -> None:
    potential_bike_duplicate = get_potential_bike_duplicate(db=db, potential_bike_duplicate_id=potential_bike_duplicate_id)

    if potential_bike_duplicate is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"description": "Potential bike duplicate not found"})

    if (
            (potential_bike_duplicate.bike1Id != discard_bike_id and potential_bike_duplicate.bike1Id != keep_bike_id)
            or (potential_bike_duplicate.bike2Id != discard_bike_id and potential_bike_duplicate.bike2Id != keep_bike_id)):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"description": "One of the bikes is not part of this potential duplicate"})

    discard_bike = get_bike(db=db, bike_id=discard_bike_id)
    keep_bike = get_bike(db=db, bike_id=keep_bike_id)

    if discard_bike is None or keep_bike is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"description": "One or more bikes not found!"})

    discard_bike_contracts = get_contracts(db=db, bike_id=discard_bike_id)

    for contract in discard_bike_contracts:
        contract.bikeId = keep_bike_id

    db.commit()

    db.delete(potential_bike_duplicate)
    db.commit()

    for potential_bike_duplicate_other in get_potential_bike_duplicates_for_bike(db=db, bike_id=discard_bike_id):
        db.delete(potential_bike_duplicate_other)
    db.commit()

    db.delete(discard_bike)

    db.commit()


def ignore_potential_bike_duplicate(db: Session, potential_bike_duplicate_id: UUID) -> models.DetectedPotentialBikeDuplicates:
    potential_bike_duplicate = get_potential_bike_duplicate(db=db, potential_bike_duplicate_id=potential_bike_duplicate_id)
    if potential_bike_duplicate is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"description": "Potential bike duplicate not found"})

    potential_bike_duplicate.ignore = True

    db.commit()

    return potential_bike_duplicate


def get_contracts_takeout_excel(db: Session) -> str:
    contracts = get_contracts(db=db)

    contracts_df = pd.DataFrame(columns=["Name", "Email Address",
                                         "Start Date", "End Date",
                                         "Make", "Model", "Colour", "Decals", "Serial Number", "Condition", "Notes",
                                         "Contract Type",
                                         "Working Volunteer", "Checking Volunteer",
                                         "Deposit Amount Collected", "Deposit Collected By",
                                         "Returned Date", "Return Received By",
                                         "Deposit Amount Returned", "Deposit Returned By"])

    for contract in contracts:
        contract_row = contract.to_raw_dict()
        contracts_df.loc[len(contracts_df)] = contract_row

    deposit_book = get_deposit_balances_book(db=db)

    deposit_holders = []
    for date in deposit_book.dayBalances:
        deposit_holders_on_date = deposit_book.dayBalances[date].balances.keys()
        for deposit_holder in deposit_holders_on_date:
            if deposit_holder not in deposit_holders:
                deposit_holders.append(deposit_holder)

    columns = ["Name", "Type"] + deposit_holders


    deposit_book_df = pd.concat([
        pd.DataFrame([{
            "Name": t.title,
            "Type": t.type,
            **t.diff_by_username
        } for t in deposit_book.dayBalances[date].transactions] + [{
            "Name": None,
            "Type": None,
        }] + [{
            "Name": "DAILY DIFF",
            "Type": None,
            **deposit_book.dayBalances[date].diff
        }] + [{
            "Name": None,
            "Type": None,
        }] + [{
            "Name": "DAILY BALANCE",
            "Type": None,
            **deposit_book.dayBalances[date].balances
        }] + [{
            "Name": None,
            "Type": None,
        }] + [{
            "Name": None,
            "Type": None,
        }], columns=columns, index=None) for date in deposit_book.dayBalances.keys()
    ], keys=deposit_book.dayBalances.keys(), names=["Date", "Row ID"])

    deposit_book_df.reset_index(level="Date", inplace=True)


    current_dir = os.path.dirname(__file__)
    data_dir = os.path.join(os.path.dirname(current_dir), "data")
    output_file_path = os.path.join(data_dir, "contracts.xlsx")

    with pd.ExcelWriter(output_file_path, engine="openpyxl") as writer:
        contracts_df.to_excel(writer, sheet_name="contracts", index=False)
        deposit_book_df.to_excel(writer, sheet_name="deposits", index=False)

    return output_file_path


