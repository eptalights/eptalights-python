from pydantic import BaseModel
from typing import List, Optional, Dict


class FunctionGraphNodeReference(BaseModel):
    """Represents a reference to a function node in a graph.

    Attributes
    ----------
    fid : str, optional
        The unique identifier for the function. Defaults to None.
    name : str
        The name of the function.
    filename : str, optional
        The name of the file where the function is defined. Defaults to None.
    """

    fid: Optional[str] = None
    name: str
    filename: Optional[str] = None


class FunctionGraphModel(BaseModel):
    """Represents a function node within a function call graph.

    Attributes
    ----------
    prev_nodes : Dict[str, List[FunctionGraphNodeReference]], optional
        A mapping of previous function nodes that call this function.
        The keys are function identifiers, and the values are lists of references
        to the corresponding function nodes.
        Defaults to an empty dictionary.
    next_nodes : Dict[str, List[FunctionGraphNodeReference]], optional
        A mapping of subsequent function nodes that this function calls.
        The keys are function identifiers, and the values are lists of references
        to the corresponding function nodes.
        Defaults to an empty dictionary.
    prev_nodes_fids : List[str], optional
        A list of function identifiers representing the previous function nodes.
        Defaults to an empty list.
    next_nodes_fids : List[str], optional
        A list of function identifiers representing the next function nodes.
        Defaults to an empty list.
    """

    prev_nodes: Dict[str, List[FunctionGraphNodeReference]] = {}
    next_nodes: Dict[str, List[FunctionGraphNodeReference]] = {}

    prev_nodes_fids: List[str] = []
    next_nodes_fids: List[str] = []
