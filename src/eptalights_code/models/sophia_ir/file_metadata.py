from pydantic import BaseModel
from typing import Dict
from eptalights_code.models.sophia_ir.tokenized_operand import TokenizedOperandModel


class ClassMetadataModel(BaseModel):
    """Represents metadata for a class within a program analysis context.

    Attributes
    ----------
    class_props : Dict[str, TokenizedOperandModel]
        A dictionary mapping property names to their tokenized representations.
        Represents the attributes (fields) of the class.
    class_methods : Dict[str, str]
        A dictionary mapping method names to their unique identifiers.
    """

    class_props: Dict[str, TokenizedOperandModel] = {}
    class_methods: Dict[str, str] = {}


class FileMetadataModel(BaseModel):
    """Represents metadata for a file within a program analysis context.

    Attributes
    ----------
    filepath : str
        The path to the file being analyzed.
    classes : Dict[str, ClassMetadataModel]
        A dictionary mapping class names to their metadata models.
    functions : Dict[str, str]
        A dictionary mapping function names to their unique identifiers.
    """

    filepath: str
    classes: Dict[str, ClassMetadataModel] = {}
    functions: Dict[str, str] = {}
