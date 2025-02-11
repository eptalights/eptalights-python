.. _cfg:

Working with Control Flow Graph (CFG)
=====================================

Data model or structure for CFG - :class:`~eptalights.models.egimple.callsite.ControlFlowGraphModel` 


1. print Control Flow Graph (CFG) structure
-------------------------------------------

.. code-block:: python
	
	fn = api.get_function_by_id(fid="/example/src/07_array.cc:main#1")
	print(fn.cfg)

	# output 
	"""
	basicblock_exit_nodes=[4, 5] basicblock_steps={2: [0, 1, 2, 3], 3: [4, 5], 4: [6, 7], 5: [8, 9, 10]} basicblock_edges={2: [5, 3], 3: [4], 4: [], 5: []}
	"""

	from pprint import pprint
	pprint(fn.cfg.model_dump())

	# output
	"""
	{'basicblock_edges': {2: [5, 3], 3: [4], 4: [], 5: []},
	 'basicblock_exit_nodes': [4, 5],
	 'basicblock_steps': {2: [0, 1, 2, 3], 3: [4, 5], 4: [6, 7], 5: [8, 9, 10]}}
	"""


2. get basic block index of a step
----------------------------------

Getting the basic block index of a step/instruction.  

.. code-block:: python
	
	fn = api.get_function_by_id(fid="/example/src/07_array.cc:main#1")
	step = fn.steps[0]
	print(step.basicblock_index)

	# output
	"""
	2
	"""
