import pylogram
from pylogram import raw


class GetUserBoosts:
    async def get_user_boosts(
            self: "pylogram.Client",
            chat_id: int | str,
            user_id: int | str = "me"
    ) -> raw.base.premium.BoostsList:
        chat_peer = await self.resolve_peer(chat_id)
        user_peer = await self.resolve_peer(user_id)

        return await self.invoke(
            raw.functions.premium.GetUserBoosts(
                peer=chat_peer,
                user_id=user_peer
            )
        )
