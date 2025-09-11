.. _php_support:

Working with PHP
================

Our approach to code analysis for PHP is completely different from existing tools, which primarily focus on the Abstract Syntax Tree (AST). In contrast, we analyze PHP from the bytecode level.

Our philosophy centers on performing code analysis at lower representations such as bytecode, instructions, or intermediate representations (IR) to achieve greater accuracy, rather than working with the AST or source-like layers.

This approach is especially relevant for PHP because, like any other language, PHP has its own syntax rules. AST-based analysis often requires in-depth knowledge of the language, so we instead transform the code into a universal, Pythonic model to simplify the process.

Additionally, many enterprise-grade PHP applications employ source code encoding mechanisms. In some cases, the original source code cannot be recovered after encoding. However, the crucial insight is that regardless of the encoding method, the code ultimately gets compiled to bytecode at runtime. This is the layer we target for extraction and transformation into a more accessible and uniform representation.

In the following sections, we will explore how to analyze several **PHP functionalities**.


1. Hello World in PHP
---------------------

First, let's understand how a simple **Hello World** program is translated into **Zend Bytecode**, and how we can interpret it using Python.

.. code-block:: php

    <!DOCTYPE html>
    <html>
    <body>
       <h1>My PHP Website</h1>
       <?php
          echo "Hello World!";
       ?>
    </body>
    </html>


When you disassembled this using **phpdbg** and inspect the **Zend Bytecode Instructions**, it appears as:

.. code-block:: sh

    $ src/v8.3.6/source/php-src-8.3.6/sapi/phpdbg/phpdbg -p* /extractor/abc.php


.. code-block:: sh

    $_main:
         ; (lines=4, args=0, vars=0, tmps=0)
         ; /extractor/abc.php:1-10
    L0001 0000 ECHO string("<!DOCTYPE html>
    <html>
    <body>
       <h1>My PHP Website</h1>
       ")
    L0006 0001 ECHO string("Hello World!")
    L0008 0002 ECHO string("</body>
    </html>
    ")
    L0010 0003 RETURN int(1)

Using Eptalight's Lifter, the PHP bytecode instructions are lifted into a SOPHIA-IR, where call sites, functions, classes, control flow graphs (CFG), and variables are extracted and made easily accessible in a Pythonic way.

.. code-block:: python

    fn = api.get_function_by_id(fid="/01_helloworld.php:main#1")
    print(fn.decompile())

    # output
    """
    main  (  )
    {
        <bb 0> :
        echo  ( '<!DOCTYPE html>\n<html>\n<body>\n   <h1>My PHP Website</h1>\n   ' );
        echo  ( 'Hello World!' );
        echo  ( '</body>\n</html>\n' );
        return 1;

    }
    """

For this example, we use the Python library to print all calls to the **echo** function along with the string-based arguments passed to it.  

.. code-block:: python

    for callsite in fn.callsite_manager.search(name="echo"):
        print(fn.steps[callsite.step_index].op, fn.steps[callsite.step_index].decompile())

    # output
    """
    CALL    echo  ( '<!DOCTYPE html>\n<html>\n<body>\n   <h1>My PHP Website</h1>\n   ' );

    CALL    echo  ( 'Hello World!' );

    CALL    echo  ( '</body>\n</html>\n' );
    """

2. Working with Classes
-----------------------

Let's explore classes in PHP and how to work with them. Consider the following class:

.. code-block:: php
    
    <?php
       class myclass {    
          public function __construct() {    
             echo "Inside the constructor of ". __CLASS__ . PHP_EOL;    
          }    
          function getClassName(){                      
             echo "from an instance method of " . __CLASS__ . "";   
          }    
       }    
       $obj = new myclass;    
       $obj->getClassName();    
    ?>

Before we do anything, let's look at how it is represented at the bytecode level.

.. code-block:: sh

    $_main:
         ; (lines=6, args=0, vars=1, tmps=4)
         ; /extractor/abc.php:1-12
    L0010 0000 V1 = NEW 0 string("myclass")
    L0010 0001 DO_FCALL
    L0010 0002 ASSIGN CV0($obj) V1
    L0011 0003 INIT_METHOD_CALL 0 CV0($obj) string("getClassName")
    L0011 0004 DO_FCALL
    L0012 0005 RETURN int(1)

    user class: myclass
    2 methods: __construct, getClassName

    myclass::__construct:
         ; (lines=2, args=0, vars=0, tmps=0)
         ; /extractor/abc.php:3-5
    L0004 0000 ECHO string("Inside the constructor of myclass
    ")
    L0005 0001 RETURN null

    myclass::getClassName:
         ; (lines=2, args=0, vars=0, tmps=0)
         ; /extractor/abc.php:6-8
    L0007 0000 ECHO string("from an instance method of myclass")
    L0008 0001 RETURN null


Let's list the functions within that class. The file gives us the following:

.. code-block:: python

    for fn in api.get_functions_by_filepath(filepath="/09_magic_constant3.php"):
        print(f"classname={fn.class_name} fname={fn.name}")

    # output
    """
    classname=None fname=main
    classname=myclass fname=__construct
    classname=myclass fname=getClassName
    """

From the functions listed above, we can see that `__construct` and `getClassName` have the class name `myclass`, since they are defined within a class.  
Any code not defined within a class is placed in the file's main function.

Let's decompile using Eptalight's library to examine this further:

.. code-block:: python

    """
    get file metadata - name of classes, functions, class properties in a file
    """
    file_metadata = api.get_file_metadata_by_filepath(filepath="/09_magic_constant3.php")

    """
    get file data - get the functions models of the names listed in the metadata
    """
    file_data = api.get_file_data_by_metadata(file_metadata)

    """
    print out pseudo-c representation of the lifted bytecode
    """
    print(file_data.decompile())

    # output
    """
    // Class Properties and Constants 
    class myclass  { 

    }

    myclass :: __construct  (  )
    {
        <bb 0> :
        echo  ( 'Inside the constructor of myclass\n' );
        return 'null';

    }

    myclass :: getClassName  (  )
    {
        <bb 0> :
        echo  ( 'from an instance method of myclass' );
        return 'null';

    }

    main  (  )
    {
        <bb 0> :
        @1 = myclass  (  );
        $obj = @1;
        $obj->getClassName  (  );
        return 1;

    }
    """

3. Working with Obfuscated PHP Code
-----------------------------------

Some PHP projects employ tools to obfuscate their code in order to hide their intentions.  
Below is a code snippet from **CloudPanel** (https://www.cloudpanel.io/), a free software tool for configuring and managing servers.

We can observe that it uses a lot of `goto` statements to obfuscate the program's control flow, and it also encodes all strings, making them unreadable to the human eye.

.. code-block:: php
    
    <?php
    namespace App;
    use Symfony\Bundle\FrameworkBundle\Kernel\MicroKernelTrait;
    use Symfony\Component\DependencyInjection\Loader\Configurator\ContainerConfigurator;
    use Symfony\Component\HttpKernel\Kernel as BaseKernel;
    use Symfony\Component\Routing\Loader\Configurator\RoutingConfigurator;
    class Kernel extends BaseKernel
    {
        use MicroKernelTrait;
        protected function configureContainer(
            ContainerConfigurator $container
        ): void {
            goto A4243;
            d61c8:
            F2ccd:
            goto C97c8;
            dc8bf:
            goto F2ccd;
            goto Cee12;
            Fcd67:
            $container->import(
                "\x2e\56\x2f\143\x6f\156\146\151\147\x2f\x7b\160\x61\143\x6b\141\x67\x65\163\x7d\x2f" .
                    $this->environment .
                    "\x2f\52\x2e\171\141\x6d\x6c"
            );
            goto f9b9a;
            Ab043:
            $container->import(
                "\56\56\x2f\143\157\x6e\x66\x69\147\57\x7b\x73\x65\162\166\151\x63\x65\x73\x7d\x5f" .
                    $this->environment .
                    "\x2e\171\x61\x6d\x6c"
            );
            goto d61c8;
            A4243:
            $container->import(
                "\x2e\x2e\x2f\x63\x6f\x6e\146\151\x67\x2f\173\x70\141\x63\153\141\147\x65\163\x7d\x2f\x2a\x2e\x79\x61\155\154"
            );
            goto Fcd67;
            a4649:
            $container->import(
                "\56\56\57\x63\x6f\x6e\x66\x69\x67\57\163\145\x72\x76\151\143\x65\163\56\171\x61\155\x6c"
            );
            goto Ab043;
            f9b9a:
            if (
                is_file(
                    \dirname(__DIR__) .
                        "\x2f\x63\157\156\146\151\147\57\163\x65\162\x76\151\143\x65\163\56\x79\x61\155\154"
                )
            ) {
                goto A3922;
            }
            goto C7490;
            Cee12:
            A3922:
            goto a4649;
            C7490:
            $container->import(
                "\x2e\x2e\57\x63\x6f\156\x66\151\x67\57\x7b\163\x65\x72\166\151\x63\x65\x73\x7d\56\160\x68\x70"
            );
            goto dc8bf;
            C97c8:
        }
    }

But when we examine the code at the bytecode level, it's readable!  
We realize that its strings are readable when compiled into bytecode using the PHP Zend engine.

.. code-block:: sh

    $_main:
         ; (lines=2, args=0, vars=0, tmps=0)
         ; /extractor/abc.php:1-64
    L0007 0000 DECLARE_CLASS string("app\\kernel") string("symfony\\component\\httpkernel\\kernel")
    L0064 0001 RETURN int(1)

    user class: App\Kernel
    1 methods: configureContainer

    App\Kernel::configureContainer:
         ; (lines=43, args=1, vars=1, tmps=14)
         ; /extractor/abc.php:10-63
    L0010 0000 CV0($container) = RECV 1
    L0013 0001 JMP 0019
    L0016 0002 JMP 0042
    L0018 0003 JMP 0002
    L0019 0004 JMP 0037
    L0021 0005 INIT_METHOD_CALL 1 CV0($container) string("import")
    L0023 0006 T1 = FETCH_OBJ_R THIS string("environment")
    L0023 0007 T2 = CONCAT string("../config/{packages}/") T1
    L0024 0008 T3 = CONCAT T2 string("/*.yaml")
    L0024 0009 SEND_VAL_EX T3 1
    L0021 0010 DO_FCALL
    L0026 0011 JMP 0027
    L0028 0012 INIT_METHOD_CALL 1 CV0($container) string("import")
    L0030 0013 T5 = FETCH_OBJ_R THIS string("environment")
    L0030 0014 T6 = CONCAT string("../config/{services}_") T5
    L0031 0015 T7 = CONCAT T6 string(".yaml")
    L0031 0016 SEND_VAL_EX T7 1
    L0028 0017 DO_FCALL
    L0033 0018 JMP 0002
    L0035 0019 INIT_METHOD_CALL 1 CV0($container) string("import")
    L0036 0020 SEND_VAL_EX string("../config/{packages}/*.yaml") 1
    L0035 0021 DO_FCALL
    L0038 0022 JMP 0005
    L0040 0023 INIT_METHOD_CALL 1 CV0($container) string("import")
    L0041 0024 SEND_VAL_EX string("../config/services.yaml") 1
    L0040 0025 DO_FCALL
    L0043 0026 JMP 0012
    L0046 0027 INIT_NS_FCALL_BY_NAME 1 string("App\\is_file")
    L0047 0028 INIT_FCALL 1 96 string("dirname")
    L0047 0029 SEND_VAL string("/extractor") 1
    L0047 0030 V11 = DO_ICALL
    L0048 0031 T12 = CONCAT V11 string("/config/services.yaml")
    L0048 0032 SEND_VAL_EX T12 1
    L0046 0033 V13 = DO_FCALL
    L0048 0034 JMPZ V13 0036
    L0051 0035 JMP 0037
    L0053 0036 JMP 0038
    L0056 0037 JMP 0023
    L0058 0038 INIT_METHOD_CALL 1 CV0($container) string("import")
    L0059 0039 SEND_VAL_EX string("../config/{services}.php") 1
    L0058 0040 DO_FCALL
    L0061 0041 JMP 0003
    L0063 0042 RETURN null


After extracting and lifting the PHP bytecode, we can print out the decompiled version of the obfuscated code above.

.. code-block:: python

    """
    get file metadata - name of classes, functions, class properties in a file
    """
    file_metadata = api.get_file_metadata_by_filepath(filepath="/09_magic_constant3.php")

    """
    get file data - get the functions models of the names listed in the metadata
    """
    file_data = api.get_file_data_by_metadata(file_metadata)

    """
    print out pseudo-c representation of the lifted bytecode
    """
    print(file_data.decompile())

    # output
    """
    // Class Properties and Constants
    class App\Kernel  {

    }

    App\Kernel :: configureContainer  ( [unnamed] $container )
    {
        <bb 0> :
        nop;
        goto 'BB_6';

        <bb 1> :
        goto 'BB_13';

        <bb 2> :
        goto 'BB_1';

        <bb 3> :
        goto 'BB_13';

        <bb 4> :
        T1 = $this->environment;
        T2 = '../config/{packages}/' + T1;
        T3 = T2 + '/*.yaml';
        $container->import  ( T3 );
        goto 'BB_8';

        <bb 5> :
        T5 = $this->environment;
        T6 = '../config/{services}_' + T5;
        T7 = T6 + '.yaml';
        $container->import  ( T7 );
        goto 'BB_1';

        <bb 6> :
        $container->import  ( '../config/{packages}/*.yaml' );
        goto 'BB_4';

        <bb 7> :
        $container->import  ( '../config/services.yaml' );
        goto 'BB_5';

        <bb 8> :
        @11 = dirname  ( '/src' );
        T12 = @11 + '/config/services.yaml';
        @13 = App\is_file  ( T12 );
        if ( @13 )
            goto <bb 9>;
        else
            goto <bb 10>;

        <bb 9> :
        goto 'BB_11';

        <bb 10> :
        goto 'BB_12';

        <bb 11> :
        goto 'BB_7';

        <bb 12> :
        $container->import  ( '../config/{services}.php' );
        goto 'BB_2';

        <bb 13> :
        return 'null';

    }

    main  (  )
    {
        <bb 0> :
        class  ( 'app\\kernel', 'symfony\\component\\httpkernel\\kernel' );
        return 1;

    }
    """

4. Working with Encoded PHP Code
--------------------------------

Most enterprise PHP source codes are encoded to look like the code below. The source code starts with a loader, followed by the encoded code, which isn't recoverable.  

Encoded PHP code can only be executed with the loader module or, in some special cases like the example with Plesk code below, a custom PHP runtime where the first part of the code starts with the loader, followed by a garbled-looking code, which is actually what gets executed.

.. code-block:: php

    <?php
        die("The file {$_SERVER['SCRIPT_FILENAME']} is part of Plesk distribution. It cannot be run outside of Plesk environment.\n");
        __sw_loader_pragma__('PLESK_18_0_59');
    ?>
    ²0 $®äûrs“7Õîõ\òå<µYúzR®µªó˜I…—5ßâÚœÓ!ç˜›”ÿ·Üxy·ò¯8¢HÆ¡çiX¢NN5zM=ºöÝ..[redacted]..


With the above garbled-looking code, we are left with working only at the bytecode level.  
After extracting the bytecode and lifting it, we can print out the decompiled code and also access variables, call sites, etc.

.. code-block:: python

    """
    get file metadata - name of classes, functions, class properties in a file
    """
    file_metadata = api.get_file_metadata_by_filepath(filepath="/09_magic_constant3.php")

    """
    get file data - get the functions models of the names listed in the metadata
    """
    file_data = api.get_file_data_by_metadata(file_metadata)

    """
    print out pseudo-c representation of the lifted bytecode
    """
    print(file_data.decompile())

    # output
    """
    main  (  )
    {
        <bb 0> :
        T3 = $$fetch_class_constant  ( 'Session', 'IS_UNDEFINED' );
        @4 = get  (  );
        @5 = @4->auth  (  );
        @6 = @5->getUser  (  );
        @7 = @6->getType  (  );
        T8 = @7 != T3;
        if ( T8 )
            goto <bb 1>;
        else
            goto <bb 2>;

        <bb 1> :
        @9 = get  ( 'webApplication' );
        $app = @9;
        $app->destroySession  (  );
        go_to_self  (  );

        <bb 2> :
        $page = '/login_up.php';
        @14 = getUrlFromRequest  ( 'success_redirect_url', 'false', 'false' );
        $successRedirectUrl = @14;
        T15 = $successRedirectUrl;
        if ( T15 )
            goto <bb 3>;
        else
            goto <bb 4>;

        <bb 3> :
        @16 = urlencode  ( $successRedirectUrl );
        T17 = '?success_redirect_url=' + @16;
        $page = $page + T17;

        <bb 4> :
        go_to  ( $page );
        return 1;

    }
    """

5. Conclusion
-------------

Even though we are focusing on the capabilities of what is possible, all variables, call sites, control flow graphs (CFG), Dataflow and more can be easily accessed using our Python library.  
Further details are provided in other sections of the documentation.
