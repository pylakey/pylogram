import pylogram
from pylogram import raw


class GetMyBoosts:
    async def get_my_boosts(self: "pylogram.Client") -> raw.types.premium.MyBoosts:
        return await self.invoke(raw.functions.premium.GetMyBoosts())
