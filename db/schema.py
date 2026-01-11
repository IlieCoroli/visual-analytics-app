from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, DateTime, Text, ForeignKey
from datetime import datetime

class Base(DeclarativeBase):
    pass

class Dataset(Base):
    __tablename__ = "datasets"
    dataset_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255))
    source_type: Mapped[str] = mapped_column(String(50))
    source_reference: Mapped[str] = mapped_column(String(500), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    row_count: Mapped[int] = mapped_column(Integer)
    column_count: Mapped[int] = mapped_column(Integer)
    snapshot_path: Mapped[str] = mapped_column(String(800), default="")

    profiles: Mapped[list["ColumnProfile"]] = relationship(back_populates="dataset", cascade="all, delete-orphan")
    logs: Mapped[list["TransformationLog"]] = relationship(back_populates="dataset", cascade="all, delete-orphan")

class ColumnProfile(Base):
    __tablename__ = "column_profiles"
    profile_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    dataset_id: Mapped[int] = mapped_column(ForeignKey("datasets.dataset_id"), index=True)
    column_name: Mapped[str] = mapped_column(String(255))
    dtype: Mapped[str] = mapped_column(String(80))
    missing_count: Mapped[int] = mapped_column(Integer)
    unique_count: Mapped[int] = mapped_column(Integer)
    summary_json: Mapped[str] = mapped_column(Text, default="{}")

    dataset: Mapped["Dataset"] = relationship(back_populates="profiles")

class TransformationLog(Base):
    __tablename__ = "transformation_logs"
    log_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    dataset_id: Mapped[int] = mapped_column(ForeignKey("datasets.dataset_id"), index=True)
    operation: Mapped[str] = mapped_column(String(120))
    parameters_json: Mapped[str] = mapped_column(Text, default="{}")
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    dataset: Mapped["Dataset"] = relationship(back_populates="logs")
