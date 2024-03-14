from .create_forum_topic import CreateForumTopic
from .delete_topic_history import DeleteTopicHistory
from .edit_forum_topic import EditForumTopic
from .get_forum_topics import GetForumTopics
from .get_forum_topics_by_id import GetForumTopicsByID
from .reorder_pinned_forum_topics import ReorderPinnedForumTopics
from .toggle_view_forum_as_messages import ToggleViewForumAsMessages
from .update_pinned_forum_topic import UpdatePinnedForumTopic


class Forums(
    CreateForumTopic,
    DeleteTopicHistory,
    EditForumTopic,
    GetForumTopics,
    GetForumTopicsByID,
    ReorderPinnedForumTopics,
    ToggleViewForumAsMessages,
    UpdatePinnedForumTopic,
):
    pass
