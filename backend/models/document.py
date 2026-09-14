from sqlalchemy import Column, Integer, String
from database import Base


class Document(Base):

    __tablename__ = "documents"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    file_name = Column(
        String,
        nullable=False
    )

    invoice_number = Column(
        String,
        nullable=True
    )

    vendor = Column(
        String,
        nullable=True
    )

    total_amount = Column(
        String,
        nullable=True
    )

    category = Column(
        String,
        nullable=True
    )

    verification_status = Column(
        String,
        nullable=True
    )

    workflow_status = Column(
        String,
        nullable=True
    )