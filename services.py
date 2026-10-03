import asyncio
from typing import Optional

import httpx 
from sqlalchemy.ext.asyncio import AsyncSession

from models import FraudCheckLog
from schemas import CheckResponse


# справочник

DISPOSABLE_DOMAINS: set[str] = {
    "mailinator.com", "10minutemail.com", "tempmail.com", "temp-mail.org",
    "guerrillamail.com", "throwawaymail.com", "yopmail.com", "sharklasers.com",
    "getnada.com", "maildrop.cc", "trashmail.com", "fakeinbox.com",
    "dispostable.com", "mintemail.com", "tempinbox.com", "mohmal.com",
    "emailondeck.com", "spamgourmet.com", "mailexpire.com", "throwam.com",
    "mailnesia.com", "mailcatch.com", "tempr.email", "discard.email",
    "mailsac.com", "inboxkitten.com", "tempmailo.com", "moakt.com",
}

FREE_DOMAINS: set[str] = {
    "gmail.com", "googlemail.com", "yandex.ru", "ya.ru",
    "mail.ru", "inbox.ru", "list.ru", "bk.ru",
    "outlook.com", "hotmail.com", "live.com", "msn.com",
    "yahoo.com", "icloud.com", "me.com", "protonmail.com",
    "rambler.ru", "aol.com", "gmx.com", "zoho.com",
}

# email checker 

def check_email(email: str) -> dict:
    """проверка по локал справочнику"""
    domain = email.rsplit("@", 1)[-1].lower()
    return {
        "email_domain": domain,
        "email_is_disposable": domain in DISPOSABLE_DOMAINS,
        "email_is_free": domain in FREE_DOMAINS,
    }

async def check_ip(ip: str) -> Optional[dict]:
    url = f"http://ip-api.com/json/{ip}?fields=status,country,countryCode,city,isp,proxy,hosting"

    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()

            if data.get("status") != "success":
                return None

        return {
            "ip_country": data.get("country"),
            "ip_country_code": data.get("countryCode"),
            "ip_city": data.get("city"),
            "ip_isp": data.get("isp"),
            "ip_is_proxy": data.get("proxy", False),
            "ip_is_hosting": data.get("hosting", False),
        }

    except (httpx.TimeoutException, httpx.HTTPError):
        return None

# скролинг

def calculate_verdict(
    ip_data: Optional[dict],
    email_data: dict,
) -> tuple[int, str]:
    """Считает фрод-скор и вердикт."""
    score = 0

    if ip_data:
        if ip_data.get("ip_is_proxy"):
            score += 40
        if ip_data.get("ip_is_hosting"):
            score += 20

    if email_data.get("email_is_disposable"):
        score += 50

    if email_data.get("email_is_free"):
        score += 5

    if score >= 50:
        verdict = "BLOCK"
    elif score >= 20:
        verdict = "MANUAL_REVIEW"
    else:
        verdict = "ALLOW"

    return score, verdict

async def run_full_check(
    email: str,
    ip_address: str,
    session: AsyncSession,
) -> CheckResponse:
    """Полная проверка: IP + email параллельно, скоринг, запись в БД."""
    failed: list[str] = []

    ip_result, email_result = await asyncio.gather(
        check_ip(ip_address),
        asyncio.to_thread(check_email, email),
    )

    if ip_result is None:
        failed.append("ip_check")

    score, verdict = calculate_verdict(
        ip_data=ip_result,
        email_data=email_result,
    )

    log = FraudCheckLog(
        email=email,
        ip_address=ip_address,
        ip_country=ip_result.get("ip_country") if ip_result else None,
        ip_country_code=ip_result.get("ip_country_code") if ip_result else None,
        ip_city=ip_result.get("ip_city") if ip_result else None,
        ip_isp=ip_result.get("ip_isp") if ip_result else None,
        ip_is_proxy=ip_result.get("ip_is_proxy", False) if ip_result else False,
        ip_is_hosting=ip_result.get("ip_is_hosting", False) if ip_result else False,
        email_domain=email_result["email_domain"],
        email_is_disposable=email_result["email_is_disposable"],
        email_is_free=email_result["email_is_free"],
        fraud_score=score,
        verdict=verdict,
        failed_checks=",".join(failed) if failed else None,
    )

    session.add(log)
    await session.commit()
    await session.refresh(log)

    return CheckResponse.model_validate(log)