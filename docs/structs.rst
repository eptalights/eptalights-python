.. _structs:

Working with Structs
====================

1. Struct Basics
----------------

Structs are handled in a manner similar to :ref:`arrays`, especially when attributes are accessed through array indexing. Let's break down the struct handling using the ``ASSIGN`` example provided.

.. code-block:: python

	fn = api.get_function_by_id(fid="/example/src/06_struct.cc:main#1")
	step = fn.steps[3]
	print(f"{step.op} {step.decompile()}")

	# output
	"""
	ASSIGN 	$T1 = &emp[i].Name;
	"""

Here’s what’s happening:
- **`emp[i]`** accesses the ``i``-th element of the ``emp`` array (which contains structs).
- **`.Name`** accesses the ``Name`` attribute of that struct.
- **`&emp[i].Name`** takes the address of the ``Name`` attribute.
- This address is assigned to the **SSA variable** ``$T1``.

Even though the full variable is complex (``&emp_0[i_5].Name_0``), you can easily access the **main variable name** without dealing with all the nested details.

.. code-block:: python

	print(step.src.lhs.variable_name)

	# output
	"""
	emp
	"""

This simplifies working with variables unless you need to perform deep introspection.

The **variables used in this step** are both the array variable ``emp`` and the index variable ``i``. Even though ``i`` isn't explicitly written in the assignment expression, it is used **as an array index**.

.. code-block:: python

	print(step.variables_used_here)

	# output
	"""
	['i', 'emp']
	"""

	print(step.ssa_variables_used_here)

	# output
	"""
	['i_5', 'emp_0']
	"""

You can inspect the tokens of complex struct variables to understand their components better. This helps in analyzing expressions with nested structures, arrays, and attributes.

To view all tokens for the variable ``emp_0`` (from the earlier ``ASSIGN`` example), you can use ``pretty_print_tokens()``.

.. code-block:: python

	step.src.lhs.pretty_print_tokens()

	# output
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
	  'value': 'emp_0',
	  'value_extended': 'emp'},
	 {'code_name': 'array_ref',
	  'discovery_depth': 1,
	  'is_base_variable': False,
	  'token_type': <TokenType.IS_SYMBOL: 'IS_SYMBOL'>,
	  'value': '[',
	  'value_extended': None},
	 {'code_name': 'ssa_name',
	  'discovery_depth': 1,
	  'is_base_variable': False,
	  'token_type': <TokenType.IS_VARIABLE: 'IS_VARIABLE'>,
	  'value': 'i_5',
	  'value_extended': 'i'},
	 {'code_name': 'array_ref',
	  'discovery_depth': 1,
	  'is_base_variable': False,
	  'token_type': <TokenType.IS_SYMBOL: 'IS_SYMBOL'>,
	  'value': ']',
	  'value_extended': None},
	 {'code_name': 'component_ref',
	  'discovery_depth': 1,
	  'is_base_variable': False,
	  'token_type': <TokenType.IS_SYMBOL: 'IS_SYMBOL'>,
	  'value': '.',
	  'value_extended': None},
	 {'code_name': 'field_decl',
	  'discovery_depth': 1,
	  'is_base_variable': False,
	  'token_type': <TokenType.IS_ATTRIBUTE: 'IS_ATTRIBUTE'>,
	  'value': 'Name_0',
	  'value_extended': 'Name'}]
	"""

If you want to **extract the struct attributes** (like ``Name``), you can iterate over the tokens and filter for attributes using ``IS_ATTRIBUTE``.

.. code-block:: python

	for token in step.src.lhs.tokens:
	    if token.token_type == models.TokenType.IS_ATTRIBUTE:
	        print(f"ssa_varname={token.value}, varname={token.value_extended}")

	# output
	"""
	ssa_varname=Name_0, varname=Name
	"""

When dealing with **nested struct attributes** like ``emp[10].attr.history.name``, manually tracking each accessed attribute using loops can get cumbersome. To simplify this, you can use:

- **`record_attributes_defined_at_steps`**: Shows where attributes are **defined** in the code.
- **`record_attributes_used_at_steps`**: Shows where attributes are **used**.

These properties work regardless of how the attributes are accessed (via ``.`` or ``->``), and they present the full attribute chain in a simple, readable format.

To viewing where struct attributes Are defined and used, extract the SSA variable from a step and inspect the attributes it defines and uses.

.. code-block:: python

	varname = step.src.lhs.variable_name
	ssa_varname = step.src.lhs.ssa_name

	ssa_variable = fn.variable_manager.get(varname).unique_ssa_variables.get(ssa_varname)

	print(ssa_variable.record_attributes_defined_at_steps)
	print(ssa_variable.record_attributes_used_at_steps)

	# output
	"""
	{2: ['#employeeID'], 7: ['#WeekAttendence']}
	{3: ['#Name'], 13: ['#Name'], 14: ['#employeeID'], 19: ['#WeekAttendence']}
	"""

- **Defined Attributes**:
	- Step ``2``: ``#employeeID`` defined.
	- Step ``7``: ``#WeekAttendence`` defined.
- **Used Attributes**:
  	- Step ``3``: ``#Name`` used.
  	- Step ``13``: ``#Name`` used again.
  	- Step ``14``: ``#employeeID`` used.
  	- Step ``19``: ``#WeekAttendence`` used.


To check which **specific attributes** are accessed at step index ``3``:

.. code-block:: python

	step = fn.steps[3]

	varname = step.src.lhs.variable_name
	ssa_varname = step.src.lhs.ssa_name

	ssa_variable = fn.variable_manager.get(varname).unique_ssa_variables.get(ssa_varname)
	print(ssa_variable.record_attributes_used_at_steps.get(step.step_index))

	# output
	"""
	['#Name']
	"""

- This indicates that the attribute **`Name`** is accessed at step `3`.

- **High-Level Access**: You can easily get the primary variable (``emp``) without handling the full complexity of the struct access (``&emp[i].Name``).
- **Implicit Variable Usage**: Variables like ``i``, which are used as array indices, are tracked in ``variables_used_here`` even though they aren't explicitly shown in the assignment statement.
- **SSA Tracking**: The SSA names (``i_5``, ``emp_0``) help in tracing variable versions through the code, useful for optimizations and analysis.
- **Token Inspection**: You can deconstruct complex variables (arrays, structs) into individual tokens to analyze them at a granular level.
- **Attribute Filtering**: By identifying tokens with ``IS_ATTRIBUTE``, you can easily extract struct attributes.
- **Simplified Handling**: Despite complex expressions like ``&emp[i].Name``, you can focus on specific parts (like ``Name``) without manually parsing the expression.

2. Handling Deeply Nested Attributes
------------------------------------

For **nested attributes** like ``emp[10].attr.history->name``, the system simplifies the path using ``#`` to separate levels, regardless of whether ``.`` or ``->`` is used:

.. code-block:: python

	print(ssa_variable.record_attributes_used_at_steps.get(step.step_index))

	# output
	"""
	['#attr#history#name']
	"""

This shows the full chain of attribute access:
- ``emp[10].attr.history.name`` → ``#attr#history#name``

- **Simplified Attribute Tracking**: No need for complex loops to track nested attributes; use ``record_attributes_used_at_steps`` and ``record_attributes_defined_at_steps``.
- **Uniform Notation**: Whether attributes are accessed via ``.`` or ``->``, the output format remains consistent using ``#`` separators.
- **Detailed Step Insight**: Easily find where specific struct attributes are used or defined within function steps.

This approach is powerful for code analysis, especially when dealing with complex data structures like nested structs!

