.. _callsites:

Working with Callsites
======================

Find out where specific functions are called and which variables are used as arguments. 
We can globally search for callsite function or search within a specific function.

Data model or structure for callsite - :class:`~eptalights.models.egimple.callsite.CallsiteModel` :class:`~eptalights.models.egimple.callsite.CallsiteManagerModel`


1. searching callsites globally across all functions
----------------------------------------------------

Search for call sites globally using ``filter_by_name``, ``filter_by_filepath``, and ``filter_by_num_of_args``. You can combine these filters in any way to tailor your search.

.. code-block:: python

	for fn, callsite in api.search_callsites(filter_by_name="malloc"):
	    print(fn.fid, callsite.fn_name)

	# output
	"""
	/example/src/03_scanf_to_malloc.cc:main#1 ['malloc']
	/example/src/13_struct_pointer_arithmetic.cc:main#1 ['malloc']
	"""


2. searching callsites within a single all functions
----------------------------------------------------

We can also search for callsites within a function.

.. code-block:: python

	fn = api.get_function_by_id(fid="/example/src/03_scanf_to_malloc.cc:main#1")

	"""
	Get all `malloc` callsite names.
	"""
	for callsite in fn.callsite_manager.search(name="malloc"):
		"""
	    print CallsiteModel model
	    """
	    print(callsite)

	# output
	"""
	# callsite model
	cid='/example/src/03_scanf_to_malloc.cc:main#1:malloc_6' step_index=6 fn_name=['malloc'] num_of_args=1 variables_used_as_callsite_arg=['$T3'] variables_defined_here=['ptr'] ssa_variables_used_as_callsite_arg=['$T3_3'] ssa_variables_defined_here=['ptr_21']
	"""


3. get callsite by id
---------------------

Each callsite also has it's own ID called `cid`. And can be used to retrieve specific callsite globally.

.. code-block:: python

	fn, callsite = api.get_callsite_by_id(cid='/example/src/03_scanf_to_malloc.cc:main#1:malloc_6')
	print(fn.fid, callsite.fn_name)

	# output
	"""
	/example/src/03_scanf_to_malloc.cc:main#1 ['malloc']
	"""


3. print callsite's step
------------------------

We can print the Pseudo-C code at the callsite's step or instruction within the function. 

.. code-block:: python

	fn = api.get_function_by_id(fid="/example/src/03_scanf_to_malloc.cc:main#1")
	for callsite in fn.callsite_manager.search(name="malloc"):
		"""
	    print step or instruction of the callsite
	    """
	    print(fn.steps[callsite.step_index].decompile())

	# output
	"""
	ptr = malloc  ( $T3 );
	"""




