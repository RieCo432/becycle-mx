from sqlalchemy.orm import Session
import app.models as models
import app.schemas as schemas
from uuid import UUID
from sqlalchemy import select


def create_deposit_exchange(
        db: Session,
        deposit_exchange_data: schemas.DepositExchangeCreate,
        from_user_id: UUID,
        to_user_id: UUID) -> models.DepositExchange:

    deposit_exchange = models.DepositExchange(
        amount=deposit_exchange_data.amount,
        fromUserId=from_user_id,
        toUserId=to_user_id
    )

    db.add(deposit_exchange)
    db.commit()

    return deposit_exchange


def get_deposit_exchanges(db: Session) -> list[models.DepositExchange]:
    deposit_exchanges = [_ for _ in db.scalars(
        select(models.DepositExchange)
        .order_by(models.DepositExchange.timestamp.desc())
    )]

    return deposit_exchanges
