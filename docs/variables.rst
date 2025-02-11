.. _variables:

Working with Variables
======================

Data model or structure for variables - :class:`~eptalights.models.egimple.variable.VariableManagerModel` :class:`~eptalights.models.egimple.variable.VariableModel` :class:`~eptalights.models.egimple.variable.SSAVariableModel`

Everything concerning variables of a function is managed through the function's ``variable_manager`` which is a :class:`~eptalights.models.egimple.variable.VariableManagerModel` data model.


1. print variable names in a function
-------------------------------------

Get all variable names.

.. code-block:: python

	fn = api.get_function_by_id(fid="/example/src/02_pointer_arithmetic.cc:main#1")

	print(f"all = {fn.variable_manager.names}")
	print(f"function_args = {fn.variable_manager.function_args}")
	print(f"local_variables = {fn.variable_manager.local_variables}")
	print(f"tmp_variables = {fn.variable_manager.tmp_variables}")

	# output
	"""
	all = ['ptr', 'x', '68952807', '$T1', '$T2', '$T3', '$T4', '$T5', '$T17']
	function_args = []
	local_variables = ['ptr', 'x', '68952807']
	tmp_variables = ['$T1', '$T2', '$T3', '$T4', '$T5', '$T17']
	"""


2. print all variable objects of a function
-------------------------------------------

Therefore dumping the informal representation or `__str__` will give you the Pydantic string representation. 

.. code-block:: python

	for var in fn.variable_manager.all():
	    """
	    print VariableModel model
	    """
	    print(var)

	# output
	"""
	vid='/example/src/02_pointer_arithmetic.cc:main#1:68952807' name='68952807' vartype=<VarType.LOCAL_VARIABLE: 'LOCAL_VARIABLE'> unique_ssa_variables={} full_declaration='int 68952807' type_declaration='int' type_props=['integer_type', 'var_decl'] tokenized_type_declaration=TokenizedOperandModel(operand_type=<TokenType.IS_UNDEF: 'IS_UNDEF'>, ssa_name=None, ssa_version=0, variable_name=None, step_index=None, position=0, used_inside_other_tokenized_operand_tokens_at_step={}, current_depth_position=0, tokens=[TokenModel(token_type=<TokenType.IS_UNDEF: 'IS_UNDEF'>, is_base_variable=False, code_name='integer_type', value='int', value_extended=None, discovery_depth=0), TokenModel(token_type=<TokenType.IS_VARIABLE: 'IS_VARIABLE'>, is_base_variable=True, code_name='var_decl', value='68952807_0', value_extended='68952807', discovery_depth=0)]) additional_info={} phi_ssa_variables={}

	vid='/example/src/02_pointer_arithmetic.cc:main#1:ptr' name='ptr' vartype=<VarType.LOCAL_VARIABLE: 'LOCAL_VARIABLE'> unique_ssa_variables={'ptr_13': SSAVariableModel(ssa_name='ptr_13', ssa_version=13, variable_name='ptr', variable_defined_at_steps=[5], variable_used_at_steps=[6, 8, 11], variable_used_in_callsites=[], record_attributes_defined_at_steps={}, record_attributes_used_at_steps={}, used_inside_other_tokenized_operand_tokens_at_step={}, tokenized_operands_defs_at_steps={5: [TokenizedOperandModel(operand_type=<TokenType.IS_UNDEF: 'IS_UNDEF'>, ssa_name='ptr_13', ssa_version=13, variable_name='ptr', step_index=5, position=1, used_inside_other_tokenized_operand_tokens_at_step={}, current_depth_position=0, tokens=[TokenModel(token_type=<TokenType.IS_VARIABLE: 'IS_VARIABLE'>, is_base_variable=True, code_name='ssa_name', value='ptr_13', value_extended='ptr', discovery_depth=0)])]}, tokenized_operands_uses_at_steps={6: [TokenizedOperandModel(operand_type=<TokenType.IS_UNDEF: 'IS_UNDEF'>, ssa_name='ptr_13', ssa_version=13, variable_name='ptr', step_index=6, position=1, used_inside_other_tokenized_operand_tokens_at_step={}, current_depth_position=1, tokens=[TokenModel(token_type=<TokenType.IS_SYMBOL: 'IS_SYMBOL'>, is_base_variable=False, code_name='mem_ref', value='*', value_extended=None, discovery_depth=1), TokenModel(token_type=<TokenType.IS_VARIABLE: 'IS_VARIABLE'>, is_base_variable=True, code_name='ssa_name', value='ptr_13', value_extended='ptr', discovery_depth=1)])], 8: [TokenizedOperandModel(operand_type=<TokenType.IS_UNDEF: 'IS_UNDEF'>, ssa_name='ptr_13', ssa_version=13, variable_name='ptr', step_index=8, position=1, used_inside_other_tokenized_operand_tokens_at_step={}, current_depth_position=0, tokens=[TokenModel(token_type=<TokenType.IS_VARIABLE: 'IS_VARIABLE'>, is_base_variable=True, code_name='ssa_name', value='ptr_13', value_extended='ptr', discovery_depth=0)])], 11: [TokenizedOperandModel(operand_type=<TokenType.IS_UNDEF: 'IS_UNDEF'>, ssa_name='ptr_13', ssa_version=13, variable_name='ptr', step_index=11, position=1, used_inside_other_tokenized_operand_tokens_at_step={}, current_depth_position=0, tokens=[TokenModel(token_type=<TokenType.IS_VARIABLE: 'IS_VARIABLE'>, is_base_variable=True, code_name='ssa_name', value='ptr_13', value_extended='ptr', discovery_depth=0)])]})} full_declaration='int * ptr' type_declaration='int *' type_props=['pointer_type', 'integer_type', 'var_decl'] tokenized_type_declaration=TokenizedOperandModel(operand_type=<TokenType.IS_UNDEF: 'IS_UNDEF'>, ssa_name=None, ssa_version=0, variable_name=None, step_index=None, position=0, used_inside_other_tokenized_operand_tokens_at_step={}, current_depth_position=0, tokens=[TokenModel(token_type=<TokenType.IS_UNDEF: 'IS_UNDEF'>, is_base_variable=False, code_name='integer_type', value='int', value_extended=None, discovery_depth=0), TokenModel(token_type=<TokenType.IS_UNDEF: 'IS_UNDEF'>, is_base_variable=False, code_name='pointer_type', value='*', value_extended=None, discovery_depth=0), TokenModel(token_type=<TokenType.IS_VARIABLE: 'IS_VARIABLE'>, is_base_variable=True, code_name='var_decl', value='ptr_0', value_extended='ptr', discovery_depth=0)]) additional_info={} phi_ssa_variables={}

	..[redacted]...
	"""


3. print local variable objects of a function
---------------------------------------------

Therefore dumping the informal representation or `__str__` will give you the Pydantic string representation. 

.. code-block:: python

	import eptalights
	from eptalights import models


	fn = api.get_function_by_id(fid="/example/src/02_pointer_arithmetic.cc:main#1")

	for var in fn.variable_manager.all():
	    """
	    check the vartype of variable
	    """
	    if var.vartype == models.VarType.LOCAL_VARIABLE:
	        """
	        print VariableModel model
	        """
	        print(var)

	"""
	vid='/example/src/02_pointer_arithmetic.cc:main#1:ptr' name='ptr' vartype=<VarType.LOCAL_VARIABLE: 'LOCAL_VARIABLE'> unique_ssa_variables={'ptr_13': SSAVariableModel(ssa_name='ptr_13', ssa_version=13, variable_name='ptr', variable_defined_at_steps=[5], variable_used_at_steps=[6, 8, 11], variable_used_in_callsites=[], record_attributes_defined_at_steps={}, record_attributes_used_at_steps={}, used_inside_other_tokenized_operand_tokens_at_step={}, tokenized_operands_defs_at_steps={5: [TokenizedOperandModel(operand_type=<TokenType.IS_UNDEF: 'IS_UNDEF'>, ssa_name='ptr_13', ssa_version=13, variable_name='ptr', step_index=5, position=1, used_inside_other_tokenized_operand_tokens_at_step={}, current_depth_position=0, tokens=[TokenModel(token_type=<TokenType.IS_VARIABLE: 'IS_VARIABLE'>, is_base_variable=True, code_name='ssa_name', value='ptr_13', value_extended='ptr', discovery_depth=0)])]}, tokenized_operands_uses_at_steps={6: [TokenizedOperandModel(operand_type=<TokenType.IS_UNDEF: 'IS_UNDEF'>, ssa_name='ptr_13', ssa_version=13, variable_name='ptr', step_index=6, position=1, used_inside_other_tokenized_operand_tokens_at_step={}, current_depth_position=1, tokens=[TokenModel(token_type=<TokenType.IS_SYMBOL: 'IS_SYMBOL'>, is_base_variable=False, code_name='mem_ref', value='*', value_extended=None, discovery_depth=1), TokenModel(token_type=<TokenType.IS_VARIABLE: 'IS_VARIABLE'>, is_base_variable=True, code_name='ssa_name', value='ptr_13', value_extended='ptr', discovery_depth=1)])], 8: [TokenizedOperandModel(operand_type=<TokenType.IS_UNDEF: 'IS_UNDEF'>, ssa_name='ptr_13', ssa_version=13, variable_name='ptr', step_index=8, position=1, used_inside_other_tokenized_operand_tokens_at_step={}, current_depth_position=0, tokens=[TokenModel(token_type=<TokenType.IS_VARIABLE: 'IS_VARIABLE'>, is_base_variable=True, code_name='ssa_name', value='ptr_13', value_extended='ptr', discovery_depth=0)])], 11: [TokenizedOperandModel(operand_type=<TokenType.IS_UNDEF: 'IS_UNDEF'>, ssa_name='ptr_13', ssa_version=13, variable_name='ptr', step_index=11, position=1, used_inside_other_tokenized_operand_tokens_at_step={}, current_depth_position=0, tokens=[TokenModel(token_type=<TokenType.IS_VARIABLE: 'IS_VARIABLE'>, is_base_variable=True, code_name='ssa_name', value='ptr_13', value_extended='ptr', discovery_depth=0)])]})} full_declaration='int * ptr' type_declaration='int *' type_props=['pointer_type', 'integer_type', 'var_decl'] tokenized_type_declaration=TokenizedOperandModel(operand_type=<TokenType.IS_UNDEF: 'IS_UNDEF'>, ssa_name=None, ssa_version=0, variable_name=None, step_index=None, position=0, used_inside_other_tokenized_operand_tokens_at_step={}, current_depth_position=0, tokens=[TokenModel(token_type=<TokenType.IS_UNDEF: 'IS_UNDEF'>, is_base_variable=False, code_name='integer_type', value='int', value_extended=None, discovery_depth=0), TokenModel(token_type=<TokenType.IS_UNDEF: 'IS_UNDEF'>, is_base_variable=False, code_name='pointer_type', value='*', value_extended=None, discovery_depth=0), TokenModel(token_type=<TokenType.IS_VARIABLE: 'IS_VARIABLE'>, is_base_variable=True, code_name='var_decl', value='ptr_0', value_extended='ptr', discovery_depth=0)]) additional_info={} phi_ssa_variables={}
	vid='/example/src/02_pointer_arithmetic.cc:main#1:x' name='x' vartype=<VarType.LOCAL_VARIABLE: 'LOCAL_VARIABLE'> unique_ssa_variables={'x_0': SSAVariableModel(ssa_name='x_0', ssa_version=0, variable_name='x', variable_defined_at_steps=[0, 1, 2, 3, 4], variable_used_at_steps=[5], variable_used_in_callsites=[], record_attributes_defined_at_steps={}, record_attributes_used_at_steps={}, used_inside_other_tokenized_operand_tokens_at_step={}, tokenized_operands_defs_at_steps={0: [TokenizedOperandModel(operand_type=<TokenType.IS_UNDEF: 'IS_UNDEF'>, ssa_name='x_0', ssa_version=0, variable_name='x', step_index=0, position=1, used_inside_other_tokenized_operand_tokens_at_step={}, current_depth_position=1, tokens=[TokenModel(token_type=<TokenType.IS_VARIABLE: 'IS_VARIABLE'>, is_base_variable=True, code_name='var_decl', value='x_0', value_extended='x', discovery_depth=1), TokenModel(token_type=<TokenType.IS_SYMBOL: 'IS_SYMBOL'>, is_base_variable=False, code_name='array_ref', value='[', value_extended=None, discovery_depth=1), TokenModel(token_type=<TokenType.IS_CONSTANT: 'IS_CONSTANT'>, is_base_variable=False, code_name='integer_cst', value='0', value_extended=None, discovery_depth=1), TokenModel(token_type=<TokenType.IS_SYMBOL: 'IS_SYMBOL'>, is_base_variable=False, code_name='array_ref', value=']', value_extended=None, discovery_depth=1)])], 1: [TokenizedOperandModel(operand_type=<TokenType.IS_UNDEF: 'IS_UNDEF'>, ssa_name='x_0', ssa_version=0, variable_name='x', step_index=1, position=1, used_inside_other_tokenized_operand_tokens_at_step={}, current_depth_position=1, tokens=[TokenModel(token_type=<TokenType.IS_VARIABLE: 'IS_VARIABLE'>, is_base_variable=True, code_name='var_decl', value='x_0', value_extended='x', discovery_depth=1), TokenModel(token_type=<TokenType.IS_SYMBOL: 'IS_SYMBOL'>, is_base_variable=False, code_name='array_ref', value='[', value_extended=None, discovery_depth=1), TokenModel(token_type=<TokenType.IS_CONSTANT: 'IS_CONSTANT'>, is_base_variable=False, code_name='integer_cst', value='1', value_extended=None, discovery_depth=1), TokenModel(token_type=<TokenType.IS_SYMBOL: 'IS_SYMBOL'>, is_base_variable=False, code_name='array_ref', value=']', value_extended=None, discovery_depth=1)])], 2: [TokenizedOperandModel(operand_type=<TokenType.IS_UNDEF: 'IS_UNDEF'>, ssa_name='x_0', ssa_version=0, variable_name='x', step_index=2, position=1, used_inside_other_tokenized_operand_tokens_at_step={}, current_depth_position=1, tokens=[TokenModel(token_type=<TokenType.IS_VARIABLE: 'IS_VARIABLE'>, is_base_variable=True, code_name='var_decl', value='x_0', value_extended='x', discovery_depth=1), TokenModel(token_type=<TokenType.IS_SYMBOL: 'IS_SYMBOL'>, is_base_variable=False, code_name='array_ref', value='[', value_extended=None, discovery_depth=1), TokenModel(token_type=<TokenType.IS_CONSTANT: 'IS_CONSTANT'>, is_base_variable=False, code_name='integer_cst', value='2', value_extended=None, discovery_depth=1), TokenModel(token_type=<TokenType.IS_SYMBOL: 'IS_SYMBOL'>, is_base_variable=False, code_name='array_ref', value=']', value_extended=None, discovery_depth=1)])], 3: [TokenizedOperandModel(operand_type=<TokenType.IS_UNDEF: 'IS_UNDEF'>, ssa_name='x_0', ssa_version=0, variable_name='x', step_index=3, position=1, used_inside_other_tokenized_operand_tokens_at_step={}, current_depth_position=1, tokens=[TokenModel(token_type=<TokenType.IS_VARIABLE: 'IS_VARIABLE'>, is_base_variable=True, code_name='var_decl', value='x_0', value_extended='x', discovery_depth=1), TokenModel(token_type=<TokenType.IS_SYMBOL: 'IS_SYMBOL'>, is_base_variable=False, code_name='array_ref', value='[', value_extended=None, discovery_depth=1), TokenModel(token_type=<TokenType.IS_CONSTANT: 'IS_CONSTANT'>, is_base_variable=False, code_name='integer_cst', value='3', value_extended=None, discovery_depth=1), TokenModel(token_type=<TokenType.IS_SYMBOL: 'IS_SYMBOL'>, is_base_variable=False, code_name='array_ref', value=']', value_extended=None, discovery_depth=1)])], 4: [TokenizedOperandModel(operand_type=<TokenType.IS_UNDEF: 'IS_UNDEF'>, ssa_name='x_0', ssa_version=0, variable_name='x', step_index=4, position=1, used_inside_other_tokenized_operand_tokens_at_step={}, current_depth_position=1, tokens=[TokenModel(token_type=<TokenType.IS_VARIABLE: 'IS_VARIABLE'>, is_base_variable=True, code_name='var_decl', value='x_0', value_extended='x', discovery_depth=1), TokenModel(token_type=<TokenType.IS_SYMBOL: 'IS_SYMBOL'>, is_base_variable=False, code_name='array_ref', value='[', value_extended=None, discovery_depth=1), TokenModel(token_type=<TokenType.IS_CONSTANT: 'IS_CONSTANT'>, is_base_variable=False, code_name='integer_cst', value='4', value_extended=None, discovery_depth=1), TokenModel(token_type=<TokenType.IS_SYMBOL: 'IS_SYMBOL'>, is_base_variable=False, code_name='array_ref', value=']', value_extended=None, discovery_depth=1)])]}, tokenized_operands_uses_at_steps={5: [TokenizedOperandModel(operand_type=<TokenType.IS_UNDEF: 'IS_UNDEF'>, ssa_name='x_0', ssa_version=0, variable_name='x', step_index=5, position=1, used_inside_other_tokenized_operand_tokens_at_step={}, current_depth_position=1, tokens=[TokenModel(token_type=<TokenType.IS_SYMBOL: 'IS_SYMBOL'>, is_base_variable=False, code_name='addr_expr', value='&', value_extended=None, discovery_depth=1), TokenModel(token_type=<TokenType.IS_VARIABLE: 'IS_VARIABLE'>, is_base_variable=True, code_name='var_decl', value='x_0', value_extended='x', discovery_depth=1), TokenModel(token_type=<TokenType.IS_SYMBOL: 'IS_SYMBOL'>, is_base_variable=False, code_name='array_ref', value='[', value_extended=None, discovery_depth=1), TokenModel(token_type=<TokenType.IS_CONSTANT: 'IS_CONSTANT'>, is_base_variable=False, code_name='integer_cst', value='2', value_extended=None, discovery_depth=1), TokenModel(token_type=<TokenType.IS_SYMBOL: 'IS_SYMBOL'>, is_base_variable=False, code_name='array_ref', value=']', value_extended=None, discovery_depth=1)])]})} full_declaration='int [ 5 ] x' type_declaration='int [ 5 ]' type_props=['var_decl_array', 'integer_type', 'var_decl'] tokenized_type_declaration=TokenizedOperandModel(operand_type=<TokenType.IS_UNDEF: 'IS_UNDEF'>, ssa_name=None, ssa_version=0, variable_name=None, step_index=None, position=0, used_inside_other_tokenized_operand_tokens_at_step={}, current_depth_position=0, tokens=[TokenModel(token_type=<TokenType.IS_UNDEF: 'IS_UNDEF'>, is_base_variable=False, code_name='integer_type', value='int', value_extended=None, discovery_depth=0), TokenModel(token_type=<TokenType.IS_VARIABLE: 'IS_VARIABLE'>, is_base_variable=True, code_name='var_decl', value='x_0', value_extended='x', discovery_depth=0), TokenModel(token_type=<TokenType.IS_UNDEF: 'IS_UNDEF'>, is_base_variable=False, code_name='var_decl', value='[', value_extended=None, discovery_depth=0), TokenModel(token_type=<TokenType.IS_UNDEF: 'IS_UNDEF'>, is_base_variable=False, code_name='var_decl', value='5', value_extended=None, discovery_depth=0), TokenModel(token_type=<TokenType.IS_UNDEF: 'IS_UNDEF'>, is_base_variable=False, code_name='var_decl', value=']', value_extended=None, discovery_depth=0)]) additional_info={} phi_ssa_variables={}
	vid='/example/src/02_pointer_arithmetic.cc:main#1:68952807' name='68952807' vartype=<VarType.LOCAL_VARIABLE: 'LOCAL_VARIABLE'> unique_ssa_variables={} full_declaration='int 68952807' type_declaration='int' type_props=['integer_type', 'var_decl'] tokenized_type_declaration=TokenizedOperandModel(operand_type=<TokenType.IS_UNDEF: 'IS_UNDEF'>, ssa_name=None, ssa_version=0, variable_name=None, step_index=None, position=0, used_inside_other_tokenized_operand_tokens_at_step={}, current_depth_position=0, tokens=[TokenModel(token_type=<TokenType.IS_UNDEF: 'IS_UNDEF'>, is_base_variable=False, code_name='integer_type', value='int', value_extended=None, discovery_depth=0), TokenModel(token_type=<TokenType.IS_VARIABLE: 'IS_VARIABLE'>, is_base_variable=True, code_name='var_decl', value='68952807_0', value_extended='68952807', discovery_depth=0)]) additional_info={} phi_ssa_variables={}
	"""


4. get variables defined or used at a specific step
---------------------------------------------------

Getting variables used at a specific step/instruction.  

.. code-block:: python

	fn = api.get_function_by_id(fid="/example/src/01_print_pointer_value.cc:main#1")

	step_index = 1
	print(f"{fn.steps[step_index].decompile()}")

	# output
	"""
	p = &c;
	"""

	for var in fn.variable_manager.used_at_step(step_index):
	    print(f"variables_used_at_step = {var.name}")

	# output
	"""
	variables_used_at_step = p
	"""

Getting variables defined at a specific step/instruction. 

.. code-block:: python

	fn = api.get_function_by_id(fid="/example/src/01_print_pointer_value.cc:main#1")

	step_index = 1
	print(f"{fn.steps[step_index].decompile()}")

	# output
	"""
	p = &c;
	"""

	for var in fn.variable_manager.defined_at_step(step_index):
	    print(f"variables_defined_at_step = {var.name}")

	# output
	"""
	variables_defined_at_step = c
	"""

Getting variables, whether defined or used, at a specific step/instruction.  

.. code-block:: python

	fn = api.get_function_by_id(fid="/example/src/01_print_pointer_value.cc:main#1")

	step_index = 1
	print(f"{fn.steps[step_index].decompile()}")

	# output
	"""
	p = &c;
	"""

	for var in fn.variable_manager.used_or_defined_at_step(step_index):
	    print(f"variables_used_or_defined_at_step = {var.name}")

	# output
	"""
	variables_used_or_defined_at_step = p
	variables_used_or_defined_at_step = c
	"""


5. get specific variable object by name
---------------------------------------

Getting a variable by name.  

.. code-block:: python

	varname = "$T1"
	var = fn.variable_manager.get(varname)
	print(var)

	# output
	vid='/example/src/01_print_pointer_value.cc:main:$T1' name='$T1' vartype=<VarType.TMP_VARIABLE: 'TMP_VARIABLE'> unique_ssa_variables={'$T1_1': SSAVariableModel(ssa_name='$T1_1', ssa_version=1, variable_name='$T1', variable_defined_at_steps=[2], variable_used_at_steps=[3], variable_used_in_callsites=['printf_3'], record_attributes_defined_at_steps={}, ..[redacted]...


6. searching variables globally across all functions
----------------------------------------------------

Search for variables globally using ``filter_by_name``, ``filter_by_filepath``, ``filter_by_type_decl``, ``is_local_var``, ``is_tmp`` and ``is_farg``. You can combine these filters in any way to tailor your search.

.. code-block:: python

	for fn, var in api.search_variables(filter_by_name="argc"):
	    print(f"fid={fn.fid}, varname={var.name}")

	"""
	fid=/example/src/16_buffer_overflow.cc:main#1, varname=argc
	fid=/example/src/16_uninitializede_var_use.cc:main#1, varname=argc
	"""


7. searching variables within a single function
-----------------------------------------------

We can also search for variables within a function.

.. code-block:: python

	for var in fn.variable_manager.search(name="argc"):
	    print(f"varname={var.name}")

	"""
	varname=argc
	"""




