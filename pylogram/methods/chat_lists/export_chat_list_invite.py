import pylogram


class ExportChatListInvite:
    async def export_chat_list_invite(
            self: "pylogram.Client",
            dialog_filter_id: int,
            title: str | None = None,
    ) -> pylogram.raw.base.ExportedChatlistInvite:
        dialog_filter = await self.get_dialog_filter_by_id(dialog_filter_id)

        if dialog_filter is None:
            raise ValueError(f'Filter with id {dialog_filter_id} not found!')

        return await self.export_dialog_filter_invite(dialog_filter, title)
