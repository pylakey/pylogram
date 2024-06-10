from .get_account_ttl import GetAccountTTL
from .get_global_privacy_settings import GetGlobalPrivacySettings
from .get_privacy import GetPrivacy
from .set_account_ttl import SetAccountTTL
from .set_global_privacy_settings import SetGlobalPrivacySettings
from .set_privacy import SetPrivacy
from .update_status import UpdateStatus


class Account(
    GetAccountTTL,
    GetGlobalPrivacySettings,
    GetPrivacy,
    SetAccountTTL,
    SetGlobalPrivacySettings,
    SetPrivacy,
    UpdateStatus,
):
    pass
