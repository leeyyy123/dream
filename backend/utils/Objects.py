from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Users:
    Name: str
    Email: str
    Password: str
    UserID: Optional[int] = None
    AvatarUrl: Optional[str] = None
    Gender: Optional[str] = None
    BirthDate: Optional[str] = None
    RegisterTime: Optional[datetime] = None
    LastLogin: Optional[datetime] = None

    def __repr__(self):
        return (f"<Users(UserID={self.UserID}, Name='{self.Name}', Email='{self.Email}', "
                f"Password={self.Password}, RegisterTime={self.RegisterTime}, LastLogin={self.LastLogin})>")