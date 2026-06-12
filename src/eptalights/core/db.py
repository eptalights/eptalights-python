from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from sqlalchemy import String, DateTime, Boolean
from sqlalchemy.dialects.sqlite import TEXT as SQLITE_TEXT
from sqlalchemy import ForeignKey

from sqlalchemy import create_engine
from sqlalchemy import select, func
from sqlalchemy import Index
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from pydantic import UUID4
import msgpack
import dill
from datetime import datetime
import time
import uuid
import hashlib
import base64
from typing import Iterator

from eptalights import models

ITER_DATAFLOW_ACTIONS_PAGE_SIZE = 25


def generate_uuid():
    return str(uuid.uuid4())


def _hash_byte_str(data):
    hash_obj = hashlib.sha3_256(data)
    hash_hex = hash_obj.hexdigest()
    return hash_hex


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
    remote_action_id: Mapped[str] = mapped_column(
        String, unique=True, nullable=True, index=True
    )
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
        # self._db_session = Session(self._db_engine)
        self._db_session = sessionmaker(bind=self._db_engine)

        try:
            Base.metadata.create_all(self._db_engine)
        except Exception as e:
            print("Error occurred during Table creation!", e)
            print(e)

    def _scalar_count(self, table) -> int:
        """
        Example:
        def get_total_file_metadata(self) -> int:
            return self._scalar_count(FileMetadataTbl)
        """
        stmt = select(func.count()).select_from(table)
        with self._db_session() as session:
            return session.execute(stmt).scalar_one()

    def get_total_functions(self) -> int:
        stmt = select(func.count()).select_from(FunctionTbl)
        with self._db_session() as session:
            result = session.execute(stmt).scalar_one_or_none()
        return result or 0

    def get_total_callsites(self) -> int:
        stmt = select(func.count()).select_from(CallsiteTbl)
        with self._db_session() as session:
            result = session.execute(stmt).scalar_one()
        return result or 0

    def get_total_file_metadata(self) -> int:
        stmt = select(func.count()).select_from(FileMetadataTbl)
        with self._db_session() as session:
            result = session.execute(stmt).scalar_one()
        return result

    def get_function_by_id(self, fid: str) -> models.FunctionModel:
        with self._db_session() as session:
            result = session.execute(
                select(FunctionTbl).where(FunctionTbl.fid == fid)
            ).scalar_one_or_none()

            if result is None:
                raise ValueError(f"Function with id {fid} not found")

            data = msgpack.unpackb(result.function_data, strict_map_key=False)

        return models.FunctionModel(**data)

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

        with self._db_session() as session:
            result = session.execute(stmt).one_or_none()

            if result is None:
                raise ValueError("Callsite not found")

            analysis_data = msgpack.unpackb(result.function_data, strict_map_key=False)

        function_model = models.FunctionModel(**analysis_data)
        callsite = function_model.callsite_manager.callsites.get(result.call_ssa_name)
        return function_model, callsite

    def get_functions_by_filepath(
        self, filepath: str
    ) -> Iterator[models.FunctionModel]:

        stmt = select(FunctionTbl).where(FunctionTbl.filepath == filepath)

        with self._db_session() as session:
            results = session.scalars(stmt).all()

        for fn in results:
            analysis_data = msgpack.unpackb(fn.function_data, strict_map_key=False)
            yield models.FunctionModel(**analysis_data)

    def get_callsites_by_filepath(
        self, filepath: str
    ) -> Iterator[tuple[models.FunctionModel, models.CallsiteModel]]:

        stmt = (
            select(
                FunctionTbl.function_data.label("function_data"),
                CallsiteTbl.name.label("cs_name"),
                CallsiteTbl.ssa_name.label("call_ssa_name"),
            )
            .join(CallsiteTbl, FunctionTbl.fid == CallsiteTbl.fid)
            .where(CallsiteTbl.filepath == filepath)
        )

        with self._db_session() as session:
            results = session.execute(stmt).all()

        for result in results:
            analysis_data = msgpack.unpackb(result.function_data, strict_map_key=False)

            function_model = models.FunctionModel(**analysis_data)

            callsite = function_model.callsite_manager.callsites.get(
                result.call_ssa_name
            )

            yield function_model, callsite

    def search_functions(
        self,
        filter_by_name: str = None,
        filter_by_filepath: str = None,
        filter_by_classname: str = None,
    ) -> Iterator[models.FunctionModel]:

        stmt = select(FunctionTbl)

        if filter_by_name:
            stmt = stmt.where(FunctionTbl.name.like(f"%{filter_by_name}%"))
        if filter_by_filepath:
            stmt = stmt.where(FunctionTbl.filepath.like(f"%{filter_by_filepath}%"))
        if filter_by_classname:
            stmt = stmt.where(FunctionTbl.classname == filter_by_classname)

        with self._db_session() as session:
            results = session.scalars(stmt).all()

        for fn in results:
            analysis_data = msgpack.unpackb(fn.function_data, strict_map_key=False)
            yield models.FunctionModel(**analysis_data)

    def search_file_metadata(
        self,
        filter_by_filepath: str = None,
    ) -> Iterator[models.FileMetadataModel]:

        stmt = select(FileMetadataTbl)

        if filter_by_filepath:
            stmt = stmt.where(FileMetadataTbl.filepath.like(f"%{filter_by_filepath}%"))

        with self._db_session() as session:
            results = session.scalars(stmt).all()

        for fp in results:
            file_metadata_data_decoded = msgpack.unpackb(
                fp.file_metadata_data, strict_map_key=False
            )
            yield models.FileMetadataModel(**file_metadata_data_decoded)

    def search_callsites(
        self,
        filter_by_name: str = None,
        filter_by_filepath: str = None,
        filter_by_num_of_args: int = None,
    ) -> Iterator[tuple[models.FunctionModel, models.CallsiteModel]]:

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

        with self._db_session() as session:
            results = session.execute(stmt).all()

        for result in results:
            analysis_data = msgpack.unpackb(result.function_data, strict_map_key=False)

            function_model = models.FunctionModel(**analysis_data)

            callsite = function_model.callsite_manager.callsites.get(
                result.call_ssa_name
            )

            yield function_model, callsite

    def get_file_metadata_by_filepath(self, filepath: str) -> models.FileMetadataModel:

        stmt = select(FileMetadataTbl).where(FileMetadataTbl.filepath == filepath)

        with self._db_session() as session:
            result = session.execute(stmt).scalar_one_or_none()

            if result is None:
                raise ValueError("FileMetadata not found")

            file_metadata_data_decoded = msgpack.unpackb(
                result.file_metadata_data, strict_map_key=False
            )

        return models.FileMetadataModel(**file_metadata_data_decoded)

    def get_functions_by_ids(self, fids: list[str]) -> dict[str, models.FunctionModel]:
        stmt = select(FunctionTbl).where(FunctionTbl.fid.in_(fids))

        with self._db_session() as session:
            results = session.scalars(stmt).all()

        out = {}
        for fn in results:
            data = msgpack.unpackb(fn.function_data, strict_map_key=False)
            model = models.FunctionModel(**data)
            out[fn.fid] = model

        return out

    def get_file_data_by_metadata(
        self, file_metadata: models.FileMetadataModel
    ) -> models.FileDataModel:

        if not isinstance(file_metadata, models.FileMetadataModel):
            raise ValueError("file_metadata must be models.FileMetadataModel")

        file_data = models.FileDataModel(filepath=file_metadata.filepath)

        # collect ALL function IDs first
        all_fids = set(file_metadata.functions.keys())

        for class_meta in file_metadata.classes.values():
            all_fids.update(class_meta.class_methods.keys())

        # batch load once
        functions_map = self.get_functions_by_ids(list(all_fids))

        # assign functions
        for fid in file_metadata.functions.keys():
            file_data.functions[fid] = functions_map.get(fid)

        # assign classes
        for classname, class_meta in file_metadata.classes.items():
            class_data = models.ClassDataModel()
            class_data.class_props = class_meta.class_props

            for class_fid in class_meta.class_methods.keys():
                class_data.class_methods[class_fid] = functions_map.get(class_fid)

            file_data.classes[classname] = class_data

        return file_data

    def get_file_data_by_filepath(self, filepath: str) -> models.FileDataModel:
        file_metadata: models.FileMetadataModel = self.get_file_metadata_by_filepath(
            filepath
        )
        file_data: models.FileDataModel = self.get_file_data_by_metadata(file_metadata)
        return file_data

    def _encode_dataflow_action_request_to_b64(self, df_reqeust):
        request_bytes = dill.dumps(df_reqeust)
        request_b64 = base64.b64encode(request_bytes).decode("utf-8")
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
        request_hash = _hash_byte_str(request_bytes)

        df_response = models.DataflowResponseModel(status=True, paths=[])
        df_response_b64 = self._encode_dataflow_action_request_to_b64(df_response)

        with self._db_session() as session:
            try:
                df = DataflowActionTbl(
                    status=models.DataflowActionStatusType.LOCAL_PENDING.value,
                    dataflow_request_hash=request_hash,
                    dataflow_request_b64=df_request_b64,
                    dataflow_response_b64=df_response_b64,
                    delete_after_read=bool(delete_after_read),
                )

                session.add(df)
                session.commit()

                # ensure values are loaded after commit
                session.refresh(df)

                return models.DataflowActionModel(
                    action_id=df.action_id,
                    status=models.DataflowActionStatusType.LOCAL_PENDING,
                    request_hash=request_hash,
                    request=df_reqeust,
                    response=df_response,
                    remote_action_id=df.remote_action_id,
                    data_created=df.data_created_as_ts(),
                )

            except IntegrityError:
                session.rollback()
                raise

            except Exception:
                session.rollback()
                raise

    def delete_dataflow_action(self, action_id: UUID4 | str):
        stmt = select(DataflowActionTbl).where(
            DataflowActionTbl.action_id == str(action_id)
        )

        with self._db_session() as session:
            try:
                result = session.execute(stmt).scalar_one_or_none()
                if result is None:
                    raise ValueError("Dataflow Action not found")

                session.delete(result)
                session.commit()

            except Exception:
                session.rollback()
                raise

    def get_dataflow_action(self, action_id: UUID4 | str) -> models.DataflowActionModel:

        with self._db_session() as session:
            stmt = select(DataflowActionTbl).where(
                DataflowActionTbl.action_id == str(action_id)
            )
            result = session.execute(stmt).scalar_one_or_none()

            if result is None:
                raise ValueError("Dataflow Action not found")

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
                remote_action_id=result.remote_action_id,
                data_created=result.data_created_as_ts(),
            )

        # Delete after read outside the session context to avoid nested session issues
        if (
            result.status == models.DataflowActionStatusType.DONE.value
            and result.delete_after_read
        ):
            self.delete_dataflow_action(action_id)

        return df_action

    def iter_dataflow_actions(self, status: models.DataflowActionStatusType = None):
        PAGE_SIZE = 25

        def yield_actions(session):
            offset = 0
            while True:
                stmt = (
                    select(DataflowActionTbl)
                    .order_by(
                        DataflowActionTbl.data_created, DataflowActionTbl.action_id
                    )
                    .limit(PAGE_SIZE)
                    .offset(offset)
                )

                if status is not None:
                    stmt = stmt.where(DataflowActionTbl.status == status.value)

                rows = session.scalars(stmt).all()
                if not rows:
                    break

                for action in rows:
                    yield models.DataflowActionModel(
                        action_id=action.action_id,
                        request_hash=action.dataflow_request_hash,
                        status=models.DataflowActionStatusType(action.status),
                        request=self._decode_dataflow_action_request_from_b64(
                            action.dataflow_request_b64
                        ),
                        response=self._decode_dataflow_action_request_from_b64(
                            action.dataflow_response_b64
                        ),
                        remote_action_id=action.remote_action_id,
                        data_created=action.data_created_as_ts(),
                    )

                offset += PAGE_SIZE

        # Proper session scope
        with self._db_session() as session:
            yield from yield_actions(session)

    def update_dataflow_action_by_local_id(
        self,
        action_id: UUID4 | str,
        status: models.DataflowActionStatusType = None,
        response_b64: str = None,
        remote_action_id: str = None,
        delete_after_read: bool = None,
    ):
        with self._db_session() as session:
            stmt = select(DataflowActionTbl).where(
                DataflowActionTbl.action_id == str(action_id)
            )
            result = session.execute(stmt).scalar_one_or_none()
            if result is None:
                return  # nothing to update

            # Update fields safely
            if remote_action_id is not None:
                result.remote_action_id = remote_action_id

            if status is not None and isinstance(
                status, models.DataflowActionStatusType
            ):
                if result.status != models.DataflowActionStatusType.DONE.value:
                    result.status = status.value

            if response_b64 is not None:
                df_response = self._decode_dataflow_action_request_from_b64(
                    response_b64
                )
                if isinstance(df_response, models.DataflowResponseModel):
                    result.dataflow_response_b64 = response_b64

            if delete_after_read is not None and isinstance(delete_after_read, bool):
                result.delete_after_read = delete_after_read

            # Commit safely
            session.commit()

    def update_dataflow_action_by_remote_id(
        self,
        remote_action_id: UUID4 | str,
        status: models.DataflowActionStatusType = None,
        response_b64: str = None,
        delete_after_read: bool = None,
    ):
        with self._db_session() as session:
            stmt = select(DataflowActionTbl).where(
                DataflowActionTbl.remote_action_id == str(remote_action_id)
            )
            result = session.execute(stmt).scalar_one_or_none()
            if result is None:
                return  # nothing to update

            # Update status safely
            if status is not None and isinstance(
                status, models.DataflowActionStatusType
            ):
                if result.status != models.DataflowActionStatusType.DONE.value:
                    result.status = status.value

            # Update response if valid
            if response_b64 is not None:
                df_response = self._decode_dataflow_action_request_from_b64(
                    response_b64
                )
                if isinstance(df_response, models.DataflowResponseModel):
                    result.dataflow_response_b64 = response_b64

            # Update delete_after_read flag safely
            if delete_after_read is not None and isinstance(delete_after_read, bool):
                result.delete_after_read = delete_after_read

            # Commit all changes
            session.commit()
