import pylogram
from pylogram import raw


class UpdateConnectedBot:
    async def update_connected_bot(
            self: "pylogram.Client",
            bot: int | str,
            existing_chats: bool | None = None,
            new_chats: bool | None = None,
            contacts: bool | None = None,
            non_contacts: bool | None = None,
            exclude_selected: bool | None = None,
            users: list[int | str] | None = None,
            can_reply: bool | None = None,
            deleted: bool | None = None,
    ) -> raw.base.Updates:
        bot = await self.resolve_peer(bot)

        if users is not None:
            users = [await self.resolve_peer(u) for u in users]

        return await self.invoke(
            raw.functions.account.UpdateConnectedBot(
                bot=bot,
                recipients=raw.types.InputBusinessRecipients(
                    existing_chats=existing_chats,
                    new_chats=new_chats,
                    contacts=contacts,
                    non_contacts=non_contacts,
                    exclude_selected=exclude_selected,
                    users=users
                ),
                can_reply=can_reply,
                deleted=deleted
            )
        )
