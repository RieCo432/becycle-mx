import os

from datetime import date, datetime, timezone
from math import ceil
from uuid import UUID

from dateutil.relativedelta import relativedelta
from fastapi import HTTPException, status, UploadFile
from sqlalchemy import select, and_
from sqlalchemy.orm import Session

import app.models as models
import app.schemas as schemas

from .transactions import get_transaction_header, post_transaction_header
from app.services.accounts_helpers import AccountTypes
from app.models import TransactionHeader, TransactionLine

CONTRACT_EXPIRE_MONTHS = int(os.environ['CONTRACT_EXPIRE_MONTHS'])


def get_contracts(db: Session, client_id: UUID | None = None, bike_id: UUID | None = None, open: bool = True, closed: bool = True, expired: bool = True, draft: bool = False) -> list[models.Contract]:
    primary_query_filter = []

    if client_id is not None:
        primary_query_filter.append((models.Contract.clientId == client_id))
    if bike_id is not None:
        primary_query_filter.append((models.Contract.bikeId == bike_id))

    contracts = [_ for _ in db.scalars(
        select(models.Contract)
        .where(
            and_(*primary_query_filter)
            & (
                ((models.Contract.returnedDate != None) & closed)
                | ((models.Contract.returnedDate == None) & (models.Contract.endDate != None) & (models.Contract.endDate < datetime.utcnow().date()) & expired)
                | ((models.Contract.returnedDate == None) & (models.Contract.endDate != None) & (models.Contract.endDate >= datetime.utcnow().date()) & open)
                | (models.Contract.isDraft == draft)
            )
        )
    )]

    return contracts


def get_contract_start_dates(db: Session) -> list[date]:
    return [_ for _ in db.scalars(
        select(models.Contract.startDate)
        .distinct()
    )]


def get_contract_returned_dates(db: Session) -> list[date]:
    return [_ for _ in db.scalars(
        select(models.Contract.returnedDate)
        .where(models.Contract.returnedDate != None)
        .distinct()
    )]


def get_contracts_by_start_date(db: Session, start_date: date) -> list[models.Contract]:
    return [_ for _ in db.scalars(
        select(models.Contract)
        .where(models.Contract.startDate == start_date)
    )]


def get_contracts_by_returned_date(db: Session, returned_date: date) -> list[models.Contract]:
    return [_ for _ in db.scalars(
        select(models.Contract)
        .where(models.Contract.returnedDate == returned_date)
    )]


def get_contracts_grouped_by_start_date(db: Session) -> dict[date, list[models.Contract]]:
    contracts_by_start_date = {start_date: get_contracts_by_start_date(db=db, start_date=start_date) for start_date in get_contract_start_dates(db=db)}
    return contracts_by_start_date


def get_contracts_grouped_by_returned_date(db: Session) -> dict[date, list[models.Contract]]:
    contracts_by_returned_date = {returned_date: get_contracts_by_returned_date(db=db, returned_date=returned_date) for returned_date in get_contract_returned_dates(db=db)}
    return contracts_by_returned_date


def get_contract(db: Session, contract_id: UUID, throw_on_draft: bool = True) -> models.Contract:
    contract = db.scalar(
        select(models.Contract)
        .where(models.Contract.id == contract_id)
    )
    if contract is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"description": f"Contract with id {contract_id} not found."})
    
    if throw_on_draft and contract.isDraft:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"description": f"Contract with id {contract_id} is a draft."})
    
    return contract


def does_contract_exist(db: Session, contract_data: schemas.ContractCreate):
    contracts = get_contracts(db=db, client_id=contract_data.clientId, bike_id=contract_data.bikeId, open=True, closed=True, expired=True)

    for contract in contracts:
        if contract.startDate == datetime.utcnow().date():
            return True

    return False


def return_contract(
        db: Session,
        contract_id: UUID,
        deposit_settled_transaction_header_id: UUID,
        return_accepting_user_id: UUID) -> models.Contract:

    contract = get_contract(db=db, contract_id=contract_id)

    deposit_settled_transaction_header = get_transaction_header(db=db, transaction_header_id=deposit_settled_transaction_header_id)
    if not deposit_settled_transaction_header:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"description": "Deposit settled transaction header not found!"},
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    account_balances_for_contract = {}
    for transaction_header in contract.depositTransactionHeaders:
        for transaction_line in transaction_header.transactionLines:
            if transaction_line.account.type == AccountTypes.LIABILITY:
                account_balances_for_contract[transaction_line.account.id] = account_balances_for_contract.get(transaction_line.account.id, 0) + transaction_line.amount
    
    liability_transaction_line = [tl for tl in deposit_settled_transaction_header.transactionLines if tl.account.type == AccountTypes.LIABILITY][0]

    if sum(
            [tl.amount for tl in deposit_settled_transaction_header.transactionLines if tl.account.type == AccountTypes.LIABILITY]
    ) != -sum(
        [tl.amount for tl in [th for th in contract.depositTransactionHeaders if th.event == "deposit_collected"][0].transactionLines if tl.account.type == AccountTypes.LIABILITY]
    ):
        for tl in deposit_settled_transaction_header.transactionLines:
            db.delete(tl)
        db.delete(deposit_settled_transaction_header)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"description": "The liability change in this transaction does not match the liability incurred when the contract was made! Transaction has been deleted."},
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    if abs(account_balances_for_contract.get(liability_transaction_line.account.id, 0)) < abs(liability_transaction_line.amount) :
        for tl in deposit_settled_transaction_header.transactionLines:
            db.delete(tl)
        db.delete(deposit_settled_transaction_header)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"description": "The selected liability account does not have enough liability on this contract! Transaction has been deleted."},
        )

    if deposit_settled_transaction_header.postedOn is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"description": "This deposit settlement transaction header isn't posted yet!"},
        )

    contract.returnAcceptingUserId = return_accepting_user_id
    # contract.depositReturningUserId = deposit_returning_user_id
    contract.returnedDate = datetime.now(timezone.utc).date()
    deposit_settled_transaction_header.contractId = contract.id

    db.commit()

    return contract


def extend_contract(db: Session, contract_id: UUID) -> models.Contract:
    contract = get_contract(db=db, contract_id=contract_id)
    
    if any([th.event == "deposit_forfeited" for th in contract.depositTransactionHeaders]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"description": "Cannot extend contract with forfeited deposit"},
        )
    
    last_deposit_transaction_header = sorted(contract.depositTransactionHeaders, key=lambda th: th.postedOn, reverse=True)[0]
    if last_deposit_transaction_header.event == "liability_dormant":
        admin = db.scalar(select(models.User).where(models.User.username == "admin"))
        if admin is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"description": "Something went wrong while re-activating the deposit liability!"},
            )
        liability_reactivated_transaction_header = TransactionHeader(
            contractId=contract.id,
            event="liability_reactivated",
            createdByUserId=admin.id,
        )
        db.add(liability_reactivated_transaction_header)
        db.flush()
        
        for tl in last_deposit_transaction_header.transactionLines:
            transaction_line = TransactionLine(
                transactionHeaderId=liability_reactivated_transaction_header.id,
                account=tl.account,
                amount=-tl.amount
            )
            db.add(transaction_line)
        db.commit()
        
        post_transaction_header(db=db, transaction_header_id=liability_reactivated_transaction_header.id, user=admin, override_access=True)
        contract.liabilityDormantSent = False
        db.commit()

    contract.endDate = (datetime.utcnow() + relativedelta(months=6)).date()

    db.commit()

    return contract


def get_client_contract(db: Session, client_id: UUID, contract_id: UUID) -> models.Contract:
    contract = db.scalar(
        select(models.Contract)
        .where(
            (models.Contract.id == contract_id)
            & (models.Contract.clientId == client_id)
        )
    )
    if contract is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"description": f"Contract with id {contract_id} not found."})
    return contract


def get_paper_contract_suggestions(db: Session, old_id: str) -> list[str]:
    return [_ for _ in db.scalars(
        select(models.PaperContract.id)
        .where(models.PaperContract.id.startswith(old_id))
    )]


def get_paper_contract(db: Session, paper_id: str) -> UUID:
    id = db.scalar(
        select(models.PaperContract.contractId)
        .where(models.PaperContract.id == paper_id)
    )
    if id is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"description": f"Paper Contract with id {paper_id} not found."})
    return id


def delete_contract(db: Session, contract_id: UUID) -> None:
    # TODO: cannot just delete a contract. the transaction headers must be dealt with
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail={"description": "Deleting Contracts is not supported at this time."})
    contract = get_contract(db=db, contract_id=contract_id)
    paper_contract = db.scalar(
        select(models.PaperContract)
        .where(models.PaperContract.contractId == contract_id)
    )
    if paper_contract is not None:
        db.delete(paper_contract)
        db.commit()
    db.delete(contract)
    db.commit()


def patch_contract_details(db: Session, contract_id: UUID, contract_patch_data: schemas.ContractPatch) -> models.Contract:
    contract = get_contract(db=db, contract_id=contract_id)

    if contract_patch_data.conditionOfBike is not None:
        contract.conditionOfBike = contract_patch_data.conditionOfBike

    if contract_patch_data.contractType is not None:
        contract.contractType = contract_patch_data.contractType

    if contract_patch_data.notes is not None:
        contract.notes = contract_patch_data.notes

    if contract_patch_data.startDate is not None:
        contract.startDate = contract_patch_data.startDate

    if contract_patch_data.endDate is not None:
        contract.endDate = contract_patch_data.endDate

    if contract_patch_data.workingUserId is not None:
        contract.workingUserId = contract_patch_data.workingUserId

    if contract_patch_data.checkingUserId is not None:
        contract.checkingUserId = contract_patch_data.checkingUserId


    if contract.returnedDate is not None and contract_patch_data.returnedDate is not None:

        if contract_patch_data.returnAcceptingUserId is not None:
            contract.returnAcceptingUserId = contract_patch_data.returnAcceptingUserId

        if contract_patch_data.returnedDate is not None:
            contract.returnedDate = contract_patch_data.returnedDate

    db.commit()

    return contract


def get_contracts_for_expiry_email(db: Session) -> list[models.Contract]:
    ending_before = datetime.utcnow().date() + relativedelta(days=14)
    return [
        _ for _ in db.scalars(
            select(models.Contract)
            .where(
                (models.Contract.returnedDate == None)
                & (models.Contract.expiryReminderSent == False)
                & (models.Contract.endDate <= ending_before)
                & (models.Contract.endDate >= datetime.utcnow().date())
            )
        )
    ]


def send_expiry_emails(db: Session):
    for contract in get_contracts_for_expiry_email(db=db):
        contract.expiryReminderSent = contract.send_expiry_reminder_email()


    db.commit()


def start_new_contract(db: Session) -> models.Contract:
    contract_draft = models.Contract(
        isDraft=True
    )

    db.add(contract_draft)
    db.commit()

    return contract_draft

def get_contract_draft(db: Session, contract_id: UUID) -> models.Contract:
    contract_draft = db.scalar(
        select(models.Contract)
        .where(models.Contract.id == contract_id)
        .where(models.Contract.isDraft == True)
    )
    if contract_draft is None:
        raise HTTPException(status_code=404, detail={"description": "Contract draft not found"})

    return contract_draft


def does_contract_draft_exist(db: Session, contract_draft_id: UUID) -> bool:
    return get_contract_draft(db=db, contract_id=contract_draft_id) is not None


def update_contract_draft_client(db: Session, contract_id: UUID, client_id: UUID) -> models.Contract:
    contract_draft = get_contract_draft(db=db, contract_id=contract_id)
    contract_draft.clientId = client_id
    db.commit()
    return contract_draft

def update_contract_draft_bike(db: Session, contract_id: UUID, bike_id: UUID) -> models.Contract:
    contract_draft = get_contract_draft(db=db, contract_id=contract_id)
    contract_draft.bikeId = bike_id
    db.commit()
    return contract_draft

def update_contract_draft_details(db: Session, contract_id: UUID, contract_details: schemas.ContractDetails) -> models.Contract:
    contract_draft = get_contract_draft(db=db, contract_id=contract_id)
    contract_draft.conditionOfBike = contract_details.conditionOfBike
    contract_draft.contractType = contract_details.contractType
    contract_draft.notes = contract_details.notes
    db.commit()
    return contract_draft

def update_contract_draft_deposit(db: Session, contract_id: UUID, deposit_collected_transaction_header_id: UUID) -> models.Contract:
    contract_draft = get_contract_draft(db=db, contract_id=contract_id)
    
    transaction_header = db.get(models.TransactionHeader, deposit_collected_transaction_header_id)
    
    if not transaction_header.postedOn:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"description": "Deposit transaction header must be posted before it can be used to collect deposit!"},
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    deposit_amount = abs([tl.amount for tl in transaction_header.transactionLines if tl.account.type == AccountTypes.LIABILITY][0])
    
    
    contract_draft.bike.roughValue = max(deposit_amount, 4000)
    transaction_header.contractId = contract_id
    db.commit()
    return contract_draft

def update_contract_draft_working_user(db: Session, contract_draft_id: UUID, working_user: models.User) -> models.Contract:
    contract_draft = get_contract_draft(db=db, contract_id=contract_draft_id)
    contract_draft.workingUserId = working_user.id
    db.commit()
    return contract_draft

def is_checking_user_same_as_working_user(db: Session, contract_draft_id: UUID, checking_user: models.User) -> bool:
    contract_draft = get_contract_draft(db=db, contract_id=contract_draft_id)
    return contract_draft.workingUserId == checking_user.id

def update_contract_draft_checking_user(db: Session, contract_id: UUID, checking_user: models.User) -> models.Contract:
    contract_draft = get_contract_draft(db=db, contract_id=contract_id)
    contract_draft.checkingUserId = checking_user.id
    db.commit()
    return contract_draft

def does_contract_exist_already(db: Session, contract_id: UUID) -> bool:
    contract_draft = get_contract_draft(db=db, contract_id=contract_id)

    matching_contract = db.scalar(
        select(models.Contract)
        .where(
            (models.Contract.clientId == contract_draft.clientId)
            & (models.Contract.bikeId == contract_draft.bikeId)
            & (models.Contract.startDate == contract_draft.startDate)
            & (models.Contract.id != contract_draft.id)
        )
    )

    return matching_contract is not None

def submit_contract(db: Session, contract_id: UUID) -> models.Contract:
    contract_draft = get_contract_draft(db=db, contract_id=contract_id)
    
    deposit_collected_transaction_headers = [_ for _ in filter(lambda header: header.event == "deposit_collected", contract_draft.depositTransactionHeaders)]
    if deposit_collected_transaction_headers is None or len(deposit_collected_transaction_headers) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"description": "Deposit transaction header not found!"},
            headers={"WWW-Authenticate": "Bearer"}
        )
    transaction_header = deposit_collected_transaction_headers[0]    
    if transaction_header.postedOn is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"description": "Deposit transaction header must be posted before it can be used to collect deposit!"},
        )
    
    contract_draft.startDate = datetime.now(timezone.utc).date()
    contract_draft.endDate = datetime.now(timezone.utc) + relativedelta(months=CONTRACT_EXPIRE_MONTHS)
    contract_draft.isDraft = False
    db.commit()
    return contract_draft


def get_collected_and_returned_deposit_amounts(db: Session, contract_id: UUID) -> tuple[int, int | None]:
    contract = get_contract(db=db, contract_id=contract_id, throw_on_draft=False)
    if contract is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"description": "Contract not found!"},
            headers={"WWW-Authenticate": "Bearer"}
        )

    deposit_amount_collected = db.scalar(
        select(models.TransactionLine.amount)
        .join(models.TransactionHeader)
        .join(models.Account)
        .where(
            (models.TransactionHeader.contractId == contract.id)
            & (models.TransactionHeader.event == "deposit_collected")
            & (models.Account.type == AccountTypes.LIABILITY)
        )
    )

    deposit_amount_returned = db.scalar(
        select(models.TransactionLine.amount)
        .join(models.TransactionHeader)
        .join(models.Account)
        .where(
            (models.TransactionHeader.contractId == contract.id)
            & (models.TransactionHeader.event == "deposit_settled")
            & (models.Account.type == AccountTypes.ASSET)
        )
    )
    
    deposit_amount_collected = -deposit_amount_collected if deposit_amount_collected is not None else 0
    deposit_amount_returned = -deposit_amount_returned if deposit_amount_returned is not None else None
    
    return deposit_amount_collected, deposit_amount_returned


def get_client_restricted_contract(db: Session, client_id: UUID, contract: models.Contract | None = None, contract_id: UUID | None = None) -> schemas.ContractRestricted:
    if contract is None and contract_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"description": "Either contract or contract_id must be provided!"},
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    if contract is None and contract_id is not None:
        contract = get_client_contract(db=db, client_id=client_id, contract_id=contract_id)

    deposit_amount_collected, deposit_amount_returned = get_collected_and_returned_deposit_amounts(db=db, contract_id=contract.id)

    return schemas.ContractRestricted(
        id=contract.id,
        startDate=contract.startDate,
        endDate=contract.endDate,
        returnedDate=contract.returnedDate,
        detailsSent=contract.detailsSent,
        expiryReminderSent=contract.expiryReminderSent,
        returnDetailsSent=contract.returnDetailsSent,
        clientId=contract.clientId,
        bikeId=contract.bikeId,
        conditionOfBike=contract.conditionOfBike,
        contractType=contract.contractType,
        notes=contract.notes,
        crimeReports=[
            schemas.CrimeReport(
                id=report.id,
                crimeNumber=report.crimeNumber,
                createdOn=report.createdOn,
                closedOn=report.closedOn,
                contractId=report.contractId
            ) for report in contract.crimeReports
        ],
        depositAmountCollectedRestricted=deposit_amount_collected,
        depositAmountReturnedRestricted=deposit_amount_returned,
        isDraft=contract.isDraft
    )

def get_client_restricted_contracts(db: Session, client_id: UUID) -> list[schemas.ContractRestricted]:
    contracts = get_contracts(db=db, client_id=client_id, open=True, closed=True, expired=True, draft=True)
    
    return [
        get_client_restricted_contract(db=db, client_id=client_id, contract=contract)
        for contract in contracts
    ]


def make_contract_liability_dormant(db: Session, contract_id: UUID, active_liability_account_id: UUID, dormant_liability_account_id: UUID, admin_user: models.User) -> None:
    contract = get_contract(db=db, contract_id=contract_id)

    liability_made_dormant_transaction_header = TransactionHeader(
        contractId=contract.id,
        event="liability_dormant",
        createdByUserId=admin_user.id,
    )
    db.add(liability_made_dormant_transaction_header)
    db.flush()

    remove_active_liability_transaction_line = TransactionLine(
        transactionHeaderId=liability_made_dormant_transaction_header.id,
        accountId=active_liability_account_id,
        amount=contract.liability_collected
    )

    add_dormant_liability_transaction_line = TransactionLine(
        transactionHeaderId=liability_made_dormant_transaction_header.id,
        accountId=dormant_liability_account_id,
        amount=-contract.liability_collected
    )

    db.add(remove_active_liability_transaction_line)
    db.add(add_dormant_liability_transaction_line)

    db.commit()

    post_transaction_header(db=db, transaction_header_id=liability_made_dormant_transaction_header.id, user=admin_user, override_access=True)


def make_all_old_liabilities_dormant(db: Session) -> None:
    # Gather the grace period
    try:
        grace_period = int(os.environ.get("CONTRACT_EXPIRY_GRACE_PERIOD_MONTHS", 6))
    except Exception as e:
        print(e, " Exiting liabilities dormancy process...")
        return

    # Get the admin account, the transactions will be done under its name
    admin_user = db.scalar(
        select(models.User)
        .where(models.User.username == "admin")
    )
    if admin_user is None:
        print("Admin user not found! Exiting liabilities dormancy process...")
        return
        


    # find the active deposit liability account
    active_bike_deposits_liability_accounts = [account for account in db.scalars(
        select (models.Account)
        .where(models.Account.type == AccountTypes.LIABILITY)
        .where(models.Account.name.like("%active%"))
    ) if "return" in account.showInUis]
    if len(active_bike_deposits_liability_accounts) != 1:
        print("Active bike deposits liability account not found! Exiting liabilities dormancy process...")
        return
    active_bike_deposits_liability_account = active_bike_deposits_liability_accounts[0]

    # find the dormant deposit liability account
    dormant_bike_deposits_liability_accounts = [account for account in db.scalars(
        select (models.Account)
        .where(models.Account.type == AccountTypes.LIABILITY)
        .where(models.Account.name.like("%dormant%"))
    ) if "return" in account.showInUis]
    if len(dormant_bike_deposits_liability_accounts) != 1:
        print("Dormant bike deposits liability account not found! Exiting liabilities dormancy process...")
        return
    dormant_bike_deposits_liability_account = dormant_bike_deposits_liability_accounts[0]


    # get unreturned contracts past the grace period
    contracts_past_grace_period = [_ for _ in db.scalars(
        select(models.Contract)
        .where(models.Contract.endDate < (datetime.now(timezone.utc) - relativedelta(months=grace_period)))
        .where(models.Contract.returnedDate == None)
    )]

    for contract in contracts_past_grace_period:
        last_transaction_header = sorted(contract.depositTransactionHeaders, key=lambda th: th.postedOn)[-1]
        # last transaction should be one of "deposit_collected", "deposit_settled", "liability_reactivated", "liability_dormant", "deposit_forfeited", or 
        # the liability should only be made dormant if the last transaction is deposit collection, or liability reactivation
        if last_transaction_header.event in ["deposit_collected", "liability_reactivated"]:
            try:
                make_contract_liability_dormant(
                    db=db,
                    contract_id=contract.id,
                    active_liability_account_id=active_bike_deposits_liability_account.id,
                    dormant_liability_account_id=dormant_bike_deposits_liability_account.id,
                    admin_user=admin_user
                )
                print(f"Liability made dormant for contract {contract.id}")
            except Exception as e:
                print(
                    f"Error making contract {contract.id} liability dormant: {e}",
                )


def send_contract_grace_period_ended_emails(db: Session) -> None:
    unnotified_contracts_with_dormant_liabilities = [_ for _ in db.scalars(
        select(models.Contract)
        .join(models.TransactionHeader)
        .where(models.TransactionHeader.event == "liability_dormant")
        .where(models.Contract.liabilityDormantSent == False)
        .distinct(models.Contract.id)
    )]
    
    for contract in unnotified_contracts_with_dormant_liabilities:
        contract.liabilityDormantSent = contract.send_contract_grace_period_ended_email()
        db.commit()


def save_contract_photo(db: Session, contract_id: UUID, photo: UploadFile, auto_commit: bool = True) -> models.ContractPhoto:
    if get_contract(db=db, contract_id=contract_id, throw_on_draft=False) is None:
        raise HTTPException(status_code=404, detail={"description": "Contract not found"})
    
    if not photo.content_type.startswith("image"):
        raise HTTPException(status_code=400, detail={"description": "Invalid file type"})
        
    from PIL import Image

    current_dir = os.path.dirname(__file__)
    temp_data_dir = os.path.join(os.path.dirname(current_dir), "data", "temp")
    output_file_path = os.path.join(temp_data_dir, photo.filename)

    with Image.open(photo.file) as image:
        larger = max(image.size)

        if larger > 4096:
            ratio = int(ceil(larger / 4096))
            image = image.reduce(ratio)

        image.save(output_file_path)

    with open(output_file_path, "rb") as fin:
        new_contract_photo = models.ContractPhoto(
            contractId=contract_id,
            contentType=photo.content_type,
            content=fin.read(),
        )

    db.add(new_contract_photo)
    if auto_commit:
        db.commit()
    
    return new_contract_photo


def add_photos_to_contract(db: Session, contract_id: UUID, photos: list[UploadFile]) -> models.Contract:
    contract = get_contract(db=db, contract_id=contract_id, throw_on_draft=False)
    
    for photo in photos:
        save_contract_photo(db=db, contract_id=contract_id, photo=photo, auto_commit=False)
    
    db.commit()
    return contract


def delete_contract_photo(db: Session, contract_id: UUID, contract_photo_id: UUID) -> None:
    photo = get_contract_photo(db=db, contract_id=contract_id, contract_photo_id=contract_photo_id)
    if photo is None:
        raise HTTPException(status_code=404, detail={"description": "Contract photo not found"})
    db.delete(photo)
    db.commit()
    
    
def get_contract_photo(db: Session, contract_id: UUID, contract_photo_id: UUID) -> dict[str, str]:
    contract = get_contract(db=db, contract_id=contract_id, throw_on_draft=False)
    if contract is None:
        raise HTTPException(status_code=404, detail={"description": "Contract not found"})
    
    photo = db.scalar(
        select(models.ContractPhoto)
        .where(models.ContractPhoto.contractId == contract_id)
        .where(models.ContractPhoto.id == contract_photo_id)
    )
    
    current_dir = os.path.dirname(__file__)
    temp_data_dir = os.path.join(os.path.dirname(current_dir), "data", "temp")

    output_file_path = os.path.join(temp_data_dir, str(photo.id))

    with open(output_file_path, "wb") as fout:
        fout.write(photo.content)

    return {"path": output_file_path, "media_type": photo.contentType}


def get_contract_photos_ids(db: Session, contract_id: UUID) -> list[UUID]:
    photos_ids = db.scalars(
        select(models.ContractPhoto.id)
        .where(models.ContractPhoto.contractId == contract_id)
    )

    return [photo_id for photo_id in photos_ids]
        