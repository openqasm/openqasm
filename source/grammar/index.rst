Grammar
=======

This is a simplified grammar for Open QASM presented in Backus-Naur
form. The unlisted productions :math:`\langle\mathrm{id}\rangle`,
:math:`\langle\mathrm{real}\rangle` and
:math:`\langle\mathrm{nninteger}\rangle` are defined by the regular
expressions below::

		id        := [a-z][A-Za-z0-9_]*
		real      := ([0-9]+\.[0-9]*|[0-9]*\.[0-9]+)([eE][-+]?[0-9]+)?
		nninteger := [1-9]+[0-9]*|0
        ...       := .*

Production rules are defined with plain text and denoted by a colon ``production : rule``.
Keywords are enclosed in quotations ``rule : "keyword"``. Whitespace denotes
concatenation. Alternatives are denoted by ``|`` and may be grouped with 
parentheses ``(rule1 | rule2 | ...)``. Optional rules are terminated with a ``?`` (zero or one), 
repetition is denoted by curly brackets ``+`` (one or more) and ``*`` (zero or more). An ellipses
``...`` is used to match any series of token.

.. productionlist::
    program: header generic_statement*
    header: version? include*
    version: "OPENQASM" real ";"
    include: "include" id ( ".inc" | ".qasm" ) ";"
    generic_statement: global_statement
        :| statement
    global_statement: subroutine_declaration
        :| kernel_declaration
        :| gate_definition
        :| calibration
    statement: expression_statement
        :| declaration_statement
        :| selection_statement
        :| iteration_statement
        :| selection_directive_statement
        :| quantum_statement
        :| timing_box
        :| pragma
    subroutine_declaration: "def" id args_declaration return_signature? program_block
    args_declaration : "(" type_and_id_list ")"
    type_and_id_list: ( classical_type_and_id_list | quantum_type_and_id_list )*
    classical_type_and_id_list: ( declare_type association "," )* declare_type association
    declare_type: dependent_type_declaration 
        :| independent_type_specifier
    dependent_type_declaration: dependent_type_specifier designator
    dependent_type_specifier: "int" | "uint" | "angle" | "fixed" | "stretch"
    designator: "[" expression "]"
    independent_type_specifier: "bit" | "creg" | "bool" 
        :| timing_type
    association: ":" id
    return_signature: "->" classical_declaration
    constant_declaration: "const" ( dependent_type_declaration | independent_type ) assignment 
    classical_declaration: ( dependent_type_declaration | independent_type ) assignment?
    program_block: "{" ( program_block | statement ) "}"
    kernel_declaration: "kernel" id classical_type_and_id_list return_signature? ";"
    expression_statement: expression ";"
        :| "return" expression ";
    expression: primary_expression 
        :| expression binaryop expression
        :| unary_operator expression 
        :| membership_test
        :| expression '[' expression ']'
        :| call "(" expression_list? ")"
        :| expression incrementor
        :| quantum_measurement
        :| expression_terminator
    expression_terminator: real | nninteger | id
        :| constant
        :| time_terminator
    constant: "pi" | "π" | "tau" | "𝜏" | "euler"
    expression_list: ( expression "," )* expression 
    unary_operator: "~" | "!"
    call: expression
        :| builtin_math
        :| cast_operator
    builtin_math: "sin" | "cos" | "tan" | "exp" | "ln" | "sqrt" | "popcount" | "lengthof"
    cast_operator: declare_type
    incrementor: "++" | "--
    pragma: "#pragma {" ... "}"
    declaration_statement: (quantum_declaration | classical_declaration | constant_declaration) ";"
    assignment_expression: expression assignment_operator expression
    binary_operator: "+" | "-" | "*" | "/" 
        :| "<<" | ">>" | "rotr" | "rotl" | "&" | "|" | "^" | "&&" | "||"
        :| ">" | "<" | ">=" | "<=" | "==" | "!="
    assignment_operator: "=" | "+=" | "-=" | "*=" | "/=" |
        :| "<<=" | ">>=" |  "&=" | "|=" | "^=" | "~=" | "->"
    membership_test: id "in" set_declaration
    index_set_declaration: "{" index_set_generators "}"
    index_set_generators: expression_list | range
    range: expression? ":" expression? ( ":" expression )?
    selection_statement: "if (" expression ")" program_block ( "else" program_block )?
    iteration_statement: "for" membership_test program_block | "while (" expression ")" program_block
    selection_directive_statement: selection_directive ";"
    selection_directive: "break" | "continue" | "exit"
    quantum_gate_definition: "gate" quantum_gate_signature quantum_gate_block
    quantum_gate_signature: id quantum_gate_args id_lis
    quantum_gate_args: ( "(" classical_type_and_id_list? ")" )?
    quantum_gate_block: "{" quantum_gate_call* "}"
    quantum_type_and_id_list: ( quantum_type_and_id "," )* quantum_type_and_id
    quantum_type_and_id: quantum_type designator? association 
    quantum_statement: quantum_instruction ";"
    quantum_instruction: quantum_gate_call
        :| quantum_measurement
    quantum_measurement: "measure" argument
    quantum_gate_modifiers: ( "inv" | "pow" "[" nninteger "]" | "ctrl" ) "@"
    quantum_gate_call: quantum_gate_name quantum_gate_args designator any_list ";"
    quantum_gate_name: "CX" | "U" | "delay" | "reset" | id
        :| quantum_gate_modifier "@" quantum_gate_name
    quantum_gate_modifier: "inv" | "ctrl"
        :| "pow" nninteger?
    quantum_gate_args: ( "(" expression_list? ")" )?
    quantum_declaration: quantum_type id designator
    quantum_type: "qubit" | "qreg"
    qubit_id_list: ( qubit_id "," )* qubit_id
    qubit_id: id | "%" [ "q" ] nninteger
    timing_box: "boxas" id gate_block
        :| "boxto" time_unit gate_block
    timing_type: "length" | "stretch" nninteger?
    time_terminator: time | "stretchinf"
    time: id time_unit
    time_unit: "dt" | "ns" | "us" | "ms" | "s"
    calibration: calibration_grammar_declaration | calibration_definition
    calibration_grammar_declaration: "defcalgrammar" id ";"
    calibration_definition: "defcal" grammar_type id calibration_args qubit_id_list return_signature calibration_body
    calibration_grammar_type: ( "openpulse" | id )*
    calibration_args: ( "(" [ id_const_list ] ")" )*
    mixed_type_specified_list: ( id_const_list | classical_type_and_id_list ) 
        :| mixed_type_specified_list
    id_const_list: ( expression_terminator "," )* expression_terminator
    calibration_body: "{" ... "}"