from .apply_boost import ApplyBoost
from .get_boosts_list import GetBoostsList
from .get_boosts_status import GetBoostsStatus
from .get_my_boosts import GetMyBoosts
from .get_user_boosts import GetUserBoosts


class Premium(
    ApplyBoost,
    GetBoostsList,
    GetBoostsStatus,
    GetMyBoosts,
    GetUserBoosts,
):
    pass
