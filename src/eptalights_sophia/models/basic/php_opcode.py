from pydantic import BaseModel
from typing import List, Optional


class SSAPhiConstraintModel(BaseModel):
    range_range_min: Optional[int] = 0
    range_range_max: Optional[int] = 0
    range_range_underflow: Optional[int] = 0
    range_range_overflow: Optional[int] = 0
    range_min_var: Optional[int] = 0
    range_max_var: Optional[int] = 0
    range_min_ssa_var: Optional[int] = 0
    range_max_ssa_var: Optional[int] = 0


class SSADefinitionPhiModel(BaseModel):
    pi: Optional[int]
    variable_index: Optional[int]
    var_num: Optional[int]
    var_name: Optional[str]
    ssa_variable_index: Optional[int]
    current_block_index: Optional[int]
    has_range_constraint: Optional[bool]
    has_constraint: Optional[bool]
    constraint: Optional[SSAPhiConstraintModel]
    sources: Optional[List[int]]


class SSABlockModel(BaseModel):
    block_index: int
    definition_phis: List[SSADefinitionPhiModel]


class SSABlocksModel(BaseModel):
    blocks_count: int
    blocks: List[SSABlockModel]


class SSAInstructionModel(BaseModel):
    op1_use: Optional[int] = 0
    op2_use: Optional[int] = 0
    result_use: Optional[int] = 0
    op1_def: Optional[int] = 0
    op2_def: Optional[int] = 0
    result_def: Optional[int] = 0
    op1_use_chain: Optional[int] = 0
    op2_use_chain: Optional[int] = 0
    res_use_chain: Optional[int] = 0


class SSAInstructionsModel(BaseModel):
    instructions_count: int
    instructions: List[SSAInstructionModel]


class SSAVariableModel(BaseModel):
    strongly_connected_component: int
    strongly_connected_component_entry: bool
    ssa_var_num: int
    definition: int
    no_val: int
    use_chain: int
    escape_state: int
    var_num: int
    var_name: str
    has_definition_phi: bool
    definition_phi: SSADefinitionPhiModel


class SSAVariablesModel(BaseModel):
    variables_count: int
    variables: List[SSAVariableModel]


class ClassPropValueModel(BaseModel):
    type: str
    value: str


class ClassConstantModel(BaseModel):
    prop_name: str
    prop_value: ClassPropValueModel


class ClassPropertyModel(BaseModel):
    prop_is_static: bool
    prop_visibility: str
    prop_name: str
    prop_value: ClassPropValueModel


class ClassAdditionInfoModel(BaseModel):
    constants_table: List[ClassConstantModel] = []
    properties_table: List[ClassPropertyModel] = []


class SSAModel(BaseModel):
    number_of_sccs: int
    number_of_ssa_variables: int
    ssa_variables: SSAVariablesModel
    ssa_instructions: SSAInstructionsModel
    ssa_blocks: SSABlocksModel


class VarSetVariableModel(BaseModel):
    var_num: int
    var_name: str


class VarSetModel(BaseModel):
    total_variables: int
    variables: List[VarSetVariableModel]


class DFGBlockModel(BaseModel):
    block_index: int
    var_def: VarSetModel
    var_in: VarSetModel
    var_out: VarSetModel
    var_tmp: VarSetModel
    var_use: VarSetModel


class DFGModel(BaseModel):
    blocks: List[DFGBlockModel]


class CFGBlockModel(BaseModel):
    first_opcode_number: int
    number_of_opcodes: int
    number_of_successors: int
    number_of_predecessors: int
    offset_of_first_predecessor: int
    immediate_dominator_block: int
    closest_loop_header: int
    steps_away_from_the_entry_in_the_dom_tree: int
    list_of_dominated_blocks: int
    next_dominated_block: int
    successor_blocks: List[int]
    successor_block_indices: List[int]


class CFGModel(BaseModel):
    blocks_count: int
    edges_count: int
    blocks: List[CFGBlockModel]
    predecessors: List[int]


class OperandModel(BaseModel):
    variable_number: int
    type: str
    value: str
    const_type: str


class InstructionModel(BaseModel):
    num: int
    has_op2: bool
    op1: Optional[OperandModel]
    op2: Optional[OperandModel]
    result: Optional[OperandModel]
    extended_value: int
    lineno: int
    value: int
    opcode_name: str
    opcode: int
    opcode_flags: int
    op1_type: int
    op2_type: int
    result_type: int
    source_line: str


class LiteralModel(BaseModel):
    type: str
    value: str


class BasicOpcodeFunctionModel(BaseModel):
    filepath: str
    filename: str
    class_name: str
    function_name: str

    num_args: int
    required_num_args: int
    number_of_instructions: int
    op_filename: str

    type: int
    cache_size: int
    number_of_cv_variables: int
    number_of_tmp_variables: int
    last_live_range: int
    last_try_catch: int
    arg_flags: List[int]
    last_literal: int
    literals: List[LiteralModel]

    instructions: List[InstructionModel]
    cfg: CFGModel
    dfg: DFGModel
    ssa: SSAModel
    class_addition_info: ClassAdditionInfoModel
