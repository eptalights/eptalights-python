from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from sqlalchemy import String, DateTime, Boolean
from sqlalchemy.dialects.sqlite import TEXT as SQLITE_TEXT
from sqlalchemy import ForeignKey

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from sqlalchemy import Index
from sqlalchemy.exc import IntegrityError

from pydantic import UUID4
import msgpack
import dill
from datetime import datetime
import time
import uuid
import xxhash
import base64

from eptalights_code import models

ITER_DATAFLOW_ACTIONS_PAGE_SIZE = 25


def generate_uuid():
    return str(uuid.uuid4())


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


class DataflowActionTbl(Base):
    __tablename__ = "dataflow_actions"
    _table_args__ = (
        Index("action_id_date_created_index", "date_created", "action_id"),
        Index(
            "action_id_date_created_status_index", "date_created", "action_id", "status"
        ),
    )

    action_id: Mapped[str] = mapped_column(
        String, primary_key=True, default=generate_uuid
    )
    status: Mapped[str] = mapped_column(String, unique=False, nullable=False)
    dataflow_request_hash: Mapped[str] = mapped_column(
        String, index=True, nullable=True
    )
    dataflow_request_b64: Mapped[str] = mapped_column(SQLITE_TEXT, nullable=False)
    dataflow_response_b64: Mapped[str] = mapped_column(SQLITE_TEXT, nullable=True)
    delete_after_read: Mapped[bool] = mapped_column(Boolean, nullable=True)
    data_created: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    def data_created_as_ts(self):
        return str(time.mktime(self.data_created.timetuple()))


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

    def _encode_dataflow_action_request_to_b64(self, df_reqeust):
        request_bytes = dill.dumps(df_reqeust)
        request_b64 = base64.b64encode(request_bytes).decode()
        return request_b64

    def _decode_dataflow_action_request_from_b64(self, df_reqeust_64):
        df_reqeust_b64 = base64.b64decode(df_reqeust_64)
        df_reqeust = dill.loads(df_reqeust_b64)
        return df_reqeust

    def create_dataflow_action(
        self,
        df_reqeust: models.DataflowRequestModel,
        delete_after_read: bool = False,
    ) -> models.DataflowActionModel:
        df_request_b64 = self._encode_dataflow_action_request_to_b64(df_reqeust)
        request_bytes = base64.b64decode(df_request_b64)
        request_hash = xxhash.xxh64(request_bytes).hexdigest()

        df_response = models.DataflowResponseModel(status=True, paths=[])
        df_response_b64 = self._encode_dataflow_action_request_to_b64(df_response)

        with self._db_session:
            try:
                df = DataflowActionTbl(
                    status=models.DataflowActionStatusType.LOCAL_PENDING.value,
                    dataflow_request_hash=request_hash,
                    dataflow_request_b64=df_request_b64,
                    dataflow_response_b64=df_response_b64,
                    delete_after_read=(
                        delete_after_read
                        if isinstance(delete_after_read, bool)
                        else False
                    ),
                )

                self._db_session.add_all([df])
                self._db_session.commit()

                df_action = models.DataflowActionModel(
                    action_id=df.action_id,
                    status=models.DataflowActionStatusType.LOCAL_PENDING,
                    request_hash=request_hash,
                    request=df_reqeust,
                    response=df_response,
                    data_created=df.data_created_as_ts(),
                )
                return df_action
            except IntegrityError:
                pass
            except Exception as e:
                raise e

    def delete_dataflow_action(self, action_id: UUID4 | str):
        stmt = select(DataflowActionTbl).where(
            DataflowActionTbl.action_id == str(action_id)
        )
        result = self._db_session.execute(stmt).scalar_one_or_none()
        if result is None:
            raise Exception("Dataflow Action not found")

        self._db_session.delete(result)
        self._db_session.commit()

    def get_dataflow_action(self, action_id: UUID4 | str) -> models.DataflowActionModel:
        stmt = select(DataflowActionTbl).where(
            DataflowActionTbl.action_id == str(action_id)
        )
        result = self._db_session.execute(stmt).scalar_one_or_none()
        if result is None:
            raise Exception("Dataflow Action not found")

        df_action = models.DataflowActionModel(
            action_id=result.action_id,
            request_hash=result.dataflow_request_hash,
            status=models.DataflowActionStatusType(result.status),
            request=self._decode_dataflow_action_request_from_b64(
                result.dataflow_request_b64
            ),
            response=self._decode_dataflow_action_request_from_b64(
                result.dataflow_response_b64
            ),
            data_created=result.data_created_as_ts(),
        )

        if (
            result.status == models.DataflowActionStatusType.DONE.value
            and result.delete_after_read
        ):
            self.delete_dataflow_action(action_id)

        return df_action

    def iter_dataflow_actions(
        self,
        status: models.DataflowActionStatusType = None,
    ) -> list[models.DataflowActionModel]:

        ITER_DATAFLOW_ACTIONS_PAGE_SIZE = 25

        def yield_actions():
            offset = 0
            while True:
                stmt = (
                    select(DataflowActionTbl)
                    .order_by(
                        DataflowActionTbl.data_created, DataflowActionTbl.action_id
                    )
                    .limit(ITER_DATAFLOW_ACTIONS_PAGE_SIZE)
                    .offset(offset)
                )

                if status is not None and isinstance(
                    status, models.DataflowActionStatusType
                ):
                    stmt = stmt.where(DataflowActionTbl.status == status.value)

                rows = self._db_session.scalars(stmt).all()
                if not rows:
                    break

                for row in rows:
                    yield row

                offset += ITER_DATAFLOW_ACTIONS_PAGE_SIZE

        with self._db_session:
            for action in yield_actions():
                df_action = models.DataflowActionModel(
                    action_id=action.action_id,
                    request_hash=action.dataflow_request_hash,
                    status=models.DataflowActionStatusType(action.status),
                    request=self._decode_dataflow_action_request_from_b64(
                        action.dataflow_request_b64
                    ),
                    response=self._decode_dataflow_action_request_from_b64(
                        action.dataflow_response_b64
                    ),
                    data_created=action.data_created_as_ts(),
                )
                yield df_action

    def update_dataflow_action(
        self,
        action_id: UUID4 | str,
        status: models.DataflowActionStatusType = None,
        response_b64: str = None,
        delete_after_read: bool = None,
    ):
        with self._db_session:
            stmt = select(DataflowActionTbl).where(
                DataflowActionTbl.action_id == str(action_id)
            )
            result = self._db_session.execute(stmt).scalar_one_or_none()
            if result is None:
                return

            if status is not None and isinstance(
                status, models.DataflowActionStatusType
            ):
                if result.status != "DONE":
                    result.status = status.value

            if response_b64 is not None:
                df_response = self._decode_dataflow_action_request_from_b64(
                    response_b64
                )
                if isinstance(df_response, models.DataflowResponseModel):
                    result.dataflow_response_b64 = response_b64

            if delete_after_read is not None and isinstance(delete_after_read, bool):
                result.delete_after_read = delete_after_read

            self._db_session.commit()
