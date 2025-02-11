.. _arrays:

Working with Arrays
===================

All step variables in Eptalights are represented as **tokenized operands** (`TokenizedOperandModel`). This means that every variable retains its full contextual details, including associated symbols (e.g., array indices) and constants, making it easier to perform fine-grained analysis.


1. Array Basics
---------------

Let’s examine the first instruction in the function ``main`` from the file ``07_array.cc``. The instruction is an assignment (``OpType.ASSIGN``), represented internally by ``EGimpleIRAssignModel``, and assigns the constant ``10`` to the first element of the array ``arr``.

.. code-block:: python

	fn = api.get_function_by_id(fid="/example/src/07_array.cc:main#1")
	step_index = 0
	step = fn.steps[step_index]

	print(f"{step.op} {step.decompile()}")

	# output
	"""
	ASSIGN  arr[0] = 10;
	"""


Even though the destination (``dst``) of this assignment is an array element (``arr[0]``), you can easily extract just the base variable name (``arr``) without dealing with the additional array index details. You can also retrieve all variables defined at this step:

.. code-block:: python

	print(step.dst.variable_name)
	print(step.dst.ssa_name)

	# output
	"""
	arr
	arr_0
	"""

	print(step.variables_defined_here)
	print(step.ssa_variables_defined_here)

	# output
	"""
	['arr']
	['arr_0']
	"""


As discussed in :ref:`tokenized_operands`, each ``TokenizedOperandModel`` includes a list of **tokens** that represent every syntactic component of the operand.

.. code-block:: python

	print(step.dst.tokens)

	# output
	"""
	[TokenModel(token_type=<TokenType.IS_VARIABLE: 'IS_VARIABLE'>, 
	            is_base_variable=True, 
	            code_name='var_decl', 
	            value='arr_0', 
	            value_extended='arr', 
	            discovery_depth=1),
	 TokenModel(token_type=<TokenType.IS_SYMBOL: 'IS_SYMBOL'>, 
	            is_base_variable=False, 
	            code_name='array_ref', 
	            value='[', 
	            value_extended=None, 
	            discovery_depth=1),
	 TokenModel(token_type=<TokenType.IS_CONSTANT: 'IS_CONSTANT'>, 
	            is_base_variable=False, 
	            code_name='integer_cst', 
	            value='0', 
	            value_extended=None, 
	            discovery_depth=1),
	 TokenModel(token_type=<TokenType.IS_SYMBOL: 'IS_SYMBOL'>, 
	            is_base_variable=False, 
	            code_name='array_ref', 
	            value=']', 
	            value_extended=None, 
	            discovery_depth=1)]
	"""


For better readability, you can use ``pretty_print_tokens()`` to visualize the tokens in a structured format:

.. code-block:: python

	step.dst.pretty_print_tokens()

	# output
	"""
	[{'code_name': 'var_decl',
	  'discovery_depth': 1,
	  'is_base_variable': True,
	  'token_type': <TokenType.IS_VARIABLE: 'IS_VARIABLE'>,
	  'value': 'arr_0',
	  'value_extended': 'arr'},
	 {'code_name': 'array_ref',
	  'discovery_depth': 1,
	  'is_base_variable': False,
	  'token_type': <TokenType.IS_SYMBOL: 'IS_SYMBOL'>,
	  'value': '[',
	  'value_extended': None},
	 {'code_name': 'integer_cst',
	  'discovery_depth': 1,
	  'is_base_variable': False,
	  'token_type': <TokenType.IS_CONSTANT: 'IS_CONSTANT'>,
	  'value': '0',
	  'value_extended': None},
	 {'code_name': 'array_ref',
	  'discovery_depth': 1,
	  'is_base_variable': False,
	  'token_type': <TokenType.IS_SYMBOL: 'IS_SYMBOL'>,
	  'value': ']',
	  'value_extended': None}]
	 """


While it's possible to manually process `TokenizedOperandModel` instances by iterating through their tokens, **Eptalights** provides a suite of **helper functions** to simplify working with complex variables, such as arrays. These helpers abstract away the need to manually filter tokens, especially when dealing with multi-dimensional arrays or nested expressions.

Let’s revisit the previous example involving an assignment to an array element (``arr[0]``). Here's how you can leverage the helper functions to work with the array indices.

.. code-block:: python

	print(step.dst.decompile())

	# output
	"""
	arr[0]
	"""

The ``array_index_tokens_iter()`` method provides a clean way to iterate over **array index tokens** without manually parsing symbols like ``[`` and ``]``.

.. code-block:: python

	for arr_idx_token in step.dst.array_index_tokens_iter():
	    print(arr_idx_token)

	# output
	"""
	token_type=<TokenType.IS_CONSTANT: 'IS_CONSTANT'> 
	is_base_variable=False 
	code_name='integer_cst' 
	value='0' 
	value_extended=None 
	discovery_depth=1
	"""

- **`IS_CONSTANT`**: Indicates that the array index is a constant (``0`` in this case).
- **`code_name='integer_cst'`**: Refers to the GIMPLE IR classification for integer constants.

If you're interested only in the **values** of the array indices (e.g., ``0``, ``1``, etc.), you can simplify further using:

.. code-block:: python

	for arr_idx_token in step.dst.array_index_tokens_iter():
		print(arr_idx_token.value)

	# output
	"""
	0
	"""

	for arr_idx_value in step.dst.array_index_token_values_iter():
	    print(arr_idx_value)

	# output
	"""
	0
	"""


2. Accessing a Specific Array Index
-----------------------------------

If you're working with multi-dimensional arrays or need a specific index, you can retrieve it directly using ``array_index_token_at_index(index)``.

.. code-block:: python

	arr_idx_token = step.dst.array_index_token_at_index(0)
	print(arr_idx_token)

	# output
	"""
	token_type=<TokenType.IS_CONSTANT: 'IS_CONSTANT'> 
	is_base_variable=False 
	code_name='integer_cst' 
	value='0' 
	value_extended=None 
	discovery_depth=1
	"""

This is particularly useful when dealing with nested arrays like ``arr[2][3]``. For example:

.. code-block:: python

	# Assuming the step represents arr[2][3]
	first_idx_token = step.dst.array_index_token_at_index(0)  # Retrieves '2'
	second_idx_token = step.dst.array_index_token_at_index(1) # Retrieves '3'

	print(first_idx_token.value, second_idx_token.value)

	# output
	"""
	2 3
	"""

When iterating through ``ASSIGN`` steps in a function, you might find that some array indices are variables. Here’s an example where step index ``17`` uses a variable (``i_5``) as an array index.

.. code-block:: python

	for step in fn.steps:
	    if step.op == models.OpType.ASSIGN:
	        if step.dst.get_total_array_index_tokens() > 0:
	            print(step.step_index, step.dst.decompile())

	# output
	"""
	0 arr[0]
	1 arr[1]
	2 arr[2]
	3 arr[3]
	4 arr[4]
	5 arr1[0]
	6 arr1[1]
	7 arr1[2]
	8 arr1[3]
	9 arr1[4]
	10 arr2[0]
	17 arr2[i]
	"""

In **step 17**, the array ``arr2_0`` uses ``i_5`` as its index instead of a constant. Let's dive deeper into **step index 17** to analyze the variable-based index:

.. code-block:: python

	step17 = fn.steps[17]
	print(step17.decompile())

	# output
	"""
	arr2[i_5]
	"""

	print(step17.dst.variable_name)  # Base variable name
	print(step17.dst.ssa_name)       # SSA variable name

	# output
	"""
	arr2
	arr2_0
	"""

	print(step17.variables_defined_here)
	print(step17.ssa_variables_defined_here)

	# output
	"""
	['arr2']
	['arr2_0']
	"""

To get the token for the array index (which is a variable in this case):

.. code-block:: python

	arr_idx_token = step17.dst.array_index_token_at_index(0)
	print(arr_idx_token)

	# output
	"""
	token_type=<TokenType.IS_VARIABLE: 'IS_VARIABLE'> 
	is_base_variable=False 
	code_name='ssa_name' 
	value='i_5' 
	value_extended='i' 
	discovery_depth=1
	"""

	print(arr_idx_token.value)          # SSA name
	print(arr_idx_token.value_extended) # Original variable name

	# output
	"""
	i_5
	i
	"""

To check where a variable (like ``i``) is used, including whether it appears **inside an array**:

.. code-block:: python

	array_step_index = 17
	varname = 'i'
	ssa_varname = 'i_5'

	var = fn.variable_manager.get(varname)
	ssa_var = var.unique_ssa_variables.get(ssa_varname)

	print(ssa_var.variable_used_at_steps)
	print(array_step_index in ssa_var.variable_used_at_steps)

	# output
	"""
	[12, 13, 17, 18]
	True
	"""

This tells us that ``i_5`` is used in steps 12, 13, 17, and 18.

To find out exactly **which arrays** the variable is used in, we can query `used_inside_other_tokenized_operand_tokens_at_step`:

.. code-block:: python

	for step_index, array_ssa_varname in ssa_var.used_inside_other_tokenized_operand_tokens_at_step.items():
	    print(f"{varname} is used at step_index={step_index} inside array ssa_variable - {array_ssa_varname}")

	# output
	"""
	i is used at step_index=17 inside array ssa_variable - ['arr2_0']
	"""

- **Use `variable_used_at_steps`** when you need to find **all occurrences** of a variable in the function.
- **Use `used_inside_other_tokenized_operand_tokens_at_step`** when you want to know if a variable is specifically used as an **array index** (or inside another tokenized operand).

This distinction is crucial for tasks like **loop optimization**, **dependency analysis**, or **detecting dynamic array accesses**.


