from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from eptalights.models.egimple.enum_types import VarType
from eptalights.models.egimple.tokenized_operand import TokenizedOperandModel


class SSAVariableModel(BaseModel):
    """Represents an SSA (Static Single Assignment) variable in program analysis.

    Attributes
    ----------
    ssa_name : str, optional
        The SSA name of the variable, if available. Defaults to None.
    ssa_version : int, optional
        The SSA version of the variable. Defaults to 0.
    variable_name : str, optional
        The original variable name before SSA transformation. Defaults to None.
    variable_defined_at_steps : list of int, optional
        A list of step indices where the variable is defined. Defaults to an empty list.
    variable_used_at_steps : list of int, optional
        A list of step indices where the variable is used. Defaults to an empty list.
    variable_used_in_callsites : list of str, optional
        A list of function call sites where this variable is used.
        Defaults to an empty list.
    record_attributes_defined_at_steps : dict of {int: list of str}, optional
        A mapping of step indices to lists of record attributes defined at each step.
        Defaults to an empty dictionary.
    record_attributes_used_at_steps : dict of {int: list of str}, optional
        A mapping of step indices to lists of record attributes used at each step.
        Defaults to an empty dictionary.
    used_inside_other_tokenized_operand_tokens_at_step :
        dict of {int: list of str}, optional
        A mapping of step indices to lists of tokenized operand tokens in which this
        variable is used. Defaults to an empty dictionary.
    tokenized_operands_defs_at_steps :
        dict of {int: list of TokenizedOperandModel}, optional
        A mapping of step indices to lists of tokenized operand definitions associated
        with this variable. Defaults to an empty dictionary.
    tokenized_operands_uses_at_steps :
        dict of {int: list of TokenizedOperandModel}, optional
        A mapping of step indices to lists of tokenized operand uses associated with
        this variable. Defaults to an empty dictionary.
    """

    ssa_name: Optional[str] = None
    ssa_version: int = 0
    variable_name: Optional[str] = None

    variable_defined_at_steps: list[int] = []
    variable_used_at_steps: list[int] = []
    variable_used_in_callsites: list[str] = []

    record_attributes_defined_at_steps: Dict[int, List[str]] = {}
    record_attributes_used_at_steps: Dict[int, List[str]] = {}

    used_inside_other_tokenized_operand_tokens_at_step: Optional[
        Dict[int, List[str]]
    ] = {}

    tokenized_operands_defs_at_steps: Dict[int, List[TokenizedOperandModel]] = {}
    tokenized_operands_uses_at_steps: Dict[int, List[TokenizedOperandModel]] = {}


class VariableModel(BaseModel):
    """Represents a variable in program analysis, including SSA details.

    Attributes
    ----------
    vid : str, optional
        A unique identifier for the variable in the format
        ``filename:function_name:variable_name``. Defaults to None.
    name : str
        The name of the variable.
    vartype : VarType, optional
        The type of the variable, defaulting to `VarType.UNDEF`.
    unique_ssa_variables : dict[str, SSAVariableModel], optional
        A mapping of SSA variable names to their corresponding
        `SSAVariableModel` instances. Defaults to an empty dictionary.
    full_declaration : str, optional
        The full declaration of the variable, if available.
    type_declaration : str, optional
        The type declaration of the variable, if available.
    type_props : list[str], optional
        A list of additional type properties. Defaults to an empty list.
    tokenized_type_declaration : TokenizedOperandModel, optional
        A tokenized representation of the variable's type declaration.
    additional_info : dict[str, Any], optional
        Additional metadata about the variable.
    phi_ssa_variables : dict[str, list[str]], optional
        A mapping of SSA variable names to lists of SSA versions used in phi functions.
        Defaults to an empty dictionary.
    """

    vid: Optional[str] = None  # filename:function_name:variable_name
    name: str
    vartype: VarType = VarType.UNDEF
    unique_ssa_variables: Dict[str, SSAVariableModel] = {}

    full_declaration: Optional[str] = None
    type_declaration: Optional[str] = None
    type_props: Optional[List[str]] = []
    tokenized_type_declaration: Optional[TokenizedOperandModel] = None
    additional_info: Dict[str, Any] = {}

    phi_ssa_variables: Dict[str, List[str]] = {}

    @property
    def used_at_steps(self) -> List[int]:
        """Get the unique execution steps where the variable is used.

        Returns
        -------
        list[int]
            A list of unique step indices where this variable is used.
        """
        steps = []
        for _, ssa_var in self.unique_ssa_variables.items():
            steps += ssa_var.variable_used_at_steps
        return list(set(steps))

    @property
    def defined_at_steps(self) -> List[int]:
        """Get the unique execution steps where the variable is defined.

        Returns
        -------
        list[int]
            A list of unique step indices where this variable is defined.
        """
        steps = []
        for _, ssa_var in self.unique_ssa_variables.items():
            steps += ssa_var.variable_defined_at_steps
        return list(set(steps))

    @property
    def ssa_variables(self) -> List[SSAVariableModel]:
        """Get all SSA versions of the variable.

        Returns
        -------
        list[SSAVariableModel]
            A list of `SSAVariableModel` instances representing SSA versions
            of this variable.
        """
        return list(self.unique_ssa_variables.values())

    def get_ssa_var(self, ssa_name: str) -> Optional[SSAVariableModel]:
        """Retrieve a specific SSA version of the variable.

        Parameters
        ----------
        ssa_name : str
            The name of the SSA variable to retrieve.

        Returns
        -------
        SSAVariableModel or None
            The `SSAVariableModel` instance corresponding to `ssa_name`, or
            None if not found.
        """
        return self.unique_ssa_variables.get(ssa_name, None)


class VariableManagerModel(BaseModel):
    """Manages variables within a function's scope, tracking
       their usage and definitions.

    Attributes
    ----------
    function_args : List[str], optional
        A list of function argument names. Defaults to an empty list.
    local_variables : List[str], optional
        A list of local variable names. Defaults to an empty list.
    tmp_variables : List[str], optional
        A list of temporary variable names. Defaults to an empty list.
    return_variables : List[str], optional
        A list of variables representing function return values.
        Defaults to an empty list.
    variables : Dict[str, VariableModel], optional
        A dictionary mapping variable names to their corresponding `VariableModel`
        instances. Defaults to an empty dictionary.
    """

    function_args: List[str] = []
    local_variables: List[str] = []
    tmp_variables: List[str] = []
    return_variables: List[str] = []
    variables: Dict[str, VariableModel] = {}

    @property
    def names(self) -> List[str]:
        """Get the list of all variable names.

        Returns
        -------
        List[str]
            A list of all variable names stored in `variables`.
        """
        return list(self.variables.keys())

    @property
    def ssa_names(self) -> List[str]:
        """Get the list of all unique SSA (Static Single Assignment) variable names.

        Returns
        -------
        List[str]
            A list of unique SSA variable names across all stored variables.
        """
        all_unique_ssa_names = []
        for var in self.variables.values():
            all_unique_ssa_names += list(var.unique_ssa_variables.keys())
        return all_unique_ssa_names

    def used_at_step(self, step_index: int) -> List[VariableModel]:
        """Retrieve variables that are used at a given step.

        Parameters
        ----------
        step_index : int
            The step index to check for variable usage.

        Returns
        -------
        List[VariableModel]
            A list of `VariableModel` instances that were used at the given step.
        """
        return [
            var for var in self.variables.values() if step_index in var.defined_at_steps
        ]

    def defined_at_step(self, step_index: int) -> List[VariableModel]:
        """Retrieve variables that are defined at a given step.

        Parameters
        ----------
        step_index : int
            The step index to check for variable definitions.

        Returns
        -------
        List[VariableModel]
            A list of `VariableModel` instances that were defined at the given step.
        """
        return [
            var for var in self.variables.values() if step_index in var.used_at_steps
        ]

    def used_or_defined_at_step(self, step_index: int) -> List[VariableModel]:
        """Retrieve variables that are either used or defined at a given step.

        Parameters
        ----------
        step_index : int
            The step index to check for variable usage or definition.

        Returns
        -------
        List[VariableModel]
            A list of `VariableModel` instances used or defined at the given step.
        """
        return [
            var
            for var in self.variables.values()
            if step_index in var.used_at_steps or step_index in var.defined_at_steps
        ]

    def get(self, name: str) -> VariableModel:
        """Retrieve a variable by its name.

        Parameters
        ----------
        name : str
            The name of the variable to retrieve.

        Returns
        -------
        VariableModel or None
            The corresponding `VariableModel` instance if found, otherwise `None`.
        """
        return self.variables.get(name, None)

    def all(self) -> List[VariableModel]:
        """Retrieve all stored variables.

        Returns
        -------
        List[VariableModel]
            A list of all `VariableModel` instances stored in `variables`.
        """
        return list(self.variables.values())

    def search(self, name: Optional[str] = None) -> List[VariableModel]:
        """Search for variables whose names contain a given substring.

        Parameters
        ----------
        name : str, optional
            The substring to search for in variable names.

        Returns
        -------
        list[VariableModel]
            A list of matching `VariableModel` instances.
        """
        _vars = []

        for varname in self.variables.keys():
            if name in varname:
                _vars.append(self.variables[varname])

        return _vars
