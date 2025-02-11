.. _functions:

Working with Functions
======================

Data model or structure for function - :class:`~eptalights.models.egimple.function.FunctionModel`


1. listing functions
--------------------

Listing all functions along with their corresponding source filenames in the project.

.. code-block:: python
	
	for fn in api.search_functions():
	    print(f"name={fn.name}, filepath={fn.filepath}")

	# output
	"""
	name=main, filepath=/example/src/07_array.cc
	name=main, filepath=/example/src/07_array.cc
	name=main, filepath=/example/src/14_struct_arithmetic.cc
	name=addNumbers, filepath=/example/src/14_struct_arithmetic.cc
	"""


Each Function comes a unique ID called ``fid``. The ``fid`` is named based on the file path, the function name and its function overloading count.

.. code-block:: python

	for fn in api.search_functions():
	    print(f"fid={fn.fid}")

	"""
	fid=/example/src/07_array.cc:main#1
	fid=/example/src/14_struct_arithmetic.cc:addNumbers#1
	fid=/example/src/14_struct_arithmetic.cc:main#1
	fid=/example/src/10_union.cc:main#1
	fid=/example/src/03_scanf_to_malloc.cc:main#1
	"""


2. get function by id
---------------------

We can retrieve a function by its ``fid``.

.. code-block:: python

	fn = api.get_function_by_id(fid="/example/src/07_array.cc:main#1")
	print(f"name={fn.name}, filepath={fn.filepath}")

	"""
	name=main, filepath=/example/src/07_array.cc
	"""


3. get functions by file path
-----------------------------

Get all functions of a specific file path.

.. code-block:: python

	for fn in api.get_functions_by_filepath(filepath="/example/src/07_array.cc"):
	    print(f"name={fn.name}, filename={fn.filepath}")

	# output
	"""
	name=main, filename=/example/src/07_array.cc
	"""


4. search functions
-------------------

Searching functions by ``filter_by_name``, ``filter_by_filepath`` or ``filter_by_classname``. 

.. code-block:: python

	for fn in api.search_functions(filter_by_name="main"):
	    print(f"name={fn.name}, filepath={fn.filepath}")

	# output
	"""
	name=main, filepath=/example/src/07_array.cc
	name=main, filepath=/example/src/14_struct_arithmetic.cc
	name=main, filepath=/example/src/10_union.cc
	name=main, filepath=/example/src/03_scanf_to_malloc.cc
	name=main, filepath=/example/src/16_buffer_overflow.cc
	name=main, filepath=/example/src/02_pointer_arithmetic.cc
	...[redacted]
	"""

	for fn in api.search_functions(filter_by_filepath="07_array.cc"):
	    print(f"name={fn.name}, filepath={fn.filepath}")

	# output
	"""
	name=main, filepath=/example/src/07_array.cc
	"""


5. dumping function Pseudo-C code
---------------------------------

Dumping the high level Pseudo-C code off the a function. Remember everything you see in the Pseudo-C dump can easily be accessed from the python API.

.. code-block:: python

	fn = api.get_function_by_id(fid="/example/src/07_array.cc:main#1")
	print(fn.decompile())

	# output
	"""
	main  (  )
	{
		<bb 2> :
		arr[0] = 10;
		arr[1] = 20;
		arr[2] = 30;
		arr[3] = 40;
		arr[4] = 50;
		arr1[0] = 1;
		arr1[1] = 2;
		arr1[2] = 3;
		arr1[3] = 4;
		arr1[4] = 5;
		arr2[0] = 1.0e+0;
		i = 0;

		<bb 3> :
		if ( i > 4 )
			goto <bb 5>;
		else
			goto <bb 4>;

		<bb 4> :
		$T1 = i;
		$T2 = $T1;
		$T3 = $T2 * 2.100000000000000088817841970012523233890533447265625e+0;
		$T4 = $T3;
		arr2[i] = $T4;
		i = i + 1;

		<bb 5> :
		$T22 = 0;
		arr = R"({)"R"(CLOBBER)"R"(})";
		arr1 = R"({)"R"(CLOBBER)"R"(})";
		arr2 = R"({)"R"(CLOBBER)"R"(})";

		<bb 6> :
		nop;
		return $T22;
	}
	"""


Every data objects are basically Pydantic models in our Python Library.  
Therefore dumping the informal representation or ``__str__`` will give you the Pydantic string representation.  
Also that means you have can take advance of all the Pydantic features like model_dumps, etc.


.. code-block:: python

	fn = api.get_function_by_id(fid="/example/src/07_array.cc:main#1")
	print(fn)

	fid='/example/src/07_array.cc:main#1' name='main' filepath='/example/src/07_array.cc' class_name=None variable_manager=VariableManagerModel(function_args=[], local_variables=['i', 'arr2', 'arr1', 'arr', '68952813'], tmp_variables=['$T1', '$T2', '$T3', '$T4', '$T22'], return_variables=['$T22'], variables={'i': VariableModel(vid='/example/src/07_array.cc:main:i', name='i', vartype=<VarType.LOCAL_VARIABLE: 'LOCAL_VARIABLE'>, unique_ssa_variables={'i_19': SSAVariableModel(ssa_name='i_19', ssa_version=19, variable_name='i', variable_defined_at_steps=[11], variable_used_at_steps=[], variable_used_in_callsites=[], record_attributes_defined_at_steps={}, record_attributes_used_at_steps={}, used_inside_other_tokenized_operand_tokens_at_step={}, tokenized_operands_defs_at_steps={11: [TokenizedOperandModel(operand_type=<TokenType.IS_UNDEF: 'IS_UNDEF'>, ssa_name='i_19', ssa_version=19, variable_name='i', step_index=11, position=1, used_inside_other_tokenized_operand_tokens_at_step={}, current_depth_position=0, tokens=[TokenModel(token_type=<TokenType.IS_VARIABLE: 'IS_VARIABLE'>, is_base_variable=True, code_name='ssa_name', value='i_19', value_extended='i', discovery_depth=0)])]}, tokenized_operands_uses_at_steps={}), 'i_5': SSAVariableModel(ssa_name='i_5', ssa_version=5, variable_name='i', variable_defined_at_steps=[], variable_used_at_steps=[12, 13, 17, 18], variable_used_in_callsites=[], ...[redacted]...






