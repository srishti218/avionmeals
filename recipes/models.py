from datetime import datetime
from database import db
import uuid
from sqlalchemy.dialects.postgresql import UUID

class Recipe(db.Model):
    __tablename__ = "recipes"

    id = db.Column(UUID(as_uuid=True), primary_key=True,default=uuid.uuid4,
    unique=True,
    nullable=False)
    user_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.JSON, nullable=False)  # full recipe JSON
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    is_saved = db.Column(db.Boolean, default=False)
