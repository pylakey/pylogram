from enum import Enum

from pylogram import raw


class PrivacyRules(list[raw.base.InputPrivacyRule], Enum):
    NOBODY = [raw.types.InputPrivacyValueDisallowAll()]
    ONLY_CONTACTS = [raw.types.InputPrivacyValueAllowContacts(), raw.types.InputPrivacyValueDisallowAll()]
    EVERYONE = [raw.types.InputPrivacyValueAllowAll()]
    CLOSE_FRIENDS = [raw.types.InputPrivacyValueAllowCloseFriends()]
