import pylogram
from pylogram import raw


class SetGlobalPrivacySettings:
    async def set_global_privacy_settings(
            self: "pylogram.Client",
            settings: raw.base.GlobalPrivacySettings
    ) -> raw.base.GlobalPrivacySettings:
        return await self.invoke(raw.functions.account.SetGlobalPrivacySettings(settings=settings))
