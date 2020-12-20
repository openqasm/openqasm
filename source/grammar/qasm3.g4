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
    : 'OPENQASM' Integer (DOT Integer)? SEMICOLON
    ;

include
    : 'include' StringLiteral SEMICOLON
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

globalStatement: subroutineDefinition
    | kernelDeclaration
    | quantumGateDefinition
    | calibrationDefinition
    ;

declarationStatement
    : ( quantumDeclaration | classicalDeclaration | constantDeclaration) SEMICOLON
    ;

comment : LineComment | BlockComment ;

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
    : Identifier ( designator | doubleDesignator | rangeDefinition )?
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
    : quantumType indexIdentifierList
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

bitDeclaration
    : bitType Identifier designator
    ;

classicalVariableDeclaration
    : singleDesignatorDeclaration
    | doubleDesignatorDeclaration
    | noDesignatorDeclaration
    | bitDeclaration
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
    : LBRACE quantumStatement* RBRACE
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
    : '~' | '!'
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
    | StringLiteral
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
    : '#pragma' LBRACE . RBRACE
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
    returnSignature? LBRACE . RBRACE
    ;

calibrationGrammar
    : 'openpulse' | Identifier
    ;

calibrationArgumentList
    : classicalArgumentList | expressionList
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

ASSIGN : '=' ;
ARROW : '->' ;

Constant : 'pi' | 'π' | 'tau' | '𝜏' | 'euler' | 'e' ;

Whitespace : [ \t]+ -> skip ;
Newline : [\r\n]+ -> skip ;

fragment Digit : [0-9] ;
Integer : Digit+ ;

fragment LowerCaseCharacter : [a-z] ;
fragment UpperCaseCharacter : [A-Z] ;

fragment SciNotation : [eE] ;
fragment PlusMinus : [-+] ;

Float : Integer* DOT Integer+ ;

RealNumber : Float (SciNotation PlusMinus? Float)? ;

fragment NumericalCharacter
    : LowerCaseCharacter
    | UpperCaseCharacter
    | '_'
    | Integer
    ;

Identifier : LowerCaseCharacter ( NumericalCharacter )* ;

fragment Quotation : '"' | '\'' ;

StringLiteral : Quotation Any Quotation ;

fragment AnyString : ~[ \t\r\n]+? ;
fragment Any : ( AnyString | Whitespace | Newline )+ ;
fragment AnyBlock : LBRACE Any? RBRACE ;

LineComment : '//' Any ; // Token because Any matches all strings
BlockComment : '/*' Any '*/' ; // Token because Any matches all strings
