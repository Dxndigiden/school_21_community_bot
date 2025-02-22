import logging

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import distinct

from bot.messages import Messages
from database.models import Level, User
from logger.logmessages import LogMessage

keybrd_logger = logging.getLogger('KEYBRD_LOGGER')


def get_keyboard(
    is_registered: bool,
    existing_user: bool,
    is_admin: bool
) -> InlineKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    if not is_registered and existing_user:
        builder.button(text="Возобновить аутентификацию")
        builder.button(text="Пройти аутентификацию заново")
    elif not is_registered:
        builder.button(text="Пройти аутентификацию")
    else:
        builder.button(text="Продолжить")
        if is_admin:
            builder.button(text="Панель администратора")
    builder.adjust(1)
    keybrd_logger.info(LogMessage.KEYBRD_IS_DONE)
    return builder.as_markup(resize_keyboard=True)


async def get_inline_keyboard(
        session: AsyncSession,
        obj: object,
) -> InlineKeyboardMarkup:
    if hasattr(obj, "role") and (obj, "is_registered"):
        result = await session.execute(select(distinct(obj.role)).where(obj.is_registered))
    elif obj is Level:
        result = await session.execute(select(distinct(Level.name)))
    else:
        result = await session.execute(select(obj))
    objects = result.scalars().all()
    builder = InlineKeyboardBuilder()
    for item in objects:
        builder.button(text=str(item)[:64], callback_data=str(item)[:64])
    if not hasattr(obj, "role"):
        builder.button(text="Назад", callback_data="Back")
    builder.adjust(2)
    keybrd_logger.info(LogMessage.KEYBRD_IS_DONE)
    return builder.as_markup(resize_keyboard=True)


async def get_admin_buttons(telegram_id: int = None) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Шифрование/дешифровка БД",
        callback_data=str("crypt_base")
    )
    builder.button(
        text="Дамп БД",
        callback_data=str("fixtures_export")
    )
    builder.button(
        text="Загрузка в БД",
        callback_data=str("fixtures_import")
    )
    # Генерируем URL с использованием telegram_id, если он передан
    if telegram_id is not None:
        url = f"https://school21.online:8500/?telegram_id={telegram_id}"
    else:
        url = "https://school21.online:8500/"
    builder.button(
        text="WEB-admin",
        url=url
    )
    builder.button(
        text="В начало",
        callback_data=str("to_begin")
    )
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)


async def get_card_button(
    user: User,
    builder: InlineKeyboardBuilder
) -> InlineKeyboardBuilder:
    builder.button(
        text=Messages.USER_FOR_LIST.format(
            user.sber_id,
            user.team_name
        ),
        callback_data=f"user_{user.id}"
    )
    return builder


async def get_buttons(**kwargs) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for key in kwargs:
        builder.button(text=str(kwargs[key]), callback_data=str(key))
    builder.adjust(2)
    keybrd_logger.info(LogMessage.KEYBRD_IS_DONE)
    return builder.as_markup(resize_keyboard=True)


async def get_confirm_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text="Подтверждаю",
                callback_data="confirm"
            )]
        ]
    )
    return builder


async def get_join_community_keyboard(
    invite_link: str
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text="Перейти в комьюнити",
                url=invite_link
            )],
            [InlineKeyboardButton(
                text="Поиск пиров",
                callback_data="search_peers"
            )]
        ]
    )
    return builder


def get_skip_inline_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text="Пропустить",
                callback_data="skip_description"
            )]
        ]
    )
    return builder
