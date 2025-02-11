from pydantic import BaseModel, validator
from typing import List, Optional, Union
from eptalights.models.egimple.tokenized_operand import TokenizedOperandModel
from eptalights.models.egimple.cfg import ControlFlowGraphModel
from eptalights.models.egimple.callsite import CallsiteManagerModel
from eptalights.models.egimple.variable import VariableManagerModel
from eptalights.models.egimple.enum_types import (
    OpType,
    ExprType,
    TokenType,
)
from eptalights.models.egimple.function_graph import FunctionGraphModel
from eptalights.core.printer import PettyPrinter


class ExprModel(BaseModel):
    """Represents an expression in a program analysis context.

    Attributes
    ----------
    expr_type : ExprType, optional
        The type of the expression. Defaults to `ExprType.UNDEF`.
    lhs : TokenizedOperandModel
        The left-hand side operand of the expression.
    rhs : TokenizedOperandModel, optional
        The right-hand side operand of the expression, if applicable.
        Defaults to `None` for unary expressions.
    """

    expr_type: ExprType = ExprType.UNDEF
    lhs: TokenizedOperandModel
    rhs: Optional[TokenizedOperandModel] = None

    def decompile(self):
        """Generate a human-readable or high-level representation.

        Returns
        -------
        str
            A string representation of the expression.
        """
        return PettyPrinter.decompile(self)


class EGimpleIRBaseModel(BaseModel):
    """Represents a base model for the GIMPLE Intermediate Representation (IR).

    Attributes
    ----------
    step_index : int, optional
        The index of the step associated with this IR. Defaults to None.
    lineno : int, optional
        The line number associated with the IR. Defaults to -1.
    basicblock_index : int, optional
        The index of the basic block where this IR is located. Defaults to None.
    low_level_steps : List[int], optional
        A list of indices representing the low-level steps in this IR. Defaults to
        an empty list.
    variables_defined_here : List[str], optional
        A list of variable names that are defined at this step. Defaults to an empty
        list.
    variables_used_here : List[str], optional
        A list of variable names that are used at this step. Defaults to an empty list.
    ssa_variables_defined_here : List[str], optional
        A list of SSA (Static Single Assignment) variables defined at this step.
        Defaults to an empty list.
    ssa_variables_used_here : List[str], optional
        A list of SSA variables used at this step. Defaults to an empty list.
    """

    step_index: Optional[int] = None
    lineno: int = -1

    basicblock_index: Optional[int] = None
    low_level_steps: List[int] = []

    variables_defined_here: List[str] = []
    variables_used_here: List[str] = []

    ssa_variables_defined_here: List[str] = []
    ssa_variables_used_here: List[str] = []

    @property
    def defined_tokenized_operands(self) -> List[str]:
        """Returns a list of tokenized operands that are defined at this step.

        Returns
        -------
        List[str]
            A list of defined operands. By default, returns an empty list.
        """
        return []

    @property
    def used_tokenized_operands(self) -> List[str]:
        """Returns a list of tokenized operands that are used at this step.

        Returns
        -------
        List[str]
            A list of used operands. By default, returns an empty list.
        """
        return []

    def update_operand_step_index(self):
        """Updates the operand step index.

        This method does not currently implement any functionality. It is a
        placeholder to be overridden by subclasses if needed.
        """
        pass

    def update_variables_defined_and_used_here(self):
        """Updates the variables defined and used at this step.

        This method is intended to be overridden by subclasses to provide
        specific behavior. Raises a `NotImplementedError` to signal that it
        has not been implemented yet.
        """
        raise NotImplementedError


class EGimpleIRNopModel(EGimpleIRBaseModel):
    """Represents a NOP (No Operation) instruction in the GIMPLE IR model.

    Attributes
    ----------
    op : OpType, optional
        The operation type associated with this instruction. Defaults to `OpType.NOP`.
    """

    op: OpType = OpType.NOP

    def update_variables_defined_and_used_here(self):
        """Update the variables defined and used in this NOP instruction.

        This method is currently a placeholder and does not modify any state.
        It is intended to be overridden or extended in future implementations
        to handle variable tracking specific to NOP operations.
        """
        pass

    def decompile(self):
        """Generate a human-readable or high-level representation.

        Returns
        -------
        str
            A string representation of the expression.
        """
        return PettyPrinter.decompile(self)


class EGimpleIRAssignModel(EGimpleIRBaseModel):
    """Represents an assignment operation in the EGimple IR.

    Attributes
    ----------
    op : OpType, optional
        The operation type, which defaults to `OpType.ASSIGN`.
    src : ExprModel
        The source expression being assigned.
    dst : TokenizedOperandModel
        The destination operand that receives the assignment.
    """

    op: OpType = OpType.ASSIGN
    src: ExprModel
    dst: TokenizedOperandModel

    @property
    def defined_tokenized_operands(self) -> List[TokenizedOperandModel]:
        """Retrieve the list of operands that are defined in this assignment.

        Returns
        -------
        List[TokenizedOperandModel]
            A list containing the destination operand.
        """
        return [self.dst]

    @property
    def used_tokenized_operands(self) -> List[TokenizedOperandModel]:
        """Retrieve the list of operands used in this assignment.

        Returns
        -------
        List[TokenizedOperandModel]
            A list of operands used in the right-hand side of the assignment.
        """
        tvars = []
        tvars.append(self.src.lhs)

        if self.src.rhs is not None:
            tvars.append(self.src.rhs)

        return tvars

    def update_operand_step_index(self) -> None:
        """Update the step index for all operands involved in this assignment.

        This ensures that the step index of the destination and source operands
        aligns with the step index of the assignment operation.
        """
        self.dst.step_index = self.step_index
        self.src.lhs.step_index = self.step_index
        if self.src.rhs is not None:
            self.src.rhs.step_index = self.step_index

    def update_variables_defined_and_used_here(self) -> None:
        """Update the lists of variables defined and used in this assignment.

        This method categorizes tokens into `ssa_variables_defined_here`
        and `ssa_variables_used_here` based on whether they are defined
        or used in this assignment operation.
        """
        for operand in self.defined_tokenized_operands:
            for token in operand.tokens:
                if token.token_type == TokenType.IS_VARIABLE:
                    if token.is_base_variable:
                        if token.value not in self.ssa_variables_used_here:
                            self.ssa_variables_defined_here.append(token.value)
                            self.variables_defined_here.append(token.value_extended)
                        else:
                            self.ssa_variables_used_here.append(token.value)
                            self.variables_used_here.append(token.value_extended)

        for operand in self.used_tokenized_operands:
            for token in operand.tokens:
                if token.token_type == TokenType.IS_VARIABLE:
                    if token.value not in self.ssa_variables_used_here:
                        self.ssa_variables_used_here.append(token.value)
                        self.variables_used_here.append(token.value_extended)

    def decompile(self):
        """Generate a human-readable or high-level representation.

        Returns
        -------
        str
            A string representation of the expression.
        """
        return PettyPrinter.decompile(self)


class EGimpleIRCallModel(EGimpleIRBaseModel):
    """Represents a function call operation in the GIMPLE IR.

    Attributes
    ----------
    op : OpType
        The operation type, which is always set to `OpType.CALL`.
    fname : str
        The name of the function being called.
    finfo : Optional[str], optional
        Additional function information, if available. Defaults to `None`.
    fargs : List[TokenizedOperandModel], optional
        A list of tokenized operands representing the function arguments.
        Defaults to an empty list.
    dst : Optional[TokenizedOperandModel], optional
        The destination operand where the function's return value is stored.
        Defaults to `None`.
    """

    op: OpType = OpType.CALL
    fname: str
    finfo: Optional[str] = None
    fargs: List[TokenizedOperandModel] = []
    dst: Optional[TokenizedOperandModel] = None

    @property
    def defined_tokenized_operands(self) -> List[TokenizedOperandModel]:
        """Return a list of tokenized operands defined by this call operation.

        Returns
        -------
        List[TokenizedOperandModel]
            A list containing the destination operand, if defined.
        """
        return [self.dst] if self.dst is not None else []

    @property
    def used_tokenized_operands(self) -> List[TokenizedOperandModel]:
        """Return a list of tokenized operands used as arguments in the call.

        Returns
        -------
        List[TokenizedOperandModel]
            A list of operands used in the function call, filtering only those
            that represent variables.
        """
        return [operand for operand in self.fargs]

    def update_operand_step_index(self) -> None:
        """Update the step index of all function arguments to match the
        current step index.
        """
        for operand in self.fargs:
            operand.step_index = self.step_index

    def update_variables_defined_and_used_here(self) -> None:
        """Update the lists of defined and used SSA variables based on
        the function call.

        This method populates `ssa_variables_defined_here` and
        `variables_defined_here` for newly defined variables, and
        `ssa_variables_used_here` and `variables_used_here` for
        referenced variables.
        """
        for operand in self.defined_tokenized_operands:
            for token in operand.tokens:
                if token.token_type == TokenType.IS_VARIABLE:
                    if token.is_base_variable:
                        if token.value not in self.ssa_variables_used_here:
                            self.ssa_variables_defined_here.append(token.value)
                            self.variables_defined_here.append(token.value_extended)
                        else:
                            self.ssa_variables_used_here.append(token.value)
                            self.variables_used_here.append(token.value_extended)

        for operand in self.used_tokenized_operands:
            for token in operand.tokens:
                if token.token_type == TokenType.IS_VARIABLE:
                    if token.value not in self.ssa_variables_used_here:
                        self.ssa_variables_used_here.append(token.value)
                        self.variables_used_here.append(token.value_extended)

    def decompile(self):
        """Generate a human-readable or high-level representation.

        Returns
        -------
        str
            A string representation of the expression.
        """
        return PettyPrinter.decompile(self)


class EGimpleIRCondModel(EGimpleIRBaseModel):
    """Represents a conditional expression in the GIMPLE intermediate representation.

    Attributes
    ----------
    op : OpType
        The operation type, set to ``OpType.COND`` by default.
    src : ExprModel
        The conditional expression being evaluated.
    true_dst_block_index : Optional[int], optional
        The index of the block to jump to if the condition is ``true``.
        Defaults to ``None``.
    false_dst_block_index : Optional[int], optional
        The index of the block to jump to if the condition is ``false``.
        Defaults to ``None``.
    """

    op: OpType = OpType.COND
    src: ExprModel
    true_dst_block_index: Optional[int] = None
    false_dst_block_index: Optional[int] = None

    @property
    def defined_tokenized_operands(self) -> list:
        """Return an empty list since conditional expressions do not
        define new operands.

        Returns
        -------
        list
            An empty list.
        """
        return []

    @property
    def used_tokenized_operands(self) -> list:
        """Return a list of tokenized operands used in the conditional expression.

        Returns
        -------
        list
            A list of variable operands used in the condition.
        """
        tvars = []
        tvars.append(self.src.lhs)

        if self.src.rhs is not None:
            tvars.append(self.src.rhs)

        return tvars

    def update_operand_step_index(self) -> None:
        """Update the step index for operands in the conditional expression.

        This method sets the `step_index` of the left-hand side (lhs) operand
        and, if present, the right-hand side (rhs) operand.
        """
        self.src.lhs.step_index = self.step_index
        if self.src.rhs is not None:
            self.src.rhs.step_index = self.step_index

    def update_variables_defined_and_used_here(self) -> None:
        """Update the lists of SSA variables and regular variables used in
        this condition.

        This method ensures that variables appearing in the conditional expression
        are tracked in `ssa_variables_used_here` and `variables_used_here`,
        avoiding duplicates.
        """
        for operand in self.used_tokenized_operands:
            for token in operand.tokens:
                if token.token_type == TokenType.IS_VARIABLE:
                    if token.value not in self.ssa_variables_used_here:
                        self.ssa_variables_used_here.append(token.value)
                        self.variables_used_here.append(token.value_extended)

    def decompile(self):
        """Generate a human-readable or high-level representation.

        Returns
        -------
        str
            A string representation of the expression.
        """
        return PettyPrinter.decompile(self)


class EGimpleIRReturnModel(EGimpleIRBaseModel):
    """Represents a RETURN operation in the GIMPLE IR.

    Attributes
    ----------
    op : OpType
        The operation type, set to `OpType.RETURN` by default.
    dst : Optional[TokenizedOperandModel], optional
        The destination operand representing the return value.
        Defaults to `None`.
    """

    op: OpType = OpType.RETURN
    dst: Optional[TokenizedOperandModel] = None

    @property
    def defined_tokenized_operands(self):
        """Retrieve the operands defined by this RETURN operation.

        Returns
        -------
        list
            An empty list, as RETURN does not define any new variables.
        """
        return []

    @property
    def used_tokenized_operands(self):
        """Retrieve the operands used by this RETURN operation.

        Returns
        -------
        list of TokenizedOperandModel
            A list containing the return operand if it is a variable.
        """
        tvars = []
        if self.dst:
            tvars.append(self.dst)
        return tvars

    def update_operand_step_index(self):
        """Update the step index for the return operand."""
        if self.dst is not None:
            self.dst.step_index = self.step_index

    def update_variables_defined_and_used_here(self):
        """Update the lists of SSA and regular variables used at
        this RETURN operation.
        """
        for operand in self.used_tokenized_operands:
            for token in operand.tokens:
                if token.token_type == TokenType.IS_VARIABLE:
                    if token.value not in self.ssa_variables_used_here:
                        self.ssa_variables_used_here.append(token.value)
                        self.variables_used_here.append(token.value_extended)

    def decompile(self):
        """Generate a human-readable or high-level representation.

        Returns
        -------
        str
            A string representation of the expression.
        """
        return PettyPrinter.decompile(self)


class EGimpleIRGotoModel(EGimpleIRBaseModel):
    """Represents a GIMPLE IR 'goto' statement within an intermediate representation.

    Attributes
    ----------
    op : OpType
        The operation type, set to `OpType.GOTO` by default.
    dst_block_index : int, optional
        The index of the destination basic block. Defaults to `None`.
    """

    op: OpType = OpType.GOTO
    dst_block_index: Optional[int] = None

    @property
    def defined_tokenized_operands(self) -> list:
        """Return an empty list, as 'goto' does not define any operands.

        Returns
        -------
        list
            An empty list.
        """
        return []

    @property
    def used_tokenized_operands(self) -> list:
        """Return an empty list, as 'goto' does not use any operands.

        Returns
        -------
        list
            An empty list.
        """
        return []

    def update_variables_defined_and_used_here(self) -> None:
        """Update variables defined and used at this 'goto' statement.

        Notes
        -----
        Since 'goto' does not define or use any variables, this method is a no-op.
        """
        pass

    def decompile(self):
        """Generate a human-readable or high-level representation.

        Returns
        -------
        str
            A string representation of the expression.
        """
        return PettyPrinter.decompile(self)


class EGimpleIRSwitchModel(EGimpleIRBaseModel):
    """Represents a SWITCH operation in the GIMPLE IR model.

    Attributes
    ----------
    op : OpType
        The operation type, set to `OpType.SWITCH`.
    switch_index : TokenizedOperandModel
        The operand representing the index or variable used in the switch condition.
    switch_cases : Optional[List[TokenizedOperandModel]], optional
        A list of operand models representing the case values in the switch statement.
        Defaults to an empty list.
    switch_label_names : Optional[List[str]], optional
        A list of label names associated with each case.
        Defaults to an empty list.
    switch_basic_blocks : Optional[List[int]], optional
        A list of basic block indices corresponding to each case.
        Defaults to an empty list.
    """

    op: OpType = OpType.SWITCH
    switch_index: TokenizedOperandModel
    switch_cases: Optional[List[TokenizedOperandModel]] = []
    switch_label_names: Optional[List[str]] = []
    switch_basic_blocks: Optional[List[int]] = []

    @property
    def defined_tokenized_operands(self) -> List[TokenizedOperandModel]:
        """Retrieve a list of tokenized operands defined at this switch statement.

        Returns
        -------
        List[TokenizedOperandModel]
            An empty list since a switch statement does not define new operands.
        """
        return []

    @property
    def used_tokenized_operands(self) -> List[TokenizedOperandModel]:
        """Retrieve a list of tokenized operands used in this switch statement.

        Returns
        -------
        List[TokenizedOperandModel]
            A list of operands used in the switch index and case values,
            if they are variables.
        """
        tvars = []
        tvars.append(self.switch_index)

        if self.switch_cases:
            for case in self.switch_cases:
                tvars.append(case)
        return tvars

    def update_operand_step_index(self) -> None:
        """Update the `step_index` attribute for all operands in this
        switch statement.
        """
        self.switch_index.step_index = self.step_index
        if self.switch_cases:
            for idx, _ in enumerate(self.switch_cases):
                self.switch_cases[idx].step_index = self.step_index

    def update_variables_defined_and_used_here(self) -> None:
        """Update the lists of SSA and regular variables used in this
        switch statement.
        """
        for operand in self.used_tokenized_operands:
            for token in operand.tokens:
                if token.token_type == TokenType.IS_VARIABLE:
                    if token.value not in self.ssa_variables_used_here:
                        self.ssa_variables_used_here.append(token.value)
                        self.variables_used_here.append(token.value_extended)

    def decompile(self):
        """Generate a human-readable or high-level representation.

        Returns
        -------
        str
            A string representation of the expression.
        """
        return PettyPrinter.decompile(self)


class FunctionModel(BaseModel):
    """Represents a function within a program analysis context.

    Attributes
    ----------
    fid : str
        A unique identifier for the function.
    name : str
        The name of the function.
    filename : str
        The name of the file where the function is defined.
    class_name : Optional[str], optional
        The name of the class containing this function (if applicable).
        Defaults to None.
    variable_manager : Optional[VariableManagerModel], optional
        An instance managing the variables within the function scope.
        Defaults to an empty `VariableManagerModel`.
    callsite_manager : Optional[CallsiteManagerModel], optional
        An instance managing the function’s call sites.
        Defaults to an empty `CallsiteManagerModel`.
    cfg : Optional[ControlFlowGraphModel], optional
        The control flow graph representing the function’s execution flow.
        Defaults to an empty `ControlFlowGraphModel`.
    steps : List[Union[EGimpleIRNopModel, EGimpleIRAssignModel,
                       EGimpleIRCallModel, EGimpleIRCondModel,
                       EGimpleIRReturnModel, EGimpleIRGotoModel,
                       EGimpleIRSwitchModel]], optional

        A list of steps representing the function’s operations in the
        intermediate representation (IR). Each step corresponds to
        an operation such as assignment, call, condition, return, etc.
        Defaults to an empty list.
    """

    fid: str
    name: str
    filepath: str
    class_name: Optional[str] = None

    variable_manager: Optional[VariableManagerModel] = VariableManagerModel()
    callsite_manager: Optional[CallsiteManagerModel] = CallsiteManagerModel()

    fgraph: Optional[FunctionGraphModel] = FunctionGraphModel()

    cfg: Optional[ControlFlowGraphModel] = ControlFlowGraphModel()

    steps: List[
        Union[
            EGimpleIRNopModel,
            EGimpleIRAssignModel,
            EGimpleIRCallModel,
            EGimpleIRCondModel,
            EGimpleIRReturnModel,
            EGimpleIRGotoModel,
            EGimpleIRSwitchModel,
        ]
    ] = []

    @validator("steps", pre=True, always=True)
    def set_steps(cls, v):
        """Validate and convert steps into their respective IR models.

        Parameters
        ----------
        v : list
            A list of step dictionaries containing operation details.

        Returns
        -------
        list
            A list of instantiated IR step models corresponding to the
            operation types.

        Raises
        ------
        Exception
            If an unknown operation type is encountered.
        """
        update_steps = []
        for step in v:
            if not isinstance(step, dict):
                step = step.model_dump()
            if step["op"] == OpType.NOP.value:
                update_steps.append(EGimpleIRNopModel(**step))
            elif step["op"] == OpType.ASSIGN.value:
                update_steps.append(EGimpleIRAssignModel(**step))
            elif step["op"] == OpType.CALL.value:
                update_steps.append(EGimpleIRCallModel(**step))
            elif step["op"] == OpType.RETURN.value:
                update_steps.append(EGimpleIRReturnModel(**step))
            elif step["op"] == OpType.COND.value:
                update_steps.append(EGimpleIRCondModel(**step))
            elif step["op"] == OpType.GOTO.value:
                update_steps.append(EGimpleIRGotoModel(**step))
            elif step["op"] == OpType.SWITCH.value:
                update_steps.append(EGimpleIRSwitchModel(**step))
            else:
                raise Exception("Unknown operation type encountered in steps.")
        return update_steps

    def decompile(self):
        """Generate a human-readable or high-level representation.

        Returns
        -------
        str
            A string representation of the expression.
        """
        return PettyPrinter.decompile(self)
