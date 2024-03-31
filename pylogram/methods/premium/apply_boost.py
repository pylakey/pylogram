import pylogram
from pylogram import raw


class ApplyBoost:
    async def apply_boost(
            self: "pylogram.Client",
            chat_id: int | str,
            slots: list[int]
    ) -> raw.base.premium.MyBoosts:
        peer = await self.resolve_peer(chat_id)
        return await self.invoke(
            raw.functions.premium.ApplyBoost(
                peer=peer,
                slots=slots
            )
        )
