import pylogram
from pylogram import raw


class GetMyBoosts:
    async def get_my_boosts(self: "pylogram.Client") -> raw.base.premium.MyBoosts:
        return await self.invoke(raw.functions.premium.GetMyBoosts())
