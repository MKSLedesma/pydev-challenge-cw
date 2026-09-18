from datetime import datetime
from typing import Optional
from sqlalchemy import DateTime, Float, String, create_engine, select
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from src.models import PharmaMetricSchema
from pandas import read_sql_table

class Base(DeclarativeBase):
    pass

class PharmaMetricORM(Base):
    __tablename__ = "pharma_metrics"

    ticker: Mapped[str] = mapped_column(String, primary_key=True)
    company: Mapped[str] = mapped_column(String, nullable=False)
    main_share_price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    currency: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    market_cap: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    week_52_price_change: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    extracted_at_utc: Mapped[datetime] = mapped_column(DateTime, nullable=False)

class DataBaseManager:
    def __init__(self, db_url = "sqlite:///pharma_pipeline.db"):
        self.engine = create_engine(db_url)
        self.session_local = sessionmaker(bind=self.engine)
        Base.metadata.create_all(self.engine)

    def save_or_update_metrics(self, records: list[PharmaMetricSchema]):
        if not records:
            return 0

        with self.session_local() as session:
            for record in records:
                data = record.model_dump()
                query = insert(PharmaMetricORM).values(**data)

                query = query.on_conflict_do_update(
                    index_elements=["ticker"],
                    set_= {
                        "company": query.excluded.company,
                        "main_share_price": query.excluded.main_share_price,
                        "currency": query.excluded.currency,
                        "market_cap": query.excluded.market_cap,
                        "week_52_price_change": query.excluded.week_52_price_change,
                        "extracted_at_utc": query.excluded.extracted_at_utc
                    }
                )
                session.execute(query)

            session.commit()
            return len(records)

    def print_all_metrics(self):
        df = read_sql_table("pharma_metrics", con=self.engine)
        print(df.to_string(index=False))