from .get_connected_bots import GetConnectedBots
from .update_business_away_message import UpdateBusinessAwayMessage
from .update_business_greeting_message import UpdateBusinessGreetingMessage
from .update_business_location import UpdateBusinessLocation
from .update_business_work_hours import UpdateBusinessWorkHours
from .update_connected_bot import UpdateConnectedBot


class Business(
    GetConnectedBots,
    UpdateBusinessAwayMessage,
    UpdateBusinessGreetingMessage,
    UpdateBusinessLocation,
    UpdateBusinessWorkHours,
    UpdateConnectedBot,
):
    pass
