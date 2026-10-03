from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Integer,String, Text, func
from sqlalchemy.orm import Mapped, mapped_column 

from database import Base


class FraudCheckLog(Base):
    """Лог проверки (email, Ip)"""

    __tablename__ = "fraud_check_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)


    #Входные данные
    email: Mapped[str] = mapped_column(String(320), index=True, nullable=False)
    ip_address: Mapped[str] = mapped_column(String(45), index=True, nullable=False)

    #IP воздействие
    ip_country: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    ip_country_code: Mapped[Optional[str]] = mapped_column(String(8), nullable=True)
    ip_city: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    ip_isp: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    ip_is_proxy: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    ip_is_hosting: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    #Email
    email_domain: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    email_is_disposable: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    email_is_free: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


    fraud_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False, index=True)
    verdict: Mapped[str] = mapped_column(String(16), nullable=False, index=True)

    #Диагностика упавших проверок
    failed_checks: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    #методанные время 
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )

    def __repr__(self) -> str:
        return (
            f"<FraudCheckLog id={self.id} email={self.email!r} "
            f"ip={self.ip_address!r} score={self.fraud_score} "
            f"verdict={self.verdict}>"
        )