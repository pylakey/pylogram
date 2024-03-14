import pylogram
from pylogram import raw


class CreateForumTopic:
    async def create_forum_topic(
            self: "pylogram.Client",
            chat_id: int | str,
            title: str,
            icon_color: int | None = None,
            icon_emoji_id: int | None = None,
            send_as: int | str | pylogram.raw.base.InputPeer | None = None
    ) -> raw.types.Updates:
        peer = await self.resolve_peer(chat_id)

        if bool(send_as) and not isinstance(send_as, pylogram.raw.base.InputPeer):
            send_as = await self.resolve_peer(send_as)

        return await self.invoke(
            raw.functions.channels.CreateForumTopic(
                channel=peer,
                title=title,
                random_id=self.rnd_id(),
                icon_color=icon_color,
                icon_emoji_id=icon_emoji_id,
                send_as=send_as
            )
        )
