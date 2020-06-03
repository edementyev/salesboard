from typing import Union

import sqlalchemy.orm
from aiogram import types
from aiogram.types import ContentTypes

from app import dp, config
from app.db import use_db_session, sql_result
from app.db.models import User
from app.dialogue import checks
from app.dialogue.checks import is_from_su, is_from_admin
from app.dialogue.messages import MESSAGES
from app.dialogue.util.keyboards import keyboard_remove
from app.dialogue.util.parse_args import parse_args
from app.dialogue.util.states import States, resolve_state, StateItem
from app.trace import trace_async, trace


# /admin
@dp.message_handler(is_from_su,
                    commands=['admin'],
                    state='*')
@parse_args(mode='message')
@trace_async
async def admin(user_id,
                user_state,
                message: types.Message):
    if not is_from_admin(message):
        config.app.admin.append(user_id)
        await message.reply(MESSAGES['admin_enable'], reply=False)
    else:
        config.app.admin.remove(user_id)
        await message.reply(MESSAGES['admin_disable'], reply=False)


# /clear
@dp.message_handler(is_from_su,
                    commands=['clear'],
                    state='*')
@parse_args(mode='message')
@resolve_state
@trace_async
async def clear_state(user_id,
                      user_state,
                      message: types.Message) -> Union[StateItem, None]:
    return None


# /start
@dp.message_handler(commands=['start'],
                    state='*')
@parse_args(mode='message')
@resolve_state
@use_db_session
@trace_async
async def start(user_id,
                user_state,
                message: types.Message,
                session: sqlalchemy.orm.Session) -> Union[StateItem, None]:
    rowcount, user, _ = sql_result(session.query(User)
                                   .filter(User.uid == user_id))
    if rowcount == 0:
        trace(User)(uid=user_id,
                    username=message.from_user.username) \
            .insert_me(session)
        message_text = MESSAGES['greetings']
        next_state = States.STATE_0_REQUEST_CITY
    else:
        message_text = MESSAGES['yo']
        next_state = States.STATE_1_MAIN
    await message.reply(message_text, reply=False)

    return next_state


# get geo
@dp.message_handler(state=States.STATE_0_REQUEST_CITY,
                    content_types=ContentTypes.TEXT)
@parse_args(mode='message')
@resolve_state
@use_db_session
@trace_async
async def location(user_id,
                   user_state,
                   message: types.Message,
                   session: sqlalchemy.orm.Session) -> Union[StateItem, None]:
    rowcount, user, _ = sql_result(session.query(User)
                                   .filter(User.uid == user_id),
                                   raise_on_empty_result=True)
    user.location = message.text
    await message.reply(MESSAGES['sign_up_complete'],
                        reply=False,
                        reply_markup=keyboard_remove)
    next_state = States.STATE_1_MAIN
    return next_state


# /upload
@dp.message_handler(commands=['upload'],
                    state=States.STATE_1_MAIN)
@parse_args(mode='message')
@resolve_state
@use_db_session
@trace_async
async def upload_command(user_id,
                         user_state,
                         message: types.Message,
                         session: sqlalchemy.orm.Session) -> Union[StateItem, None]:
    upload_rowcount = 0

    _, user, _ = sql_result(session.query(User)
                            .filter(User.uid == user_id),
                            raise_on_empty_result=True)

    passed, next_state, message_text = checks.upload(user, upload_rowcount, session)
    await message.reply(message_text,
                        reply=True)
    return next_state


# /upload -> process action
@dp.message_handler(state=States.STATE_2_UPLOAD)
@parse_args(mode='message')
@resolve_state
@use_db_session
@trace_async
async def upload_action(user_id,
                        user_state,
                        message: types.Message,
                        session: sqlalchemy.orm.Session) -> Union[StateItem, None]:
    next_state = States.STATE_1_MAIN
    await message.reply(MESSAGES['upload_complete'],
                        reply=True)
    return next_state


# /mycards
@dp.message_handler(commands=['mycards'],
                    state=States.STATE_1_MAIN)
@parse_args(mode='message')
@resolve_state
@use_db_session
@trace_async
async def mycards(user_id,
                  user_state,
                  message: types.Message,
                  session: sqlalchemy.orm.Session) -> Union[StateItem, None]:
    await message.reply('Show me my cards',
                        reply=False)
    return None
