from enum import Enum, auto
from eptalights_code.core.printer import PrettyPrinter


class AutoStrEnum(str, Enum):
    @staticmethod
    def _generate_next_value_(
        name: str, start: int, count: int, last_values: list
    ) -> str:
        return name


class VarType(AutoStrEnum):
    """Represents the type of a variable in program analysis.

    Attributes
    ----------

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

    def __str__(self) -> str:
        """Returns the string representation of the enumeration value."""
        return self.name


class TokenType(AutoStrEnum):
    """
    An enumeration representing the token type of an element.

    Attributes
    ----------

    IS_UNDEF
        Represents an undefined token type.

    IS_VARIABLE
        Represents a variable token type.
        Example: Array access used with a variable index,
        e.g., `a[n]` where `a` and `n` are variables.

    IS_CONSTANT
        Represents a constant token type.
        Example: Array access used with a constant index, e.g., `a[10]`.

    IS_SYMBOL
        Represents a symbol token type.
        Example: Symbols like `[`, `]`, `*`, `.`, `->`, `&`, etc.

    IS_ATTRIBUTE
        Represents an attribute token type.
        Example: Struct field access, e.g., `st.data`, `st->data`.

    IS_TYPE
        Represents a type token type.
        Example: Type declaration, e.g., `struct FILE fp`.

    IS_FUNCTION
        Represents a function token type.
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
        Represents both a variable and a function token type.
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
    Enumeration of operation types.

    Attributes
    ----------

    NOP
        No operation.
    ASSIGN
        Assignment operation.
    CALL
        Function or method call.
    RETURN
        Return from a function or method.
    COND
        Conditional operation (e.g., if-else).
    GOTO
        Unconditional jump to another location.
    SWITCH
        Switch-case operation.
    LABEL
        Label for jump or branch operations.
    """

    NOP = auto()
    ASSIGN = auto()
    CALL = auto()
    RETURN = auto()
    COND = auto()
    GOTO = auto()
    SWITCH = auto()
    LABEL = auto()

    def __str__(self) -> str:
        """
        Returns the string representation of the operation type.

        Returns
        -------
        str
            The name of the operation type.
        """
        return f"{self.name}"


class ExprType(AutoStrEnum):
    """
    Numeration of expression types.

    Attributes
    ----------

    NO_EXPR
        No expression.

    MULT_EXPR
        Multiplication expression (`lhs * rhs`).

    PLUS_EXPR
        Addition expression (`lhs + rhs`).

    MINUS_EXPR
        Subtraction expression (`lhs - rhs`).

    RDIV_EXPR
        Right division expression (`lhs / rhs`).

    DIV_EXPR
        Division expression (`lhs / rhs`).

    MOD_EXPR
        Modulo expression (`lhs % rhs`).

    GREATER_THAN_OR_EQUAL_EXPR
        Greater than or equal to expression (`lhs >= rhs`).

    GREATER_THAN_EXPR
        Greater than expression (`lhs > rhs`).

    LESS_THAN_EXPR
        Less than expression (`lhs < rhs`).

    LESS_THAN_OR_EQUAL_EXPR
        Less than or equal to expression (`lhs <= rhs`).

    EQUAL_EXPR
        Equal to expression (`lhs == rhs`).

    NOT_EQUAL_EXPR
        Not equal to expression (`lhs != rhs`).

    BITWISE_AND_EXPR
        Bitwise AND expression (`lhs && rhs`).

    BITWISE_EXCLUSIVE_OR_EXPR
        Bitwise exclusive OR expression (`lhs & rhs`).

    BITWISE_INCLUSIVE_OR_EXPR
        Bitwise inclusive OR expression (`lhs | rhs`).

    BITWISE_NOT_EXPR
        Bitwise NOT expression (`~lhs`).

    TRUNC_DIV_EXPR
        Truncated division expression (`lhs / rhs`).

    TRUNC_MOD_EXPR
        Truncated modulo expression (`lhs % rhs`).

    LSHIFT_EXPR
        Left shift expression (`lhs << rhs`).

    RSHIFT_EXPR
        Right shift expression (`lhs >> rhs`).

    RROTATE_EXPR
        Right rotate expression (`(((x) << (b)) | ((x) >> (32 - (b))))`).

    NEGATE_EXPR
        Negate expression (`~lhs`).

    MIN_EXPR
        Minimum expression (`(lhs < rhs)`).

    MAX_EXPR
        Maximum expression (`(lhs > rhs)`).

    POINTER_PLUS_EXPR
        Pointer plus expression (`lhs + rhs`).
        This node represents pointer arithmetic.
        The first operand is always a pointer/reference type.
        The second operand is always an unsigned integer type compatible with sizetype.
        This is the only binary arithmetic operand that can operate on pointer types.

    FIX_TRUNC_EXPR
        Fix trunc expression (conversion of floating-point value to an integer).
        These nodes represent conversion of a floating-point value to an integer.
        The single operand will have a floating-point type, while the complete
        expression will have an integral (or boolean) type.
        The operand is rounded towards zero.

        dst[bool, int] = (floating-point type)rhs

    REALPART_EXPR
        TODO

    IMAGPART_EXPR
        TODO

    ABS_EXPR
        TODO

    ABSU_EXPR
        These nodes represent the absolute value of the single operand in equivalent
        unsigned type such that ABSU_EXPR of TYPE_MIN is well defined.

    SPACESHIP_EXPR
        Maximum expression (`(lhs <=> rhs)`).

    UNDEF
        Undefined expression.
    """  # noqa: E501

    NO_EXPR = auto()
    MULT_EXPR = auto()
    PLUS_EXPR = auto()
    MINUS_EXPR = auto()
    RDIV_EXPR = auto()
    DIV_EXPR = auto()
    MOD_EXPR = auto()
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
    REALPART_EXPR = auto()
    IMAGPART_EXPR = auto()
    ABS_EXPR = auto()
    ABSU_EXPR = auto()
    SPACESHIP_EXPR = auto()
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
        return PrettyPrinter.decompile(self)


class DataflowActionStatusType(AutoStrEnum):
    """
    Represents the lifecycle status of data in the dataflow process.

    Attributes
    ----------
    LOCAL_PENDING
        Data is stored locally and waiting to be sent to the API.
    QUEUED
        Data has been received by the server and is queued for processing.
    PROCESSING
        Data is currently being processed by the server.
    DONE
        Data has been fully processed and the workflow is complete.
    UNDEF
        Undefined status, used as a fallback or error state.
    """

    LOCAL_PENDING = auto()
    REMOTE_PROCESSING = auto()
    DONE = auto()

    def __str__(self) -> str:
        """Returns the string representation of the enumeration value."""
        return self.name
