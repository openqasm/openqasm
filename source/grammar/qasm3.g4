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
    | assignmentStatement
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

globalStatement
    : subroutineDefinition
    | kernelDeclaration
    | quantumGateDefinition
    | calibrationDefinition
    ;

declarationStatement
    : ( quantumDeclaration | classicalDeclaration | constantDeclaration) SEMICOLON
    ;

assignmentStatement
    :
    (
        Identifier assignmentOperator expression
        |   expression ARROW Identifier
        |   quantumMeasurementAssignment
    )
    SEMICOLON
    ;

comment : LineComment | BlockComment ;

returnSignature
    : ARROW classicalType
    ;

programBlock
    : LBRACE statement* RBRACE
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
    : Identifier ( designator | concatenateExpression )?
    ;

indexIdentifierList
    : ( indexIdentifier COMMA )* indexIdentifier
    ;

indexEqualsAssignmentList
    : ( indexIdentifier equalsExpression? COMMA)* indexIdentifier equalsExpression?
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
    : 'const' Identifier equalsExpression
    ;

singleDesignatorDeclaration
    : singleDesignatorType designator equalsAssignmentList
    ;

doubleDesignatorDeclaration
    : doubleDesignatorType doubleDesignator equalsAssignmentList
    ;

noDesignatorDeclaration
    : noDesignatorType equalsAssignmentList
    ;

bitDeclaration
    : bitType indexEqualsAssignmentList
    ;

classicalDeclaration
    : singleDesignatorDeclaration
    | doubleDesignatorDeclaration
    | noDesignatorDeclaration
    | bitDeclaration
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
    : 'let' Identifier EQUALS concatenateExpression SEMICOLON
    ;

// Register Concatenation and Slicing
concatenateExpression
    : Identifier rangeDefinition
    | Identifier '||' Identifier
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
    : LBRACE ( quantumStatement | comment )* RBRACE
    ;

quantumStatement
    : quantumInstruction SEMICOLON
    ;

quantumInstruction
    : quantumGateCall
    | quantumMeasurement
    | quantumBarrier
    ;

quantumMeasurement
    : 'measure' indexIdentifierList
    ;

quantumMeasurementAssignment
    : quantumMeasurement ARROW indexIdentifierList
    | indexIdentifierList EQUALS quantumMeasurement
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
    | expression incrementor
    | concatenateExpression
    | expression LBRACKET expression RBRACKET
    | LPAREN expression RPAREN
    | membershipTest
    | call expressionList
    | subroutineCall
    | kernelCall
    | quantumMeasurement
    | MINUS expression
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

equalsExpression
    : EQUALS expression
    ;

assignmentOperator
    : EQUALS
    | '+=' | '-=' | '*=' | '/=' | '&=' | '|=' | '~=' | '^=' | '<<=' | '>>='
    ;

equalsAssignmentList
    : ( Identifier equalsExpression? COMMA)* Identifier equalsExpression?
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
    : 'kernel' Identifier LPAREN classicalTypeList? RPAREN returnSignature?
    classicalType? SEMICOLON
    ;

kernelCall
    : Identifier LPAREN expressionList? RPAREN
    ;

/* Subroutines */

subroutineDefinition
    : 'def' Identifier LPAREN classicalArgumentList? RPAREN quantumArgumentList?
    returnSignature? programBlock
    ;

subroutineCall
    : Identifier LPAREN expressionList? RPAREN expressionList
    ;

/* Directives */

pragma
    : '#pragma' LBRACE . RBRACE
    ;

/* Circuit Timing */

timingType
    : 'length'
    | 'stretch' Integer?
    ;

timingBox
    : 'boxas' Identifier quantumBlock
    | 'boxto' TimeLiteral quantumBlock
    ;

timeTerminator
    : timeIdentifier | 'stretchinf'
    ;

timeIdentifier
    : TimeLiteral
    | MINUS? 'lengthof' LPAREN Identifier RPAREN
    ;


timeInstructionName
    : 'delay'
    | 'rotary'
    ;

timeInstruction
    : timeInstructionName ( LPAREN expressionList? RPAREN )? designator indexIdentifierList
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

EQUALS : '=' ;
ARROW : '->' ;

MINUS : '-' ;

Constant : MINUS? ( 'pi' | 'π' | 'tau' | '𝜏' | 'euler' | 'e' );

Whitespace : [ \t]+ -> skip ;
Newline : [\r\n]+ -> skip ;

fragment Digit : [0-9] ;
Integer : MINUS? Digit+ ;

fragment ValidUnicode : [\p{Lu}\p{Ll}\p{Lt}\p{Lm}\p{Lo}\p{Nl}] ; // valid unicode chars
fragment Letter : [A-Za-z] ;
fragment FirstIdCharacter : '_' | '%' | ValidUnicode | Letter ;
fragment GeneralIdCharacter : FirstIdCharacter | Integer;

Identifier : FirstIdCharacter GeneralIdCharacter* ;

fragment SciNotation : [eE] ;
fragment PlusMinus : [-+] ;
fragment Float : Integer* DOT Integer+ ;

RealNumber : MINUS? Float (SciNotation PlusMinus? Float)? ;

fragment TimeUnit : 'dt' | 'ns' | 'us' | 'µs' | 'ms' | 's' ;

TimeLiteral : RealNumber TimeUnit ;  // represents explicit time value in SI or backend units

fragment Quotation : '"' | '\'' ;

StringLiteral : Quotation Any Quotation ;

fragment AnyString : ~[ \t\r\n]+? ;
fragment Any : ( AnyString | Whitespace | Newline )+ ;
fragment AnyBlock : LBRACE Any? RBRACE ;

LineComment : '//' ~('\r'|'\n')*; // Token because Any matches all strings
BlockComment : '/*' Any '*/' ; // Token because Any matches all strings
