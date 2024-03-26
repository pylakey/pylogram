import logging

import pylogram
from pylogram.types.messages_and_media.message import Str

logger = logging.getLogger(__name__)


def parse_raw_message(
        client: "pylogram.Client",
        message: pylogram.raw.base.Message,
        users: dict,
        chats: dict
) -> pylogram.types.Message:
    if isinstance(message, pylogram.raw.types.MessageEmpty):
        return pylogram.types.Message(
            id=message.id,
            empty=True,
            client=client,
            raw_message=message
        )

    from_peer_id = pylogram.utils.get_raw_peer_id(message.from_id)
    peer_id = pylogram.utils.get_raw_peer_id(message.peer_id)
    user_id = from_peer_id or peer_id

    if isinstance(message, pylogram.raw.types.MessageService):
        action = message.action
        new_chat_members = None
        left_chat_member = None
        new_chat_title = None
        delete_chat_photo = None
        migrate_to_chat_id = None
        migrate_from_chat_id = None
        group_chat_created = None
        channel_chat_created = None
        new_chat_photo = None
        video_chat_scheduled = None
        video_chat_started = None
        video_chat_ended = None
        video_chat_members_invited = None
        web_app_data = None
        service_type = None

        if isinstance(action, pylogram.raw.types.MessageActionChatAddUser):
            new_chat_members = [pylogram.types.User._parse(client, users[i]) for i in action.users]
            service_type = pylogram.enums.MessageServiceType.NEW_CHAT_MEMBERS
        elif isinstance(action, pylogram.raw.types.MessageActionChatJoinedByLink):
            new_chat_members = [
                pylogram.types.User._parse(client, users[pylogram.utils.get_raw_peer_id(message.from_id)])]
            service_type = pylogram.enums.MessageServiceType.NEW_CHAT_MEMBERS
        elif isinstance(action, pylogram.raw.types.MessageActionChatDeleteUser):
            left_chat_member = pylogram.types.User._parse(client, users[action.user_id])
            service_type = pylogram.enums.MessageServiceType.LEFT_CHAT_MEMBERS
        elif isinstance(action, pylogram.raw.types.MessageActionChatEditTitle):
            new_chat_title = action.title
            service_type = pylogram.enums.MessageServiceType.NEW_CHAT_TITLE
        elif isinstance(action, pylogram.raw.types.MessageActionChatDeletePhoto):
            delete_chat_photo = True
            service_type = pylogram.enums.MessageServiceType.DELETE_CHAT_PHOTO
        elif isinstance(action, pylogram.raw.types.MessageActionChatMigrateTo):
            migrate_to_chat_id = action.channel_id
            service_type = pylogram.enums.MessageServiceType.MIGRATE_TO_CHAT_ID
        elif isinstance(action, pylogram.raw.types.MessageActionChannelMigrateFrom):
            migrate_from_chat_id = action.chat_id
            service_type = pylogram.enums.MessageServiceType.MIGRATE_FROM_CHAT_ID
        elif isinstance(action, pylogram.raw.types.MessageActionChatCreate):
            group_chat_created = True
            service_type = pylogram.enums.MessageServiceType.GROUP_CHAT_CREATED
        elif isinstance(action, pylogram.raw.types.MessageActionChannelCreate):
            channel_chat_created = True
            service_type = pylogram.enums.MessageServiceType.CHANNEL_CHAT_CREATED
        elif isinstance(action, pylogram.raw.types.MessageActionChatEditPhoto):
            new_chat_photo = pylogram.types.Photo._parse(client, action.photo)
            service_type = pylogram.enums.MessageServiceType.NEW_CHAT_PHOTO
        elif isinstance(action, pylogram.raw.types.MessageActionGroupCallScheduled):
            video_chat_scheduled = pylogram.types.VideoChatScheduled._parse(action)
            service_type = pylogram.enums.MessageServiceType.VIDEO_CHAT_SCHEDULED
        elif isinstance(action, pylogram.raw.types.MessageActionGroupCall):
            if action.duration:
                video_chat_ended = pylogram.types.VideoChatEnded._parse(action)
                service_type = pylogram.enums.MessageServiceType.VIDEO_CHAT_ENDED
            else:
                video_chat_started = pylogram.types.VideoChatStarted()
                service_type = pylogram.enums.MessageServiceType.VIDEO_CHAT_STARTED
        elif isinstance(action, pylogram.raw.types.MessageActionInviteToGroupCall):
            video_chat_members_invited = pylogram.types.VideoChatMembersInvited._parse(client, action, users)
            service_type = pylogram.enums.MessageServiceType.VIDEO_CHAT_MEMBERS_INVITED
        elif isinstance(action, pylogram.raw.types.MessageActionWebViewDataSentMe):
            web_app_data = pylogram.types.WebAppData._parse(action)
            service_type = pylogram.enums.MessageServiceType.WEB_APP_DATA

        chat = pylogram.types.Chat._parse(client, message, users, chats, is_chat=True)
        from_user = pylogram.types.User._parse(client, users.get(user_id))
        sender_chat = (
            pylogram.types.Chat._parse(client, message, users, chats, is_chat=False)
            if not from_user
            else None
        )

        parsed_message = pylogram.types.Message(
            id=message.id,
            date=pylogram.utils.timestamp_to_datetime(message.date),
            chat=chat,
            from_user=from_user,
            sender_chat=sender_chat,
            service=service_type,
            new_chat_members=new_chat_members,
            left_chat_member=left_chat_member,
            new_chat_title=new_chat_title,
            new_chat_photo=new_chat_photo,
            delete_chat_photo=delete_chat_photo,
            migrate_to_chat_id=pylogram.utils.get_channel_id(migrate_to_chat_id) if migrate_to_chat_id else None,
            migrate_from_chat_id=-migrate_from_chat_id if migrate_from_chat_id else None,
            group_chat_created=group_chat_created,
            channel_chat_created=channel_chat_created,
            video_chat_scheduled=video_chat_scheduled,
            video_chat_started=video_chat_started,
            video_chat_ended=video_chat_ended,
            video_chat_members_invited=video_chat_members_invited,
            web_app_data=web_app_data,
            client=client,
            reply_to=message.reply_to,
            raw_message=message
            # TODO: supergroup_chat_created
        )

        if isinstance(action, pylogram.raw.types.MessageActionPinMessage):
            parsed_message.service = pylogram.enums.MessageServiceType.PINNED_MESSAGE
        elif isinstance(action, pylogram.raw.types.MessageActionGameScore):
            parsed_message.service = pylogram.enums.MessageServiceType.GAME_HIGH_SCORE
            parsed_message.game_high_score = pylogram.types.GameHighScore._parse_action(client, message, users)

        client.message_cache[(parsed_message.chat.id, parsed_message.id)] = parsed_message

        return parsed_message
    elif isinstance(message, pylogram.raw.types.Message):
        entities = [pylogram.types.MessageEntity._parse(client, entity, users) for entity in message.entities]
        entities = pylogram.types.List(filter(lambda x: x is not None, entities))

        forward_from = None
        forward_sender_name = None
        forward_from_chat = None
        forward_from_message_id = None
        forward_signature = None
        forward_date = None

        forward_header = message.fwd_from  # type: pylogram.raw.types.MessageFwdHeader

        if forward_header:
            forward_date = pylogram.utils.timestamp_to_datetime(forward_header.date)

            if forward_header.from_id:
                raw_peer_id = pylogram.utils.get_raw_peer_id(forward_header.from_id)
                peer_id = pylogram.utils.get_peer_id(forward_header.from_id)

                if peer_id > 0:
                    forward_from = pylogram.types.User._parse(client, users[raw_peer_id])
                else:
                    forward_from_chat = pylogram.types.Chat._parse_channel_chat(client, chats[raw_peer_id])
                    forward_from_message_id = forward_header.channel_post
                    forward_signature = forward_header.post_author
            elif forward_header.from_name:
                forward_sender_name = forward_header.from_name

        photo = None
        location = None
        contact = None
        venue = None
        game = None
        audio = None
        voice = None
        animation = None
        video = None
        video_note = None
        sticker = None
        document = None
        web_page = None
        poll = None
        dice = None

        media = message.media
        media_type = None
        has_media_spoiler = None

        if media:
            if isinstance(media, pylogram.raw.types.MessageMediaPhoto):
                photo = pylogram.types.Photo._parse(client, media.photo, media.ttl_seconds)
                media_type = pylogram.enums.MessageMediaType.PHOTO
                has_media_spoiler = media.spoiler
            elif isinstance(media, pylogram.raw.types.MessageMediaGeo):
                location = pylogram.types.Location._parse(client, media.geo)
                media_type = pylogram.enums.MessageMediaType.LOCATION
            elif isinstance(media, pylogram.raw.types.MessageMediaContact):
                contact = pylogram.types.Contact._parse(client, media)
                media_type = pylogram.enums.MessageMediaType.CONTACT
            elif isinstance(media, pylogram.raw.types.MessageMediaVenue):
                venue = pylogram.types.Venue._parse(client, media)
                media_type = pylogram.enums.MessageMediaType.VENUE
            elif isinstance(media, pylogram.raw.types.MessageMediaGame):
                game = pylogram.types.Game._parse(client, message)
                media_type = pylogram.enums.MessageMediaType.GAME
            elif isinstance(media, pylogram.raw.types.MessageMediaDocument):
                doc = media.document

                if isinstance(doc, pylogram.raw.types.Document):
                    attributes = {type(i): i for i in doc.attributes}

                    file_name = getattr(
                        attributes.get(
                            pylogram.raw.types.DocumentAttributeFilename, None
                        ), "file_name", None
                    )

                    if pylogram.raw.types.DocumentAttributeAnimated in attributes:
                        video_attributes = attributes.get(pylogram.raw.types.DocumentAttributeVideo, None)
                        animation = pylogram.types.Animation._parse(client, doc, video_attributes, file_name)
                        media_type = pylogram.enums.MessageMediaType.ANIMATION
                        has_media_spoiler = media.spoiler
                    elif pylogram.raw.types.DocumentAttributeSticker in attributes:
                        # sticker = await pylogram.types.Sticker._parse(client, doc, attributes)
                        media_type = pylogram.enums.MessageMediaType.STICKER
                    elif pylogram.raw.types.DocumentAttributeVideo in attributes:
                        video_attributes = attributes[pylogram.raw.types.DocumentAttributeVideo]

                        if video_attributes.round_message:
                            video_note = pylogram.types.VideoNote._parse(client, doc, video_attributes)
                            media_type = pylogram.enums.MessageMediaType.VIDEO_NOTE
                        else:
                            video = pylogram.types.Video._parse(client, doc, video_attributes, file_name,
                                                                media.ttl_seconds)
                            media_type = pylogram.enums.MessageMediaType.VIDEO
                            has_media_spoiler = media.spoiler
                    elif pylogram.raw.types.DocumentAttributeAudio in attributes:
                        audio_attributes = attributes[pylogram.raw.types.DocumentAttributeAudio]

                        if audio_attributes.voice:
                            voice = pylogram.types.Voice._parse(client, doc, audio_attributes)
                            media_type = pylogram.enums.MessageMediaType.VOICE
                        else:
                            audio = pylogram.types.Audio._parse(client, doc, audio_attributes, file_name)
                            media_type = pylogram.enums.MessageMediaType.AUDIO
                    else:
                        document = pylogram.types.Document._parse(client, doc, file_name)
                        media_type = pylogram.enums.MessageMediaType.DOCUMENT
            elif isinstance(media, pylogram.raw.types.MessageMediaWebPage):
                if isinstance(media.webpage, pylogram.raw.types.WebPage):
                    web_page = pylogram.types.WebPage._parse(client, media.webpage)
                    media_type = pylogram.enums.MessageMediaType.WEB_PAGE
                else:
                    media = None
            elif isinstance(media, pylogram.raw.types.MessageMediaPoll):
                poll = pylogram.types.Poll._parse(client, media)
                media_type = pylogram.enums.MessageMediaType.POLL
            elif isinstance(media, pylogram.raw.types.MessageMediaDice):
                dice = pylogram.types.Dice._parse(client, media)
                media_type = pylogram.enums.MessageMediaType.DICE
            else:
                media = None

        reply_markup = message.reply_markup

        if reply_markup:
            if isinstance(reply_markup, pylogram.raw.types.ReplyKeyboardForceReply):
                reply_markup = pylogram.types.ForceReply.read(reply_markup)
            elif isinstance(reply_markup, pylogram.raw.types.ReplyKeyboardMarkup):
                reply_markup = pylogram.types.ReplyKeyboardMarkup.read(reply_markup)
            elif isinstance(reply_markup, pylogram.raw.types.ReplyInlineMarkup):
                reply_markup = pylogram.types.InlineKeyboardMarkup.read(reply_markup)
            elif isinstance(reply_markup, pylogram.raw.types.ReplyKeyboardHide):
                reply_markup = pylogram.types.ReplyKeyboardRemove.read(reply_markup)
            else:
                reply_markup = None

        from_user = pylogram.types.User._parse(client, users.get(user_id))
        sender_chat = (
            pylogram.types.Chat._parse(client, message, users, chats, is_chat=False)
            if not from_user
            else None
        )

        reactions = pylogram.types.MessageReactions._parse(client, message.reactions)

        parsed_message = pylogram.types.Message(
            id=message.id,
            date=pylogram.utils.timestamp_to_datetime(message.date),
            chat=pylogram.types.Chat._parse(client, message, users, chats, is_chat=True),
            from_user=from_user,
            sender_chat=sender_chat,
            text=(
                Str(message.message).init(entities) or None
                if media is None or web_page is not None
                else None
            ),
            caption=(
                Str(message.message).init(entities) or None
                if media is not None and web_page is None
                else None
            ),
            entities=(
                entities or None
                if media is None or web_page is not None
                else None
            ),
            caption_entities=(
                entities or None
                if media is not None and web_page is None
                else None
            ),
            author_signature=message.post_author,
            has_protected_content=message.noforwards,
            has_media_spoiler=has_media_spoiler,
            forward_from=forward_from,
            forward_sender_name=forward_sender_name,
            forward_from_chat=forward_from_chat,
            forward_from_message_id=forward_from_message_id,
            forward_signature=forward_signature,
            forward_date=forward_date,
            mentioned=message.mentioned,
            from_scheduled=message.from_scheduled,
            media=media_type,
            edit_date=pylogram.utils.timestamp_to_datetime(message.edit_date),
            media_group_id=message.grouped_id,
            photo=photo,
            location=location,
            contact=contact,
            venue=venue,
            audio=audio,
            voice=voice,
            animation=animation,
            game=game,
            video=video,
            video_note=video_note,
            sticker=sticker,
            document=document,
            web_page=web_page,
            poll=poll,
            dice=dice,
            views=message.views,
            forwards=message.forwards,
            via_bot=pylogram.types.User._parse(client, users.get(message.via_bot_id)),
            outgoing=message.out,
            reply_markup=reply_markup,
            reactions=reactions,
            client=client,
            reply_to=message.reply_to,
            raw_message=message
        )

        if isinstance(message.reply_to, pylogram.raw.types.MessageReplyHeader):
            parsed_message.reply_to_message_id = message.reply_to.reply_to_msg_id
            parsed_message.reply_to_top_message_id = message.reply_to.reply_to_top_id

        if not parsed_message.poll:  # Do not cache poll messages
            client.message_cache[(parsed_message.chat.id, parsed_message.id)] = parsed_message

        return parsed_message


def parse_raw_dialog_chat(
        client: "pylogram.Client",
        dialog: pylogram.raw.base.Dialog,
        users: dict[int, pylogram.raw.base.User],
        chats: dict[int, pylogram.raw.base.Chat],
        *,
        raise_if_left: bool = True,
        raise_if_migrated: bool = True,
) -> pylogram.types.Chat:
    dialog_raw_peer_id = pylogram.utils.get_raw_peer_id(dialog.peer)

    if isinstance(dialog.peer, pylogram.raw.types.PeerUser):
        # noinspection PyProtectedMember
        return pylogram.types.Chat._parse_user_chat(client, users[dialog_raw_peer_id])

    raw_chat = chats.get(dialog_raw_peer_id)

    if dialog_raw_peer_id == 1825406697:
        print(raw_chat)

    if not bool(raw_chat):
        raise ValueError(f"Something is going wrong, chat {dialog_raw_peer_id} not found")

    if isinstance(raw_chat, pylogram.raw.types.ChatEmpty):
        raise ValueError(f"Chat {dialog_raw_peer_id} is empty")

    if isinstance(raw_chat, (pylogram.raw.types.ChatForbidden, pylogram.raw.types.ChannelForbidden)):
        raise ValueError(f"Chat {dialog_raw_peer_id} is forbidden")

    if raise_if_left and raw_chat.left:
        raise ValueError(f"Chat {dialog_raw_peer_id} is left")

    if isinstance(raw_chat, pylogram.raw.types.Chat):
        if raise_if_migrated and raw_chat.deactivated:
            raise ValueError(f"Chat {dialog_raw_peer_id} is deactivated and migrated")
        # noinspection PyProtectedMember
        return pylogram.types.Chat._parse_chat_chat(client, raw_chat)

    elif isinstance(raw_chat, pylogram.raw.types.Channel):
        # noinspection PyProtectedMember
        return pylogram.types.Chat._parse_channel_chat(client, raw_chat)

    raise ValueError("Unknown peer type")


def parse_raw_dialogs(
        client: "pylogram.Client",
        dialogs: list[pylogram.raw.base.Dialog],
        messages: dict[tuple[int, int], pylogram.raw.base.Message],
        users: dict[int, pylogram.raw.base.User],
        chats: dict[int, pylogram.raw.base.Chat],
        *,
        ignore_left: bool = True,
        ignore_migrated: bool = True,
) -> list[pylogram.types.Dialog]:
    result: list[pylogram.types.Dialog] = []

    for dialog in dialogs:
        dialog_peer_id = pylogram.utils.get_raw_peer_id(dialog.peer)

        if not bool(dialog.top_message):
            continue

        try:
            chat = parse_raw_dialog_chat(
                client,
                dialog,
                users,
                chats,
                raise_if_left=ignore_left,
                raise_if_migrated=ignore_migrated
            )
        except ValueError as e:
            logger.debug(f'Unable to parse dialog chat: {e}', exc_info=True)
            continue

        top_message = parse_raw_message(client, messages[(dialog_peer_id, dialog.top_message)], users, chats)
        parsed_dialog = pylogram.types.Dialog(
            client=client,
            chat=chat,
            top_message=top_message,
            unread_mark=dialog.unread_mark,
            unread_mentions_count=dialog.unread_mentions_count,
            unread_messages_count=dialog.unread_count,
            is_pinned=dialog.pinned,
            raw_dialog=dialog
        )
        result.append(parsed_dialog)

    return result
