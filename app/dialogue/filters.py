from typing import Union

import sqlalchemy.orm
from aiogram import types
from aiogram.types import KeyboardButton, InlineKeyboardButton

from app import config
from app.db.models import User
from app.middlewares import db_session, sql_result


@db_session
def filter_user_active(message: types.Message, session: sqlalchemy.orm.Session):
    rowcount, _, _ = sql_result(session.query(User)
                                .filter(User.uid == message.from_user.id)
                                .filter(User.active == True))
    return rowcount > 0


def filter_button_pressed(button: Union[KeyboardButton, InlineKeyboardButton]):
    if isinstance(button, KeyboardButton):
        def expr(message: types.Message):
            return message.text == button.text
    elif isinstance(button, InlineKeyboardButton):
        def expr(callback_query: types.CallbackQuery):
            return callback_query.data == button.callback_data
    else:
        return None
    return expr


def filter_su(message: types.Message):
    return message.from_user.id in config.app.su


def filter_admin(message: types.Message):
    return message.from_user.id in config.app.admin

