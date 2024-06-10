import pylogram
from pylogram import raw


class GetPrivacy:
    async def get_privacy(
            self: "pylogram.Client",
            key: raw.base.InputPrivacyKey,
    ) -> raw.base.account.PrivacyRules:
        return await self.invoke(raw.functions.account.GetPrivacy(key=key))

    async def get_privacy_about(
            self: "GetPrivacy",
    ) -> raw.base.account.PrivacyRules:
        return await self.get_privacy(raw.types.InputPrivacyKeyAbout())

    async def get_privacy_added_by_phone(
            self: "GetPrivacy",
    ) -> raw.base.account.PrivacyRules:
        return await self.get_privacy(raw.types.InputPrivacyKeyAddedByPhone())

    async def get_privacy_birthday(
            self: "GetPrivacy",
    ) -> raw.base.account.PrivacyRules:
        return await self.get_privacy(raw.types.InputPrivacyKeyBirthday())

    async def get_privacy_chat_invite(
            self: "GetPrivacy",
    ) -> raw.base.account.PrivacyRules:
        return await self.get_privacy(raw.types.InputPrivacyKeyChatInvite())

    async def get_privacy_forwards(
            self: "GetPrivacy",
    ) -> raw.base.account.PrivacyRules:
        return await self.get_privacy(raw.types.InputPrivacyKeyForwards())

    async def get_privacy_phone_call(
            self: "GetPrivacy",
    ) -> raw.base.account.PrivacyRules:
        return await self.get_privacy(raw.types.InputPrivacyKeyPhoneCall())

    async def get_privacy_phone_number(
            self: "GetPrivacy",
    ) -> raw.base.account.PrivacyRules:
        return await self.get_privacy(raw.types.InputPrivacyKeyPhoneNumber())

    async def get_privacy_phone_p2p(
            self: "GetPrivacy",
    ) -> raw.base.account.PrivacyRules:
        return await self.get_privacy(raw.types.InputPrivacyKeyPhoneP2P())

    async def get_privacy_profile_photo(
            self: "GetPrivacy",
    ) -> raw.base.account.PrivacyRules:
        return await self.get_privacy(raw.types.InputPrivacyKeyProfilePhoto())

    async def get_privacy_status_timestamp(
            self: "GetPrivacy",
    ) -> raw.base.account.PrivacyRules:
        return await self.get_privacy(raw.types.InputPrivacyKeyStatusTimestamp())

    async def get_privacy_voice_messages(
            self: "GetPrivacy",
    ) -> raw.base.account.PrivacyRules:
        return await self.get_privacy(raw.types.InputPrivacyKeyVoiceMessages())
