import os
from aiohttp import web
import asyncio
import logging
import math
import re
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, F, types
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, InputMediaPhoto, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

BOT_TOKEN = "8836079710:AAGyv8vhyOTqvZaR5wAEEEEGLzYUIkXChk0"
CHANNEL_ID = -1004409881507
ADMIN_ID = 7468058583

# --- ССЫЛКИ ДЛЯ ВШИТОГО ТЕКСТА ПОСТА ---
BOT_USERNAME = "admiral_rf4_bot"
POST_LINK = "https://t.me/c/4409881507/14"
TIKTOK_LINK = "https://www.tiktok.com/@admiral_rr4?_r=1&_t=ZS-98ct8BmhqMa"

# Настройка стабильной сессии с увеличенным таймаутом
session = AiohttpSession(timeout=60)
bot = Bot(token=BOT_TOKEN, session=session)
dp = Dispatcher(storage=MemoryStorage())
async def start_web_server():
    app = web.Application()
    app.router.add_get('/', lambda r: web.Response(text="OK"))
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

ITEMS_PER_PAGE = 12

# --- НАСТРОЙКИ СИСТЕМЫ МОДЕРАЦИИ ЧАТА ---
USER_WARNINGS = {}

BAD_WORDS = [
    "хуй", "хуя", "хуе", "хую", "хуи", "хуёв", "хули", "похуй", "дохуя", "нихуя", "захуяч",
    "пизд", "пезд", "пизж", "написд", "опизд",
    "ебат", "ебал", "ебан", "ёбан", "ебёт", "выеб", "заеб", "поеб", "доеб", "перееб", "наеб",
    "бляд", "блять", "бля",
    "сук", "сучк",
    "мудак", "мудил",
    "пидор", "педик", "пидар",
    "гандон", "гондон",
    "залуп",
    "дроч",
    "мразь", "уеб", "ублюд", "сволоч",
    "дурак", "дебил", "идиот", "тупой", "урод", "скотина", "чмо"
]

ADS_REGEX = re.compile(
    r"(?:https?://)?(?:www\.)?(?:t\.me/|telegram\.me/|vk\.com/|instagram\.com/|tiktok\.com/|bit\.ly/|\@[\w_]+)",
    re.IGNORECASE
)

WATERBODY_FISH = {
    "Ладожский архипелаг": [
        "Разнорыбица", "Сиг чёрный", "Сиг ладожский озёрный", "Сиг вуоксинский",
        "Сиг валаамский", "Сиг-лудога", "Палия кряжевая", "Палия обыкновенная",
        "Палия лудожная", "Судак", "Лосось атлантический", "Сиг свирский",
        "Осётр балтийский", "Лосось ладожский", "Ряпушка", "Корюшка",
        "Рыбец", "Налим", "Щука обыкновенная", "Омуль байкальский",
        "Сиг волховский", "Рипус", "Лещ", "Осётр ладожский",
        "Форель озерная", "Плотва обыкновенная", "Сом", "Колюшка трёхиглая", "Угорь"
    ],
    "Ладожское оз.": [
        "Разнорыбица", "Корюшка", "Сиг волховский", "Рипус", "Ряпушка",
        "Колюшка трёхиглая", "Сиг вуоксинский", "Сиг-лудога", "Палия кряжевая",
        "Сиг валаамский", "Карась серебряный", "Белоглазка", "Рыбец",
        "Палия лудожная", "Плотва обыкновенная", "Гольян", "Лосось ладожский",
        "Окунь", "Хариус европейский", "Форель озерная", "Карась золотой",
        "Осётр балтийский", "Густера", "Язь", "Синец", "Уклейка", "Налим",
        "Судак", "Лещ", "Ерш", "Лосось атлантический", "Палия обыкновенная"
    ],
    "Норвежское море": [
        "Разнорыбица", "Треска атлантическая", "Путассу северная", "Окунь морской норвежский",
        "Мерланг", "Сайра атлантическая", "Сайда", "Тюрбо", "Зубатка полосатая",
        "Поллак", "Мерлуза", "Пикша", "Макрель атлантическая", "Камбала палтусовидная",
        "Краб съедобный", "Меч-рыба", "Зубатка пятнистая", "Керчак европейский",
        "Мольва голубая", "Менёк", "Скат полярный", "Горбыль серебристый",
        "Кальмар обыкновенный", "Акула гигантская", "Акула гренландская полярная",
        "Сельдь атлантическая", "Опах краснопёрый", "Краб камчатский", "Камбала морская",
        "Камбала хоботная", "Устрица съедобная", "Катран", "Окунь морской золотистый",
        "Палтус синекорый", "Сардина европейская", "Конгер", "Берикс красный",
        "Бельдюга европейская", "Тунец голубой", "Скат колючий", "Палтус атлантический",
        "Пинагор", "Мольва обыкновенная", "Окунь-клювач", "Окунь каменный",
        "Ликод Эсмарка", "Мидия", "Морской чёрт", "Акула плащеносная",
        "Центролоф чёрный", "Гребешок исландский", "Макрурус северный",
        "Зубатка синяя", "Акула сельдевая атлантическая", "Гимантолоф атлантический",
        "Угольщик обыкновенный", "Ликод полуголый", "Химера европейская"
    ],
    "оз. Комариное": [
        "Разнорыбица", "Вьюн", "Лягушка", "Ротан", "Ерш", "Карп Кои Мидори-гои",
        "Язь", "Линь золотистый", "Карась золотой", "Плотва обыкновенная",
        "Лещ", "Окунь", "Линь", "Карась серебряный", "Уклейка", "Голавль",
        "Густера", "Карп зеркальный", "Карп чешуйчатый", "Щука обыкновенная", "Сом"
    ],
    "оз. Куори": [
        "Разнорыбица", "Форель озерная", "Форель радужная", "Форель севанская",
        "Голец арктический", "Голец куорский", "Ряпушка", "Гольян озёрный",
        "Палия обыкновенная", "Окунь", "Пелядь", "Плотва обыкновенная",
        "Налим", "Лещ", "Густера", "Хариус европейский", "Язь", "Щука обыкновенная"
    ],
    "оз. Лосиное": [
        "Разнорыбица", "Окунь белый", "Сомик канальный", "Горбыль речной",
        "Солнечник красноухий", "Солнечник синежаберный", "Краппи чёрный",
        "Краппи белый", "Доросома северная", "Вармоус", "Окунь большеротый",
        "Окунь малоротый", "Окунь павлиний", "Окунь пятнистый", "Сомик оливковый",
        "Лаврак полосатый", "Лаврак гибридный", "Судак светлопёрый",
        "Панцирник пятнистый", "Щука панцирная", "Карась серебряный",
        "Карась золотой", "Карп чешуйчатый", "Плотва обыкновенная", "Линь", "Окунь", "Ерш"
    ],
    "оз. Медвежье": [
        "Разнорыбица", "Амур белый", "Амур чёрный",
        "Амур белый - альбинос", "Карп чешуйчатый", "Карп зеркальный",
        "Карп голый", "Линь", "Линь золотистый", "Карась золотой",
        "Карась серебряный", "Лещ", "Плотва обыкновенная", "Голавль",
        "Усач обыкновенный", "Усач - альбинос", "Лягушка"
    ],
    "оз. Медное": [
        "Разнорыбица", "Карасекарп", "Карп Динкенбюльский зеркальный", "Усач обыкновенный",
        "Карп Супер Фрикс", "Карп Кои Кохаку", "Карп Кои Орэндзи Огон",
        "Линь Квольсдорфский", "Карп Кои Наруми Асаги", "Карп Кои Мамэсибори Госики",
        "Линь", "Карп Динкенбюльский голый", "Карп Кои Хи Уцури",
        "Карп Динкенбюльский линейный", "Карп Кои Ёцусиро", "Карась золотой",
        "Карп чешуйчатый", "Карп зеркальный", "Карп голый", "Карась серебряный",
        "Лягушка", "Язь", "Лещ", "Плотва обыкновенная"
    ],
    "оз. Старый Острог": [
        "Разнорыбица", "Амур чёрный", "Лещ", "Амур белый", "Налим",
        "Щука обыкновенная", "Сиг острожский", "Карп чешуйчатый", "Густера",
        "Угорь", "Окунь", "Ротан", "Карась золотой", "Карась серебряный",
        "Линь", "Плотва обыкновенная", "Язь", "Лягушка", "Ерш"
    ],
    "оз. Янтарное": [
        "Разнорыбица", "Карп чешуйчатый", "Карп рамчатый", "Карп зеркальный",
        "Карп чешуйчатый - призрак", "Карп линейный", "Карп зеркальный - призрак",
        "Карп красный Старвас - чешуйчатый", "Карп голый", "Карп голый - призрак",
        "Карп зеркальный - альбинос", "Карп красный Старвас - зеркальный",
        "Карп чешуйчатый - альбинос", "Карп линейный - призрак", "Усач обыкновенный",
        "Амур белый", "Карп рамчатый - призрак", "Карп линейный - альбинос",
        "Карп рамчатый - альбинос", "Карась золотой", "Язь",
        "Карп голый - альбинос", "Плотва обыкновенная", "Линь", "Угорь"
    ],
    "р. Ахтуба": [
        "Разнорыбица", "Сельдь Кесслера", "Сазан", "Толстолобик пёстрый",
        "Пузанок каспийский", "Буффало чёрный", "Усач короткоголовый",
        "Сельдь Бражникова", "Шемая каспийская", "Лещ восточный",
        "Колюшка малая южная", "Буффало большеротый", "Белорыбица",
        "Осётр русский", "Кутум", "Осётр персидский", "Сом", "Севрюга",
        "Стерлядь", "Шип", "Чехонь", "Лосось каспийский", "Голавль",
        "Толстолобик белый", "Белуга каспийская", "Линь", "Амур белый",
        "Плотва обыкновенная", "Жерех", "Сом альбинос", "Вьюн",
        "Карась серебряный", "Краснопёрка", "Карась золотой", "Окунь",
        "Налим", "Карп чешуйчатый", "Язь", "Минога каспийская", "Густера",
        "Рак речной", "Синец", "Дрейссена речная", "Судак", "Ерш"
    ],
    "р. Белая": [
        "Разнорыбица", "Хариус европейский", "Жерех", "Сиг-пыжьян",
        "Форель ручьевая", "Голавль", "Хариус западносибирский", "Рак речной",
        "Язь", "Ерш", "Белоглазка", "Перловица", "Судак",
        "Щука обыкновенная", "Подуст", "Таймень", "Елец", "Налим",
        "Сом", "Плотва обыкновенная", "Уклейка", "Густера", "Пескарь обыкновенный"
    ],
    "р. Волхов": [
        "Разнорыбица", "Рыбец", "Белоглазка", "Синец", "Лосось ладожский",
        "Лосось атлантический", "Судак", "Ерш", "Пескарь обыкновенный",
        "Жерех", "Елец", "Перловица", "Щука обыкновенная", "Сом", "Уклейка",
        "Окунь", "Язь", "Рак речной", "Карп чешуйчатый", "Ряпушка", "Лещ",
        "Угорь", "Линь", "Густера", "Дрейссена речная"
    ],
    "р. Вьюнок": [
        "Разнорыбица", "Пескарь обыкновенный", "Ерш-носарь", "Уклейка",
        "Белоглазка", "Дрейссена речная", "Рак речной", "Берш", "Елец",
        "Перловица", "Подуст", "Густера", "Синец", "Голавль", "Лягушка",
        "Налим", "Лещ", "Окунь", "Ерш", "Сом", "Судак", "Жерех",
        "Щука обыкновенная", "Плотва обыкновенная", "Линь", "Ротан",
        "Карась золотой"
    ],
    "р. Нижняя Тунгуска": [
        "Разнорыбица", "Плотва сибирская", "Елец сибирский", "Гольян озёрный",
        "Ряпушка сибирская", "Пелядь", "Омуль арктический", "Чир", "Муксун",
        "Тугун", "Голец арктический", "Таймень", "Нельма",
        "Хариус восточносибирский", "Сиг-пыжьян", "Омуль байкальский",
        "Сом амурский", "Подкаменщик сибирский", "Осётр восточносибирский",
        "Хариус западносибирский", "Форель ручьевая", "Горбуша", "Голец Дрягина",
        "Пескарь сибирский", "Лещ восточный", "Валёк", "Корюшка азиатская",
        "Щука обыкновенная", "Ленок острорылый", "Голец сибирский-усач",
        "Перловица", "Стерлядь сибирская", "Язь", "Колюшка трёхиглая",
        "Окунь", "Налим"
    ],
    "р. Северский Донец": [
        "Разнорыбица", "Сельдь черноморская", "Тюлька черноморская", "Тарань",
        "Подуст", "Шемая черноморская", "Окунь солнечный", "Чехонь",
        "Вырезуб", "Белуга черноморская", "Дрейссена речная", "Ерш-носарь",
        "Густера", "Плотва обыкновенная", "Рак речной", "Сазан", "Голавль",
        "Белоглазка", "Карась серебряный", "Краснопёрка", "Лещ", "Амур белый",
        "Перловица", "Жерех", "Карась золотой", "Елец", "Судак", "Берш",
        "Язь", "Ерш", "Сом", "Щука обыкновенная", "Налим"
    ],
    "р. Сура": [
        "Разнорыбица", "Берш", "Толстолобик белый", "Сом", "Толстолобик пёстрый",
        "Налим", "Перловица", "Судак", "Жерех", "Сазан", "Дрейссена речная",
        "Рыбец", "Язь", "Густера", "Осётр русский", "Чехонь", "Окунь",
        "Краснопёрка", "Лещ", "Лягушка", "Стерлядь", "Белоглазка", "Ротан",
        "Подуст", "Елец", "Ерш"
    ],
    "р. Яма": [
        "Разнорыбица", "Кижуч", "Ленок тупорылый", "Краснопёр монгольский",
        "Кунджа", "Корюшка азиатская", "Мальма", "Сима жилая",
        "Голец Леванидова", "Чукучан", "Нерка", "Кета",
        "Краснопёр-Угай крупночешуйчатый", "Сима", "Микижа", "Нейва",
        "Колюшка девятииглая", "Голец сибирский-усач", "Валёк", "Чавыча",
        "Ленок острорылый", "Хариус восточносибирский", "Налим",
        "Минога дальневосточная ручьевая", "Голец арктический", "Калуга",
        "Горбуша", "Минога трёхзубая"
    ]
}

WATERBODY_TAGS = {
    "оз. Лосиное": "лосиное", "оз. Комариное": "комариное", "р. Вьюнок": "вьюнок",
    "оз. Старый Острог": "острог", "р. Белая": "белая", "оз. Куори": "куори",
    "оз. Медвежье": "медвежье", "р. Волхов": "волхов", "р. Северский Донец": "донец",
    "р. Сура": "сура", "Ладожское оз.": "ладожское", "Ладожский архипелаг": "архипелаг",
    "оз. Янтарное": "янтарное", "р. Ахтуба": "ахтуба", "оз. Медное": "медное",
    "р. Нижняя Тунгуска": "тунгуска", "р. Яма": "яма", "Норвежское море": "норвежское"
}

MODERATION_POSTS = {}


class PostForm(StatesGroup):
    post_type = State()
    waterbody = State()
    coords = State()
    fish = State()
    typing_custom_fish = State()
    clip = State()
    depth = State()
    speed = State()
    temp = State()
    square = State()
    comment = State()
    show_author = State()
    photos = State()


# --- 1. ГЛАВНЫЙ ХЕНДЛЕР /start ---
@dp.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    try:
        await state.clear()
        await state.set_state(PostForm.post_type)
        text, kb = await show_type_keyboard(message, state)
        await message.answer(text, reply_markup=kb)
    except Exception as e:
        logging.error(f"Ошибка в хендлере /start: {e}", exc_info=True)


def get_control_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⏩ Пропустить", callback_data="skip_step")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_post")]
    ])


def get_fish_keyboard(water_name: str, page: int = 1, selected_fish: list = None) -> InlineKeyboardMarkup:
    if selected_fish is None:
        selected_fish = []

    fish_list = WATERBODY_FISH.get(water_name, ["Разнорыбица"])
    total_pages = math.ceil(len(fish_list) / ITEMS_PER_PAGE) or 1
    page = max(1, min(page, total_pages))

    start_offset = (page - 1) * ITEMS_PER_PAGE
    end_offset = start_offset + ITEMS_PER_PAGE

    builder = InlineKeyboardBuilder()

    fish_buttons = []
    for idx in range(start_offset, min(end_offset, len(fish_list))):
        fish = fish_list[idx]
        mark = "✅ " if fish in selected_fish else ""
        fish_buttons.append(InlineKeyboardButton(
            text=f"{mark}{fish}",
            callback_data=f"fidx_{idx}:{page}"
        ))
    builder.row(*fish_buttons, width=2)

    nav_row = []
    if page > 1:
        nav_row.append(InlineKeyboardButton(text="◀️ Назад", callback_data=f"fpg:{page - 1}"))

    nav_row.append(InlineKeyboardButton(text=f"Стр. {page}/{total_pages}", callback_data="noop"))

    if page < total_pages:
        nav_row.append(InlineKeyboardButton(text="Вперёд ▶️", callback_data=f"fpg:{page + 1}"))
    builder.row(*nav_row)

    builder.row(InlineKeyboardButton(text="✍️ Ввести вручную", callback_data="manual_fish"))

    control_row = []
    if len(selected_fish) > 0:
        control_row.append(InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_fish"))
    control_row.append(InlineKeyboardButton(text="⏩ Пропустить", callback_data="skip_step"))

    builder.row(*control_row)
    builder.row(InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_post"))

    return builder.as_markup()


async def show_type_keyboard(message: types.Message, state: FSMContext):
    data = await state.get_data()
    selected_type = data.get("post_type", None)

    types_list = ["Фарм", "Трофей", "Задания", "Уникальное", "Квалификация"]
    buttons = []
    for i in range(0, len(types_list), 2):
        t1 = types_list[i]
        p1 = "✅ " if t1 == selected_type else ""
        row = [InlineKeyboardButton(text=f"{p1}{t1}", callback_data=f"stype_{t1}")]
        if i + 1 < len(types_list):
            t2 = types_list[i + 1]
            p2 = "✅ " if t2 == selected_type else ""
            row.append(InlineKeyboardButton(text=f"{p2}{t2}", callback_data=f"stype_{t2}"))
        buttons.append(row)

    if selected_type:
        buttons.append([InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_type")])

    buttons.append([InlineKeyboardButton(text="⏩ Пропустить", callback_data="skip_step")])
    buttons.append([InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_post")])

    user_name = message.from_user.first_name if message.from_user else "Рыбак"

    text = (
        f"Приветствую, {user_name}!\n\n"
        "Делись своими успехами, раздачами и трофеями Русской Рыбалки 4.\n\n"
        "📌 Выберите тип вашей публикации ниже и нажмите Подтвердить:"
    )
    return text, InlineKeyboardMarkup(inline_keyboard=buttons)


# --- МАСТЕР СОЗДАНИЯ ПОСТОВ ---
@dp.callback_query(F.data.startswith("stype_"))
async def select_type(call: CallbackQuery, state: FSMContext):
    stype = call.data.replace("stype_", "")
    await state.update_data(post_type=stype)
    text, kb = await show_type_keyboard(call.message, state)
    await call.message.edit_text(text, reply_markup=kb)
    await call.answer()


@dp.callback_query(F.data == "confirm_type")
async def confirm_type(call: CallbackQuery, state: FSMContext):
    await go_to_waterbody(call, state)


async def go_to_waterbody(event, state: FSMContext):
    await state.set_state(PostForm.waterbody)
    wb_list = list(WATERBODY_FISH.keys())
    wb_buttons = [[InlineKeyboardButton(text=wb, callback_data=f"wb_{i}")] for i, wb in enumerate(wb_list)]
    wb_buttons.append([InlineKeyboardButton(text="⏩ Пропустить", callback_data="skip_step")])
    wb_buttons.append([InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_post")])

    text = "Выберите водоём из списка:"
    if isinstance(event, CallbackQuery):
        await event.message.answer(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=wb_buttons))
        await event.answer()
    else:
        await event.answer(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=wb_buttons))


@dp.callback_query(F.data.startswith("wb_"))
async def process_waterbody(call: CallbackQuery, state: FSMContext):
    idx = int(call.data.replace("wb_", ""))
    wb_list = list(WATERBODY_FISH.keys())
    if idx >= len(wb_list):
        await call.answer("Ошибка водоема", show_alert=True)
        return
    wb_name = wb_list[idx]
    await state.update_data(waterbody=wb_name, selected_fish=[])
    await state.set_state(PostForm.coords)
    await call.message.answer(f"Водоём: {wb_name}")
    await call.message.answer("Укажите координаты точки:", reply_markup=get_control_kb())
    await call.answer()


@dp.message(PostForm.coords)
async def process_coords(message: types.Message, state: FSMContext):
    if not message.text:
        await message.answer("Отправьте текстовые координаты:")
        return
    await state.update_data(coords=message.text)
    await state.set_state(PostForm.fish)
    await render_fish_picker(message, state)


async def render_fish_picker(event, state: FSMContext, page: int = 1):
    data = await state.get_data()
    wb = data.get("waterbody", "")
    selected = data.get("selected_fish", [])
    kb = get_fish_keyboard(wb, page=page, selected_fish=selected)
    text = "Укажите рыбу (можно выбрать до 4):"

    if isinstance(event, CallbackQuery):
        await event.message.edit_text(text, reply_markup=kb)
    else:
        await event.answer(text, reply_markup=kb)


@dp.callback_query(F.data.startswith("fpg:"))
async def process_fish_page(call: CallbackQuery, state: FSMContext):
    page = int(call.data.split(":")[1])
    await render_fish_picker(call, state, page=page)
    await call.answer()


@dp.callback_query(F.data == "noop")
async def process_noop(call: CallbackQuery):
    await call.answer()


@dp.callback_query(F.data.startswith("fidx_"))
async def toggle_fish_by_index(call: CallbackQuery, state: FSMContext):
    raw_data = call.data.replace("fidx_", "")
    idx_str, page_str = raw_data.split(":")
    idx = int(idx_str)
    page = int(page_str)

    data = await state.get_data()
    wb = data.get("waterbody", "")
    fish_list = WATERBODY_FISH.get(wb, ["Разнорыбица"])

    if idx >= len(fish_list):
        await call.answer("Ошибка индекса рыбы", show_alert=True)
        return

    fish_name = fish_list[idx]
    selected = data.get("selected_fish", [])

    if fish_name in selected:
        selected.remove(fish_name)
    else:
        if len(selected) >= 4:
            await call.answer("Не более 4 видов!", show_alert=True)
            return
        selected.append(fish_name)

    await state.update_data(selected_fish=selected)
    await render_fish_picker(call, state, page=page)
    await call.answer()


@dp.callback_query(F.data == "manual_fish")
async def start_manual_fish(call: CallbackQuery, state: FSMContext):
    await state.set_state(PostForm.typing_custom_fish)
    await call.message.answer("Напишите название рыбы сообщением:")
    await call.answer()


@dp.message(PostForm.typing_custom_fish)
async def process_custom_fish(message: Message, state: FSMContext):
    custom_fish = message.text.strip()
    data = await state.get_data()
    selected = data.get("selected_fish", [])

    if len(selected) >= 4:
        await message.answer("⚠️ Вы уже выбрали максимум 4 рыбы.")
        await state.set_state(PostForm.clip)
        await message.answer("Укажите клипсу:", reply_markup=get_control_kb())
        return

    if custom_fish not in selected:
        selected.append(custom_fish)
        await state.update_data(selected_fish=selected)

    await state.set_state(PostForm.fish)
    await message.answer(f"Добавлена рыба: <b>{custom_fish}</b>", parse_mode="HTML")
    await render_fish_picker(message, state, page=1)


@dp.callback_query(F.data == "confirm_fish")
async def confirm_fish(call: CallbackQuery, state: FSMContext):
    await state.set_state(PostForm.clip)
    await call.message.answer("Укажите клипсу:", reply_markup=get_control_kb())
    await call.answer()


@dp.message(PostForm.clip)
async def process_clip(message: types.Message, state: FSMContext):
    if not message.text:
        return
    await state.update_data(clip=message.text)
    await state.set_state(PostForm.depth)
    await message.answer("Укажите глубину:", reply_markup=get_control_kb())


@dp.message(PostForm.depth)
async def process_depth(message: types.Message, state: FSMContext):
    if not message.text:
        return
    await state.update_data(depth=message.text)
    await state.set_state(PostForm.speed)
    await message.answer("Укажите скорость подмотки:", reply_markup=get_control_kb())


@dp.message(PostForm.speed)
async def process_speed(message: types.Message, state: FSMContext):
    if not message.text:
        return
    await state.update_data(speed=message.text)
    await state.set_state(PostForm.temp)

    temp_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❄️ Пониженная", callback_data="temp_Пониженная"),
         InlineKeyboardButton(text="🌡️ Нормальная", callback_data="temp_Нормальная")],
        [InlineKeyboardButton(text="☀️ Повышенная", callback_data="temp_Повышенная")],
        [InlineKeyboardButton(text="⏩ Пропустить", callback_data="skip_step")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_post")]
    ])
    await message.answer("Укажите температуру воды:", reply_markup=temp_kb)


@dp.callback_query(PostForm.temp, F.data.startswith("temp_"))
async def process_temp_choice(call: CallbackQuery, state: FSMContext):
    temp_value = call.data.replace("temp_", "")
    await state.update_data(temp=temp_value)
    await state.set_state(PostForm.square)
    await call.message.answer(f"Температура: <b>{temp_value}</b>", parse_mode="HTML")
    await call.message.answer("Укажите квадрат карты:", reply_markup=get_control_kb())
    await call.answer()


@dp.message(PostForm.square)
async def process_square(message: types.Message, state: FSMContext):
    if not message.text:
        return
    await state.update_data(square=message.text)
    await state.set_state(PostForm.comment)
    await message.answer("Укажите комментарий (до 900 символов):", reply_markup=get_control_kb())


@dp.message(PostForm.comment)
async def process_comment(message: types.Message, state: FSMContext):
    if not message.text:
        return
    await state.update_data(comment=message.text)
    await ask_show_author(message, state)


async def ask_show_author(event, state: FSMContext):
    await state.set_state(PostForm.show_author)
    author_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👤 Показывать автора", callback_data="author_yes"),
         InlineKeyboardButton(text="🕵️‍♂️ Анонимно", callback_data="author_no")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_post")]
    ])
    text = "Отображать автора (вас) в итоговой публикации?"
    if isinstance(event, CallbackQuery):
        await event.message.answer(text, reply_markup=author_kb)
        await event.answer()
    else:
        await event.answer(text, reply_markup=author_kb)


@dp.callback_query(PostForm.show_author, F.data.in_({"author_yes", "author_no"}))
async def process_author_choice(call: CallbackQuery, state: FSMContext):
    show_author = True if call.data == "author_yes" else False
    await state.update_data(show_author=show_author)
    await state.set_state(PostForm.photos)
    await state.update_data(photos=[])

    finish_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Готово (отправить)", callback_data="finish_photos")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_post")]
    ])
    auth_status = "Показывать автора" if show_author else "Анонимно"
    await call.message.answer(
        f"Режим автора: <b>{auth_status}</b>\n\n"
        "Отправьте скриншоты (от 1 до 4 шт). После завершения нажмите 'Готово':",
        reply_markup=finish_kb,
        parse_mode="HTML"
    )
    await call.answer()


@dp.message(PostForm.photos, F.photo)
async def process_photos(message: types.Message, state: FSMContext):
    data = await state.get_data()
    photos = data.get("photos", [])
    if len(photos) >= 4:
        await message.answer("Загружено максимум (4 фото). Нажмите кнопку 'Готово'.")
        return

    photos.append(message.photo[-1].file_id)
    await state.update_data(photos=photos)

    finish_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Готово (отправить)", callback_data="finish_photos")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_post")]
    ])
    await message.answer(f"Загружено фото: {len(photos)}/4", reply_markup=finish_kb)


@dp.callback_query(F.data == "skip_step")
async def skip_step(call: CallbackQuery, state: FSMContext):
    curr_state = await state.get_state()
    if curr_state == PostForm.post_type.state:
        await state.update_data(post_type="Не указано")
        await go_to_waterbody(call, state)
    elif curr_state == PostForm.waterbody.state:
        await state.update_data(waterbody="Не указано")
        await state.set_state(PostForm.coords)
        await call.message.answer("Водоём: Не указано")
        await call.message.answer("Укажите координаты точки:", reply_markup=get_control_kb())
    elif curr_state == PostForm.coords.state:
        await state.update_data(coords="Не указано")
        await state.set_state(PostForm.fish)
        await call.message.answer("Координаты: Не указано")
        await render_fish_picker(call, state)
    elif curr_state in [PostForm.fish.state, PostForm.typing_custom_fish.state]:
        await state.update_data(selected_fish=[])
        await state.set_state(PostForm.clip)
        await call.message.answer("Рыба: Не указано")
        await call.message.answer("Укажите клипсу:", reply_markup=get_control_kb())
    elif curr_state == PostForm.clip.state:
        await state.update_data(clip="Не указано")
        await state.set_state(PostForm.depth)
        await call.message.answer("Клипса: Не указано")
        await call.message.answer("Укажите глубину:", reply_markup=get_control_kb())
    elif curr_state == PostForm.depth.state:
        await state.update_data(depth="Не указано")
        await state.set_state(PostForm.speed)
        await call.message.answer("Глубина: Не указано")
        await call.message.answer("Укажите скорость подмотки:", reply_markup=get_control_kb())
    elif curr_state == PostForm.speed.state:
        await state.update_data(speed="Не указано")
        await state.set_state(PostForm.temp)
        temp_kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❄️ Пониженная", callback_data="temp_Пониженная"),
             InlineKeyboardButton(text="🌡️ Нормальная", callback_data="temp_Нормальная")],
            [InlineKeyboardButton(text="☀️ Повышенная", callback_data="temp_Повышенная")],
            [InlineKeyboardButton(text="⏩ Пропустить", callback_data="skip_step")],
            [InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_post")]
        ])
        await call.message.answer("Скорость подмотки: Не указано")
        await call.message.answer("Укажите температуру воды:", reply_markup=temp_kb)
    elif curr_state == PostForm.temp.state:
        await state.update_data(temp="Не указано")
        await state.set_state(PostForm.square)
        await call.message.answer("Температура: Не указано")
        await call.message.answer("Укажите квадрат карты:", reply_markup=get_control_kb())
    elif curr_state == PostForm.square.state:
        await state.update_data(square="Не указано")
        await state.set_state(PostForm.comment)
        await call.message.answer("Квадрат карты: Не указано")
        await call.message.answer("Укажите комментарий:", reply_markup=get_control_kb())
    elif curr_state == PostForm.comment.state:
        await state.update_data(comment="Не указано")
        await call.message.answer("Комментарий: Не указано")
        await ask_show_author(call, state)
    await call.answer()


@dp.callback_query(F.data == "cancel_post")
async def cancel_post(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.answer("❌ Форма отменена. Нажмите /start для начала.")
    await call.answer()


@dp.callback_query(F.data == "finish_photos")
async def finish_photos(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    photos = data.get("photos", [])
    if not photos:
        await call.answer("Загрузите хотя бы 1 фото!", show_alert=True)
        return

    raw_ptype = data.get('post_type')
    ptype_tag = f"#{raw_ptype.lower()}_admiral_rf4" if raw_ptype and raw_ptype != "Не указано" else ""

    raw_wb = data.get('waterbody')
    if raw_wb and raw_wb != "Не указано":
        wb_clean = WATERBODY_TAGS.get(raw_wb, raw_wb.lower().replace("оз. ", "").replace("р. ", "").replace(" ", "_"))
        wb_tag = f"#{wb_clean}_admiral_rf4"
    else:
        wb_tag = ""

    caption_lines = []
    if ptype_tag:
        caption_lines.append(ptype_tag)
    if wb_tag:
        caption_lines.append(f"<b>Водоём:</b> {wb_tag}")

    fish_selected = data.get("selected_fish", [])
    if fish_selected:
        caption_lines.append(f"- <b>Рыба:</b> {', '.join(fish_selected)}")

    for key, label in [('coords', 'Координаты'), ('square', 'Квадрат'), ('clip', 'Клипса'),
                       ('depth', 'Глубина'), ('speed', 'Скорость'), ('temp', 'Температура'),
                       ('comment', 'Комментарий')]:
        val = data.get(key)
        if val and val != "Не указано":
            caption_lines.append(f"- <b>{label}:</b> {val}")

    if data.get("show_author"):
        user = call.from_user
        author_str = f"@{user.username}" if user.username else f'<a href="tg://user?id={user.id}">{user.first_name}</a>'
        caption_lines.append(f"- <b>Автор:</b> {author_str}")

    offer_post_url = f"https://t.me/{BOT_USERNAME}?start=1"
    caption_lines.extend([
        "",
        f'📍 <a href="{offer_post_url}"><b>ПРЕДЛОЖИТЬ ПОСТ</b></a>',
        f'<a href="{POST_LINK}"><b>ПОИСК ТОЧКИ</b></a> | <a href="{TIKTOK_LINK}"><b>TIKTOK КАНАЛ</b></a>'
    ])

    caption = "\n".join(caption_lines)
    post_key = f"{call.from_user.id}_{call.message.message_id}"
    MODERATION_POSTS[post_key] = {"photos": photos, "caption": caption}

    admin_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Опубликовать", callback_data=f"app_{post_key}"),
         InlineKeyboardButton(text="❌ Отклонить", callback_data=f"rej_{post_key}")]
    ])

    media = [InputMediaPhoto(media=photos[0], caption=f"📥 <b>Пост на проверку:</b>\n\n{caption}", parse_mode="HTML")]
    for p in photos[1:]:
        media.append(InputMediaPhoto(media=p))

    await bot.send_media_group(chat_id=ADMIN_ID, media=media)
    await bot.send_message(chat_id=ADMIN_ID, text="Выберите действие для модерации:", reply_markup=admin_kb)

    await call.message.answer("Ваш пост успешно отправлен на модерацию!")
    await state.clear()
    await call.answer()


@dp.callback_query(F.data.startswith("app_"))
async def approve_post(call: CallbackQuery):
    post_key = call.data.replace("app_", "")
    post_data = MODERATION_POSTS.get(post_key)
    if not post_data:
        await call.answer("Ошибка: Данные поста не найдены в памяти.", show_alert=True)
        return

    photos, caption = post_data["photos"], post_data["caption"]
    try:
        media = [InputMediaPhoto(media=photos[0], caption=caption, parse_mode="HTML")]
        for p in photos[1:]:
            media.append(InputMediaPhoto(media=p))
        await bot.send_media_group(chat_id=CHANNEL_ID, media=media)
        await call.message.edit_text("✅ Пост успешно опубликован в канал!")
        MODERATION_POSTS.pop(post_key, None)
    except Exception as e:
        await call.message.edit_text(f"❌ Ошибка при публикации: {e}")
    await call.answer()


@dp.callback_query(F.data.startswith("rej_"))
async def reject_post(call: CallbackQuery):
    post_key = call.data.replace("rej_", "")
    MODERATION_POSTS.pop(post_key, None)
    await call.message.edit_text("❌ Пост отклонен.")
    await call.answer()


# --- МОДЕРАЦИЯ И БАНЫ ---
async def punish_user(message: types.Message, reason: str):
    user = message.from_user
    if user and user.id == ADMIN_ID:
        return
    try:
        member = await message.bot.get_chat_member(chat_id=message.chat.id, user_id=user.id)
        if getattr(member, "status", None) in ("creator", "administrator"):
            return
    except Exception:
        pass

    user_id = user.id
    current_mutes = USER_WARNINGS.get(user_id, 0) + 1
    USER_WARNINGS[user_id] = current_mutes

    days_mapping = {1: 1, 2: 3, 3: 7}
    mute_days = days_mapping.get(current_mutes, 14)
    until_date = datetime.now() + timedelta(days=mute_days)

    if user.first_name and user.first_name.strip().lower() != "group":
        display_name = user.first_name
    elif user.username:
        display_name = f"@{user.username}"
    else:
        display_name = "Рыбак"

    try:
        await message.bot.restrict_chat_member(
            chat_id=message.chat.id,
            user_id=user_id,
            permissions=types.ChatPermissions(can_send_messages=False),
            until_date=until_date
        )
        await message.delete()
        warning_msg = await message.answer(
            f"🚫 Пользователь <b>{display_name}</b> наказан за <b>{reason}</b>.\n"
            f"🔇 Срок мута: <b>{mute_days} дн.</b> (Нарушение №{current_mutes}).",
            parse_mode="HTML"
        )
        await asyncio.sleep(10)
        await warning_msg.delete()
    except Exception as e:
        logging.error(f"Не удалось выдать мут: {e}")


@dp.message(Command("unmute"))
async def cmd_unmute(message: types.Message):
    if message.chat.type not in ("group", "supergroup"):
        return

    # Разрешаем выполнение сразу главному администратору по ID ИЛИ создателю/админу чата
    user_id = message.from_user.id if message.from_user else None
    is_admin = (user_id == ADMIN_ID)

    if not is_admin and user_id:
        try:
            member = await message.bot.get_chat_member(chat_id=message.chat.id, user_id=user_id)
            if getattr(member, "status", None) in ("creator", "administrator"):
                is_admin = True
        except Exception as e:
            logging.error(f"Ошибка проверки прав через API: {e}")

    # Если отправлено анонимно от имени канала (когда ID совпадает с ID чата или канала)
    if not is_admin:
        if message.sender_chat and message.sender_chat.id == message.chat.id:
            is_admin = True

    if not is_admin:
        await message.reply("⚠️ У вас нет прав администратора.")
        return

    target_user = None

    if message.reply_to_message and message.reply_to_message.from_user:
        target_user = message.reply_to_message.from_user
    else:
        args = message.text.split(maxsplit=1)
        if len(args) > 1:
            identifier = args[1].strip()
            try:
                if identifier.isdigit():
                    chat_member = await message.bot.get_chat_member(chat_id=message.chat.id, user_id=int(identifier))
                    target_user = chat_member.user
                elif identifier.startswith("@"):
                    # Поиск по юзернейму через прямое обращение к API если потребуется, либо по reply
                    pass
            except Exception:
                pass

    if not target_user:
        await message.reply(
            "⚠️ Ответьте на сообщение пользователя или укажите его ID (например, <code>/unmute 123456789</code>), чтобы размутить.",
            parse_mode="HTML")
        return

    if target_user.id == message.bot.id:
        await message.reply("⚠️ Нельзя применить к боту.", parse_mode="HTML")
        return

    try:
        await message.bot.restrict_chat_member(
            chat_id=message.chat.id,
            user_id=target_user.id,
            permissions=types.ChatPermissions(
                can_send_messages=True,
                can_send_audios=True,
                can_send_documents=True,
                can_send_photos=True,
                can_send_videos=True,
                can_send_video_notes=True,
                can_send_voice_notes=True,
                can_send_polls=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True
            )
        )
        USER_WARNINGS.pop(target_user.id, None)

        unmute_msg = await message.answer(f"🔊 Пользователь {target_user.full_name} успешно размучен!",
                                          parse_mode="HTML")

        try:
            await message.delete()
        except Exception:
            pass

        await asyncio.sleep(10)
        await unmute_msg.delete()
    except Exception as e:
        logging.error(f"Ошибка размута: {e}")
        await message.reply(f"⚠️ Не удалось размутить пользователя. Ошибка: {e}")


@dp.message(F.text & ~F.via_bot)
async def check_chat_content(message: types.Message):
    if message.chat.type not in ("group", "supergroup"):
        return
    text_lower = message.text.lower()
    if ADS_REGEX.search(message.text) and BOT_USERNAME.lower() not in text_lower:
        await punish_user(message, "рекламу / сторонние ссылки")
        return
    if any(bad_word in text_lower for bad_word in BAD_WORDS):
        await punish_user(message, "использование ненормативной лексики / оскорблений")
        return


async def main():
    logging.basicConfig(level=logging.INFO)
    await start_web_server()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
