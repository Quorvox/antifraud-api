from ipaddress import IPv4Address, IPv6Address
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field



class CheckRequest(BaseModel):
    """Клиент присылает на /api/v1/check""" #docstring

    email: EmailStr = Field(..., examples=["user@mailinator.email"])
    ip_address: IPv4Address | IPv6Address = Field(..., exampless=["8.8.8.8"])


class CheckResponse(BaseModel):
    """Результат проверки - то, что отдаем клиенту"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    ip_address: str


    ip_country: Optional[str] = None
    ip_country_code: Optional[str] = None
    ip_city: Optional[str] = None
    ip_isp: Optional[str] = None
    ip_is_proxy: bool = False
    ip_is_hosting: bool = False

    email_domain: Optional[str] = None
    email_is_disposable: bool = False
    email_is_free: bool = False

    fraud_score: int
    verdict: str
    failed_checks: Optional[str] = None