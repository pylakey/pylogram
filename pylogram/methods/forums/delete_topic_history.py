import pylogram
from pylogram import raw


class DeleteTopicHistory:
    async def delete_topic_history(
            self: "pylogram.Client",
            chat_id: int | str,
            top_msg_id: int
    ) -> raw.types.messages.AffectedHistory:
        peer = await self.resolve_peer(chat_id)
        return await self.invoke(
            raw.functions.channels.DeleteTopicHistory(
                channel=peer,
                top_msg_id=top_msg_id
            )
        )
