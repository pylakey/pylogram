import pylogram
from pylogram import raw


class UpdateStatus:
    async def update_status(
            self: "pylogram.Client",
            offline: bool = False
    ) -> bool:
        return await self.invoke(raw.functions.account.UpdateStatus(offline=offline))
