from database import db
import uuid

class UserCredits(db.Model):
    __tablename__ = "user_credits"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.UUID(as_uuid=True),
        nullable=False,
        unique=True,
        default=uuid.uuid4
    )

    total_credits = db.Column(db.Integer, default=200)
    credits_used = db.Column(db.Integer, default=0)
