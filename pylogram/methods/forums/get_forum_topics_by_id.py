import pylogram
from pylogram import raw


class GetForumTopicsByID:
    async def get_forum_topics_by_id(
            self: "pylogram.Client",
            chat_id: int | str,
            topics: list[int]
    ) -> raw.types.messages.ForumTopics:
        peer = await self.resolve_peer(chat_id)
        return await self.invoke(
            raw.functions.channels.GetForumTopicsByID(
                channel=peer,
                topics=topics
            )
        )
