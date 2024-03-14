import pylogram
from pylogram import raw


class GetForumTopics:
    async def get_forum_topics(
            self: "pylogram.Client",
            chat_id: int | str,
            offset_date: int = 0,
            offset_id: int = 0,
            offset_topic: int = 0,
            limit: int = 100,
            q: str | None = None
    ) -> raw.types.messages.ForumTopics:
        peer = await self.resolve_peer(chat_id)
        return await self.invoke(
            raw.functions.channels.GetForumTopics(
                channel=peer,
                offset_date=offset_date,
                offset_id=offset_id,
                offset_topic=offset_topic,
                limit=limit,
                q=q
            )
        )
