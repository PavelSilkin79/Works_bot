import os
from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram_dialog import Dialog, DialogManager, StartMode, Window
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.kbd import SwitchTo, Column, Button, Select, Multiselect
from aiogram_dialog.widgets.input import TextInput
from sqlalchemy import select, delete, func
from .command import setup_db
from models import Welders
from states.states import WeldersSG, CommandSG


# Директория для сохранения фотографий
PHOTO_DIR = 'photos'
os.makedirs(PHOTO_DIR, exist_ok=True)

welders_router = Router()


async def back_command(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.start(state=CommandSG.start, mode=StartMode.RESET_STACK)

# Стартовый командный хэндлер
async def start_command(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    session_factory = await setup_db()
    if not session_factory:
        await callback.answer("⚠ Ошибка: База данных недоступна.")
        return

    await dialog_manager.start(
        state=WeldersSG.start,
        mode=StartMode.RESET_STACK,
        data={"session_factory": session_factory}
    )
    dialog_manager.start_data = {"session_factory": session_factory}


async def weld_list(dialog_manager: DialogManager, **kwargs):
    start_data = dialog_manager.start_data or {}
    session_factory = start_data.get("session_factory")

    if not session_factory:
        return {"welders": []}  # Возвращаем пустой список вместо ошибки

    async with session_factory() as session:
        result = await session.execute(select(Welders))
        organizations = result.scalars().all()
        return {"welders": welders}


# Добавление организации
async def add_weld_name(event: Message, widget: TextInput, dialog_manager: DialogManager, text: str):
    dialog_manager.dialog_data["name"] = text
    await dialog_manager.next()

async def add_weld_surname(event: Message, widget: TextInput, dialog_manager: DialogManager, text: str):
     # Проверка на существование фамилии
    session_factory = await setup_db()

    async with session_factory() as session:
        existing_weld = await session.execute(
            Welders.__table__.select().where(func.lower(Welders.name) == text.lower())
        )
        existing_weld = existing_weld.scalars().first()

        if existing_weld:
            # фамилия уже существует, прерываем выполнение
            await event.answer(f"Фамилия '{text}' уже существует.")
            await dialog_manager.done()
            return
    # Если фамилия  не существует, сохраняем название в данных диалога
    dialog_manager.dialog_data["surname"] = text
    await dialog_manager.next()

async def add_weld_patronymic (event: Message, widget: TextInput, dialog_manager: DialogManager, text: str):
    dialog_manager.dialog_data["patronymic"] = text
    await dialog_manager.next()

async def add_weld_address(event: Message, widget: TextInput, dialog_manager: DialogManager, text: str):
    dialog_manager.dialog_data["address"] = text
    await dialog_manager.next()

async def add_weld_phone(event: Message, widget: TextInput, dialog_manager: DialogManager, text: str):
    dialog_manager.dialog_data["phone"] = text
    await dialog_manager.next()

async def add_weld_email(event:Message, widget: TextInput, dialog_manager: DialogManager, text: str):
    session_factory = await setup_db()
    dialog_manager.dialog_data["email"] = text

    async with session_factory() as session:
        new_welders= Welders(
            name=dialog_manager.dialog_data["name"],
            surname=dialog_manager.dialog_data["surname"],
            patronymic=dialog_manager.dialog_data["patronymic"],
            phone=dialog_manager.dialog_data["phone"],
            address=dialog_manager.dialog_data["address"],
            email=dialog_manager.dialog_data["email"],
        )
        session.add(new_welders)
        await session.commit()

    # Отправляем сообщение, что организация была добавлена
    await event.answer(f"Сварщик '{dialog_manager.dialog_data['name']}' успешно добавлен!")# Надо добавить фамилию
    await dialog_manager.done()
    await dialog_manager.start(state=CommandSG.start, mode=StartMode.RESET_STACK)

async def delete_selected_weld(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    start_data = dialog_manager.start_data or {}
    session_factory = start_data.get("session_factory")

    if not session_factory:
        await callback.answer("⚠ Ошибка: База данных недоступна.")
        return

    selected_weld = dialog_manager.find("del_weld_multi").get_checked()
    if not selected_weld:
        await callback.answer("⚠ Вы не выбрали сварщика для удаления.")
        return

    # Преобразуем ID из строк в числа
    try:
        selected_welds = list(map(int, selected_welds))
    except ValueError:
        await callback.answer("⚠ Ошибка: Некорректный формат ID.")
        return

    async with session_factory() as session:
        await session.execute(delete(Welders).where(Welders.id.in_(selected_welds)))
        await session.commit()

    await callback.answer("✅ Сварщики удалены!")
     # Обновляем данные вручную через restart
    await dialog_manager.reset_stack()
    await dialog_manager.start(state=CommandSG.start)


async def save_selected_weld_id(callback: CallbackQuery, select: Select, dialog_manager: DialogManager, item_id: str):
    dialog_manager.dialog_data["edit_weld_id"] = int(item_id)  # Сохраняем ID выбранного монтажника
    await dialog_manager.next()  # Переход к следующему шагу


# Редактирование данных сварщика
async def edit_weld_field(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    # Получаем id кнопки, которая была нажата (например, "name", "phone", "address", "email")
    field = button.widget_id
    dialog_manager.dialog_data["edit_field"] = field  # Сохраняем поле, которое будем редактировать
    await dialog_manager.next()

async def save_edited_field(event: Message, widget: TextInput, dialog_manager: DialogManager, text: str):
    edit_field = dialog_manager.dialog_data.get("edit_field")
    edit_org_id = dialog_manager.dialog_data.get("edit_weld_id")

    if not edit_field:
        await event.answer("Ошибка: Не выбран элемент для редактирования.")
        return

    if not edit_weld_id:
        await event.answer("Ошибка: ID организации отсутствует.")
        return

    # Запрос на обновление в базе данных
    session_factory = dialog_manager.start_data.get("session_factory")
    async with session_factory() as session:
        result = await session.execute(select(Welders).where(Welders.id == edit_weld_id))
        weld = result.scalar_one_or_none()

        if weld:
            setattr(weld, edit_field, str(text))  # Редактируем нужное поле
            await session.commit()
            await event.answer(f"✅ {edit_field.capitalize()} обновлено: {text}")
        else:
            await event.answer("Ошибка: Данные о сварщике не найдена.")

    await dialog_manager.done()
    await dialog_manager.reset_stack()
    await dialog_manager.start(state=CommandSG.start)

welders_dialog = Dialog(
    Window(
        Const("Выберите действие:"),
        Column(
            SwitchTo(Const("✅ Добавить сварщика"), id="add_name", state=WeldersSG.add_name),
            SwitchTo(Const("📝 Редактировать"), id="select_welders", state=WeldersSG.select_weld),
            SwitchTo(Const("❌ Удалить"), id="delete_welders", state=WeldersSG.delete_weld),
            Button(Const("🔙 Назад"), id="back", on_click=back_command),
        ),
        state=WeldersSG.start,
    ),

    Window(
        Const("Введите имя сварщика:"),
        TextInput(id="name_input", on_success=add_weld_name),
        SwitchTo(Const("🔙 Назад"), id="back", state=WeldersSG.start),
        state=WeldersSG.add_name,
    ),
        Window(
        Const("Введите фамилию сварщика:"),
        TextInput(id="surname_input", on_success=add_weld_surname),
        SwitchTo(Const("🔙 Назад"), id="back", state=WeldersSG.start),
        state=WeldersSG.add_surname,
    ),
    Window(
        Const("Введите отчество сварщика:"),
        TextInput(id="patronymic_input", on_success=add_weld_patronymic),
        SwitchTo(Const("🔙 Назад"), id="back", state=WeldersSG.start),
        state=WeldersSG.add_patronymic,
    ),
    Window(
        Const("Введите телефон сварщика:"),
        TextInput(id="phone_input", on_success=add_weld_phone),
        SwitchTo(Const("🔙 Назад"), id="back", state=WeldersSG.start),
        state=WeldersSG.add_phone,
    ),
    Window(
        Const("Введите адрес проживания сварщика:"),
        TextInput(id="address_input", on_success=add_weld_address),
        SwitchTo(Const("🔙 Назад"), id="back", state=WeldersSG.start),
        state=WeldersSG.add_address,
    ),
    Window(
        Const("Введите email сварщика:"),
        TextInput(id="email_input", on_success=add_weld_email),
        SwitchTo(Const("🔙 Назад"), id="back", state=WeldersSG.start),
        state=WeldersSG.add_email,
    ),
    Window(
        Const("Выберите организации для удаления:"),
        Column(
            Multiselect(
                checked_text=Format("{item.name} ✅"),  # Когда элемент выбран
                unchecked_text=Format("{item.name} ❌"),  # Когда элемент НЕ выбран
                id="del_weld_multi",
                item_id_getter=lambda item: item.id,  # Получаем ID организации
                items="welders",
            )
        ),
        Button(Const("❌ Удалить выбранные"), id="confirm_delete", on_click=delete_selected_weld),
        SwitchTo(Const("🔙 Назад"), id="back", state=WeldersSG.start),
        state=WeldersSG.delete_weld,
        getter=weld_list,
    ),
    Window(
        Const("Выберите сварщика для редактирования:"),
        Column(
            Select(
                Format("{item.name}"),  # Показываем название организации
                id="edit_weld_select",
                item_id_getter=lambda item: str(item.id),  # ID должен быть строкой
                items="welders",
                on_click=save_selected_weld_id,  # Вызываем обработчик при выборе
            )
        ),
        SwitchTo(Const("🔙 Назад"), id="back", state=WeldersSG.start),
        state=WeldersSG.select_weld,
        getter=weld_list,  # Загружаем список организаций
    ),
    Window(
        Const("Выберите, что редактировать:"),
        Column(
            Button(Const("Имя"), id="name", on_click=edit_weld_field),
            Button(Const("Фамилия"), id="surname", on_click=edit_weld_field),
            Button(Const("Отчество"), id="patronymic", on_click=edit_weld_field),
            Button(Const("Телефон"), id="phone", on_click=edit_weld_field),
            Button(Const("Адрес"), id="address", on_click=edit_weld_field),
            Button(Const("Email"), id="email", on_click=edit_weld_field),
        ),
        SwitchTo(Const("🔙 Назад"), id="back", state=WeldersSG.select_weld),
        state=WeldersSG.select_field_weld,
    ),
    Window(
        Const("Введите новое значение:"),
        TextInput(id="new_value_input", on_success=save_edited_field),
        SwitchTo(Const("🔙 Назад"), id="back", state=WeldersSG.select_field_weld),
        state=WeldersSG.edit_field_weld,
    ),
)

welders_router.include_router(welders_dialog)