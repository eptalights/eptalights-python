.. _quickstart:

Quickstart
==========

Eptalights technology operates in three forms:

1. Extract bytecode or IR data from source code.  
2. Convert the extracted bytecode/IR into clean, Pythonic instructions using our cloud-based lifter.
3. Download and interact with the database locally using our Python Library.

If you already have the database and configuration, you can proceed. However, if this is new to you, you can find more details above. Visit :ref:`started`.   

If you want to quickly try it out, you can use our sample project, which includes preloaded database files, available here: `Example Projects <https://github.com/eptalights/sophia-python-examples>`_.


1. Setting up Locally
---------------------

.. code-block:: sh

	# setup python environment 
	python -m venv venv
	. venv/bin/activate

	# install sophia-python library
	pip install git+https://github.com/eptalights/sophia-python.git

	# change directory where `sophia_ir.db` and `sophia_ir.toml` are located
	# or update the `sophia_ir.toml` to point to where these files reside.
	cd /path/to/project

	# go to step 2


2. Testing our Local Setup
--------------------------

You can either create a python test file in the directory or enter python REPL.

.. code-block:: python

	import eptalights_sophia
	api = eptalights_sophia.LocalAPI("./sophia_ir.toml")

	for fn in api.search_functions():
	    print(fn.name)

	# output
	"""
	init_rootfs
	rootfs_init_fs_context
	readonly
	root_dev_setup
	root_delay_setup
	mount_nodev_root
	do_mount_root
	fs_names_setup
	rootwait_timeout_setup
	prepare_namespace
	no_initrd
	early_initrd
	early_initrdmem
	initrd_load
	init_linuxrc
	kernel_do_mounts_initrd_sysctls_init
	...
	"""


Visit other pages to learn how to navigate through functions, call sites, CFGs, variables, and more.




