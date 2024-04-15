from .check_chat_list_invite import CheckChatListInvite
from .delete_dialog_filter import DeleteDialogFilter
from .edit_exported_invite import EditExportedInvite
from .export_chat_list_invite import ExportChatListInvite
from .export_dialog_filter import ExportDialogFilter
from .export_dialog_filter_invite import ExportDialogFilterInvite
from .get_chat_list_updates import GetChatListUpdates
from .get_dialog_filters import GetDialogFilters
from .get_exported_invites import GetExportedInvites
from .get_suggested_dialog_filters import GetSuggestedDialogFilters
from .join_chat_list_invite import JoinChatListInvite
from .join_chat_list_updates import JoinChatListUpdates
from .leave_dialog_filter import LeaveDialogFilter
from .update_dialog_filter import UpdateDialogFilter
from .update_dialog_filters_order import UpdateDialogFiltersOrder
from .update_exported_invite import UpdateExportedInvite


class ChatLists(
    CheckChatListInvite,
    DeleteDialogFilter,
    EditExportedInvite,
    ExportChatListInvite,
    ExportDialogFilter,
    ExportDialogFilterInvite,
    GetChatListUpdates,
    GetDialogFilters,
    GetExportedInvites,
    GetSuggestedDialogFilters,
    JoinChatListInvite,
    JoinChatListUpdates,
    LeaveDialogFilter,
    UpdateDialogFilter,
    UpdateDialogFiltersOrder,
    UpdateExportedInvite,
):
    pass
