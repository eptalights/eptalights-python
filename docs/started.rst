.. _started:

Getting Started
===============

Eptalights makes code analysis easier, faster, and more efficient. Whether you're a developer, researcher, or security expert, our technology simplifies complex processes into ``three`` powerful steps:


1. Extract ByteCode or IR Data from Your Source Code
----------------------------------------------------

Eptalights makes it easy to extract ByteCode or Intermediate Representation (IR) from your source code. Whether you're analyzing C, C++, or other languages, our tools simplify the process, giving you quick access to the underlying structure of your code. Currently Supported Languages:

- **C/C++** (using `eptalights-code-extractor-cxx <https://github.com/eptalights/eptalights-code-extractor-cxx>`_)
- **PHP** (using `eptalights-code-extractor-php <https://github.com/eptalights/eptalights-code-extractor-php>`_)
- **Java** (using `eptalights-code-extractor-java <https://github.com/eptalights/eptalights-code-extractor-java>`_)
- **More to be Added ...**

Visit any of our supported language extractor and follow the documentation to generate the IR/bytecode in your desired directory.


2. Transform And Lift Code to SophiaIR models
----------------------------------------------

Once you've extracted the ByteCode or IR, leverage our powerful cloud-based lifter to convert it into a streamlined set of ``SophiaIR`` models below. 

1. Functions - :class:`~eptalights_code.models.sophia_ir.function.FunctionModel`  
2. Control Flow graphs (CFG) - :class:`~eptalights_code.models.sophia_ir.cfg.ControlFlowGraphModel`  
3. Call Sites - :class:`~eptalights_code.models.sophia_ir.callsite.CallsiteModel`  
4. Variables (defined/used) - :class:`~eptalights_code.models.sophia_ir.variable.VariableModel` 
5. File Metadata - :class:`~eptalights_code.models.sophia_ir.file_metadata.FileMetadataModel`  
6. Class Metadata - :class:`~eptalights_code.models.sophia_ir.file_metadata.ClassMetadataModel`  
7. More ...

This transformation helps in simplifying complex code, making it easier to analyze, detect bugs or variants, and understand and spot patterns without getting lost in complicated details.

.. note:: 
   Our cloud-based lifter is currently in ``beta``, but we're here to help! If you need assistance transforming your code, we're happy to do it for you. Feel free to reach out to us `here <https://calendly.com/eptalights>`_.


3. Flexible Database Access
---------------------------

Choose how you interact with your data:

- **Local Access**: Download the database and work offline with ease.

.. code-block:: python
	
	import eptalights_code
	api = eptalights_code.LocalAPI("eptalights_code.toml")

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

Visit other pages to learn how to navigate through functions, call sites, CFGs, variables, and more.

	