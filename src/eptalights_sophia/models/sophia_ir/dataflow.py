from typing import List, Optional, Union, Callable
from pydantic import BaseModel
from enum import auto
from eptalights_sophia.models.sophia_ir.enum_types import AutoStrEnum, OpType
from eptalights_sophia.models.sophia_ir import function as function_model


class SinkResultType(AutoStrEnum):
    """Enumeration representing possible sink result types.

    Attributes
    ----------
    CONTINUE : SinkResultType
        Indicates that the process should continue.
    OK : SinkResultType
        Indicates a successful result.
    STOP : SinkResultType
        Indicates that the process should stop.
    """

    CONTINUE = auto()
    OK = auto()
    STOP = auto()

    def __str__(self) -> str:
        """Return the string representation of the enum member.

        Returns
        -------
        str
            The name of the enumeration member.
        """
        return f"{self.name}"


class DataflowEventModel(BaseModel):
    """Represents a dataflow event in the dataflow analysis.

    Attributes
    ----------
    op : OpType
        The operation type associated with this dataflow event.
    lineno : int
        The line number where this dataflow event occurs.
    variable_name : str
        The name of the variable involved in this event.
    ssa_variable_name : str
        The SSA (Static Single Assignment) name of the variable.
    ssa_version : int
        The SSA version number of the variable.
    data_direction : str, optional
        The direction of data flow (e.g., "read" or "write"). Defaults to None.
    var_depth_pos : int
        Internal property for debugging variable position.
    step_index : int
        The step index of the program execution where this event occurs.
    record_attributes_defined_here : List[str], optional
        A list of record attributes that are defined at this event.
        Defaults to an empty list.
    record_attributes_used_here : List[str], optional
        A list of record attributes that are used at this event.
        Defaults to an empty list.
    used_inside_other_tokenized_operand_tokens_here : bool, optional
        Indicates whether this variable is used inside other tokenized operand tokens.
        Defaults to False.
    current_record_attibute_tracked : str, optional
        Current record attribute being tracked. Defaults to None.
    """

    op: OpType
    lineno: int
    variable_name: str
    ssa_variable_name: str
    ssa_version: int
    data_direction: Optional[str] = None
    var_depth_pos: int
    step_index: int
    record_attributes_defined_here: Optional[List[str]] = []
    record_attributes_used_here: Optional[List[str]] = []
    used_inside_other_tokenized_operand_tokens_here: bool = False
    current_record_attibute_tracked: Optional[str] = None


class DataflowStateModel(BaseModel):
    """Represents the state of data flow analysis at a specific point in execution.

    Attributes
    ----------
    current_event : DataflowEventModel
        The current data flow event being processed.
    current_function : FunctionModel
        The function in which the current event is occurring.
    current_step : Union[
        function_model.SophiaIRNopModel,
        function_model.SophiaIRAssignModel,
        function_model.SophiaIRCallModel,
        function_model.SophiaIRCondModel,
        function_model.SophiaIRReturnModel,
        function_model.SophiaIRGotoModel,
        function_model.SophiaIRSwitchModel
    ]
        The current step in the execution, represented by one of the SOPHIA IR models.
    previous_events : List[DataflowEventModel], optional
        A list of previous data flow events leading up to the current state.
        Defaults to an empty list.
    """

    current_event: DataflowEventModel
    current_function: function_model.FunctionModel
    current_step: Union[
        function_model.SophiaIRNopModel,
        function_model.SophiaIRAssignModel,
        function_model.SophiaIRCallModel,
        function_model.SophiaIRCondModel,
        function_model.SophiaIRReturnModel,
        function_model.SophiaIRGotoModel,
        function_model.SophiaIRSwitchModel,
    ]
    previous_events: List[DataflowEventModel] = []


class DataflowPathModel(BaseModel):
    """Represents a sequence of data flow events in a program analysis context.

    Attributes
    ----------
    events : List[DataflowEventModel], optional
        A list of data flow events that constitute this path.
        Defaults to an empty list.
    passthru_callsites : List[str], optional
        A list of function call sites that the data flow passes through.
        Defaults to an empty list.
    data_mutation_count : int
        The number of times data was mutated. Defaults to 0.
    """

    events: List[DataflowEventModel] = []
    passthru_callsites: List[str] = []
    data_mutation_count: int = 0


class DataflowRequestModel(BaseModel):
    """Represents a request for data flow analysis.

    Attributes
    ----------
    source_variable_name : str
        The name of the variable that serves as a data flow source.
    start_from_step_index : int, optional
        The index of the step from which the data flow source starts.
        If not provided, it defaults to None.
    sink_callback_fn : Callable[[DataflowStateModel], SinkResultType]
        A function that processes a `DataflowStateModel` and returns a `SinkResultType`.
        This function represents the sink in the data flow analysis.

        Example::

            def reachability_to_malloc_sink(
                state: DataflowStateModel
            ) -> SinkResultType:
                if (
                    state.current_event.op == models.OpType.CALL
                    and state.current_step.fname == "malloc"
                ):
                    return models.SinkResultType.OK
                return models.SinkResultType.CONTINUE

    function : FunctionModel
        The function model representing the target function for data flow analysis.
    timeout_secs : int, optional
        The maximum time (in seconds) allowed for the analysis.
        Defaults to 180 seconds (3 minutes). Maximum is 600 seconds (10 minutes).
    strict_record_attributes_tracking : bool
        If True, strictly tracks data within complex records or variables,
        following only specific attributes rather than the base variable.

        Example::

            # Given the following code:

            a.attr = 10
            x = a
            print(a.something_else)

            # If `strict_record_attributes_tracking` is False, the data flow path will
            # include `print(a.something_else)`, since it tracks `a` as a whole.

            # However, if `strict_record_attributes_tracking` is True, the data flow
            # path will **not** include `print(a.something_else)`, as it focuses only
            # on `a.attr`.

            # Another case:

            a.attr = 10
            x = a
            print(a.attr)

            # Here, the `print(a.attr)` statement **will** be included in the data
            # flow path, as it matches the tracked attribute.

            # Using strict attribute tracking is encouraged for accuracy, unless
            # attributes cause side effects or a different behavior is required.
    """

    function: function_model.FunctionModel
    source_variable_name: str
    sink_callback_fn: Callable[[DataflowStateModel], SinkResultType]
    start_from_step_index: Optional[int] = None
    timeout_secs: int = 180  # Default: 180 secs (3 min), Max: 600 secs (10 min)
    strict_record_attributes_tracking: bool = True


class DataflowResponseModel(BaseModel):
    """Represents the response model for a dataflow analysis request.

    Attributes
    ----------
    status : bool
        Indicates whether the dataflow analysis was successful.
    paths : List[DataflowPathModel], optional
        A list of dataflow paths resulting from the analysis.
        Defaults to an empty list.
    error_message : Optional[str], optional
        An error message if the analysis failed.
        Defaults to None.
    """

    status: bool
    paths: List[DataflowPathModel] = []
    error_message: Optional[str] = None
