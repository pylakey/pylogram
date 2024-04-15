import pylogram


class ExportDialogFilterInvite:
    async def export_dialog_filter_invite(
            self: "pylogram.Client",
            dialog_filter: pylogram.raw.base.DialogFilter,
            title: str | None = None
    ) -> pylogram.raw.base.ExportedChatlistInvite:
        if isinstance(dialog_filter, pylogram.raw.types.DialogFilterDefault):
            raise ValueError('Default filters cannot be exported!')

        result = await self.invoke(
            pylogram.raw.functions.chatlists.ExportChatlistInvite(
                title=title or dialog_filter.title,
                chatlist=pylogram.raw.types.InputChatlistDialogFilter(
                    filter_id=dialog_filter.id
                ),
                peers=dialog_filter.include_peers
            )
        )

        return result.invite
