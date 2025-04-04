.. _started:

Getting Started
===============

Eptalights makes code analysis smarter, faster, and more efficient. Whether you're a developer, researcher, or security expert, our technology simplifies complex processes into ``three`` powerful steps:


1. Extract ByteCode or IR Data from Your Source Code
----------------------------------------------------

Eptalights makes it easy to extract ByteCode or Intermediate Representation (IR) from your source code. Whether you're analyzing C, C++, or other languages, our tools simplify the process, giving you quick access to the underlying structure of your code. Currently Supported Languages:

- **C/C++** (using `GCC GIMPLE IR Extractor <https://github.com/eptalights/gimple-extractor>`_)
- **PHP** (using `PHP Byetcode Extractor <https://github.com/eptalights/php-bytecode-extractor>`_)
- **More to be Added ...**

Visit any of our supported language extractors and follow the documentation to generate the IR/bytecode in your desired directory.


2. Transform Code with Our Cloud-Based Lifter
---------------------------------------------

Once you've extracted the ByteCode or IR, leverage our powerful cloud-based lifter to convert it into a streamlined set of data models below. 

1. Functions - :class:`~eptalights.models.egimple.function.FunctionModel`  
2. Control Flow graphs (CFG) - :class:`~eptalights.models.egimple.function.ControlFlowGraphModel`  
3. Call Sites - :class:`~eptalights.models.egimple.function.CallsiteModel`  
4. Variables (defined/used) - :class:`~eptalights.models.egimple.function.VariableModel` 
5. File Metadata - :class:`~eptalights.models.egimple.file_metadata.FileMetadataModel`  
6. More ...

This transformation helps in simplifying complex code, making it easier to analyze, detect bugs or variants, and understand and spot patterns without getting lost in complicated details.


.. note:: 
   Our cloud-based lifter is currently in ``beta``, but we're here to help! If you need assistance transforming your code, we're happy to do it for you. Feel free to reach out to us `here <https://calendly.com/eptalights>`_.


3. Flexible Database Access
---------------------------

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

Visit other pages to learn how to navigate through functions, call sites, CFGs, variables, and more.

	