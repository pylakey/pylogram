import pylogram
from pylogram import raw


class GetBoostsList:
    async def get_boosts_list(
            self: "pylogram.Client",
            chat_id: int | str,
            offset: str = "",
            limit: int = 0,
            gifts: bool | None = None
    ) -> raw.base.premium.BoostsList:
        chat_peer = await self.resolve_peer(chat_id)

        return await self.invoke(
            raw.functions.premium.GetBoostsList(
                peer=chat_peer,
                offset=offset,
                limit=limit,
                gifts=gifts
            )
        )
