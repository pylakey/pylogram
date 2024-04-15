import pylogram
from pylogram import utils


class CheckChatListInvite:
    async def check_chat_list_invite(
            self: "pylogram.Client",
            invite_link: str
    ) -> pylogram.raw.base.chatlists.ChatlistInvite:
        return await self.invoke(
            pylogram.raw.functions.chatlists.CheckChatlistInvite(
                slug=utils.chat_list_invite_link_to_slug(invite_link)
            )
        )
