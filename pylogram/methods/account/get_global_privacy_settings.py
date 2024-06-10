import pylogram
from pylogram import raw


class GetGlobalPrivacySettings:

    async def get_global_privacy_settings(
            self: "pylogram.Client",
    ) -> raw.base.GlobalPrivacySettings:
        return await self.invoke(raw.functions.account.GetGlobalPrivacySettings())
