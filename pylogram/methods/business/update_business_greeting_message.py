import pylogram
from pylogram import raw


class UpdateBusinessGreetingMessage:
    async def update_business_greeting_message(
            self: "pylogram.Client",
            shortcut_id: int,
            no_activity_days: int,
            existing_chats: bool | None = None,
            new_chats: bool | None = None,
            contacts: bool | None = None,
            non_contacts: bool | None = None,
            exclude_selected: bool | None = None,
            users: list[int | str] | None = None
    ) -> bool:
        if users is not None:
            users = [await self.resolve_peer(u) for u in users]

        return await self.invoke(
            raw.functions.account.UpdateBusinessGreetingMessage(
                message=raw.types.InputBusinessGreetingMessage(
                    shortcut_id=shortcut_id,
                    recipients=raw.types.InputBusinessRecipients(
                        existing_chats=existing_chats,
                        new_chats=new_chats,
                        contacts=contacts,
                        non_contacts=non_contacts,
                        exclude_selected=exclude_selected,
                        users=users
                    ),
                    no_activity_days=no_activity_days,
                )
            )
        )
