.. _tokenized_operands:

Working with Tokenized Operands
===============================

All variables and constants used inside a step orr instruction of a function are tokenized operands.  

By leveraging tokenized operands and their underlying tokens, you can perform precise, granular analysis of code structures, preserving all semantic and syntactic information necessary for comprehensive static analysis.


1. Basics of Tokenized Operands
-------------------------------

**Tokenized operands** are a specialized data type composed of individual tokens that encapsulate all syntactic details, including symbols, constants, and variable references. This design ensures that every element of the operand whether it’s a symbol like ``&`` or a constant is preserved with complete fidelity.

A tokenized operand can represent either:

1. **Variables** (e.g. - ``p``), or  
2. **Non-variables** (e.g. - constants like ``5`` or expressions like ``&`` in ``&c``).

Consider the following step extracted from a function in the Eptalights API:

.. code-block:: python

	fn = api.get_function_by_id(fid="/example/src/01_print_pointer_value.cc:main#1")
	step_index = 1
	step = fn.steps[step_index]

	print(f"{step.op} {step.decompile()}")

	# output
	"""
	ASSIGN  p = &c;
	"""

This ``ASSIGN`` operation has:

1. The **left-hand side (LHS)** as ``p`` (the defined operand).
2. The **right-hand side (RHS)** as ``&c`` (the used operand).


To access the defined operands (on the left-hand side), you can use ``step.defined_tokenized_operands`` or directly refer to ``step.dst``:

.. code-block:: python
	
	for t_operand in step.defined_tokenized_operands:
	    print(f"operand={t_operand.decompile()}, operand_type={type(t_operand)}")

	# output
	"""
	operand=p, operand_type=<class 'eptalights.models.egimple.tokenized_operand.TokenizedOperandModel'>
	"""

	# Alternatively:
	print(f"operand={step.dst.decompile()}, operand_type={type(step.dst)}")

	# output
	"""
	operand=p, operand_type=<class 'eptalights.models.egimple.tokenized_operand.TokenizedOperandModel'>
	"""


For used operands (on the right-hand side), access them via ``step.used_tokenized_operands`` or directly through ``step.src.lhs``:

.. code-block:: python

	print(step.src.lhs.tokens)

	# output 
	"""
	[TokenModel(token_type=<TokenType.IS_SYMBOL: 'IS_SYMBOL'>, is_base_variable=False, code_name='addr_expr', value='&', value_extended=None, discovery_depth=1), TokenModel(token_type=<TokenType.IS_VARIABLE: 'IS_VARIABLE'>, is_base_variable=True, code_name='var_decl', value='c_0', value_extended='c', discovery_depth=1)]
	"""

	# Alternatively:
	print(step.dst.tokens)

	# output 
	"""
	[TokenModel(token_type=<TokenType.IS_VARIABLE: 'IS_VARIABLE'>, is_base_variable=True, code_name='ssa_name', value='p_4', value_extended='p', discovery_depth=0)]
	"""


2. Inspecting Tokens within Tokenized Operands
----------------------------------------------

Since tokenized operands are collections of tokens, let’s examine the tokens for both ``p`` and ``&c``:

.. code-block:: python

	print(step.dst.tokens)  # Tokens for 'p'

	# Output:
	"""
	[TokenModel(token_type=<TokenType.IS_VARIABLE: 'IS_VARIABLE'>, 
	            is_base_variable=True, 
	            code_name='ssa_name', 
	            value='p_4', 
	            value_extended='p', 
	            discovery_depth=0)]
	"""

	print(step.src.lhs.tokens)  # Tokens for '&c'

	# Output:
	"""
	[TokenModel(token_type=<TokenType.IS_SYMBOL: 'IS_SYMBOL'>, 
	            is_base_variable=False, 
	            code_name='addr_expr', 
	            value='&', 
	            value_extended=None, 
	            discovery_depth=1), 
	 TokenModel(token_type=<TokenType.IS_VARIABLE: 'IS_VARIABLE'>, 
	            is_base_variable=True, 
	            code_name='var_decl', 
	            value='c_0', 
	            value_extended='c', 
	            discovery_depth=1)]
	"""

For a more readable output, you can use the `pretty_print_tokens()` method:

.. code-block:: python

	# Pretty print tokens for '&c'
	step.src.lhs.pretty_print_tokens()

	# Output:
	"""
	[{'code_name': 'addr_expr',
	  'discovery_depth': 1,
	  'is_base_variable': False,
	  'token_type': <TokenType.IS_SYMBOL: 'IS_SYMBOL'>,
	  'value': '&',
	  'value_extended': None},
	 {'code_name': 'var_decl',
	  'discovery_depth': 1,
	  'is_base_variable': True,
	  'token_type': <TokenType.IS_VARIABLE: 'IS_VARIABLE'>,
	  'value': 'c_0',
	  'value_extended': 'c'}]
	"""

	# Pretty print tokens for 'p'
	step.dst.pretty_print_tokens()

	# Output:
	"""
	[{'code_name': 'ssa_name',
	  'discovery_depth': 0,
	  'is_base_variable': True,
	  'token_type': <TokenType.IS_VARIABLE: 'IS_VARIABLE'>,
	  'value': 'p_4',
	  'value_extended': 'p'}]
	"""

Or we could just print the Pseudo-C code with the ``decompile()`` method:

.. code-block:: python

	print(step.src.lhs.decompile())

	# output
	"""
	&c
	"""

	print(step.dst.decompile())

	# output
	"""
	p
	"""


3. Analyzing Constant Tokenized Operands
----------------------------------------

In addition to variables and symbols, **constants** are also represented as tokenized operands. This ensures that constant values, such as string literals or numeric constants, retain their complete syntactic and semantic information during analysis.

Let’s examine an example where a string constant is passed as an argument to the `printf` function:

.. code-block:: python

	fn = api.get_function_by_id(fid="/example/src/03_scanf_to_malloc.cc:main#1")
	step_index = 1
	step = fn.steps[step_index]

	print(f"{step.op} {step.decompile()}")

	# output
	"""
	CALL    printf ( R"("Enter number of elements: ")" );
	"""


In this function call, the first argument is a **raw string literal** (`R"("Enter number of elements: ")"`). We can access and analyze this constant tokenized operand using `step.fargs[0]`.

To retrieve and inspect the constant operand:

.. code-block:: python

	# Decompile the first function argument (the constant string)
	print(step.fargs[0].decompile())

	# This output shows the raw string literal passed to ``printf``
	"""
	R"("Enter number of elements: ")"
	"""

Now, let’s explore the underlying tokens of this constant operand:

.. code-block:: python

	print(step.fargs[0].tokens)

	# output
	"""
	[TokenModel(token_type=<TokenType.IS_CONSTANT: 'IS_CONSTANT'>, 
            is_base_variable=False, 
            code_name='string_cst', 
            value='"Enter number of elements: "', 
            value_extended=None, 
            discovery_depth=1)]
    """

- **`token_type=<TokenType.IS_CONSTANT>`**: Indicates that this token represents a constant.
- **`code_name='string_cst'`**: This refers to the GCC GIMPLE IR classification for string constants.
- **`value='"Enter number of elements: "'`**: Holds the actual string literal value.
- **`is_base_variable=False`**: Since this is a constant and not a variable, ``is_base_variable`` is set to ``False``.
- **`discovery_depth=1`**: Represents how deeply nested the token is within the IR tree structure.

Constant tokenized operands, such as string literals, are treated with the same structural detail as variables and symbols. This allows for comprehensive analysis and manipulation, preserving their exact representation within the intermediate representation (IR).


4. Token Structure and Key Attributes
-------------------------------------

Each token is an instance of the :class:`~eptalights.models.egimple.tokenized_operand.TokenModel`. Important fields include:

- **`value`**: The actual value of the token (e.g., ``&``, ``c_0``, ``p_4``). For variables, this holds the SSA version of the variable.
- **`value_extended`**: The base name of the variable, without the SSA suffix (e.g., ``c``, ``p``).
- **`token_type`**: The type of token, defined in :class:`~eptalights.models.egimple.enum_types.TokenType`. This can represent symbols, variables, constants, or attributes (in the case of structs).
- **`is_base_variable`**: A boolean indicating whether the token represents the main variable. This is particularly useful when dealing with nested variable references like ``main_var[another_var]``.
- **`code_name`** and **`discovery_depth`**: These reflect GCC GIMPLE IR-specific properties and are primarily useful for debugging or advanced GIMPLE analysis.


5. More Docs on How to use Tokenized Operands
---------------------------------------------

* :ref:`arrays`
* :ref:`structs`










