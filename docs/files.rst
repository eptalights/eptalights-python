.. _files:

Working with File Metadata and File Data
=========================================

Eptalights provides two levels of file representation:

* **FileMetadataModel** — lightweight structural metadata (fast, minimal loading)
* **FileDataModel** — fully hydrated analysis data (functions, classes, CFGs, etc.)

This separation allows efficient database access while supporting deep program analysis when needed.

----------------------------------------
File Metadata vs File Data
----------------------------------------

.. list-table:: File Representation Models
   :widths: 30 70
   :header-rows: 1

   * - Model
     - Description
   * - FileMetadataModel
     - Lightweight file structure containing class names, function IDs, and tokenized properties
   * - FileDataModel
     - Fully loaded file containing resolved FunctionModel and ClassDataModel objects

----------------------------------------
1. Fetch File Metadata
----------------------------------------

Use metadata when you only need structural information about a file.

.. code-block:: python

   file_meta = api.get_file_metadata_by_filepath(
       "/example/src/user_service.php"
   )

   print(file_meta.filepath)

   # output
   """
   /example/src/user_service.php
   """

Metadata includes:

* class names
* function IDs
* tokenized class properties

.. code-block:: python

   print(file_meta.functions)

   print(file_meta.classes)

----------------------------------------
2. Convert Metadata → Full File Data
----------------------------------------

Once metadata is loaded, you can hydrate it into full analysis objects:

.. code-block:: python

   file_data = api.get_file_data_by_metadata(file_meta)

This step:

* Resolves function IDs into full FunctionModel objects
* Loads class methods into executable analysis models
* Preserves structural metadata

----------------------------------------
3. Fetch File Data Directly
----------------------------------------

You can skip metadata and directly fetch full analysis data:

.. code-block:: python

   file_data = api.get_file_data_by_filepath(
       "/example/src/user_service.php"
   )

This internally performs:

#. Load FileMetadataModel from database
#. Collect all function IDs
#. Batch fetch FunctionModel objects
#. Construct FileDataModel

----------------------------------------
4. Working with File Data
----------------------------------------

FileDataModel contains fully resolved program structures.

.. code-block:: python

   print(file_data.filepath)

   print(file_data.functions.keys())

   print(file_data.classes.keys())

----------------------------------------
5. Access Class Data
----------------------------------------

.. code-block:: python

   cls = file_data.classes["UserService"]

   print(cls.class_props)

   print(cls.class_methods.keys())

Each class contains:

* Tokenized properties
* Fully resolved methods (:class:`~eptalights.models.sophia_ir.function.FunctionModel`)

----------------------------------------
6. Method Resolution Example
----------------------------------------

.. code-block:: python

   method = file_data.classes["UserService"].class_methods["create_user"]

   print(method.name)

----------------------------------------
Performance Notes
----------------------------------------

Use **FileMetadataModel** when performing:

* fast structural scanning of large codebases
* indexing files without loading functions

Use **FileDataModel** when performing:

* CFG analysis
* function-level inspection
* decompilation
* call graph traversal

Metadata → Data conversion is optimized via batch function loading for efficiency.