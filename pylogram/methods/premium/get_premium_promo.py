import pylogram
from pylogram import raw


class GetPremiumPromo:
    async def get_premium_promo(
            self: "pylogram.Client",
    ) -> raw.types.help.PremiumPromo:
        return await self.invoke(raw.functions.help.GetPremiumPromo())
