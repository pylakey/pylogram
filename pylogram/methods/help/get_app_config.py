import pylogram
from pylogram import raw


class GetAppConfig:
    async def get_app_config(
            self: "pylogram.Client",
            hash_: int = 0
    ) -> raw.base.help.AppConfig:
        # TODO: Add pagination support
        return await self.invoke(raw.functions.help.GetAppConfig(hash=hash_))
