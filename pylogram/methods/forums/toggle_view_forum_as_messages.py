import pylogram
from pylogram import raw


class ToggleViewForumAsMessages:
    async def toggle_view_forum_as_messages(
            self: "pylogram.Client",
            chat_id: int | str,
            enabled: bool,
    ) -> raw.types.Updates:
        peer = await self.resolve_peer(chat_id)
        return await self.invoke(
            raw.functions.channels.ToggleViewForumAsMessages(
                channel=peer,
                enabled=enabled
            )
        )
