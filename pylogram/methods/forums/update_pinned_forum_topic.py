import pylogram
from pylogram import raw


class UpdatePinnedForumTopic:
    async def update_pinned_forum_topic(
            self: "pylogram.Client",
            chat_id: int | str,
            topic_id: int,
            pinned: bool,
    ) -> raw.types.Updates:
        peer = await self.resolve_peer(chat_id)
        return await self.invoke(
            raw.functions.channels.UpdatePinnedForumTopic(
                channel=peer,
                topic_id=topic_id,
                pinned=pinned
            )
        )
