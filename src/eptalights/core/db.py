from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from sqlalchemy import String
from sqlalchemy.dialects.sqlite import TEXT as SQLITE_TEXT
from sqlalchemy import ForeignKey

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy import select, func

import msgpack

from eptalights import models


class Base(DeclarativeBase):
    pass


class FunctionTbl(Base):
    __tablename__ = "functions"
    fid: Mapped[str] = mapped_column(String, primary_key=True, unique=True)
    name: Mapped[str] = mapped_column(String, index=True, nullable=False)
    classname: Mapped[str] = mapped_column(String, index=True, nullable=True)
    filepath: Mapped[str] = mapped_column(String, index=True, nullable=False)
    function_data: Mapped[str] = mapped_column(SQLITE_TEXT, nullable=True)


class CallsiteTbl(Base):
    __tablename__ = "callsites"
    cid: Mapped[str] = mapped_column(String, primary_key=True, unique=True)
    name: Mapped[str] = mapped_column(String, index=True, nullable=False)
    ssa_name: Mapped[str] = mapped_column(String, index=False, nullable=False)
    num_of_args: Mapped[int] = mapped_column(index=False, nullable=False, default=0)
    fid: Mapped[str] = mapped_column(ForeignKey("functions.fid"))
    filepath: Mapped[str] = mapped_column(String, index=True, nullable=True)


class FileMetadataTbl(Base):
    __tablename__ = "file_metadata"
    filepath: Mapped[str] = mapped_column(String, primary_key=True, unique=True)
    file_metadata_data: Mapped[str] = mapped_column(SQLITE_TEXT, nullable=True)


class DatabaseAPI:
    def __init__(self, dbpath: str = None):
        if dbpath is not None:
            self.db_init(dbpath)

    def db_init(self, dbpath: str):
        self._db_engine = create_engine(f"sqlite:///{dbpath}")
        self._db_session = Session(self._db_engine)

        try:
            Base.metadata.create_all(self._db_engine)
        except Exception as e:
            print("Error occurred during Table creation!", e)
            print(e)

    def get_total_functions(self) -> int:
        stmt = select(func.count()).select_from(FunctionTbl)
        result = self._db_session.execute(stmt).scalar()
        return result

    def get_total_callsites(self) -> int:
        stmt = select(func.count()).select_from(CallsiteTbl)
        result = self._db_session.execute(stmt).scalar()
        return result

    def get_total_file_metadata(self) -> int:
        stmt = select(func.count()).select_from(FileMetadataTbl)
        result = self._db_session.execute(stmt).scalar()
        return result

    def get_function_by_id(self, fid: str) -> models.FunctionModel:
        stmt = select(FunctionTbl).where(FunctionTbl.fid == fid)
        result1 = self._db_session.execute(stmt).scalar_one_or_none()
        if result1 is None:
            raise Exception("Function not found")

        analysis_data = msgpack.unpackb(result1.function_data, strict_map_key=False)
        analysis_model_decoded = models.FunctionModel(**analysis_data)
        return analysis_model_decoded

    def get_callsite_by_id(
        self, cid: str
    ) -> tuple[models.FunctionModel, models.CallsiteModel]:
        stmt = (
            select(
                FunctionTbl.function_data.label("function_data"),
                CallsiteTbl.name.label("call_name"),
                CallsiteTbl.ssa_name.label("call_ssa_name"),
            )
            .join(CallsiteTbl, FunctionTbl.fid == CallsiteTbl.fid)
            .where(CallsiteTbl.cid == cid)
        )

        result1 = self._db_session.execute(stmt).fetchone()
        if result1 is None:
            raise Exception("Callsite not found")

        analysis_data = msgpack.unpackb(result1.function_data, strict_map_key=False)

        analysis_model_decoded = models.FunctionModel(**analysis_data)
        return (
            analysis_model_decoded,
            analysis_model_decoded.callsite_manager.callsites.get(
                result1.call_ssa_name
            ),
        )

    def get_functions_by_filepath(self, filepath: str) -> list[models.FunctionModel]:
        stmt = select(FunctionTbl).where(FunctionTbl.filepath == filepath)
        for fn in self._db_session.scalars(stmt):
            analysis_data = msgpack.unpackb(fn.function_data, strict_map_key=False)
            am = models.FunctionModel(**analysis_data)
            yield am

    def get_callsites_by_filepath(
        self, filepath: str
    ) -> list[tuple[models.FunctionModel, models.CallsiteModel]]:
        stmt = (
            select(
                FunctionTbl.function_data.label("function_data"),
                CallsiteTbl.name.label("cs_name"),
                CallsiteTbl.ssa_name.label("call_ssa_name"),
            )
            .join(CallsiteTbl, FunctionTbl.fid == CallsiteTbl.fid)
            .where(CallsiteTbl.filepath == filepath)
        )

        for result in self._db_session.execute(stmt).all():
            analysis_data = msgpack.unpackb(result.function_data, strict_map_key=False)
            am = models.FunctionModel(**analysis_data)
            cs = am.callsite_manager.callsites.get(result.call_ssa_name)
            yield (am, cs)

    def search_functions(
        self,
        filter_by_name: str = None,
        filter_by_filepath: str = None,
        filter_by_classname: str = None,
    ) -> list[models.FunctionModel]:
        stmt = select(FunctionTbl)

        if filter_by_name:
            stmt = stmt.where(FunctionTbl.name.like(f"%{filter_by_name}%"))
        if filter_by_filepath:
            stmt = stmt.where(FunctionTbl.filepath.like(f"%{filter_by_filepath}%"))
        if filter_by_classname:
            stmt = stmt.where(FunctionTbl.classname == filter_by_classname)

        for fn in self._db_session.scalars(stmt):
            analysis_data = msgpack.unpackb(fn.function_data, strict_map_key=False)
            am = models.FunctionModel(**analysis_data)
            yield am

    def search_file_metadata(
        self,
        filter_by_filepath: str = None,
    ) -> list[models.FileMetadataModel]:
        stmt = select(FileMetadataTbl)

        if filter_by_filepath:
            stmt = stmt.where(FileMetadataTbl.filepath.like(f"%{filter_by_filepath}%"))

        for fp in self._db_session.scalars(stmt):
            file_metadata_data_decoded = msgpack.unpackb(
                fp.file_metadata_data, strict_map_key=False
            )
            fem = models.FileMetadataModel(**file_metadata_data_decoded)
            yield fem

    def search_callsites(
        self,
        filter_by_name: str = None,
        filter_by_filepath: str = None,
        filter_by_num_of_args: str = None,
    ) -> list[tuple[models.FunctionModel, models.CallsiteModel]]:
        stmt = select(
            FunctionTbl.function_data.label("function_data"),
            CallsiteTbl.ssa_name.label("call_ssa_name"),
        ).join(CallsiteTbl, FunctionTbl.fid == CallsiteTbl.fid)

        if filter_by_name:
            stmt = stmt.where(CallsiteTbl.name.like(f"%{filter_by_name}%"))
        if filter_by_filepath:
            stmt = stmt.where(FunctionTbl.filepath.like(f"%{filter_by_filepath}%"))
        if filter_by_num_of_args is not None:
            stmt = stmt.where(CallsiteTbl.num_of_args == filter_by_num_of_args)

        for result in self._db_session.execute(stmt).all():
            analysis_data = msgpack.unpackb(result.function_data, strict_map_key=False)
            am = models.FunctionModel(**analysis_data)
            cs = am.callsite_manager.callsites.get(result.call_ssa_name)
            yield am, cs

    def get_file_metadata_by_filepath(self, filepath: str) -> models.FileMetadataModel:
        stmt = select(FileMetadataTbl).where(FileMetadataTbl.filepath == filepath)

        result = self._db_session.execute(stmt).scalar_one_or_none()
        if result is None:
            raise Exception("FileMetadata not found")

        file_metadata_data_decoded = msgpack.unpackb(
            result.file_metadata_data, strict_map_key=False
        )

        fem = models.FileMetadataModel(**file_metadata_data_decoded)
        return fem

    def get_file_data_by_metadata(
        self, file_metadata: models.FileMetadataModel
    ) -> models.FileMetadataModel:
        if not isinstance(file_metadata, models.FileMetadataModel):
            raise Exception("file_metadata musst be models.FileMetadataModel type")

        file_data = models.FileDataModel(filepath=file_metadata.filepath)

        for fid in file_metadata.functions.keys():
            file_data.functions[fid] = self.get_function_by_id(fid)

        for classname in file_metadata.classes.keys():
            file_data.classes[classname] = models.ClassDataModel()
            file_data.classes[classname].class_props = file_metadata.classes[
                classname
            ].class_props

            for class_fid in file_metadata.classes[classname].class_methods.keys():
                file_data.classes[classname].class_methods[class_fid] = (
                    self.get_function_by_id(class_fid)
                )

        return file_data

    def get_file_data_by_filepath(self, filepath: str) -> models.FileDataModel:
        file_metadata: models.FileMetadataModel = self.get_file_metadata_by_filepath(
            filepath
        )
        file_data: models.FileDataModel = self.get_file_data_by_metadata(file_metadata)
        return file_data
