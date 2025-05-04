from sqlalchemy import select, delete, func
from db import models


class WeldServices:

    @staticmethod
    async def get_all_welders(session):
        result = await session.execute(select(Welders))
        return result.scalars().all()

    @staticmethod
    async def create_welder(session, data: dict):
        new_welder = Welders(
            name=data["name"],
            surname=data["surname"],
            patronymic=data["patronymic"],
            photo_id=data["photo_id"],
            phone=data["phone"],
            address=data["address"],
            email=data["email"],
        )
        session.add(new_welder)
        await session.commit()

    @staticmethod
    async def check_welder_exists(session, surname: str):
        result = await session.execute(
            Welders.__table__.select().where(func.lower(Welders.name) == surname.lower())
        )
        return result.scalars().first() is not None

    @staticmethod
    async def delete_welders_by_ids(session, ids: list[int]):
        await session.execute(delete(Welders).where(Welders.id.in_(ids)))
        await session.commit()

    @staticmethod
    async def get_welder_by_id(session, weld_id: int):
        return await session.get(Welders, weld_id)

    @staticmethod
    async def update_welder_field(session, weld, field: str, value: str):
        setattr(weld, field, value)
        await session.commit()
