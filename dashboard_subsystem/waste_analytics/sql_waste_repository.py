
from sqlmodel import Session, select

from waste_analytics.category import Category
from waste_analytics.waste_record import WasteRecord
from waste_analytics.waste_repository import WasteRepository
from waste_analytics.db_models import WasteRecordRow


class SQLWasteRepository(WasteRepository):

    def __init__(self, engine):
        self._engine = engine

    def add(self, record):
        row = WasteRecordRow(
            id=record.get_id(),
            item=record.get_item(),
            category=record.get_category().value,
            region_code=record.get_region_code(),
            created_at=record.get_created_at()
        )

        with Session(self._engine) as session:
            session.add(row)
            session.commit()

    def get_all(self):
        with Session(self._engine) as session:
            rows = session.exec(select(WasteRecordRow)).all()
            return [self._to_record(row) for row in rows]

    def get_by_region(self, region_code):
        with Session(self._engine) as session:
            statement = select(WasteRecordRow).where(
                WasteRecordRow.region_code == region_code
            )
            rows = session.exec(statement).all()
            return [self._to_record(row) for row in rows]

    def _to_record(self, row):
        return WasteRecord(
            row.item,
            Category(row.category),
            row.region_code,
            record_id=row.id,
            created_at=row.created_at
        )
