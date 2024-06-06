from .get_app_config import GetAppConfig
from .get_app_update import GetAppUpdate
from .get_cdn_config import GetCdnConfig
from .get_config import GetConfig
from .get_premium_promo import GetPremiumPromo


class Help(
    GetAppConfig,
    GetAppUpdate,
    GetCdnConfig,
    GetConfig,
    GetPremiumPromo
):
    pass
