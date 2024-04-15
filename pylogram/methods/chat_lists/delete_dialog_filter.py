import pylogram


class DeleteDialogFilter:
    async def delete_dialog_filter(self: "pylogram.Client", dialog_filter_id: int) -> bool:
        return await self.invoke(
            pylogram.raw.functions.messages.UpdateDialogFilter(
                id=dialog_filter_id,
                filter=None
            )
        )
