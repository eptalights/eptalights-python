from pydantic import BaseModel, StrictInt
from typing import List, Optional, Dict
from pprint import pprint
from eptalights.models.egimple.enum_types import TokenType
from eptalights.core.printer import PettyPrinter


class TokenModel(BaseModel):
    """Represents a token model with attributes holding metadata.

    Attributes
    ----------
    model_config : dict
        Configuration dictionary for model validation settings, such as enabling
        assignment validation.
    token_type : TokenType
        The type of the token, defaults to `TokenType.IS_UNDEF`.
    is_base_variable : bool
        Flag indicating whether the token is a base variable, defaults to `False`.
    code_name : str, optional
        An optional string representing the code name of the token.
    value : str, optional
        An optional string representing the token's value.
    value_extended : str, optional
        An optional extended value of the token.
    discovery_depth : int
        The depth of discovery for the token, defaults to `0`.
    """

    model_config = {"validate_assignment": True}

    token_type: TokenType = TokenType.IS_UNDEF
    is_base_variable: bool = False
    code_name: Optional[str] = None
    value: Optional[str] = None
    value_extended: Optional[str] = None
    discovery_depth: int = 0


class TokenizedOperandModel(BaseModel):
    """Represents a tokenized operand used within a specific step of program analysis.

    Attributes
    ----------
    operand_type : TokenType, optional
        The type of operand. Defaults to ``TokenType.IS_UNDEF``.
    ssa_name : str, optional
        The SSA name for the operand.
    ssa_version : int
        The version of the SSA name. Defaults to 0.
    variable_name : str, optional
        The variable name for the operand.
    step_index : int, optional
        The index of the step where the operand is used.
    position : int
        The position of the operand within a specific context. Defaults to 0.
    used_inside_other_tokenized_operand_tokens_at_step : dict[int, list[str]], optional
        A dictionary where keys represent step indices and values are lists of tokens
        used in other tokenized operands at those steps.
        Defaults to an empty dictionary.
    current_depth_position : int
        The current depth position of the operand. Defaults to 0.
    tokens : list[TokenModel]
        A list of tokens associated with the operand.
    _debug_visited_nodes : list[str], optional
        For debugging purposes, tracks visited nodes during analysis. Defaults to an
        empty list.
    """

    model_config = {"validate_assignment": True}

    operand_type: Optional[TokenType] = TokenType.IS_UNDEF
    ssa_name: Optional[str] = None
    ssa_version: StrictInt = 0
    variable_name: Optional[str] = None
    step_index: Optional[StrictInt] = None
    position: StrictInt = 0
    used_inside_other_tokenized_operand_tokens_at_step: Dict[StrictInt, List[str]] = {}
    current_depth_position: StrictInt = 0
    tokens: List[TokenModel] = []
    _debug_visited_nodes: List[str] = []

    def has_ssa_variable_extracted(self) -> bool:
        """Checks whether the operand has an SSA variable extracted.

        Returns
        -------
        bool
            True if both `variable_name` and `ssa_name` are not None, otherwise False.
        """
        if self.variable_name is None or self.ssa_name is None:
            return False
        return True

    def has_constant_in_tokens(self) -> bool:
        """Checks if any token in the operand is a constant.

        Returns
        -------
        bool
            True if a constant token is found, otherwise False.
        """
        return any(token.is_constant for token in self.tokens)

    def get_field_attributes_used_in_tokens(self) -> List[str]:
        """Extracts and returns the attribute values used in the tokens.

        Returns
        -------
        list[str]
            A list of attribute values from tokens with type ``TokenType.IS_ATTRIBUTE``.
        """
        return [
            token.value_extended
            for token in self.tokens
            if token.token_type == TokenType.IS_ATTRIBUTE
        ]

    def array_index_tokens_iter(self) -> List[TokenModel]:
        """Yields the tokens representing array indices.

        Yields
        ------
        TokenModel
            The token representing an array index.
        """
        for idx, token in enumerate(self.tokens):
            if token.value == "[":
                yield self.tokens[idx + 1]

    def array_index_token_values_iter(self) -> List[TokenModel]:
        """Yields the values of tokens representing array indices.

        Yields
        ------
        str
            The value of the token representing an array index.
        """
        for idx, token in enumerate(self.tokens):
            if token.value == "[":
                yield self.tokens[idx + 1].value

    def array_index_token_at_index(self, idx: int) -> TokenModel:
        """Retrieves the array index token at a specified index.

        Parameters
        ----------
        idx : int
            The index of the array token to retrieve.

        Returns
        -------
        TokenModel
            The token at the specified index, or an empty ``TokenModel`` if not found.
        """
        arr_index_token = TokenModel()
        for arr_idx, token in enumerate(self.array_index_tokens_iter()):
            if idx == arr_idx:
                arr_index_token = token
                break
        return arr_index_token

    def get_total_array_index_tokens(self) -> int:
        """Returns the total number of array index tokens.

        Returns
        -------
        int
            The total number of array index tokens.
        """
        return sum(1 for _ in self.array_index_tokens_iter())

    def constant_index_tokens_iter(self) -> List[TokenModel]:
        """Yields tokens that represent constants.

        Yields
        ------
        TokenModel
            The token representing a constant.
        """
        for idx, token in enumerate(self.tokens):
            if token.token_type == TokenType.IS_CONSTANT:
                yield self.tokens[idx]

    def constant_token_at_index(self, idx: int) -> TokenModel:
        """Retrieves the constant token at a specified index.

        Parameters
        ----------
        idx : int
            The index of the constant token to retrieve.

        Returns
        -------
        TokenModel
            The token at the specified index, or an empty ``TokenModel`` if not found.
        """
        const_index_token = TokenModel()
        for arr_idx, token in enumerate(self.constant_index_tokens_iter()):
            if idx == arr_idx:
                const_index_token = token
                break
        return const_index_token

    def symbol_index_tokens_iter(self) -> List[TokenModel]:
        """Yields tokens that represent symbols.

        Yields
        ------
        TokenModel
            The token representing a symbol.
        """
        for idx, token in enumerate(self.tokens):
            if token.token_type == TokenType.IS_SYMBOL:
                yield self.tokens[idx]

    def symbol_token_at_index(self, idx: int) -> TokenModel:
        """Retrieves the symbol token at a specified index.

        Parameters
        ----------
        idx : int
            The index of the symbol token to retrieve.

        Returns
        -------
        TokenModel
            The token at the specified index, or an empty ``TokenModel`` if not found.
        """
        index_token = TokenModel()
        for arr_idx, token in enumerate(self.symbol_index_tokens_iter()):
            if idx == arr_idx:
                index_token = token
                break
        return index_token

    def pretty_print_tokens(self):
        """Prints a pretty representation of the tokens.

        This function converts the tokens to a dictionary format and prints them
        for debugging purposes.
        """
        _ptokens = [t.model_dump() for t in self.tokens]
        pprint(_ptokens)

    def decompile(self):
        """Generate a human-readable or high-level representation.

        Returns
        -------
        str
            A string representation of the expression.
        """
        return PettyPrinter.decompile(self)
