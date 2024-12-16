import os
from uuid import uuid4
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.types import Message, FSInputFile
from sqlalchemy.ext.asyncio import AsyncSession


from db import get_db
from models import Organization, Employee
from config import Config


bot = Bot(token=Config.TOKEN)
dp = Dispatcher(storage=RedisStorage())

#Директория для сщхранения фотографий
PHOTO_DIR = 'photos'
os.makedirs(PHOTO_DIR, exist_ok=True)


class OrgStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_contact = State()


class EmpStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_contact = State()
    waiting_for_photo = State()
    waiting_for_organiztion_id = State()


#Добавление организаций
@dp.message(Command('add_organiization'))
async def add_organiization(message: Message, state: FSMContext):
    await message.answer('Введите название организации')
    await state.set_state(OrgStates.waiting_for_name)


@dp.message(OrgStates.waiting_for_name)
async def set_org_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer('Введите контактные данные организации: ')
    await state.set_state(OrgStates.waiting_for_contact)


@dp.message(OrgStates.waiting_for_contact)
async def save_organization(message: Message, state: FSMContext, db: AsyncSession = get_db()):
    data = await state.get_data()
    organization = Organization(name=data['name'], contact=message.text)
    async with db as session:
        session.add(organization)
        await session.commit()
    await message.answer(f'Организация {organization.name} успешно добавлена!')
    await state.clear()


#Добавление сотрудников
@dp.message(Command('add_employee'))
async def add_employee(message: Message, state: FSMContext):
    await message.answer('Введите имя сотрудника: ')
    await state.set_state(EmpStates.waiting_for_name)

@dp.message(EmpStates.waiting_for_name)
async def set_employee_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer('Введите контактные данные сотрудника: ')
    await state.set_state(EmpStates.waiting_for_contact)


@dp.message(EmpStates.waiting_for_contact)
async def set_employee_contact(message: Message, state: FSMContext):
    await state.update_data(contact=message.text)
    await message.answer('Отправьте фотографию сотрудника: ')
    await state.set_state(EmpStates.waiting_for_photo)


@dp.message(EmpStates.waiting_for_photo, content_types=types.ContentType.PHOTO)
async def set_employee_photo(message: Message, state: FSMContext):
    photo = message.photo[-1]
    file_id = photo.file_id
    file = await bot.get_file(file_id)
    file_path = f'{PHOTO_DIR}/{uuid4()}.jpg'
    await bot.download_file(file.file_path, file_path)

    await state.update_data(photo_path=file_path)
    await message.answer('Ввудите ID организации, к которой относится сотрудник: ')
    await state.set_state(EmpStates.waiting_for_organization_id)


@dp.message(EmpStates.waiting_for_organization_id)
async def save_employee(message: Message, state: FSMContext, db: AsyncSession = get_db()):
    data = await state.get_data()
    employee = Employee(
        name=data['name'],
        contact=data['contact'],
        photo_path=data['photo_path'],
        organization_id=int(message.text),
    )
    async with db as session:
        session.add(employee)
        await session.commit()
    await message.answer(f'Сотрудник {employee.name} успешно добавлен!')
    await state.clear()


#Вывод всех организаций
@dp.message(Command('list_organizations'))
async def list_organizations(message: Message, db: AsyncSession = get_db()):
    async with db as session:
        result = await session.execute(Organization.__table__.select())
        organizations = result.fetchall()

    if not organizations:
        await message.answer('Организаций нет')
    else:
        text = '\n'.join([f'{org.id}. {org.name}({org.contact})' for org in organizations])
        await message.answer(text)

#Вывод всех сотрудников
@dp.message(Command('list_employees'))
async def list_employees(message: Message, db: AsyncSession = get_db()):
    async with db as session:
        result = await session.execute(Employee.__table__.select())
        employees = result.fetchall()

    if not employees:
        await message.answer('Список сотрудников пуст.')
    else:
        text = '\n'.join([f'{emp.id}. {emp.name}({emp.contact}) - Организация ID: {emp.organization_id}' for emp in employees])
        await message.answer(text)


if __name__ == '__main__':
    import asyncio
    from sqlalchemy.ext.asyncio import create_async_engine

    from db import engine, Base

    async def init_models():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

    asyncio.run(init_models())
    dp.run_polling(bot)
