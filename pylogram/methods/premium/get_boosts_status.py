import pylogram
from pylogram import raw


class GetBoostsStatus:
    async def get_boosts_status(
            self: "pylogram.Client",
            chat_id: int | str,
    ) -> raw.base.premium.BoostsStatus:
        chat_peer = await self.resolve_peer(chat_id)

        return await self.invoke(
            raw.functions.premium.GetBoostsStatus(
                peer=chat_peer,
            )
        )
