from typing import Optional, List

from sqlalchemy.orm import Session

from app.core.auth.security import get_password_hash
from app.modules.auth.models import Account, AccountToken, AdminUser


class AccountRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, email: str, username: str, password: str) -> Account:
        hashed_password = get_password_hash(password)
        db_account = Account(
            email=email,
            username=username,
            hashed_password=hashed_password
        )
        self.db.add(db_account)
        self.db.commit()
        self.db.refresh(db_account)
        return db_account

    def get_by_id(self, account_id: str) -> Optional[Account]:
        return self.db.query(Account).filter(Account.id == account_id).first()

    def get_by_email(self, email: str) -> Optional[Account]:
        return self.db.query(Account).filter(Account.email == email).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Account]:
        return self.db.query(Account).offset(skip).limit(limit).all()

    def update(self, account_id: str, **kwargs) -> Optional[Account]:
        account = self.get_by_id(account_id)
        if account:
            for key, value in kwargs.items():
                if key == 'password':
                    value = get_password_hash(value)
                    key = 'hashed_password'
                setattr(account, key, value)
            self.db.commit()
            self.db.refresh(account)
        return account

    def delete(self, account_id: str) -> bool:
        account = self.get_by_id(account_id)
        if account:
            self.db.delete(account)
            self.db.commit()
            return True
        return False


class AccountTokenRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, account_id: str, token: str, description: Optional[str] = None) -> AccountToken:
        db_token = AccountToken(
            account_id=account_id,
            token=token,
            description=description
        )
        self.db.add(db_token)
        self.db.commit()
        self.db.refresh(db_token)
        return db_token

    def get_by_id(self, token_id: str) -> Optional[AccountToken]:
        return self.db.query(AccountToken).filter(AccountToken.id == token_id).first()

    def get_by_account_id(self, account_id: str) -> List[AccountToken]:
        return self.db.query(AccountToken).filter(AccountToken.account_id == account_id).all()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[AccountToken]:
        return self.db.query(AccountToken).offset(skip).limit(limit).all()

    def update(self, token_id: str, **kwargs) -> Optional[AccountToken]:
        token = self.get_by_id(token_id)
        if token:
            for key, value in kwargs.items():
                setattr(token, key, value)
            self.db.commit()
            self.db.refresh(token)
        return token

    def delete(self, token_id: str) -> bool:
        token = self.get_by_id(token_id)
        if token:
            self.db.delete(token)
            self.db.commit()
            return True
        return False


class AdminUserRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, email: str, username: str, password: str) -> AdminUser:
        hashed_password = get_password_hash(password)
        db_user = AdminUser(
            email=email,
            username=username,
            hashed_password=hashed_password
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def get_by_id(self, user_id: str) -> Optional[AdminUser]:
        return self.db.query(AdminUser).filter(AdminUser.id == user_id).first()

    def get_by_email(self, email: str) -> Optional[AdminUser]:
        return self.db.query(AdminUser).filter(AdminUser.email == email).first()

    def get_all(self) -> List[AdminUser]:
        return self.db.query(AdminUser).all()

    def update(self, user_id: str, **kwargs) -> Optional[AdminUser]:
        user = self.get_by_id(user_id)
        if user:
            for key, value in kwargs.items():
                if key == 'password':
                    value = get_password_hash(value)
                    key = 'hashed_password'
                setattr(user, key, value)
            self.db.commit()
            self.db.refresh(user)
        return user

    def delete(self, user_id: str) -> bool:
        user = self.get_by_id(user_id)
        if user:
            self.db.delete(user)
            self.db.commit()
            return True
        return False
