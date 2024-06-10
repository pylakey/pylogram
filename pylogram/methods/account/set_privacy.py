import pylogram
from pylogram import raw


class SetPrivacy:
    async def set_privacy(
            self: "pylogram.Client",
            key: raw.base.InputPrivacyKey,
            rules: list[raw.base.InputPrivacyRule] = None,
    ) -> raw.base.account.PrivacyRules:
        return await self.invoke(raw.functions.account.SetPrivacy(key=key, rules=rules))

    async def set_privacy_about(
            self: "SetPrivacy",
            rules: list[raw.base.InputPrivacyRule] = None,
    ) -> raw.base.account.PrivacyRules:
        return await self.set_privacy(raw.types.InputPrivacyKeyAbout(), rules)

    async def set_privacy_added_by_phone(
            self: "SetPrivacy",
            rules: list[raw.base.InputPrivacyRule] = None,
    ) -> raw.base.account.PrivacyRules:
        return await self.set_privacy(raw.types.InputPrivacyKeyAddedByPhone(), rules)

    async def set_privacy_birthday(
            self: "SetPrivacy",
            rules: list[raw.base.InputPrivacyRule] = None,
    ) -> raw.base.account.PrivacyRules:
        return await self.set_privacy(raw.types.InputPrivacyKeyBirthday(), rules)

    async def set_privacy_chat_invite(
            self: "SetPrivacy",
            rules: list[raw.base.InputPrivacyRule] = None,
    ) -> raw.base.account.PrivacyRules:
        return await self.set_privacy(raw.types.InputPrivacyKeyChatInvite(), rules)

    async def set_privacy_forwards(
            self: "SetPrivacy",
            rules: list[raw.base.InputPrivacyRule] = None,
    ) -> raw.base.account.PrivacyRules:
        return await self.set_privacy(raw.types.InputPrivacyKeyForwards(), rules)

    async def set_privacy_phone_call(
            self: "SetPrivacy",
            rules: list[raw.base.InputPrivacyRule] = None,
    ) -> raw.base.account.PrivacyRules:
        return await self.set_privacy(raw.types.InputPrivacyKeyPhoneCall(), rules)

    async def set_privacy_phone_number(
            self: "SetPrivacy",
            rules: list[raw.base.InputPrivacyRule] = None,
    ) -> raw.base.account.PrivacyRules:
        return await self.set_privacy(raw.types.InputPrivacyKeyPhoneNumber(), rules)

    async def set_privacy_phone_p2p(
            self: "SetPrivacy",
            rules: list[raw.base.InputPrivacyRule] = None,
    ) -> raw.base.account.PrivacyRules:
        return await self.set_privacy(raw.types.InputPrivacyKeyPhoneP2P(), rules)

    async def set_privacy_profile_photo(
            self: "SetPrivacy",
            rules: list[raw.base.InputPrivacyRule] = None,
    ) -> raw.base.account.PrivacyRules:
        return await self.set_privacy(raw.types.InputPrivacyKeyProfilePhoto(), rules)

    async def set_privacy_status_timestamp(
            self: "SetPrivacy",
            rules: list[raw.base.InputPrivacyRule] = None,
    ) -> raw.base.account.PrivacyRules:
        return await self.set_privacy(raw.types.InputPrivacyKeyStatusTimestamp(), rules)

    async def set_privacy_voice_messages(
            self: "SetPrivacy",
            rules: list[raw.base.InputPrivacyRule] = None,
    ) -> raw.base.account.PrivacyRules:
        return await self.set_privacy(raw.types.InputPrivacyKeyVoiceMessages(), rules)
