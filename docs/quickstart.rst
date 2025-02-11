.. _quickstart:

Quickstart
==========

Eptalights technology operates in three forms:

1. Extracting Bytecode or IR information from source code.  
2. Using our cloud-based lifter to transform the Bytecode/IR into 7 OpCode instructions.  
3. Downloading and using the database locally, or interacting with it remotely from anywhere.

If you already have the database and configuration, you can proceed. However, if this is new to you, you can find more details above. Visit :ref:`started`.   

You can also try out with our sample project which includes database files here: `Example Projects <https://github.com/eptalights/eptalights-python-examples>`_.


1. Setting up Locally
---------------------

.. code-block:: sh

	# setup python environment 
	python -m venv evnv
	. venv/bin/activate

	# install eptalights-python library
	pip install eptalights
	# or 
	pip install git+https://github.com/eptalights/eptalights-python.git

	# change directory where `eptalights.db` and `eptalights.toml` are located
	# or update the `eptalights.toml` to point to where these files reside.
	cd /path/to/project

	# go to step 2


2. Testing our Local Setup
--------------------------

You can either create a python test file in the directory or enter python REPL.

.. code-block:: python

	import eptalights
	api = eptalights.LocalAPI("./eptalights.toml")

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




