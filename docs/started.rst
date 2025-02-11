.. _started:

Getting Started
===============

Eptalights makes code analysis smarter, faster, and more efficient. Whether you're a developer, researcher, or security expert, our technology simplifies complex processes into ``three`` powerful steps:


1. Extract ByteCode or IR Data from Your Source Code
----------------------------------------------------

Eptalights makes it easy to extract ByteCode or Intermediate Representation (IR) from your source code. Whether you're analyzing C, C++, or other languages, our tools simplify the process, giving you quick access to the underlying structure of your code. Currently Supported Languages:

- **C/C++** (via `GCC GIMPLE <https://github.com/eptalights/gimple-extractor>`_)
- **More to be Added ...**

Visit any of our supported language extractors and follow the documentation to generate the IR/bytecode in your desired directory.


2. Transform Code with Our Cloud-Based Lifter
---------------------------------------------

Once you've extracted the ByteCode or IR, leverage our powerful cloud-based lifter to convert it into a streamlined set of data models below. 

1. Functions - :class:`~eptalights.models.egimple.function.FunctionModel`  
2. 7 OpCode Instructions :class:`~eptalights.models.egimple.function.EGimpleIRNopModel` :class:`~eptalights.models.egimple.function.EGimpleIRAssignModel` :class:`~eptalights.models.egimple.function.EGimpleIRCallModel` :class:`~eptalights.models.egimple.function.EGimpleIRCondModel` :class:`~eptalights.models.egimple.function.EGimpleIRReturnModel` :class:`~eptalights.models.egimple.function.EGimpleIRGotoModel` :class:`~eptalights.models.egimple.function.EGimpleIRSwitchModel`
3. Variables (defined/used), call sites, control flow graphs (CFG), and more. - :class:`~eptalights.models.egimple.function.CallsiteModel` :class:`~eptalights.models.egimple.function.ControlFlowGraphModel` :class:`~eptalights.models.egimple.function.VariableModel`

This transformation helps in simplifying complex code, making it easier to analyze, detect bugs or variants, and understand and spot patterns without getting lost in complicated details.


.. note:: 
   Our cloud-based lifter is currently in ``beta``, but we're here to help! If you need assistance transforming your code, we're happy to do it for you. Feel free to reach out to us `here <https://calendly.com/eptalights>`_.


3. Flexible Database Access: Local or Remote
--------------------------------------------

Choose how you interact with your data:

- **Local Access**: Download the database and work offline with ease.

.. code-block:: python
	
	import eptalights
	api = eptalights.LocalAPI("eptalights.toml")

	for fn in api.search_functions():
	    print(fn.name)

	# output
	"""
	main
	main
	main
	addNumbers
	addNumbers
	main
	main
	main
	main
	"""

- **Remote Access**: Connect to our servers and access the database from anywhere in the world.

.. code-block:: python

	import eptalights 
	api = eptalights.RemoteAPI("eptalights.toml")

	for fn in api.search_functions():
	    print(fn.name)

	# output
	"""
	main
	main
	main
	addNumbers
	addNumbers
	main
	main
	main
	main
	"""

With Eptalights, you get the flexibility and power needed to streamline your code analysis workflows, whether you're working locally or in the cloud.

Visit other pages to learn how to navigate through functions, call sites, CFGs, variables, and more.

	