CS 6390 Fall 2019 Final Project
=======================================
Anish Moorthy and Nicholas Martucci

Included files
--------------------------------------
- language.py              Defines the keywords, base value types, and built-in functions of the Dead-Simple Language (DSL).
- dsl_parser.py            Tokenizes a DSL program
- dsl_types.py             Contains classes for function, value, and reference types as wells as classes for type specifiers.
- env.py                   Contains classes for the environments that map the bindings of names to values for the interpreter and names to types for the affine_checker.
- interpreter.py           Evaluates a DSL program.
- affine_checker.py        Performs type-checking of unrestricted, linear, and affine variables in a DSL program.
- typecheck_errors.py      Includes the type-checking errors that can be raised by the affine_checker.
- test_interpreter.py      Suite of tests that demonstrate the functionality of the interpreter.
- test_affine_checker.py   Suite of tests that demonstrate the correctness of the affine_checker.
- presentation.ipynb       Executable notebook used to summarize and demonstrate our work for final presentation
