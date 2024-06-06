import pylogram
from pylogram import raw


class GetAppUpdate:
    async def get_app_update(
            self: "pylogram.Client",
            source: str,
    ) -> raw.base.help.AppUpdate:
        return await self.invoke(raw.functions.help.GetAppUpdate(source=source))
