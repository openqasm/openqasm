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
    : 'OPENQASM' ( Integer | RealNumber ) SEMICOLON
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
    | timingStatement
    | pragma
    ;

globalStatement
    : subroutineDefinition
    | kernelDeclaration
    | quantumGateDefinition
    | calibration
    ;

declarationStatement
    : ( quantumDeclaration | classicalDeclaration | constantDeclaration ) SEMICOLON
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
    : concatenateExpression
    | Identifier designator?
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
    : singleDesignatorType designator
    | doubleDesignatorType doubleDesignator
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
    : LBRACE ( quantumStatement | timingStatement )* RBRACE
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
    : ( 'inv' | 'pow' LBRACKET expression RBRACKET | 'ctrl' ) '@'
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
    | MINUS? ( Integer | RealNumber )
    | Identifier
    | StringLiteral
    | timingTerminator
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
    : 'kernel' Identifier ( LPAREN classicalTypeList? RPAREN )? returnSignature?
    classicalType? SEMICOLON
    ;

// if called w/ out parentheses, is ambiguous; may get matched as identifier
kernelCall
    : Identifier LPAREN expressionList? RPAREN
    ;

/* Subroutines */

subroutineDefinition
    : 'def' Identifier ( LPAREN classicalArgumentList? RPAREN )? quantumArgumentList?
    returnSignature? programBlock
    ;

// if called w/ out paretheses, is ambiguous; may get matched as identifier
subroutineCall
    : Identifier ( LPAREN expressionList? RPAREN )? expressionList
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
    | 'boxto' TimingLiteral quantumBlock
    ;

timingTerminator
    : timingIdentifier | 'stretchinf'
    ;

timingIdentifier
    : TimingLiteral
    | MINUS? 'lengthof' LPAREN ( Identifier | quantumBlock ) RPAREN
    ;

timingInstructionName
    : 'delay'
    | 'rotary'
    ;

timingInstruction
    : timingInstructionName ( LPAREN expressionList? RPAREN )? designator indexIdentifierList
    ;

timingStatement
    : timingInstruction SEMICOLON
    | timingBox
    ;

/* Pulse Level Descriptions of Gates and Measurement */
// TODO: Update when pulse grammar is formalized ****

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
    returnSignature? LBRACE .*? RBRACE  // for now, match anything inside body
    ;

calibrationGrammar
    : '"openpulse"' | StringLiteral // currently: pulse grammar string can be anything
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
Integer : Digit+ ;

fragment ValidUnicode : [\p{Lu}\p{Ll}\p{Lt}\p{Lm}\p{Lo}\p{Nl}] ; // valid unicode chars
fragment Letter : [A-Za-z] ;
fragment FirstIdCharacter : '_' | '%' | ValidUnicode | Letter ;
fragment GeneralIdCharacter : FirstIdCharacter | Integer;

Identifier : FirstIdCharacter GeneralIdCharacter* ;

fragment SciNotation : [eE] ;
fragment PlusMinus : [-+] ;
fragment Float : Digit+ DOT Digit* ;
RealNumber : Float (SciNotation PlusMinus? Float)? ;

fragment TimeUnit : 'dt' | 'ns' | 'us' | 'µs' | 'ms' | 's' ;
// represents explicit time value in SI or backend units
TimingLiteral : MINUS? (Integer | RealNumber ) TimeUnit ;

// allow ``"str"`` and ``'str'``
StringLiteral
    : '"' ~["\r\t\n]+? '"'
    | '\'' ~['\r\t\n]+? '\''
    ;

// skip comments
LineComment : '//' ~[\r\n]* -> skip;
BlockComment : '/*' .*? '*/' -> skip;
