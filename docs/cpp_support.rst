.. _cpp_support:

Working with C++ Data Types
===========================

We'll dive into how to analyze **C++ functionalities** like ``vectors``, ``maps``, ``operator overloading``, ``function overloading``, etc.


1. Hello World in C++
---------------------

First, let's understanding how a simple **Hello World** program translates into **GIMPLE IR** and how we can interpret this using Python.

.. code-block:: c++

	#include <iostream>

	int main() {
	    std::cout << "Hello World!";
	    return 0;
	}

When you compile this using **GCC** and inspect the **GIMPLE IR** (GCC’s intermediate representation), it appears as:

.. code-block:: c++

	main ()
	{
	  int D.40872;
	  int _3;

	  <bb 2> :
	  gimple_call <operator<<, NULL, &cout, "Hello World!">
	  gimple_assign <integer_cst, _3, 0, NULL, NULL>

	  <bb 3> :
	  gimple_label <<L0>>
	  gimple_return <_3>

	}

- **GIMPLE IR Simplifies C++ Constructs:**  
  Even complex C++ features like operator overloading get reduced to basic function calls, which can be analyzed systematically.

Using the **`eptalights`** library, we can convert and decompile this GIMPLE IR into a **pseudo-C-like code** to easily understand what's happening.

.. code-block:: python

	fn = api.get_function_by_id(fid="/example/src/01_helloworld.cpp:main#1")
	print(fn.decompile())

	# output
	"""
	main  (  )
	{
		<bb 2> :
		std::basic_ostream<char, std::char_traits<char>>& std::operator<<<std::char_traits<char>>  ( &std::cout, R"("Hello World!")" );
		$T3 = 0;

		<bb 3> :
		nop;
		return $T3;
	}
	"""

1. At the core, **GCC treats C++ as C** with **structs** and **functions**. Even complex constructs like ``std::cout << "Hello World!"`` are broken down into function calls and assignments.

2. The **operator overload** ``operator<<`` is explicitly shown as a function call:
   ```
   std::operator<<<std::char_traits<char>>  ( &std::cout, R"("Hello World!")" );
   ```

Now let's say we want to **programmatically find all string arguments** passed to ``std::cout`` via ``operator<<``. Here's how we can do that:

.. code-block:: python

	"""
	find all `operator<<` callsites
	"""
	for callsite in fn.callsite_manager.search(name="operator<<"):
	    """
	    check if the first argument is `std::cout` and also num_of_args is 2
	    """
	    if 'std::cout' in callsite.variables_used_as_callsite_arg and callsite.num_of_args == 2:
	        """
	        print the second argument off the call arguments
	        """
	        step = fn.steps[callsite.step_index]
	        print(step.fargs[1].readable()) 

	# output
	"""
	""Hello World!""
	"""

What's Happening Here?

1. **Search for `operator<<` Call Sites:**  
   - We scan the function for any calls to the **`operator<<`** function, which is responsible for the stream insertion (i.e., `std::cout <<`).

2. **Filter for `std::cout` Calls:**  
   - We ensure the first argument is **`std::cout`** and that exactly **two arguments** are passed (e.g., `std::cout << "Hello World!"`).

3. **Extract the String Argument:**  
   - We retrieve and print the **second argument** (which is the string being printed).



2. Working with operator overloading in C++
-------------------------------------------

Let's explore **operator overloading** in C++ by analyzing the internal structure of an overloaded operator and tracking how it’s used in a project. 

Suppose we have a C++ file ``04_operator_overloading.cpp`` with a class that overloads the **increment (`++`) operator**.

.. code-block:: c++

	#include <iostream>
	using namespace std;

	class Check
	{
	    private:
	       int i;
	    public:
	       Check(): i(0) {  }
	       void operator ++() 
	          { ++i; }
	       void Display() 
	          { cout << "i=" << i << endl; }
	};

	int main()
	{
	    Check obj;

	    // Displays the value of data member i for object obj
	    obj.Display();

	    // Invokes operator function void operator ++( )
	    ++obj; 
	  
	    // Displays the value of data member i for object obj
	    obj.Display();

	    return 0;
	}

First, we load the project configuration and list all functions (including class methods) defined in the file.

.. code-block:: python

	# get functions (includiinig class methods) defined in a file
	for fn in api.get_functions_by_filepath(filepath="/example/src/04_operator_overloading.cpp"):
	    print(f"fname={fn.name}")

	# output
	"""
	fname=_GLOBAL__sub_I_main
	fname=__static_initialization_and_destruction_0
	fname=main
	fname=Check::operator++
	fname=Check::Display
	fname=Check::Check
	"""

Now, let's inspect the overloaded **increment operator** function ``Check::operator++`` by viewing its **Pseudo-C** code.

.. code-block:: python

	fn = api.get_function_by_id(fid="/example/src/04_operator_overloading.cpp:Check::operator++#1")
	print(fn.decompile())

	# output
	"""
	Check::operator++  ( this )
	{
		<bb 2> :
		$T1 = this->i;
		$T2 = $T1 + 1;
		this->i = $T2;
		return;
	}
	"""

Explanation of the Decompiled Code:

1. **`this->i`**  
   - ``$T1 = this->i;``  
   The current value of the member variable ``i`` is loaded into a temporary variable ``$T1``.

2. **Increment Operation**  
   - ``$T2 = $T1 + 1;``  
   The increment operation is performed, and the result is stored in another temporary variable ``$T2``.

3. **Assignment Back to Member Variable**  
   - ``this->i = $T2;``  
   The incremented value is assigned back to ``i``.

We can list all the variables (including SSA variables) used in the overloaded operator function.

.. code-block:: python

	fn = api.get_function_by_id(fid="/example/src/04_operator_overloading.cpp:Check::operator++#1")
	print(fn.variable_manager.names)

	# output
	"""
	['this', '$T1', '$T2']
	"""

Finally, let’s search for all locations where ``Check::operator++`` is invoked in the codebase.

.. code-block:: python
	
	for fn, callsite in api.search_callsites(filter_by_name="Check::operator++"):
		print(f"{callsite.fn_name} is called in `{fn.name}` in `{fn.filepath}`")

	# output
	"""
	['Check::operator++'] is called in `main` in `/example/src/04_operator_overloading.cpp`
	"""


3. Working with vectors
-----------------------

Let's start by decompiling the Pseudo-C code for a simple vector example to see how vectors are handled internally.

.. code-block:: python

	fn = api.get_function_by_id(fid="/example/src/05_vector.cpp:main#1")
	print(fn.decompile())

	# output
	"""
	main  (  )
	{

		<bb 2> :
		std::vector<int, std::allocator<int>>::vector  ( &vect );
		689541713 = 10;
		std::vector<int, std::allocator<int>>::push_back  ( &vect, &689541713 );

		<bb 3> :
		689541713 = R"({)"R"(CLOBBER)"R"(})";
		689541714 = 20;
		std::vector<int, std::allocator<int>>::push_back  ( &vect, &689541714 );

		<bb 4> :
		689541714 = R"({)"R"(CLOBBER)"R"(})";
		689541715 = 30;
		std::vector<int, std::allocator<int>>::push_back  ( &vect, &689541715 );

		...redacted
	}
	"""

In **GIMPLE IR**, C++ ``std::vector`` is essentially treated as a ``struct``. Let's inspect the type of the ``vect`` variable.

.. code-block:: python

	fn = api.get_function_by_id(fid="/example/src/05_vector.cpp:main#1")

	print(fn.variable_manager.get('vect').full_declaration)
	print(fn.variable_manager.get('vect').type_declaration)

	# output
	"""
	struct vector vect
	struct vector
	"""

C++ vectors are represented as ``struct vector`` types in GIMPLE IR, and operations like ``push_back`` are treated as function calls.

1. **Vector Initialization:**
   ```c++
   std::vector<int, std::allocator<int>>::vector  ( &vect );
   ```
   This is the constructor call initializing the `vect` variable.

2. **Adding Elements with `push_back`:**
   ```c++
   689541713 = 10;
   std::vector<int, std::allocator<int>>::push_back  ( &vect, &689541713 );
   ```
   - `689541713` is a temporary variable holding the value `10`, which is passed to `push_back`.


To retrieve all values pushed to the vector, we can:

1. **Find all `push_back` calls**.
2. **Extract the second argument** passed to `push_back` (the value).
3. **Track where the value is defined** and retrieve its actual content.

.. code-block:: python

	# Get all callsites to `::push_back`
	for cs in fn.callsite_manager.search(name='::push_back'):
	    # Get second argument and its SSA version
	    second_arg = cs.variables_used_as_callsite_arg[1]
	    second_arg_ssa = cs.ssa_variables_used_as_callsite_arg[1]

	    # Retrieve the SSA variable
	    ssa_variable = fn.variable_manager.get(second_arg).get_ssa_var(second_arg_ssa)

	    # Get steps where the variable is defined
	    for step_index in ssa_variable.variable_defined_at_steps:
	        print(fn.steps[step_index].decompile())

	# output
	"""
	689541713 = 10;
	689541714 = 20;
	689541715 = 30;
	"""

To isolate just the numeric values being assigned, we can print the **left-hand side (LHS)** of the assignment.

.. code-block:: python

	# Get all callsites to `::push_back`
	for cs in fn.callsite_manager.search(name='::push_back'):
	    # Get second argument and its SSA version
	    second_arg = cs.variables_used_as_callsite_arg[1]
	    second_arg_ssa = cs.ssa_variables_used_as_callsite_arg[1]

	    # Retrieve the SSA variable
	    ssa_variable = fn.variable_manager.get(second_arg).get_ssa_var(second_arg_ssa)

	    # Print only the LHS of the assignment
	    for step_index in ssa_variable.variable_defined_at_steps:
	        step = fn.steps[step_index]
	        print(step.src.lhs.decompile())

	# output
	"""
	10
	20
	30
	"""


4. Working with maps
--------------------

When we declare a map like ``std::map<std::string, int> mp;``, the **pPseudo-C** representation shows it as a `struct map`.

.. code-block:: c++

	struct map mp;


and initialized with

.. code-block:: c++

	std::map<std::__cxx11::basic_string ...redacted const, int>>>::map  ( &mp );


To insert key-value pairs, the GIMPLE IR represents the process in multiple steps:

1. **Create the key (`std::string`):**

.. code-block:: c++

	struct allocator 689546326;
	struct key_type 689546327;

	std::allocator<char>::allocator  ( &689546326 );
	std::__cxx11::basic_string  ( &689546327, R"("one")", &689546326 );


2. **Insert the key into the map using `operator[]`:**

.. code-block:: c++
	
	$T22 = operator[]  ( &mp, &689546327 );


3. **Assign the value to the key:**

.. code-block:: c++

	$T1 = $T22;
	*$T1 = 1;


This sequence represents the statement ``mp["one"] = 1`` in the original C++ code.

To clarify, the above can be simplified into the following Pseudo-C code:

.. code-block:: c++

	struct map mp;
	struct allocator 689546326;
	struct key_type 689546327;
	mapped_type & $T22;

	map ( &mp );
	allocator<char>::allocator  ( &689546326 );
	basic_string  ( &689546327, R"("one")", &689546326 );

	$T22 = operator[] ( &mp, &689546327 );
	$T1 = $T22;
	*$T1 = 1;


Now, let's see how to extract all keys from the map using eptalights.

.. code-block:: python

	"""
	Get all callsites where `std::map` is initialized
	"""
	for cs in fn.callsite_manager.search(name='::map'):
	    """
	    there might be a lot of function with `::map` in it like:

	    - std::map<...>>>::~map
	    - std::map<...>>>::end
	    - std::map<...>>>::begin
	    - std::map<...>>>::operator[]

	    but we are only interested in ones ending with `::map`:

	    - std::map<...>>>::map

	    we could have search for `>::map` for a save us with addition
	    checking but for the sake of education on our APIs
	    """
	    if not cs.fn_name[0].endswith("::map"):
	        continue

	    # Ensure only one argument (the map instance)
	    if cs.num_of_args != 1:
	        continue

	    # Get the map's variable name (which is currently 'mp')
	    map_struct_name = cs.variables_used_as_callsite_arg[0]

	    """
	    Find all `operator[]` calls that use this map instance
	    """
	    for operator_cs in fn.callsite_manager.search(name='>::operator[]'):
	    	# Ensure it has exactly two arguments: map and key
	        if operator_cs.num_of_args != 2:
	            continue

	        # Check if this operator[] is called on our map
	        if map_struct_name not in cs.variables_used_as_callsite_arg[0]:
	            continue

	        # Extract the key (second argument)
	        key_type_var = operator_cs.variables_used_as_callsite_arg[1]
	        key_type_ssa_var = operator_cs.ssa_variables_used_as_callsite_arg[1]

	        # Retrieve the key variable details
	        key_type = fn.variable_manager.get(key_type_var).get_ssa_var(key_type_ssa_var)

	        """
	        Find where the key is defined in `basic_string`
	        """
	        for kt_cs_name in key_type.variable_used_in_callsites:
	            if ">::basic_string" not in kt_cs_name:
	                continue

	            # Get the callsite and step for the key creation
	            kt_cs = fn.callsite_manager.by_ssa_name(ssa_name=kt_cs_name)
	            step = fn.steps[kt_cs.step_index]

	            """
	            # Extract the key's actual string value which is the second argument of : 
	            ::basic_string  ( &689546327, R"("one")", &689546326 );
	            """
	            map_key_value = step.fargs[1].readable()

	# output
	"""
	""one""
	""two""
	""three""
	"""

1. **Maps in GIMPLE IR:**
   - C++ ``std::map`` is represented as a ``struct map`` in GIMPLE IR.
   - The ``operator[]`` function is used for inserting and accessing values.

2. **Tracking Key Insertion:**
   - The key is created using ``basic_string``, and its value is stored in a temporary variable.
   - The value is then assigned to the map using the pointer returned from ``operator[]``.

3. **Extracting Keys and Values with eptalights:**
   - By identifying ``operator[]`` callsites and tracing their arguments, we can retrieve all the keys inserted into the map.


5. Working with function overloading in C++
-------------------------------------------

Function overloading allows multiple functions to have the same name but differ in **argument types** or **number of parameters**.

In **Eptalights**, overloaded functions are uniquely identified by their **function IDs (fid)**.

To identify overloaded functions, we can list all functions in a file and observe multiple entries for the same function name but with different identifiers (``#1``, ``#2``, ``#3``, etc.).

.. code-block:: python

	for fn in api.get_functions_by_filepath(filepath="/example/src/09_function_overloading.cpp"):
	    print(fn.fid)

	# output
	"""
	/example/src/09_function_overloading.cpp:_GLOBAL__sub_I_main#1
	/example/src/09_function_overloading.cpp:__static_initialization_and_destruction_0#1
	/example/src/09_function_overloading.cpp:Geeks::func#1
	/example/src/09_function_overloading.cpp:Geeks::func#2
	/example/src/09_function_overloading.cpp:Geeks::func#3
	/example/src/09_function_overloading.cpp:main#1
	"""

Above, ``Geeks::func`` is overloaded three times.

We can decompile each version of `Geeks::func` to understand their differences.

.. code-block:: python

	for fn in api.get_functions_by_filepath(filepath="/example/src/09_function_overloading.cpp"):
	    if "Geeks::func" not in fn.name:
	        continue

	    print(fn.fid)
	    print(fn.decompile())

	# output
	"""
	// /example/src/09_function_overloading.cpp:Geeks::func#1
	Geeks::func  ( this, x )
	{
		<bb 2> :
		$T5 = std::operator<<  ( &std::cout, R"("value of x is ")" );
		$T1 = $T5;
		$T8 = std::ostream::operator<<  ( $T1, x );
		$T2 = $T8;
		std::ostream::operator<<  ( $T2, std::endl );
		return;
	}

	// /example/src/09_function_overloading.cpp:Geeks::func#2
	Geeks::func  ( this, x )
	{
		<bb 2> :
		$T5 = std::operator<<  ( &std::cout, R"("value of x is ")" );
		$T1 = $T5;
		$T8 = std::ostream::operator<<  ( $T1, x );
		$T2 = $T8;
		std::ostream::operator<<  ( $T2, std::endl );
		return;
	}

	// /example/src/09_function_overloading.cpp:Geeks::func#3
	Geeks::func  ( this, x, y )
	{
		<bb 2> :
		$T7 = std::operator<<  ( &std::cout, R"("value of x and y is ")" );
		$T1 = $T7;
		$T10 = std::ostream::operator<<  ( $T1, x );
		$T2 = $T10;
		$T12 = std::operator<<  ( $T2, R"(", ")" );
		$T3 = $T12;
		$T15 = std::ostream::operator<<  ( $T3, y );
		$T4 = $T15;
		std::ostream::operator<<  ( $T4, std::endl );
		return;
	}
	"""

1. **`Geeks::func#1`** and **`Geeks::func#2`** both accept one argument `x`.
2. **`Geeks::func#3`** accepts two arguments, `x` and `y`.

Even though ``Geeks::func#1`` and ``Geeks::func#2`` have the same number of arguments, their **argument types** differ. We can inspect these using the variable manager.

.. code-block:: python

	func1_id = "/example/src/09_function_overloading.cpp:Geeks::func#1"
	func2_id = "/example/src/09_function_overloading.cpp:Geeks::func#2"

	fn1 = api.get_function_by_id(func1_id)
	fn2 = api.get_function_by_id(func2_id)

	print("func#1 = ", fn1.variable_manager.get('x').full_declaration)
	print("func#2 = ", fn2.variable_manager.get('x').full_declaration)

	# output
	"""
	func#1 =  int x
	func#2 =  double x
	"""

- **`Geeks::func#1`** accepts an **integer** argument.
- **`Geeks::func#2`** accepts a **double** argument.

1. **Unique Identification:**  
   In Eptalights IR, each overloaded function is uniquely identified by its ``fid``, such as ``Geeks::func#1``, ``Geeks::func#2``, etc.

2. **Differentiation Criteria:**  
   Overloaded functions differ by:
   - The **number** of parameters.
   - The **types** of parameters.
