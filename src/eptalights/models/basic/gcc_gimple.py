# from __future__ import annotations
from pydantic import BaseModel, validator
from typing import List, Optional, Any, Union, Dict
from enum import Enum, auto


class VarType(str, Enum):
    PARAM_VAR = auto()
    LOCAL_VAR = auto()
    GLOBAL_VAR = auto()
    TMP_VAR = auto()
    DECL_VAR = auto()
    COMPLEX_DECL_VAR = auto()
    UNF_VAR = auto()


class GimpleDataValueModel(BaseModel):
    code_class: str
    code_name: str
    value_type: str
    value: Union[List["GimpleDataValueModel"], str]


class GimpleTreeValueModel(BaseModel):
    values: Optional[List[GimpleDataValueModel]] = []


class GimpleFunctionArgModel(BaseModel):
    arg: Optional[GimpleTreeValueModel] = None
    var_type: Optional[GimpleTreeValueModel] = None
    var_def: Optional[GimpleTreeValueModel] = None
    var_ssa_name_var: Optional[GimpleTreeValueModel] = None
    var_declaration: Optional[GimpleTreeValueModel] = None


class GimpleFunctionLocalVariableModel(BaseModel):
    arg: Optional[GimpleTreeValueModel] = None
    var_declaration: Optional[GimpleTreeValueModel] = None


class GimpleFunctionLocalSSAVariableModel(BaseModel):
    arg: Optional[GimpleTreeValueModel] = None
    var_type: Optional[GimpleTreeValueModel] = None


class GimpleFunctionInfoModel(BaseModel):
    fn_filename: str
    fn_name: str
    fn_start_line_no: int
    fn_end_line_no: int
    fn_source_lines: Optional[Dict[str, str]] = {}
    fn_args: Optional[List[GimpleFunctionArgModel]] = []
    fn_local_variables: Optional[List[GimpleFunctionLocalVariableModel]] = []
    fn_ssa_variables: Optional[List[GimpleFunctionLocalSSAVariableModel]] = []
    fn_ssa_names: Optional[List[GimpleTreeValueModel]] = []
    fn_decl: Optional[GimpleTreeValueModel] = None


class GimpleRHSPhiModel(BaseModel):
    basic_block_src_index: int
    column: int
    line: int
    phi_rhs: Optional[GimpleTreeValueModel] = None


class GimpleBasicBlockPhiModel(BaseModel):
    phi_lhs: GimpleTreeValueModel
    gimple_phi_rhs_list: Optional[List[GimpleRHSPhiModel]] = []


class GimpleBasicBlockModel(BaseModel):
    bb_index: int
    bb_edges: Optional[List[int]] = []
    phis: List[GimpleBasicBlockPhiModel]


class GimpleAssignModel(BaseModel):
    gassign_has_rhs_arg1: bool
    gassign_has_rhs_arg2: bool
    gassign_has_rhs_arg3: bool
    gassign_lhs_arg: Optional[GimpleTreeValueModel] = None
    gassign_rhs_arg1: Optional[GimpleTreeValueModel] = None
    gassign_rhs_arg2: Optional[GimpleTreeValueModel] = None
    gassign_rhs_arg3: Optional[GimpleTreeValueModel] = None
    gassign_subcode: str


class GimpleCallModel(BaseModel):
    gcall_args: Optional[List[GimpleTreeValueModel]] = []
    gcall_call_num_of_args: int
    gcall_fn: Optional[GimpleTreeValueModel] = None
    gcall_has_lhs: bool
    gcall_lhs_arg: Optional[GimpleTreeValueModel] = None


class GimpleCondModel(BaseModel):
    gcond_has_true_goto_label: bool
    gcond_has_false_else_goto_label: bool
    gcond_rhs: GimpleTreeValueModel
    gcond_lhs: GimpleTreeValueModel
    gcond_true_goto_label: Optional[GimpleTreeValueModel] = None
    gcond_false_else_goto_label: Optional[GimpleTreeValueModel] = None
    gcond_tree_code_name: str
    gcond_has_goto_true_edge: bool
    gcond_has_else_goto_false_edge: bool
    goto_true_edge: int
    else_goto_false_edge: int


class GimpleLabelModel(BaseModel):
    glabel_is_non_local: bool
    glabel_label: Optional[GimpleTreeValueModel] = None


class GimpleGotoModel(BaseModel):
    ggoto_dest_goto_label: Optional[GimpleTreeValueModel] = None


class GimpleNopModel(BaseModel):
    gnop_nop_str: Optional[str] = None


class GimpleReturnModel(BaseModel):
    greturn_has_greturn_return_value: bool
    greturn_return_value: Optional[GimpleTreeValueModel] = None


class GimpleSwitchModel(BaseModel):
    gswitch_switch_index: Optional[GimpleTreeValueModel] = None
    gswitch_switch_case_labels: Optional[List[GimpleTreeValueModel]] = []
    gswitch_switch_labels: Optional[List[GimpleTreeValueModel]] = []


class GimpleTryModel(BaseModel):
    gtry_try_type_kind: str
    gtry_has_try_cleanup: bool
    gtry_try_cleanup: Any
    gtry_try_eval: Any


class GimplePhiModel(BaseModel):
    gphi_lhs: Optional[GimpleTreeValueModel] = None
    gphi_phi_args: Optional[List[GimpleTreeValueModel]] = []
    gphi_phi_args_basicblock_src_index: Optional[List[int]] = []
    gphi_phi_args_locations: Optional[List[str]] = []


class GimpleAsmModel(BaseModel):
    gasm_string_code: str
    gasm_input_operands: Optional[List[GimpleTreeValueModel]] = []
    gasm_output_operands: Optional[List[GimpleTreeValueModel]] = []
    gasm_clobber_operands: Optional[List[GimpleTreeValueModel]] = []
    gasm_labels: Optional[List[GimpleTreeValueModel]] = []
    gasm_volatile: bool
    gasm_inline: bool


class GimpleBindModel(BaseModel):
    gbind_bind_vars: str
    gbind_bind_body: Any


class GimpleBlockModel(BaseModel):
    basic_block_edges: Optional[List[int]] = []
    basic_block_index: int
    gimple_code: str
    gimple_expr_code: str
    lineno: int
    args: Any

    @validator("args")
    def decode_args(cls, v, values):
        if values["gimple_code"] == "gimple_assign":
            return GimpleAssignModel(**v)

        if values["gimple_code"] == "gimple_call":
            return GimpleCallModel(**v)

        if values["gimple_code"] == "gimple_cond":
            return GimpleCondModel(**v)

        if values["gimple_code"] == "gimple_label":
            return GimpleLabelModel(**v)

        if values["gimple_code"] == "gimple_goto":
            return GimpleGotoModel(**v)

        if values["gimple_code"] == "gimple_nop":
            return GimpleNopModel(**v)

        if values["gimple_code"] == "gimple_return":
            return GimpleReturnModel(**v)

        if values["gimple_code"] == "gimple_switch":
            return GimpleSwitchModel(**v)

        if values["gimple_code"] == "gimple_try":
            return GimpleTryModel(**v)

        if values["gimple_code"] == "gimple_phi":
            return GimplePhiModel(**v)

        if values["gimple_code"] == "gimple_asm":
            return GimpleAsmModel(**v)

        if values["gimple_code"] == "gimple_bind":
            return GimpleBindModel(**v)

        return v


class BasicGimpleFunctionModel(BaseModel):
    function_info: GimpleFunctionInfoModel
    basicblocks: Optional[List[GimpleBasicBlockModel]] = []
    gimples: Optional[List[GimpleBlockModel]] = []


GimpleDataValueModel.model_rebuild()
