import pylogram
from pylogram import raw


class EditForumTopic:
    async def edit_forum_topic(
            self: "pylogram.Client",
            chat_id: int | str,
            topic_id: int,
            title: str | None = None,
            icon_emoji_id: int | None = None,
            closed: bool | None = None,
            hidden: bool | None = None,
    ) -> raw.types.Updates:
        peer = await self.resolve_peer(chat_id)
        return await self.invoke(
            raw.functions.channels.EditForumTopic(
                channel=peer,
                topic_id=topic_id,
                title=title,
                icon_emoji_id=icon_emoji_id,
                closed=closed,
                hidden=hidden
            )
        )
