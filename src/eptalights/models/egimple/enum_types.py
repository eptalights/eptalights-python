from enum import Enum, auto
from eptalights.core.printer import PettyPrinter


class AutoStrEnum(str, Enum):
    """
    StrEnum where enum.auto() returns the field name.
    See https://docs.python.org/3.9/library/enum.html#using-automatic-values
    """

    @staticmethod
    def _generate_next_value_(
        name: str, start: int, count: int, last_values: list
    ) -> str:
        return name


class VarType(AutoStrEnum):
    """
    VariableType Enumeration
    ========================

    An enumeration representing the type of a variable.

    Enumeration Members
    -------------------
    FUNCTION_ARGUMENT
        Represents a function argument.

    LOCAL_VARIABLE
        Represents a local variable.

    TMP_VARIABLE
        Represents a temporary variable.

    GLOBAL_VARIABLE
        Represents a global variable.

    UNDEF
        Represents an undefined variable type.
    """

    FUNCTION_ARGUMENT = auto()
    LOCAL_VARIABLE = auto()
    TMP_VARIABLE = auto()
    GLOBAL_VARIABLE = auto()
    UNDEF = auto()

    def __str__(self):
        return f"{self.name}"


class TokenType(AutoStrEnum):
    """
    DepthType Enumeration
    =====================

    An enumeration representing the depth type of an element.

    Enumeration Members
    -------------------

    IS_UNDEF
        Represents an undefined depth type.

    IS_VARIABLE
        Represents a variable depth type.
        Example: Array access used with a variable index,
        e.g., `a[n]` where `a` and `n` are variables.

    IS_CONSTANT
        Represents a constant depth type.
        Example: Array access used with a constant index, e.g., `a[10]`.

    IS_SYMBOL
        Represents a symbol depth type.
        Example: Symbols like `[`, `]`, `*`, `.`, `->`, `&`, etc.

    IS_ATTRIBUTE
        Represents an attribute depth type.
        Example: Struct field access, e.g., `st.data`, `st->data`.

    IS_TYPE
        Represents a type depth type.
        Example: Type declaration, e.g., `struct FILE fp`.

    IS_FUNCTION
        Represents a function depth type.
        Example: Functions passed as arguments to calls,
        e.g., `select_files` and `alphasort`.

        Example Usage:

        .. code-block:: c

            int select_files(const struct dirent *dirbuf)
            {
                if (dirbuf->d_name[0] == '.')
                    return 0;
                else
                    return 1;
            }

            int alphasort(const struct dirent **a, const struct dirent **b)
            {
                return (strcmp((*a)->d_name, (*b)->d_name));
            }

            int scandir(
                const char *dir,
                struct dirent ***namelist,
                int (*select) (const struct dirent *),
                int (*compar) (const struct dirent **, const struct dirent **)
            )

    IS_VARIABLE_AND_IS_FUNCTION
        Represents both a variable and a function depth type.
    """

    IS_UNDEF = auto()
    IS_VARIABLE = auto()
    IS_CONSTANT = auto()
    IS_SYMBOL = auto()
    IS_ATTRIBUTE = auto()
    IS_TYPE = auto()
    IS_FUNCTION = auto()
    IS_VARIABLE_AND_IS_FUNCTION = auto()

    def __str__(self):
        return f"{self.name}"


class OpType(AutoStrEnum):
    """
    MidLevelOpType
    ==============

    Enumeration of mid-level operation types.

    Attributes
    ----------
    NOP : auto()
        No operation.

    ASSIGN : auto()
        Assignment operation.

    CALL : auto()
        Call operation.

    RETURN : auto()
        Return operation.

    COND : auto()
        Conditional operation.

    GOTO : auto()
        Goto operation.

    SWITCH : auto()
        Switch operation.

    UNDEF : auto()
        Undefined operation.

    Methods
    -------
    __str__()
        Returns a string representation of the enumeration value.

        Returns
        -------
        str
            The string representation of the enumeration value.
    """

    NOP = auto()
    ASSIGN = auto()
    CALL = auto()
    RETURN = auto()
    COND = auto()
    GOTO = auto()
    SWITCH = auto()

    def __str__(self):
        return f"{self.name}"


class ExprType(AutoStrEnum):
    """
    MidLevelExprType
    ================

    Enumeration of mid-level expression types.

    Attributes
    ----------
    NO_EXPR : auto()
        No expression.

    MULT_EXPR : auto()
        Multiplication expression (`lhs * rhs`).

    PLUS_EXPR : auto()
        Addition expression (`lhs + rhs`).

    MINUS_EXPR : auto()
        Subtraction expression (`lhs - rhs`).

    RDIV_EXPR : auto()
        Right division expression (`lhs / rhs`).

    GREATER_THAN_OR_EQUAL_EXPR : auto()
        Greater than or equal to expression (`lhs >= rhs`).

    GREATER_THAN_EXPR : auto()
        Greater than expression (`lhs > rhs`).

    LESS_THAN_EXPR : auto()
        Less than expression (`lhs < rhs`).

    LESS_THAN_OR_EQUAL_EXPR : auto()
        Less than or equal to expression (`lhs <= rhs`).

    EQUAL_EXPR : auto()
        Equal to expression (`lhs == rhs`).

    NOT_EQUAL_EXPR : auto()
        Not equal to expression (`lhs != rhs`).

    BITWISE_AND_EXPR : auto()
        Bitwise AND expression (`lhs && rhs`).

    BITWISE_EXCLUSIVE_OR_EXPR : auto()
        Bitwise exclusive OR expression (`lhs & rhs`).

    BITWISE_INCLUSIVE_OR_EXPR : auto()
        Bitwise inclusive OR expression (`lhs | rhs`).

    BITWISE_NOT_EXPR : auto()
        Bitwise NOT expression (`~lhs`).

    TRUNC_DIV_EXPR : auto()
        Truncated division expression (`lhs / rhs`).

    TRUNC_MOD_EXPR : auto()
        Truncated modulo expression (`lhs % rhs`).

    LSHIFT_EXPR : auto()
        Left shift expression (`lhs << rhs`).

    RSHIFT_EXPR : auto()
        Right shift expression (`lhs >> rhs`).

    RROTATE_EXPR : auto()
        Right rotate expression (`(((x) << (b)) | ((x) >> (32 - (b))))`).

    NEGATE_EXPR : auto()
        Negate expression (`~lhs`).

    MIN_EXPR : auto()
        Minimum expression (`(lhs < rhs)`).

    MAX_EXPR : auto()
        Maximum expression (`(lhs > rhs)`).

    POINTER_PLUS_EXPR : auto()
        Pointer plus expression (`lhs + rhs`).
        This node represents pointer arithmetic.
        The first operand is always a pointer/reference type.
        The second operand is always an unsigned integer type compatible with sizetype.
        This is the only binary arithmetic operand that can operate on pointer types.


    FIX_TRUNC_EXPR : auto()
        Fix trunc expression (conversion of floating-point value to an integer).
        These nodes represent conversion of a floating-point value to an integer.
        The single operand will have a floating-point type, while the complete
        expression will have an integral (or boolean) type.
        The operand is rounded towards zero.

    dst[bool, int] = (floating-point type)rhs

    UNDEF : auto()
        Undefined expression.
    """  # noqa: E501

    NO_EXPR = auto()
    MULT_EXPR = auto()
    PLUS_EXPR = auto()
    MINUS_EXPR = auto()
    RDIV_EXPR = auto()
    MOD_EXPR = auto()
    DIV_EXPR = auto()
    GREATER_THAN_OR_EQUAL_EXPR = auto()
    GREATER_THAN_EXPR = auto()
    LESS_THAN_EXPR = auto()
    LESS_THAN_OR_EQUAL_EXPR = auto()
    EQUAL_EXPR = auto()
    NOT_EQUAL_EXPR = auto()
    BITWISE_AND_EXPR = auto()
    BITWISE_EXCLUSIVE_OR_EXPR = auto()
    BITWISE_INCLUSIVE_OR_EXPR = auto()
    BITWISE_NOT_EXPR = auto()
    TRUNC_DIV_EXPR = auto()
    TRUNC_MOD_EXPR = auto()
    LSHIFT_EXPR = auto()
    RSHIFT_EXPR = auto()
    RROTATE_EXPR = auto()
    NEGATE_EXPR = auto()
    MIN_EXPR = auto()
    MAX_EXPR = auto()
    POINTER_PLUS_EXPR = auto()
    FIX_TRUNC_EXPR = auto()
    UNDEF = auto()

    def __str__(self):
        return f"{self.name}"

    def decompile(self):
        """Generate a human-readable or high-level representation.

        Returns
        -------
        str
            A string representation of the expression.
        """
        return PettyPrinter.decompile(self)
