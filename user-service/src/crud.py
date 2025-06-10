# user-service/src/crud.py
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from models import User # Assuming models.py is in the same directory or accessible in PYTHONPATH
from typing import List, Optional, Dict, Any

class UserCRUD:
    """
    CRUD class for user database operations
    """

    def create_user(self, db: Session, user_data: Dict[str, Any]) -> User:
        """
        Create a new user
        """
        try:
            db_user = User(**user_data)
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            return db_user
        except IntegrityError:
            db.rollback()
            raise ValueError("User with this email already exists")

    def get_user(self, db: Session, user_id: int) -> Optional[User]:
        """
        Get user by ID
        """
        return db.query(User).filter(User.id == user_id).first()

    def get_user_by_email(self, db: Session, email: str) -> Optional[User]:
        """
        Get user by email
        """
        return db.query(User).filter(User.email == email).first()

    def get_users(self, db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        """
        Get a list of users with pagination
        """
        return db.query(User).offset(skip).limit(limit).all()

    def update_user(self, db: Session, user_id: int, user_data: Dict[str, Any]) -> Optional[User]:
        """
        Update user information
        """
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user:
            return None

        for field, value in user_data.items():
            if hasattr(db_user, field) and value is not None:
                setattr(db_user, field, value)

        try:
            db.commit()
            db.refresh(db_user)
            return db_user
        except IntegrityError:
            db.rollback()
            raise ValueError("Update failed due to constraint violation")

    def delete_user(self, db: Session, user_id: int) -> bool:
        """
        Delete a user
        """
        db_user = db.query(User).filter(User.id == user_id).first()
        if not db_user:
            return False

        db.delete(db_user)
        db.commit()
        return True

    def get_active_users(self, db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        """
        Get active users
        """
        return db.query(User).filter(User.is_active == True).offset(skip).limit(limit).all()

    def verify_user(self, db: Session, user_id: int) -> Optional[User]:
        """
        Verify a user
        """
        return self.update_user(db, user_id, {"is_verified": True})

    def deactivate_user(self, db: Session, user_id: int) -> Optional[User]:
        """
        Deactivate a user
        """
        return self.update_user(db, user_id, {"is_active": False})