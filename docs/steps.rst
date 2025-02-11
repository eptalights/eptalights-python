.. _steps:


Working with Steps or Instructions
==================================

Data model or structure for steps - :class:`~eptalights.models.egimple.function.EGimpleIRNopModel` :class:`~eptalights.models.egimple.function.EGimpleIRAssignModel` :class:`~eptalights.models.egimple.function.EGimpleIRCallModel` :class:`~eptalights.models.egimple.function.EGimpleIRCondModel` :class:`~eptalights.models.egimple.function.EGimpleIRReturnModel` :class:`~eptalights.models.egimple.function.EGimpleIRGotoModel` :class:`~eptalights.models.egimple.function.EGimpleIRSwitchModel`

Steps are essentially instructions or individual IR code statements. All steps have unique identifier called ``step_index``.


1. print OP and Pseudo-C code of steps
--------------------------------------

Steps are simply the instructions of the function and can be found in `fn.steps`.  

.. code-block:: python

	for step in fn.steps:
	    print(step.op, step.decompile())

	"""
	ASSIGN 	sum = 0;

	CALL 	printf  ( R"("Enter number of elements: ")" );

	CALL 	*__isoc99_scanf  ( R"("%d")", &n );

	ASSIGN 	$T1 = n;

	ASSIGN 	$T2 = $T1;

	ASSIGN 	$T3 = $T2 * 4;

	CALL 	ptr = malloc  ( $T3 );

	COND 	if ( ptr == 0 )
			goto <bb 5>;
		else
			goto <bb 7>;

	CALL 	printf  ( R"("Error! memory not allocated.")" );

	CALL 	exit  ( 0 );
	"""


2. print steps of a basicblock
------------------------------

We first get the mapping of ``basicblock_index`` to ``step_index`` list from the function's ``cfg`` and print out ``op`` and ``Pseudo-C`` for each basicblocks.

.. code-block:: python

	for basicblock_index, basicblock_steps in fn.cfg.basicblock_steps.items():
	    print(f"\n-------------")
	    print(f"basicblock_index: {basicblock_index}\n")

	    for step_index in basicblock_steps:
	        step = fn.steps[step_index]
	        print(f"step_index={step.step_index} op={step.op}, code={step.decompile()}")

	"""
	-------------
	basicblock_index: 2

	step_index=0 op=ASSIGN, code=	x[0] = 1;

	step_index=1 op=ASSIGN, code=	x[1] = 2;

	step_index=2 op=ASSIGN, code=	x[2] = 3;

	step_index=3 op=ASSIGN, code=	x[3] = 4;

	step_index=4 op=ASSIGN, code=	x[4] = 5;

	step_index=5 op=ASSIGN, code=	ptr = &x[2];

	step_index=6 op=ASSIGN, code=	$T1 = *ptr;

	step_index=7 op=CALL, code=	printf  ( R"("*ptr = %d \n")", $T1 );


	-------------
	basicblock_index: 3

	step_index=8 op=ASSIGN, code=	$T2 = ptr + 4;

	step_index=9 op=ASSIGN, code=	$T3 = *$T2;

	step_index=10 op=CALL, code=	printf  ( R"("*(ptr+1) = %d \n")", $T3 );


	-------------
	basicblock_index: 4

	step_index=11 op=ASSIGN, code=	$T4 = ptr + 18446744073709551612;

	step_index=12 op=ASSIGN, code=	$T5 = *$T4;

	step_index=13 op=CALL, code=	printf  ( R"("*(ptr-1) = %d")", $T5 );


	-------------
	basicblock_index: 5

	step_index=14 op=ASSIGN, code=	$T17 = 0;

	step_index=15 op=ASSIGN, code=	x = R"({)"R"(CLOBBER)"R"(})";


	-------------
	basicblock_index: 6

	step_index=16 op=NOP, code=	nop;

	step_index=17 op=RETURN, code=	return $T17;


	-------------
	basicblock_index: 7

	step_index=18 op=NOP, code=	nop;

	step_index=19 op=ASSIGN, code=	x = R"({)"R"(CLOBBER)"R"(})";

	step_index=20 op=NOP, code=	nop;
	"""
