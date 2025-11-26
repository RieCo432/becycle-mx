import shutil
from datetime import datetime, date
import os
from math import ceil
from uuid import UUID

import pandas as pd
from sqlalchemy import select

import app.models as models
import app.schemas as schemas
from sqlalchemy.orm import Session
from fastapi import UploadFile, HTTPException, status


def create_expense(db: Session, expense_user: models.User, expense_data: schemas.ExpenseBase, receipt_file: UploadFile) -> models.Expense:
    if receipt_file.content_type.startswith("image"):
        from PIL import Image

        current_dir = os.path.dirname(__file__)
        temp_data_dir = os.path.join(os.path.dirname(current_dir), "data", "temp")
        output_file_path = os.path.join(temp_data_dir, receipt_file.filename)

        with Image.open(receipt_file.file) as image:
            larger = max(image.size)

            if larger > 2048:
                ratio = int(ceil(larger / 2048))
                image = image.reduce(ratio)

            image.save(output_file_path)

        with open(output_file_path, "rb") as fin:
            new_expense_receipt = models.ExpenseReceipt(
                content=fin.read(),
            )

    else:
        new_expense_receipt = models.ExpenseReceipt(
            content=receipt_file.file.read(),
        )

    db.add(new_expense_receipt)
    db.commit()

    new_expense = models.Expense(
        type=expense_data.type,
        notes=expense_data.notes,
        expenseUserId=expense_user.id,
        expenseDate=expense_data.expenseDate,
        receiptContentType=receipt_file.content_type,
        amount=expense_data.amount,
        receiptFileId=new_expense_receipt.id,
        tagId=expense_data.tagId
    )
    db.add(new_expense)
    db.commit()

    return new_expense


def get_expense_receipt_file(db: Session, expense_id: UUID) -> dict[str, str]:
    expense = db.scalar(
        select(models.Expense)
        .where(models.Expense.id == expense_id)
    )

    current_dir = os.path.dirname(__file__)
    temp_data_dir = os.path.join(os.path.dirname(current_dir), "data", "temp")
    output_file_path = os.path.join(temp_data_dir, str(expense.id))

    with open(output_file_path, "wb") as fout:
        fout.write(expense.receiptFile.content)

    return {"path": output_file_path, "media_type": expense.receiptContentType}


def patch_expense_transferred(db: Session, expense_id: UUID, treasurer_user: models.User) -> models.Expense:
    expense = db.scalar(
        select(models.Expense)
        .where(
            (models.Expense.transferDate == None)
            & (models.Expense.id == expense_id)
        )
    )

    if expense is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"description": "This expense does not exist or has already been transferred"})

    expense.treasurerUserId = treasurer_user.id
    expense.transferDate = datetime.utcnow().date()

    db.commit()

    return expense


def delete_expense(db: Session, expense_id: UUID) -> None:
    expense = db.scalar(
        select(models.Expense)
        .where(models.Expense.id == expense_id)
    )

    if expense is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"description": "Expense not found"})

    db.delete(expense)
    db.commit()


def update_expense(db: Session, expense_id: UUID, updated_expense_data: schemas.ExpenseUpdate) -> models.Expense:
    expense = db.scalar(
        select(models.Expense)
        .where(models.Expense.id == expense_id)
    )

    if expense is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"description": "Expense not found"})

    if updated_expense_data.type is not None:
        expense.type = updated_expense_data.type
    if updated_expense_data.notes is not None:
        expense.notes = updated_expense_data.notes
    if updated_expense_data.expenseDate is not None:
        expense.expenseDate = updated_expense_data.expenseDate
    if updated_expense_data.amount is not None:
        expense.amount = updated_expense_data.amount
    if updated_expense_data.tagId is not None:
        expense.tagId = updated_expense_data.tagId
    if updated_expense_data.expenseUserId is not None:
        expense.expenseUserId = updated_expense_data.expenseUserId
    if updated_expense_data.transferred is not None:
        if updated_expense_data.transferred:
            if updated_expense_data.treasurerUserId is not None:
                expense.treasurerUserId = updated_expense_data.treasurerUserId
            if updated_expense_data.transferDate is not None:
                expense.transferDate = updated_expense_data.transferDate
        else:
            expense.treasurerUserId = None
            expense.transferDate = None

    db.commit()
    return expense


def get_expenses(db: Session, tag_id: str | None) -> list[models.Expense]:
    expenses = select(models.Expense)
    if tag_id is not None:
        expenses = expenses.where(models.Expense.tagId == tag_id)
    return [
        _ for _ in db.scalars(expenses)
    ]

def get_expense_tags(db: Session, inactive: bool) -> list[models.ExpenseTag]:
    tags = select(models.ExpenseTag)

    if not inactive:
        tags = tags.where(models.ExpenseTag.active == True)

    return [_ for _ in db.scalars(tags)]

def create_expense_tag(db: Session, expense_tag: schemas.ExpenseTag) -> models.ExpenseTag:
    new_expense_tag = models.ExpenseTag(
        id=expense_tag.id,
        description=expense_tag.description,
        active=expense_tag.active,
    )
    db.add(new_expense_tag)
    db.commit()
    return new_expense_tag

def update_expense_tag(db: Session, expense_tag_id: str, expense_tag_update: schemas.ExpenseTagUpdate) -> models.ExpenseTag:
    expense_tag = db.scalar(select(models.ExpenseTag).where(models.ExpenseTag.id == expense_tag_id))
    if expense_tag_update.description is not None:
        expense_tag.description = expense_tag_update.description
    if expense_tag_update.active is not None:
        expense_tag.active = expense_tag_update.active
    db.commit()

    return expense_tag

def does_expense_exist(db: Session, expense_user: models.User, expense_data: schemas.ExpenseBase) -> bool:
    existing_expense = db.scalar(
        select(models.Expense)
        .where(
            (models.Expense.expenseUserId == expense_user.id)
            & (models.Expense.type == expense_data.type)
            & (models.Expense.amount == expense_data.amount)
            & (models.Expense.tagId == expense_data.tagId)
            & (models.Expense.expenseDate == expense_data.expenseDate)
        )
    )
    return existing_expense is not None


def get_all_expenses_and_receipts(db: Session, start_date: date, end_date: date) -> dict[str, str]:
    all_receipts_in_period = [_ for _ in db.scalars(
        select(models.Expense)
        .where(
            (models.Expense.transferDate != None)
            & (models.Expense.transferDate >= start_date)
            & (models.Expense.transferDate <= end_date)
        )
        .order_by(models.Expense.transferDate.desc())
    )]

    expenses_data = []

    current_dir = os.path.dirname(__file__)

    temp_data_dir = os.path.join(os.path.dirname(current_dir), "data", "temp")

    export_dir = "expenses-export-"+datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

    export_dir_path = os.path.join(temp_data_dir, export_dir)
    receipts_dir = os.path.join(export_dir_path, "receipts")

    os.makedirs(receipts_dir, exist_ok=True)

    for expense in all_receipts_in_period:
        receipt_file_name = str(expense.receiptFileId) + "." + expense.receiptContentType.split("/")[1]

        expenses_data.append({
            "transferDate": expense.transferDate,
            "expenseDate": expense.expenseDate,
            "username": expense.expenseUser.username,
            "amountOut": abs(expense.amount) if expense.amount < 0 else "",
            "amountIn": expense.amount if expense.amount > 0 else "",
            "tagId": expense.tagId,
            "type": expense.type,
            "notes": expense.notes,
            "receiptId": receipt_file_name
        })


        output_file_path = os.path.join(receipts_dir, receipt_file_name)
        with open(output_file_path, "wb") as fout:
            fout.write(expense.receiptFile.content)


    expenses_filepath = os.path.join(export_dir_path, "expenses.xlsx")
    expenses_df = pd.DataFrame(expenses_data)

    with pd.ExcelWriter(expenses_filepath, engine="openpyxl") as writer:
        expenses_df.to_excel(writer, sheet_name="Expenses", index=False)

    zip_name = export_dir + ".zip"
    zip_path = os.path.join(temp_data_dir, export_dir)
    shutil.make_archive(zip_path, "zip", export_dir_path)

    return {
        "path": zip_path+".zip",
        "filename": zip_name,
        "media_type": "application/zip"
    }

