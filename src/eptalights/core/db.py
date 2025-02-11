from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from sqlalchemy import String
from sqlalchemy.dialects.sqlite import TEXT as SQLITE_TEXT
from sqlalchemy import ForeignKey

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy import select, update
import sqlalchemy

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


class VariableTbl(Base):
    __tablename__ = "variables"
    vid: Mapped[str] = mapped_column(String, primary_key=True, unique=True)
    name: Mapped[str] = mapped_column(String, index=True, nullable=False)
    full_declaration: Mapped[str] = mapped_column(String, index=True, nullable=True)
    is_local_var: Mapped[bool] = mapped_column(
        index=False, nullable=False, default=False
    )
    is_tmp: Mapped[bool] = mapped_column(index=False, nullable=False, default=False)
    is_farg: Mapped[bool] = mapped_column(index=False, nullable=False, default=False)
    fid: Mapped[str] = mapped_column(ForeignKey("functions.fid"))
    filepath: Mapped[str] = mapped_column(String, index=True, nullable=True)


class CallsiteTbl(Base):
    __tablename__ = "callsites"
    cid: Mapped[str] = mapped_column(String, primary_key=True, unique=True)
    name: Mapped[str] = mapped_column(String, index=True, nullable=False)
    ssa_name: Mapped[str] = mapped_column(String, index=False, nullable=False)
    num_of_args: Mapped[int] = mapped_column(index=False, nullable=False, default=0)
    fid: Mapped[str] = mapped_column(ForeignKey("functions.fid"))
    filepath: Mapped[str] = mapped_column(String, index=True, nullable=True)


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

    def get_variable_by_id(
        self, vid: str
    ) -> tuple[models.FunctionModel, models.VariableModel]:
        stmt = (
            select(
                FunctionTbl.function_data.label("function_data"),
                VariableTbl.name.label("var_name"),
            )
            .join(VariableTbl, FunctionTbl.fid == VariableTbl.fid)
            .where(VariableTbl.vid == vid)
        )

        result1 = self._db_session.execute(stmt).fetchone()
        if result1 is None:
            raise Exception("Variable not found")

        analysis_data = msgpack.unpackb(result1.function_data, strict_map_key=False)

        am = models.FunctionModel(**analysis_data)
        return am, am.variable_manager.variables.get(result1.var_name)

    def get_functions_by_filepath(self, filepath: str) -> list[models.FunctionModel]:
        stmt = select(FunctionTbl).where(FunctionTbl.filepath == filepath)
        for func in self._db_session.scalars(stmt):
            analysis_data = msgpack.unpackb(func.function_data, strict_map_key=False)
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

    def get_variables_by_filepath(
        self, filepath: str
    ) -> list[tuple[models.FunctionModel, models.VariableModel]]:
        stmt = (
            select(
                FunctionTbl.function_data.label("function_data"),
                VariableTbl.name.label("var_name"),
            )
            .join(VariableTbl, FunctionTbl.fid == VariableTbl.fid)
            .where(VariableTbl.filepath == filepath)
        )

        for result in self._db_session.execute(stmt).all():
            analysis_data = msgpack.unpackb(result.function_data, strict_map_key=False)
            am = models.FunctionModel(**analysis_data)
            vr = am.variable_manager.variables.get(result.var_name)
            yield (am, vr)

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

        for func in self._db_session.scalars(stmt):
            analysis_data = msgpack.unpackb(func.function_data, strict_map_key=False)
            am = models.FunctionModel(**analysis_data)
            yield am

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

    def search_variables(
        self,
        filter_by_name: str = None,
        filter_by_filepath: str = None,
        filter_by_type_decl: str = None,
        is_local_var: bool = None,
        is_tmp: bool = None,
        is_farg: bool = None,
    ) -> list[tuple[models.FunctionModel, models.VariableModel]]:
        stmt = select(
            FunctionTbl.function_data.label("function_data"),
            VariableTbl.name.label("var_name"),
        ).join(VariableTbl, FunctionTbl.fid == VariableTbl.fid)

        if filter_by_name:
            stmt = stmt.where(VariableTbl.name.like(f"%{filter_by_name}%"))
        if filter_by_filepath:
            stmt = stmt.where(FunctionTbl.filepath.like(f"%{filter_by_filepath}%"))
        if filter_by_type_decl:
            stmt = stmt.where(
                VariableTbl.full_declaration.like(f"%{filter_by_type_decl}%")
            )
        if is_local_var is not None:
            stmt = stmt.where(VariableTbl.is_local_var == is_local_var)
        if is_tmp is not None:
            stmt = stmt.where(VariableTbl.is_tmp == is_tmp)
        if is_farg is not None:
            stmt = stmt.where(VariableTbl.is_farg == is_farg)

        for result in self._db_session.execute(stmt).all():
            analysis_data = msgpack.unpackb(result.function_data, strict_map_key=False)
            am = models.FunctionModel(**analysis_data)
            vr = am.variable_manager.variables.get(result.var_name)
            yield am, vr

    def write_function(self, analysis_model: models.FunctionModel):
        """
        add some additional fid_index to handle function overloading uniqueness
        """
        fid_index = 1
        while True:
            stmt = select(FunctionTbl).where(
                FunctionTbl.fid == f"{analysis_model.fid}#{fid_index}"
            )
            result = self._db_session.execute(stmt).scalar_one_or_none()
            if result is not None:
                fid_index += 1
                continue

            analysis_model.fid = f"{analysis_model.fid}#{fid_index}"
            break

        # get varnames
        var_rows = []
        for varname, var in analysis_model.variable_manager.variables.items():
            """
            if there its not the first function, update all vars vids
            """
            var.vid = f"{analysis_model.fid}:{varname}"
            analysis_model.variable_manager.variables[varname] = var

            is_tmp = False
            is_local_var = False
            is_farg = False

            if varname in analysis_model.variable_manager.function_args:
                is_farg = True

            if varname in analysis_model.variable_manager.local_variables:
                is_local_var = True

            if varname in analysis_model.variable_manager.tmp_variables:
                is_tmp = True

            v = VariableTbl(
                vid=var.vid,
                name=var.name,
                full_declaration=var.full_declaration,
                is_local_var=is_local_var,
                is_farg=is_farg,
                is_tmp=is_tmp,
                fid=analysis_model.fid,
                filepath=analysis_model.filepath,
            )
            var_rows.append(v)

        # get callsites
        cs_rows = []
        for cs_ssa_name, cs in analysis_model.callsite_manager.callsites.items():
            cid = f"{analysis_model.fid}:{cs_ssa_name}"
            analysis_model.callsite_manager.callsites[cs_ssa_name].cid = cid

            c = CallsiteTbl(
                cid=cid,
                name=cs.name,
                ssa_name=cs_ssa_name,
                num_of_args=cs.num_of_args,
                fid=analysis_model.fid,
                filepath=analysis_model.filepath,
            )
            cs_rows.append(c)

        analysis_model_encoded = msgpack.packb(
            analysis_model.model_dump(), use_bin_type=True
        )

        with self._db_session:
            try:
                fn = FunctionTbl(
                    fid=analysis_model.fid,
                    filepath=analysis_model.filepath,
                    name=analysis_model.name,
                    function_data=analysis_model_encoded,
                )

                self._db_session.add_all([fn])

                if var_rows:
                    self._db_session.add_all(var_rows)

                if cs_rows:
                    self._db_session.add_all(cs_rows)

                self._db_session.commit()
            except sqlalchemy.exc.IntegrityError:
                pass
            except Exception as e:
                raise e

    def build_function_call_graph(self):
        function_not_available_in_db = []
        stmt1 = select(FunctionTbl)

        for func in self._db_session.scalars(stmt1):

            analysis_data = msgpack.unpackb(func.function_data, strict_map_key=False)
            am = models.FunctionModel(**analysis_data)

            print(f"Generating function graph for {am.name} --- {am.filepath}")

            for callsite_fname in am.callsite_manager.callsites.keys():
                callsite_rows = []

                if callsite_fname not in function_not_available_in_db:
                    stmt2 = select(FunctionTbl).where(
                        FunctionTbl.name == callsite_fname
                    )
                    callsite_rows = list(self._db_session.scalars(stmt2))

                if not callsite_rows:
                    if callsite_fname not in function_not_available_in_db:
                        function_not_available_in_db.append(callsite_fname)

                    if not am.fgraph.next_nodes.get(callsite_fname, None):
                        am.fgraph.next_nodes[callsite_fname] = []

                    am.fgraph.next_nodes[callsite_fname].append(
                        models.FunctionGraphNodeReference(
                            fid=None, name=callsite_fname, filepath=None
                        )
                    )
                    am_encoded = msgpack.packb(am.model_dump(), use_bin_type=True)

                    stmt3 = (
                        update(FunctionTbl)
                        .where(FunctionTbl.fid == am.fid)
                        .values(function_data=am_encoded)
                    )
                    self._db_session.execute(stmt3)
                    self._db_session.commit()

                for callsite_row in callsite_rows:
                    callsite_analysis_data = msgpack.unpackb(
                        callsite_row.function_data, strict_map_key=False
                    )
                    callsite_am = models.FunctionModel(**callsite_analysis_data)

                    if not callsite_am.fgraph.prev_nodes.get(am.name, None):
                        callsite_am.fgraph.prev_nodes[am.name] = []

                    if am.fid not in callsite_am.fgraph.prev_nodes_fids:
                        callsite_am.fgraph.prev_nodes[am.name].append(
                            models.FunctionGraphNodeReference(
                                fid=am.fid,
                                name=am.name,
                                filepath=am.filepath,
                            )
                        )
                        callsite_am.fgraph.prev_nodes_fids.append(am.fid)
                        callsite_am_encoded = msgpack.packb(
                            callsite_am.model_dump(), use_bin_type=True
                        )

                        stmt3 = (
                            update(FunctionTbl)
                            .where(FunctionTbl.fid == callsite_am.fid)
                            .values(function_data=callsite_am_encoded)
                        )
                        self._db_session.execute(stmt3)
                        self._db_session.commit()

                    if not am.fgraph.next_nodes.get(callsite_fname, None):
                        am.fgraph.next_nodes[callsite_fname] = []

                    if callsite_am.fid not in am.fgraph.next_nodes_fids:
                        am.fgraph.next_nodes[callsite_fname].append(
                            models.FunctionGraphNodeReference(
                                fid=callsite_am.fid,
                                name=callsite_am.name,
                                filepath=callsite_am.filepath,
                            )
                        )
                        am.fgraph.next_nodes_fids.append(callsite_am.fid)
                        am_encoded = msgpack.packb(am.model_dump(), use_bin_type=True)

                        stmt3 = (
                            update(FunctionTbl)
                            .where(FunctionTbl.fid == am.fid)
                            .values(function_data=am_encoded)
                        )
                        self._db_session.execute(stmt3)
                        self._db_session.commit()
