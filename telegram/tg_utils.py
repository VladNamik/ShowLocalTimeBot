from datetime import datetime
from pytz import timezone
from typing import Optional

import aiogram.types as tg_types
from aiogram import Bot

import db.db_map as db_types
from db.db_utils import *
from utils import BOT_DB_SESSION_MAKER_KEY


def save_user_if_needed(bot: Bot, tg_user: tg_types.User) -> bool:
    if not tg_user.is_bot:
        db_session_maker = bot.get(BOT_DB_SESSION_MAKER_KEY)
        if db_session_maker is not None:
            with db_session_maker() as session:
                if get_user_by_id(session, tg_user.id) is None:
                    user = db_types.User(user_id=tg_user.id, first_name=tg_user.first_name,
                                         last_name=tg_user.last_name, mention=tg_user.mention)
                    add_user(session, user)
                    session.commit()
                    return True

    return False


def save_group_if_needed(bot: Bot, tg_chat: tg_types.Chat) -> bool:
    db_session_maker = bot.get(BOT_DB_SESSION_MAKER_KEY)
    if db_session_maker is not None:
        with db_session_maker() as session:
            if get_group_by_id(session, tg_chat.id) is None:
                group = db_types.Group(group_id=tg_chat.id, name=tg_chat.full_name)
                add_group(session, group)
                session.commit()
                return True

    return False


def remove_group_if_needed(bot: Bot, tg_chat: tg_types.Chat):
    # TODO: remove group
    pass


def save_user_in_group_if_needed(bot: Bot, tg_user: tg_types.User, tg_chat: tg_types.Chat) -> bool:
    if not tg_user.is_bot:
        db_session_maker = bot.get(BOT_DB_SESSION_MAKER_KEY)
        if db_session_maker is not None:
            with db_session_maker() as session:
                if get_user_group_entry(session, tg_chat.id, tg_user.id) is None:
                    user = get_user_by_id(session, tg_user.id)
                    group = get_group_by_id(session, tg_chat.id)
                    # TODO: do we need to save user and group if they are not in db?
                    if user is not None and group is not None:
                        add_user_to_group(session, group_id=tg_chat.id, user_id=tg_user.id)
                        session.commit()
                        return True

    return False


def update_user_timezone(bot: Bot, tg_user: tg_types.User, timezone: str):
    db_session_maker = bot.get(BOT_DB_SESSION_MAKER_KEY)
    with db_session_maker() as session:
        user = get_user_by_id(session, tg_user.id)
        if user is not None:
            user.timezone = timezone
        session.commit()


def get_time_user_map(bot: Bot, tg_user: tg_types.User, tg_chat: tg_types.Chat,
                      time_from_message: datetime) -> Optional[dict]:
    if not tg_user.is_bot and time_from_message is not None:
        db_session_maker = bot.get(BOT_DB_SESSION_MAKER_KEY)
        with db_session_maker() as session:
            user = get_user_by_id(session, tg_user.id)
            if user is not None and user.timezone is not None:
                all_users = get_users_for_group(session, tg_chat.id)

                time_user_map = dict()
                aware_time_from_message = timezone(user.timezone).localize(time_from_message)
                for user_from_group in all_users:
                    if user_from_group.timezone is not None:
                        time = aware_time_from_message.astimezone(timezone(user_from_group.timezone)).strftime("%H:%M")
                        if time not in time_user_map:
                            time_user_map[time] = [user_from_group]
                        else:
                            time_user_map[time].append(user_from_group)

                return time_user_map

    return None


def make_mentions_time_str(users_list: list, time_str: str) -> str:
    return f"{', '.join(map(lambda user_data: user_data.mention, users_list))}: {time_str}"
