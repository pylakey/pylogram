import pylogram


class UpdateDialogFiltersOrder:
    async def update_dialog_filters_order(self: "pylogram.Client", order: list[int]) -> bool:
        return await self.invoke(
            pylogram.raw.functions.messages.UpdateDialogFiltersOrder(
                order=order
            )
        )
