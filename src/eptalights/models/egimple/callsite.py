from pydantic import BaseModel
from typing import List, Dict, Optional


class CallsiteModel(BaseModel):
    """Represents a function call site.

    Attributes
    ----------
    cid : Optional[str], optional
        The unique identifier for the call site. Defaults to None.
    step_index : int
        The index of the step in which this call occurs.
    fn_name : List[str]
        The name of the function being called, stored as a list of strings.
    num_of_args : int, optional
        The number of arguments passed to the function call. Defaults to 0.
    variables_used_as_callsite_arg : List[str], optional
        A list of variable names that are used as arguments at the call site.
        Defaults to an empty list.
    variables_defined_here : List[str], optional
        A list of variable names that are defined at the call site.
        Defaults to an empty list.
    ssa_variables_used_as_callsite_arg : List[str], optional
        A list of SSA (Static Single Assignment) variables used as arguments.
        Defaults to an empty list.
    ssa_variables_defined_here : List[str], optional
        A list of SSA variables defined at the call site.
        Defaults to an empty list.
    """

    cid: Optional[str] = None
    step_index: int
    fn_name: List[str]
    num_of_args: int = 0

    variables_used_as_callsite_arg: List[str] = []
    variables_defined_here: List[str] = []

    ssa_variables_used_as_callsite_arg: List[str] = []
    ssa_variables_defined_here: List[str] = []

    @property
    def name(self) -> str:
        """Return the function name as a concatenated string.

        Returns
        -------
        str
            The function name as a single string.
        """
        return "".join(self.fn_name)


class CallsiteManagerModel(BaseModel):
    """Manages function call sites.

    Attributes
    ----------
    step_callsites : dict[int, str], optional
        A mapping from step indices to SSA (Static Single Assignment)
        variable names. Defaults to an empty dictionary.
    unique_callsites : dict[str, List[str]], optional
        A mapping from function names to lists of their SSA variable names.
        Defaults to an empty dictionary.
    callsites : dict[str, CallsiteModel], optional
        A mapping from SSA variable names to their corresponding
        `CallsiteModel` instances. Defaults to an empty dictionary.
    """

    step_callsites: Dict[int, str] = {}
    unique_callsites: Dict[str, List[str]] = {}
    callsites: Dict[str, CallsiteModel] = {}

    @property
    def steps(self) -> List[int]:
        """Return a list of step indices where function calls occur.

        Returns
        -------
        list[int]
            A list of step indices.
        """
        return list(self.step_callsites.keys())

    @property
    def names(self) -> List[str]:
        """Return a list of unique function names found in call sites.

        Returns
        -------
        list[str]
            A list of function names.
        """
        return list(self.unique_callsites.keys())

    @property
    def ssa_names(self) -> List[str]:
        """Return a list of all SSA variable names used in function calls.

        Returns
        -------
        list[str]
            A list of SSA variable names.
        """
        all_unique_ssa_names = []
        for _, ssa_names in self.unique_callsites.items():
            all_unique_ssa_names += ssa_names
        return all_unique_ssa_names

    def by_ssa_name(self, ssa_name: str) -> Optional[CallsiteModel]:
        """Retrieve a call site model by its SSA variable name.

        Parameters
        ----------
        ssa_name : str
            The SSA variable name of the call site.

        Returns
        -------
        CallsiteModel or None
            The corresponding `CallsiteModel` instance if found,
            otherwise `None`.
        """
        return self.callsites.get(ssa_name)

    def at_step(self, step_index: int) -> Optional[CallsiteModel]:
        """Retrieve a call site at a given step index.

        Parameters
        ----------
        step_index : int
            The index of the step.

        Returns
        -------
        CallsiteModel or None
            The `CallsiteModel` instance if found, otherwise `None`.
        """
        callsite_ssa = self.step_callsites.get(step_index)
        return self.callsites.get(callsite_ssa) if callsite_ssa else None

    def all(self, name: Optional[str] = None) -> List[CallsiteModel]:
        """Retrieve all call sites or those matching a specific function name.

        Parameters
        ----------
        name : str, optional
            The function name to filter by. If `None`, all call sites are
            returned.

        Returns
        -------
        list[CallsiteModel]
            A list of matching `CallsiteModel` instances.
        """
        _callsites = []
        if name is not None:
            callsite_ssa_names = self.unique_callsites.get(name, [])
            for callsite_ssa_name in callsite_ssa_names:
                callsite = self.callsites.get(callsite_ssa_name)
                if callsite:
                    _callsites.append(callsite)
        else:
            _callsites = list(self.callsites.values())

        return _callsites

    def search(self, name: Optional[str] = None) -> List[CallsiteModel]:
        """Search for call sites whose function names contain a given substring.

        Parameters
        ----------
        name : str, optional
            The substring to search for in function names.

        Returns
        -------
        list[CallsiteModel]
            A list of matching `CallsiteModel` instances.
        """
        callsite_ssa_names = []
        _callsites = []

        for cs_name, cs_ssa_names in self.unique_callsites.items():
            if name in cs_name:
                callsite_ssa_names += cs_ssa_names

        for callsite_ssa_name in callsite_ssa_names:
            callsite = self.callsites.get(callsite_ssa_name)
            if callsite:
                _callsites.append(callsite)

        return _callsites
