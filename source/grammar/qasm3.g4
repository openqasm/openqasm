/**** ANTLRv4  grammar for OpenQASM3.0. ****/

grammar qasm3;

/** Parser grammar **/

program
    : header statement*
    ;

header
    : version? include*
    ;

version
    : 'OPENQASM' Integer (DOT Integer)?
    ;

include
    : 'include' Identifier '.qasm' SEMICOLON
    ;

statement
    : globalStatement
    | expressionStatement
    | declarationStatement
    | branchingStatement
    | loopStatement
    | controlDirectiveStatement
    | aliasStatement
    | quantumStatement
    | timeStatement
    | pragma
    | comment
    ;

globalStatement: subroutine Definition
    | kernelDeclaration
    | quantumGateDefinition
    | calibrationDefinition
    ;

declarationStatement
    : ( quantumDeclaration | classicalDeclaration | constantDeclaration) SEMICOLON
    ;

comment
    : '//' AnyString? '\n'
    | '/*' AnyString? '*/'
    ;

returnSignature
    : ARROW classicalDeclaration
    ;

programBlock
    : LBRACE ( programBlock | statement ) RBRACE
    ;

/* Types and Casting */

designator
    : LBRACKET expression RBRACKET
    ;

doubleDesignator
    : LBRACKET expression COMMA expression RBRACKET
    ;

identifierList
    : ( Identifier COMMA )* Identifier
    ;

indexIdentifier
    : Identifier designator?
    ;

indexIdentifierList
    : ( indexIdentifier COMMA )* indexIdentifier
    ;

association
    : COLON Identifier
    ;

// Quantum Types
quantumType
    : 'qubit'
    | 'qreg'
    ;

quantumDeclaration
    : quantumType Identifier designator
    ;

quantumArgument
    : quantumType designator? association
    ;

quantumArgumentList
    : ( quantumArgument COMMA )* quantumArgument
    ;

// Classical Types
bitType
    : 'bit'
    | 'creg'
    ;

singleDesignatorType
    : 'int'
    | 'uint'
    | 'float'
    | 'angle'
    ;

doubleDesignatorType
    : 'fixed'
    ;

noDesignatorType
    : 'bool'
    | timingType
    ;

classicalType
    : singleDesignatorType designator?
    | doubleDesignatorType doubleDesignator?
    | noDesignatorType
    | bitType designator?
    ;

constantDeclaration
    : 'const' Identifier ASSIGN expression
    ;

singleDesignatorDeclaration
    : singleDesignatorType designator Identifier
    ;

doubleDesignatorDeclaration
    : doubleDesignatorType doubleDesignator Identifier
    ;

noDesignatorDeclaration
    : noDesignatorType Identifier
    ;

classicalVariableDeclaration
    : singleDesignatorDeclaration
    | doubleDesignatorDeclaration
    | noDesignatorDeclaration
    ;

classicalDeclaration
    : classicalVariableDeclaration assignmentExpression?
    ;

classicalTypeList
    : ( classicalType COMMA )* classicalType
    ;

classicalArgument
    : classicalType association
    ;

classicalArgumentList
    : ( classicalArgument COMMA )* classicalArgument
    ;

// Aliasing
aliasStatement
    : 'let' Identifier ASSIGN concatenateExpression
    ;

// Register Concatenation and Slicing
concatenateExpression
    : ASSIGN
    ( Identifier rangeDefinition
    | Identifier '||' Identifier
    | Identifier LBRACKET expressionList RBRACKET )
    ;

rangeDefinition
    : LBRACKET expression? COLON expression? ( COLON expression )? RBRACKET
    ;

/* Gates and Built-in Quantum Instructions */

quantumGateDefinition
    : 'gate' quantumGateSignature quantumBlock
    ;

quantumGateSignature
    : Identifier ( LPAREN classicalArgumentList? RPAREN )? identifierList
    ;

quantumBlock
    : LBRACE ( quantumBlock | quantumStatement) RBRACE
    ;

quantumStatement
    : ( quantumInstruction | quantumMeasurementDeclaration ) SEMICOLON
    ;

quantumInstruction
    : quantumGateCall
    | quantumMeasurement
    | quantumBarrier
    ;

quantumMeasurement
    : 'measure' indexIdentifierList
    ;

quantumMeasurementDeclaration
    : quantumMeasurement ARROW indexIdentifierList
    | indexIdentifierList ASSIGN quantumMeasurement
    ;

quantumBarrier
    : 'barrier' indexIdentifierList
    ;

quantumGateModifier
    : ( 'inv' | 'pow' LPAREN Integer RPAREN | 'ctrl' ) '@'
    ;

quantumGateCall
    : quantumGateName ( LPAREN expressionList? RPAREN )? indexIdentifierList
    ;

quantumGateName
    : 'CX'
    | 'U'
    | 'reset'
    | Identifier
    | quantumGateModifier quantumGateName
    ;

/* Classical Instructions */

unaryOperator
    : '~' | '!' | builtInMath
    ;

binaryOperator
    : '+' | '-' | '*' | '/' | '<<' | '>>' | 'rotl' | 'rotr' | '&&' | '||' | '&' | '|' | '^'
    | '>' | '<' | '>=' | '<=' | '==' | '!='
    ;

expressionStatement
    : expression SEMICOLON
    | 'return' expressionStatement
    ;

expression
    : expression binaryOperator expression
    | unaryOperator expression
    | membershipTest
    | expression LBRACKET expression RBRACKET
    | call LPAREN expressionList? RPAREN
    | expression incrementor
    | quantumMeasurement
    | expressionTerminator
    ;

expressionTerminator
    : Constant
    | Integer
    | RealNumber
    | Identifier
    | timeTerminator
    ;

expressionList
    : ( expression COMMA )* expression
    ;

call
    : Identifier
    | builtInMath
    | castOperator
    ;

builtInMath
    : 'sin' | 'cos' | 'tan' | 'exp' | 'ln' | 'sqrt' | 'popcount' | 'lengthof'
    ;

castOperator
    : classicalType
    ;

incrementor
    : '++'
    | '--'
    ;

assignmentExpression
    : assignmentOperator expression
    ;

assignmentOperator
    : ASSIGN
    | ARROW
    | '+=' | '-=' | '*=' | '/=' | '&=' | '|=' | '~=' | '^=' | '<<=' | '>>='
    ;

membershipTest
    : Identifier 'in' setDeclaration
    ;

setDeclaration
    : LBRACE expressionList RBRACE
    | rangeDefinition
    ;

loopBranchBlock
    : statement
    | programBlock
    ;

branchingStatement
    : 'if' LPAREN expression RPAREN loopBranchBlock ( 'else' loopBranchBlock )?
    ;

loopStatement: ( 'for' membershipTest | 'while' LPAREN expression RPAREN ) loopBranchBlock
    ;

controlDirectiveStatement
    : controlDirective SEMICOLON
    ;

controlDirective
    : 'break'
    | 'continue'
    | 'end'
    ;

kernelDeclaration
    : 'kernel' Identifier ( LPAREN classicalTypeList? RPAREN )? returnSignature?
    classicalType? SEMICOLON
    ;

/* Subroutines */

subroutineDefinition
    : 'def' Identifier ( LPAREN subroutineArgumentList? RPAREN )? returnSignature? programBlock
    ;

subroutineArgumentList
    : classicalArgumentList | quantumArgumentList
    ;

/* Directives */

pragma
    : '#pragma' LBRACE AnyString? RBRACE
    ;

/* Circuit Timing */

timeUnit
    : 'dt' | 'ns' | 'us' | 'ms' | 's'
    ;

timingType
    : 'length'
    | 'stretch' Integer?
    ;

timingBox
    : 'boxas' Identifier quantumBlock
    | 'boxto' timeUnit quantumBlock
    ;

timeTerminator
    : timeIdentifier | 'stretchinf'
    ;

timeIdentifier
    : Identifier timeUnit?
    | 'lengthof' LPAREN Identifier RPAREN
    ;


timeInstructionName
    : 'delay'
    | 'rotary'
    ;

timeInstruction
    : timeInstructionName ( LPAREN expressionList? RPAREN )? designator
    ( rangeDefinition | indexIdentifierList )
    ;

timeStatement
    : timeInstruction SEMICOLON
    | timingBox
    ;

/* Pulse Level Descriptions of Gates and Measurement */

calibration
    : calibrationGrammarDeclaration
    | calibrationDefinition
    ;

calibrationGrammarDeclaration
    : 'defcalgrammar' calibrationGrammar SEMICOLON
    ;

calibrationDefinition
    : 'defcal' calibrationGrammar? Identifier
    ( LPAREN calibrationArgumentList? RPAREN )? identifierList
    returnSignature calibrationBody
    ;

calibrationGrammar
    : 'openpulse' | Identifier
    ;

calibrationArgumentList
    : classicalArgumentList | expressionList
    ;

calibrationBody
    : LBRACE AnyString? RBRACE
    ;

/** Lexer grammar **/
LBRACKET : '[' ;
RBRACKET : ']' ;

LBRACE : '{' ;
RBRACE : '}' ;

LPAREN : '(' ;
RPAREN : ')' ;

COLON: ':' ;
SEMICOLON : ';' ;

DOT : '.' ;
COMMA : ',' ;

AnyString : ( . | '\n' )+? ;

ASSIGN : '=' ;
ARROW : '->' ;

Constant : 'pi' | 'π' | 'tau' | '𝜏' | 'euler' | 'e' ;

Identifier
    : [a-z] [A-Za-z0-9_]*
    ;

RealNumber
    : [0-9]* DOT [0-9]* ([eE] [-+]? [0-9]+)?
    ;

Integer
    : [1-9]+ [0-9]*
    | '0'
    ;
