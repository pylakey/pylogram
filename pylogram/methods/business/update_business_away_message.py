import pylogram
from pylogram import raw


class UpdateBusinessAwayMessage:
    async def update_business_away_message(
            self: "pylogram.Client",
            shortcut_id: int,
            schedule: raw.base.BusinessAwayMessageSchedule,
            existing_chats: bool | None = None,
            new_chats: bool | None = None,
            contacts: bool | None = None,
            non_contacts: bool | None = None,
            exclude_selected: bool | None = None,
            users: list[int | str] | None = None,
            offline_only: bool | None = None,
    ) -> bool:
        if users is not None:
            users = [await self.resolve_peer(u) for u in users]

        return await self.invoke(
            raw.functions.account.UpdateBusinessAwayMessage(
                message=raw.types.InputBusinessAwayMessage(
                    shortcut_id=shortcut_id,
                    schedule=schedule,
                    recipients=raw.types.InputBusinessRecipients(
                        existing_chats=existing_chats,
                        new_chats=new_chats,
                        contacts=contacts,
                        non_contacts=non_contacts,
                        exclude_selected=exclude_selected,
                        users=users
                    ),
                    offline_only=offline_only
                )
            )
        )
