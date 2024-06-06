import pylogram
from pylogram import raw


class GetConfig:
    async def get_config(
            self: "pylogram.Client",
    ) -> raw.base.Config:
        return await self.invoke(raw.functions.help.GetConfig())
