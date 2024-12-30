from datetime import datetime
import os
from math import ceil
from uuid import UUID

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


def get_expenses(db: Session) -> list[models.Expense]:
    return [
        _ for _ in db.scalars(select(models.Expense))
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

