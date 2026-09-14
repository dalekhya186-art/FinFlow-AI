
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime

from database import Base


class Transaction(Base):

    __tablename__ = "transactions"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    customer_id = Column(
        String,
        index=True,
        nullable=False
    )

    document_id = Column(
        Integer,
        nullable=True
    )

    transaction_type = Column(
        String,
        nullable=True
    )

    document_number = Column(
        String,
        nullable=True
    )

    amount = Column(
        String,
        nullable=True
    )

    paid_amount = Column(
        String,
        nullable=True
    )

    due_amount = Column(
        String,
        nullable=True
    )

    payment_status = Column(
        String,
        nullable=True
    )

    transaction_date = Column(
        String,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )
