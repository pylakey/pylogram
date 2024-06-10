import pylogram
from pylogram import raw


class GetAccountTTL:
    async def get_account_ttl(
            self: "pylogram.Client",
    ) -> raw.base.AccountDaysTTL:
        return await self.invoke(raw.functions.account.GetAccountTTL())
