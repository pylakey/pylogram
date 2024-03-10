import pylogram
from pylogram import raw


class GetConnectedBots:
    async def get_connected_bots(
            self: "pylogram.Client",
    ) -> raw.types.account.ConnectedBots:
        return await self.invoke(raw.functions.account.GetConnectedBots())
