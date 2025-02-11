from typing import List, Dict
from pydantic import BaseModel


class ControlFlowGraphModel(BaseModel):
    """Represents a control flow graph (CFG) model.

    Attributes
    ----------
    basicblock_exit_nodes : List[int], optional
        A list of basic block exit nodes. Defaults to an empty list.
    basicblock_steps : Dict[int, List[int]], optional
        A mapping of basic block indices to their corresponding step indices.
        Defaults to an empty dictionary.
    basicblock_edges : Dict[int, List[int]], optional
        A mapping of basic block indices to their successor basic blocks.
        Defaults to an empty dictionary.
    """

    basicblock_exit_nodes: List[int] = []
    basicblock_steps: Dict[int, List[int]] = {}
    basicblock_edges: Dict[int, List[int]] = {}
