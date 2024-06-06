import pylogram
from pylogram import raw


class GetCdnConfig:
    async def get_cdn_config(
            self: "pylogram.Client",
    ) -> raw.base.CdnConfig:
        return await self.invoke(raw.functions.help.GetCdnConfig())
