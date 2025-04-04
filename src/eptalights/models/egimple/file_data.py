from pydantic import BaseModel
from typing import Dict
from eptalights.models.egimple.tokenized_operand import TokenizedOperandModel
from eptalights.models.egimple.function import FunctionModel
from eptalights.core.printer import PrettyPrinter


class ClassDataModel(BaseModel):
    """Represents a class within a program analysis context.

    Attributes
    ----------
    class_props : Dict[str, TokenizedOperandModel]
        A dictionary mapping property names to their tokenized representations.
        Represents the attributes (fields) of the class.
    class_methods : Dict[str, FunctionModel]
        A dictionary mapping method names to their corresponding function models.
        Represents the functions (methods) of the class.
    """

    class_props: Dict[str, TokenizedOperandModel] = {}
    class_methods: Dict[str, FunctionModel] = {}


class FileDataModel(BaseModel):
    """Represents a file within a program analysis context.

    Attributes
    ----------
    filepath : str
        The path to the file being analyzed.
    classes : Dict[str, ClassDataModel]
        A dictionary mapping class names to their corresponding class models.
    functions : Dict[str, FunctionModel]
        A dictionary mapping function names to their corresponding function models.
    """

    filepath: str
    classes: Dict[str, ClassDataModel] = {}
    functions: Dict[str, FunctionModel] = {}

    def decompile(self) -> str:
        """Generates a human-readable or high-level representation of the file.

        Returns
        -------
        str
            A string representation of the decompiled file.
        """
        return PrettyPrinter.decompile(self)
