.. _quickstart:

Quickstart
==========

Eptalights code analysis operates in three main steps:

#. Extract bytecode or IR data from your application.
#. Convert the extracted bytecode/IR into clean, Pythonic instructions using the cloud-based lifter.
#. Download and interact with the analysis database locally using our Python library.

If you already have a database and configuration, you can skip ahead. Otherwise, see :ref:`started` for full setup instructions.

For a quick test, you can use our sample project, which includes preloaded database files: `Example Projects <https://github.com/eptalights/eptalights-python-examples>`_.

1. Setting Up Locally
---------------------

Create a Python virtual environment and install the Eptalights library:

.. code-block:: bash

   # setup python environment
   python -m venv venv
   . venv/bin/activate

   # install the Eptalights library
   pip install eptalights

Change to the directory containing your ``eptalights.db`` and ``eptalights.toml`` files, or update your ``eptalights.toml`` to point to their location:

.. code-block:: bash

   cd /path/to/project

After this, you are ready to proceed to testing the local setup.

2. Testing Your Local Setup
---------------------------

You can either create a Python test file in the directory or use the Python REPL:

.. code-block:: python

   import eptalights

   api = eptalights.LocalAPI("./eptalights.toml")

   for fn in api.search_functions():
       print(fn.name)

Example output:

.. code-block:: text

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

The local API allows you to navigate functions, call sites, control flow graphs, variables, and more.

Continue to other sections for advanced queries and exploration of your analysis database.

----

Questions or need help?
-----------------------

Join our Discord for support and discussions:

`Eptalights Discord <https://discord.gg/mskuGs3EC>`_