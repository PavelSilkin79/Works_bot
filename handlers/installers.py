import os
from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.enums import ParseMode
from aiogram_dialog import Dialog, DialogManager, StartMode, Window
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.kbd import SwitchTo, Column, Button, Select, Multiselect, Row
from aiogram_dialog.widgets.input import TextInput, MessageInput
from sqlalchemy import select, delete, func
from .command import setup_db
from models import Installers
from states.states import InstallersSG, CommandSG


installers_router = Router()


async def back_command(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.start(state=CommandSG.start, mode=StartMode.RESET_STACK)


# Стартовый командный хэндлер
async def start_command(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    session_factory = dialog_manager.middleware_data.get("session_factory")
    if not session_factory:
        await callback.answer("⚠ Ошибка: База данных недоступна.")
        return

    await dialog_manager.start(
        state=InstallersSG.start,
        mode=StartMode.RESET_STACK,
        data={"session_factory": session_factory}
    )
    dialog_manager.start_data = {"session_factory": session_factory}


async def inst_list(dialog_manager: DialogManager, **kwargs):
    session_factory = dialog_manager.middleware_data.get("session_factory")

    if not session_factory:
        await dialog_manager.done("❗ Ошибка подключения к базе данных.")
        return {"installers": []}  # Возвращаем пустой список вместо ошибки

    async with session_factory() as session:
        result = await session.execute(select(Installers))
        installers = result.scalars().all()

        if not installers:
            # Получаем объект сообщения или колбэка
            event = dialog_manager.event
            if hasattr(event, "message"):
                await event.message.answer("❗ Список монтажников пуст. Возвращаемся в меню.")
            elif hasattr(event, "callback_query"):
                await event.callback_query.message.answer("❗ Список монтажников пуст. Возвращаемся в меню.")

            await dialog_manager.start(CommandSG.start, mode=StartMode.RESET_STACK)
            return {}
        return {"installers": installers}


# Добавление организации
async def add_inst_name(event: Message, widget: TextInput, dialog_manager: DialogManager, text: str):
    dialog_manager.dialog_data["name"] = text
    await dialog_manager.next()

async def add_inst_surname(event: Message, widget: TextInput, dialog_manager: DialogManager, text: str):
     # Проверка на существование фамилии
    session_factory = dialog_manager.middleware_data.get("session_factory")

    async with session_factory() as session:
        existing_inst = await session.execute(
            Installers.__table__.select().where(func.lower(Installers.name) == text.lower())
        )
        existing_inst = existing_inst.scalars().first()

        if existing_inst:
            # фамилия уже существует, прерываем выполнение
            await event.answer(f"Фамилия '{text}' уже существует.")
            await dialog_manager.done()
            return
    # Если фамилия  не существует, сохраняем название в данных диалога
    dialog_manager.dialog_data["surname"] = text
    await dialog_manager.next()

async def add_inst_patronymic (event: Message, widget: TextInput, dialog_manager: DialogManager, text: str):
    dialog_manager.dialog_data["patronymic"] = text
    await dialog_manager.next()

async def add_inst_photo(message: Message, widget: MessageInput, dialog_manager: DialogManager):
    if not message.photo:
        await message.answer("Пожалуйста, отправьте фото или нажмите «Пропустить».")
        return

    file_id = message.photo[-1].file_id
    dialog_manager.dialog_data["photo_id"] = file_id
    await message.answer("Фото сохранено.")
    await dialog_manager.next()

async def add_inst_address(event: Message, widget: TextInput, dialog_manager: DialogManager, text: str):
    dialog_manager.dialog_data["address"] = text
    await dialog_manager.next()

async def add_inst_phone(event: Message, widget: TextInput, dialog_manager: DialogManager, text: str):
    dialog_manager.dialog_data["phone"] = text
    await dialog_manager.next()

async def add_inst_email(event:Message, widget: TextInput, dialog_manager: DialogManager, text: str):
    session_factory = dialog_manager.middleware_data.get("session_factory")
    dialog_manager.dialog_data["email"] = text

    async with session_factory() as session:
        new_installers= Installers(
            name=dialog_manager.dialog_data["name"],
            surname=dialog_manager.dialog_data["surname"],
            patronymic=dialog_manager.dialog_data["patronymic"],
            photo_id=dialog_manager.dialog_data["photo_id"],
            phone=dialog_manager.dialog_data["phone"],
            address=dialog_manager.dialog_data["address"],
            email=dialog_manager.dialog_data["email"],
        )
        session.add(new_installers)
        await session.commit()

    # Отправляем сообщение, что монтажник был добавлен
    await event.answer(f"Монтажник {dialog_manager.dialog_data['name']} {dialog_manager.dialog_data["surname"]} успешно добавлен!")# надо добавить еще и фамилию
    await dialog_manager.done()
    await dialog_manager.start(state=CommandSG.start, mode=StartMode.RESET_STACK)

async def skip_photo(c: CallbackQuery, button: Button, manager: DialogManager):
    manager.dialog_data["photo"] = None
    await c.message.answer("Фото пропущено.")
    await manager.next()

async def delete_selected_inst(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    session_factory = dialog_manager.middleware_data.get("session_factory")

    if not session_factory:
        await callback.answer("⚠ Ошибка: База данных недоступна.")
        return

    selected_insts = dialog_manager.find("del_inst_multi").get_checked()
    if not selected_insts:
        await callback.answer("⚠ Вы не выбрали монтажников для удаления.")
        return

    # Преобразуем ID из строк в числа
    try:
        selected_insts = list(map(int, selected_insts))
    except ValueError:
        await callback.answer("⚠ Ошибка: Некорректный формат ID.")
        return

    async with session_factory() as session:
        await session.execute(delete(Installers).where(Installers.id.in_(selected_insts)))
        await session.commit()

    await callback.answer("✅ Монтажники удалены!")
     # Обновляем данные вручную через restart
    await dialog_manager.reset_stack()
    await dialog_manager.start(state=CommandSG.start)


async def save_selected_inst_id(callback: CallbackQuery, select: Select, dialog_manager: DialogManager, item_id: str):
    dialog_manager.dialog_data["edit_inst_id"] = int(item_id)  # Сохраняем ID выбранного монтажника
    await dialog_manager.next()  # Переход к следующему шагу


# Редактирование данных монтажника
async def edit_inst_field(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    # Получаем id кнопки, которая была нажата (например, "name", "phone", "address", "email")
    field = button.widget_id
    dialog_manager.dialog_data["edit_field"] = field  # Сохраняем поле, которое будем редактировать
    await dialog_manager.next()

async def save_edited_field(event: Message, widget: TextInput, dialog_manager: DialogManager, text: str):
    edit_field = dialog_manager.dialog_data.get("edit_field")
    edit_inst_id = dialog_manager.dialog_data.get("edit_inst_id")

    if not edit_field:
        await event.answer("Ошибка: Не выбран элемент для редактирования.")
        return

    if not edit_inst_id:
        await event.answer("Ошибка: ID монтажник отсутствует.")
        return

    # Запрос на обновление в базе данных
    session_factory = dialog_manager.middleware_data.get("session_factory")
    async with session_factory() as session:
        result = await session.execute(select(Installers).where(Installers.id == edit_inst_id))
        inst = result.scalar_one_or_none()

        if inst:
            setattr(inst, edit_field, str(text))  # Редактируем нужное поле
            await session.commit()
            FIELD_NAMES = {
                "address": "Адрес",
                "phone": "Телефон",
                "email": "Email",
                "name": "Имя",
                "surname": "Фамилия",
                "patronymic": "Отчество",
                "photo_id": "Фото"
            }

            field_label = FIELD_NAMES.get(edit_field, edit_field)
            await event.answer(
            f"✅ Поле *{field_label}* обновлено на: *{text}*",
            parse_mode="Markdown"
            )
            #await event.answer(f"✅ {edit_field.capitalize()} обновлено: {text}")
        else:
            await event.answer("Ошибка: Данные о монтажнике не найдена.")

    await dialog_manager.done()
    await dialog_manager.reset_stack()
    await dialog_manager.start(state=CommandSG.start)

installers_dialog = Dialog(
    Window(
        Const("Выберите действие:"),
        Column(
            SwitchTo(Const("✅ Добавить монтажника"), id="add_name", state=InstallersSG.add_name),
            SwitchTo(Const("📝 Редактировать"), id="select_installers", state=InstallersSG.select_inst),
            SwitchTo(Const("❌ Удалить"), id="delete_installers", state=InstallersSG.delete_inst),
            Button(Const("🔙 Назад"), id="back", on_click=back_command),
        ),
        state=InstallersSG.start,
    ),

    Window(
        Const("Введите имя монтажника:"),
        TextInput(id="name_input", on_success=add_inst_name),
        SwitchTo(Const("🔙 Назад"), id="back", state=InstallersSG.start),
        state=InstallersSG.add_name,
    ),
    Window(
        Const("Введите фамилию монтажника:"),
        TextInput(id="surname_input", on_success=add_inst_surname),
        SwitchTo(Const("🔙 Назад"), id="back", state=InstallersSG.start),
        state=InstallersSG.add_surname,
    ),
    Window(
        Const("Введите отчество монтажника:"),
        TextInput(id="patronymic_input", on_success=add_inst_patronymic),
        SwitchTo(Const("🔙 Назад"), id="back", state=InstallersSG.start),
        state=InstallersSG.add_patronymic,
    ),
    Window(
        Const("Пожалуйста, отправьте фото монтажника или нажмите «Пропустить»:"),
        MessageInput(add_inst_photo, content_types=["photo"]),
        Row(Button(Const("Пропустить"), id="skip_photo", on_click=skip_photo),),
        state=InstallersSG.add_photo,
    ),
    Window(
        Const("Введите телефон монтажника:"),
        TextInput(id="phone_input", on_success=add_inst_phone),
        SwitchTo(Const("🔙 Назад"), id="back", state=InstallersSG.start),
        state=InstallersSG.add_phone,
    ),
    Window(
        Const("Введите адрес проживания монтажника:"),
        TextInput(id="address_input", on_success=add_inst_address),
        SwitchTo(Const("🔙 Назад"), id="back", state=InstallersSG.start),
        state=InstallersSG.add_address,
    ),
    Window(
        Const("Введите email монтажника:"),
        TextInput(id="email_input", on_success=add_inst_email),
        SwitchTo(Const("🔙 Назад"), id="back", state=InstallersSG.start),
        state=InstallersSG.add_email,
    ),
    Window(
        Const("Выберите монтажника для удаления:"),
        Column(
            Multiselect(
                checked_text=Format("{item.name} {item.surname} ✅"),  # Когда элемент выбран
                unchecked_text=Format("{item.name} {item.surname} ❌"),  # Когда элемент НЕ выбран
                id="del_inst_multi",
                item_id_getter=lambda item: item.id,  # Получаем ID элемента
                items="installers",
            )
        ),
        Button(Const("❌ Удалить выбранные"), id="confirm_delete", on_click=delete_selected_inst),
        SwitchTo(Const("🔙 Назад"), id="back", state=InstallersSG.start),
        state=InstallersSG.delete_inst,
        getter=inst_list,
    ),
    Window(
        Const("Выберите монтажника для редактирования:"),
        Column(
            Select(
                Format("{item.name} {item.surname}"),  # Показываем имя и фамилию монтажника
                id="edit_inst_select",
                item_id_getter=lambda item: str(item.id),  # ID должен быть строкой
                items="installers",
                on_click=save_selected_inst_id,  # Вызываем обработчик при выборе
            )
        ),
        SwitchTo(Const("🔙 Назад"), id="back", state=InstallersSG.start),
        state=InstallersSG.select_inst,
        getter=inst_list,  # Загружаем список монтажников
    ),
    Window(
        Const("Выберите, что редактировать:"),
        Column(
            Button(Const("Имя"), id="name", on_click=edit_inst_field),
            Button(Const("Фамилия"), id="surname", on_click=edit_inst_field),
            Button(Const("Отчество"), id="patronymic", on_click=edit_inst_field),
            Button(Const("Телефон"), id="phone", on_click=edit_inst_field),
            Button(Const("Адрес"), id="address", on_click=edit_inst_field),
            Button(Const("Email"), id="email", on_click=edit_inst_field),
        ),
        SwitchTo(Const("🔙 Назад"), id="back", state=InstallersSG.select_inst),
        state=InstallersSG.select_field_inst,
    ),
    Window(
        Const("Введите новое значение:"),
        TextInput(id="new_value_input", on_success=save_edited_field),
        SwitchTo(Const("🔙 Назад"), id="back", state=InstallersSG.select_field_inst),
        state=InstallersSG.edit_field_inst,
    ),
)

installers_router.include_router(installers_dialog)