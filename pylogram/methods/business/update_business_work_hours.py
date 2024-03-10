import pylogram
from pylogram import raw


class UpdateBusinessWorkHours:
    async def update_business_work_hours(
            self: "pylogram.Client",
            timezone_id: str,
            weekly_open: list[raw.types.BusinessWeeklyOpen],
            open_now: bool = None
    ) -> bool:
        return await self.invoke(
            raw.functions.account.UpdateBusinessWorkHours(
                business_work_hours=raw.types.BusinessWorkHours(
                    timezone_id=timezone_id,
                    weekly_open=weekly_open,
                    open_now=open_now
                )
            )
        )
