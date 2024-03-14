import pylogram
from pylogram import raw


class ReorderPinnedForumTopics:
    async def reorder_pinned_forum_topics(
            self: "pylogram.Client",
            chat_id: int | str,
            order: list[int],
            force: bool | None = None,
    ) -> raw.types.Updates:
        peer = await self.resolve_peer(chat_id)
        return await self.invoke(
            raw.functions.channels.ReorderPinnedForumTopics(
                channel=peer,
                order=order,
                force=force
            )
        )
