from typing import List, Optional, Dict, Any
from pydantic import BaseModel, validator
from enum import Enum, auto


class AutoStrEnum(str, Enum):
    @staticmethod
    def _generate_next_value_(
        name: str, start: int, count: int, last_values: list
    ) -> str:
        return name


class StmtType(AutoStrEnum):
    JIDENTITY = auto()
    JINVOKE = auto()
    JRETURNVOID = auto()
    JRETURN = auto()
    JASSIGN = auto()
    JGOTO = auto()
    JIF = auto()
    JTHROW = auto()
    JSWITCH = auto()
    JNOP = auto()
    UNDEF = auto()

    def __str__(self) -> str:
        return self.name


class ValueTokenType(AutoStrEnum):
    CONSTANT = auto()
    TYPE = auto()
    SYMBOL = auto()
    VARIABLE = auto()
    ATTRIBUTE = auto()
    UNDEF = auto()

    def __str__(self) -> str:
        return self.name


class ValueTokenModel(BaseModel):
    token_type: ValueTokenType
    token_value: Any


class ValueModel(BaseModel):
    value_type: str
    value_tokens: List[ValueTokenModel] = []


class ExprModel(BaseModel):
    expr_type: Optional[str] = None
    lhs: ValueModel
    rhs: Optional[ValueModel] = None


class BaseStmtModel(BaseModel):
    op: StmtType = StmtType.UNDEF
    falls_through: Optional[bool] = True
    has_branches: Optional[bool] = False
    block_index: int = -1


class JIdentityStmtModel(BaseStmtModel):
    op: StmtType = StmtType.JIDENTITY
    left: ValueModel
    right: ValueModel


class JInvokeStmtModel(BaseStmtModel):
    op: StmtType = StmtType.JINVOKE
    method_name: Optional[str] = None
    method_base: Optional[str] = None
    method_name_type: Optional[str] = None
    method_base_type: Optional[str] = None
    args: List[ValueModel] = []
    return_arg: Optional[ValueModel] = None


class JReturnVoidStmtModel(BaseStmtModel):
    op: StmtType = StmtType.JRETURNVOID


class JNopStmtModel(BaseStmtModel):
    op: StmtType = StmtType.JNOP


class JReturnStmtModel(BaseStmtModel):
    op: StmtType = StmtType.JRETURN
    arg: ValueModel


class JThrowStmtModel(BaseStmtModel):
    op: StmtType = StmtType.JTHROW
    arg: ValueModel


class JGotoStmtModel(BaseStmtModel):
    op: StmtType = StmtType.JGOTO
    targets: List[int] = []


class JSwitchStmtModel(BaseStmtModel):
    op: StmtType = StmtType.JSWITCH
    switch_index: ValueModel
    switch_cases: Optional[List[ValueModel]] = []
    switch_targets: Optional[List[int]] = []


class JIfStmtModel(BaseStmtModel):
    op: StmtType = StmtType.JIF
    src: ExprModel
    true_block_index: Optional[int] = None
    false_block_index: Optional[int] = None


class JAssignStmtModel(BaseStmtModel):
    op: StmtType = StmtType.JASSIGN
    left: ValueModel
    right: ExprModel


class VariableModel(BaseModel):
    var: ValueModel
    vartype: str


class MethodModel(BaseModel):
    name: str
    return_type: str
    is_public: bool
    is_private: bool
    is_static: bool
    is_protected: bool
    is_native: bool
    is_final: bool
    is_concrete: bool
    is_abstract: bool
    has_body: bool
    param_count: int = 0
    block_indices: List[int] = []
    block_successors: Dict[int, List[int]] = {}
    block_predecessors: Dict[int, List[int]] = {}
    instructions: List[Any] = []
    local_vars: List[VariableModel] = []
    param_vars: List[VariableModel] = []

    @validator("instructions", pre=True, always=True)
    def set_steps(cls, v):
        update_instructions = []
        for instruction in v:
            if not isinstance(instruction, dict):
                instruction = instruction.model_dump()
            if instruction["op"] == StmtType.JIDENTITY.value:
                update_instructions.append(JIdentityStmtModel(**instruction))
            elif instruction["op"] == StmtType.JINVOKE.value:
                update_instructions.append(JInvokeStmtModel(**instruction))
            elif instruction["op"] == StmtType.JRETURNVOID.value:
                update_instructions.append(JReturnVoidStmtModel(**instruction))
            elif instruction["op"] == StmtType.JRETURN.value:
                update_instructions.append(JReturnStmtModel(**instruction))
            elif instruction["op"] == StmtType.JASSIGN.value:
                update_instructions.append(JAssignStmtModel(**instruction))
            elif instruction["op"] == StmtType.JGOTO.value:
                update_instructions.append(JGotoStmtModel(**instruction))
            elif instruction["op"] == StmtType.JIF.value:
                update_instructions.append(JIfStmtModel(**instruction))
            elif instruction["op"] == StmtType.JTHROW.value:
                update_instructions.append(JThrowStmtModel(**instruction))
            elif instruction["op"] == StmtType.JSWITCH.value:
                update_instructions.append(JSwitchStmtModel(**instruction))
            elif instruction["op"] == StmtType.JNOP.value:
                update_instructions.append(JNopStmtModel(**instruction))
            else:
                raise Exception("Unknown operation type encountered in steps.")
        return update_instructions


class ClassPropertyModel(BaseModel):
    name: str
    type: str
    is_public: bool
    is_private: bool
    is_static: bool
    is_protected: bool
    is_final: bool


class JVMClassModel(BaseModel):
    filename: str
    name: str
    class_source: str
    is_public: bool
    is_private: bool
    is_static: bool
    is_concrete: bool
    is_abstract: bool
    is_annotation: bool
    is_interface: bool
    is_application_class: bool
    is_enum: bool
    is_final: bool
    is_inner_class: bool
    is_library_class: bool
    is_super: bool
    interfaces: List[str] = []
    class_props: List[ClassPropertyModel] = []
    outer_class: Optional[str] = None
    super_class: Optional[str] = None
    methods: List[MethodModel] = []
