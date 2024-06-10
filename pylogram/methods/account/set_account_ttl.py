import pylogram
from pylogram import raw
from pylogram.raw.types import AccountDaysTTL


class SetAccountTTL:
    async def set_account_ttl(
            self: "pylogram.Client",
            days: int = 365
    ) -> raw.base.AccountDaysTTL:
        return await self.invoke(raw.functions.account.SetAccountTTL(ttl=AccountDaysTTL(days=days)))
