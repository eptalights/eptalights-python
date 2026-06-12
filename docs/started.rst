.. _started:

Getting Started
===============

Eptalights simplifies large-scale code analysis by transforming application artifacts into searchable datasets and APIs. The workflow consists of **three main steps**:

#. Extract analysis data from your application
#. Configure your workspace and create a build
#. Explore the resulting analysis database

1. Extract Analysis Data from Your Application
----------------------------------------------

Before running an analysis, generate the intermediate representation (IR), bytecode, or instruction data required by the platform.

Choose the extractor that matches your technology stack:

* **C/C++ Applications** — Generate GIMPLE IR directly from your source code using the GCC plugin:

  `eptalights-extractor-cxx <https://github.com/eptalights/eptalights-extractor-cxx>`_

* **PHP Applications** — Extract PHP bytecode for analysis using:

  `eptalights-extractor-php <https://github.com/eptalights/eptalights-extractor-php>`_

* **JVM-Based Applications** — Extract bytecode and metadata from Java, Kotlin, Scala, Groovy, Clojure, and other JVM languages. Supports class files, JARs, WARs, EARs, and packaged applications:

  `eptalights-extractor-java <https://github.com/eptalights/eptalights-extractor-java>`_

* **Additional language extractors** — Coming soon.

Follow the documentation for your selected extractor to generate the required analysis artifacts and store them in a directory of your choice.

2. Configure Your Workspace and Create a Build
----------------------------------------------

After generating the extractor output, create a dedicated workspace for your Eptalights project. This workspace will contain your configuration file and any generated analysis databases.

**Important:** This step requires a valid `project_id`.

* Projects can be created at: `https://platform.eptalights.com/ <https://platform.eptalights.com/>`_
* The code type of your project **must match the extractor** used in Step 1.
* Once your project is created, copy the `project_id` into your ``eptalights.toml`` configuration file.
* For shared projects, copy the shared project ID into your configuration file instead.

Create and enter a project directory:

.. code-block:: bash

   mkdir your-project-name
   cd your-project-name

Install the Eptalights CLI and SDK:

.. code-block:: bash

   pip install eptalights

Configure authentication:

.. code-block:: bash

   export EPTALIGHTS_API_KEY="your-api-token"

Create an ``eptalights.toml`` file in the workspace:

.. code-block:: toml

   project_id = "your-project-id"
   extractor_output_path = "path-to-extractor-output"

Where:

* ``project_id`` — Your Eptalights project identifier (from the platform or shared project).
* ``extractor_output_path`` — Path to the directory containing the IR or bytecode generated in Step 1.

Create a build:

.. code-block:: bash

   eptalights_builder --name your-unique-build-name

**Notes:**

* Build names must be unique within a project.
* Common choices: version numbers, release tags, commit hashes, CI/CD build identifiers.

After the build completes, download the generated analysis database:

.. code-block:: bash

   eptalights_downloader --name your-unique-build-name

.. important::

   Both ``eptalights_builder`` and ``eptalights_downloader`` must be executed from the directory containing the ``eptalights.toml`` file.

3. Explore Your Analysis Database
---------------------------------

Once the database has been downloaded, you can query it locally using the Eptalights API.

.. code-block:: python

   import eptalights

   api = eptalights.LocalAPI("eptalights.toml")

   for fn in api.search_functions():
       print(fn.name)

Example output:

.. code-block:: text

   main
   main
   main
   addNumbers
   addNumbers
   main
   main
   main
   main

The local API provides access to rich analysis data, including:

* Functions
* Control Flow Graphs (CFGs)
* Call Sites
* Variables
* File Metadata
* Class Metadata
* Additional program structures

Continue to the following sections to learn how to search, navigate, and analyze your application using the Eptalights API.

----

Questions or need help?
-----------------------

Join our Discord for support and discussions:

`Eptalights Discord <https://discord.gg/mskuGs3EC>`_