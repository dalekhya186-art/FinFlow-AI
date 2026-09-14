from sqlalchemy import Column, Integer, String, Boolean
from database import Base


class User(Base):

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    email = Column(
        String,
        unique=True,
        index=True,
        nullable=False
    )

    password = Column(
        String,
        nullable=False
    )

    name = Column(
        String,
        nullable=True
    )

    automatic_verification = Column(
        Boolean,
        default=True
    )

    ai_categorization = Column(
        Boolean,
        default=True
    )

    processing_notifications = Column(
        Boolean,
        default=True
    )