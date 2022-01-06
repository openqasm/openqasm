/***** ANTLRv4  grammar for OpenQASM3.0. *****/

grammar qasm3;

/**** Parser grammar ****/

program
    : header (globalStatement | statement)*
    ;

header
    : version? include* io*
    ;

version
    : 'OPENQASM' ( Integer | RealNumber ) SEMICOLON
    ;

include
    : 'include' StringLiteral SEMICOLON
    ;

ioIdentifier
    : 'input'
    | 'output'
    ;
io
    : ioIdentifier classicalType Identifier SEMICOLON
    ;

globalStatement
    : subroutineDefinition
    | externDeclaration
    | quantumGateDefinition
    | calibration
    | quantumDeclarationStatement  // qubits are declared globally
    | pragma
    ;

statement
    : expressionStatement
    | assignmentStatement
    | classicalDeclarationStatement
    | branchingStatement
    | loopStatement
    | endStatement
    | aliasStatement
    | quantumStatement
    ;

quantumDeclarationStatement : quantumDeclaration SEMICOLON ;

classicalDeclarationStatement
    : ( classicalDeclaration | constantDeclaration ) SEMICOLON
    ;

classicalAssignment: indexedIdentifier assignmentOperator expression;

assignmentStatement : ( classicalAssignment | quantumMeasurementAssignment ) SEMICOLON ;

returnSignature
    : ARROW classicalType
    ;

/*** Types and Casting ***/

designator
    : LBRACKET expression RBRACKET
    ;

identifierList
    : ( Identifier COMMA )* Identifier
    ;

/** Quantum Types **/
quantumDeclaration
    : 'qreg' Identifier designator? | 'qubit' designator? Identifier
    ;

quantumArgument
    : 'qreg' Identifier designator? | 'qubit' designator? Identifier
    ;

quantumArgumentList
    : quantumArgument ( COMMA quantumArgument )*
    ;

/** Classical Types **/
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

noDesignatorType
    : 'bool'
    | timingType
    ;

nonArrayType
    : singleDesignatorType designator
    | noDesignatorType
    | bitType designator?
    | COMPLEX LBRACKET numericType RBRACKET
    ;

arrayType: ARRAY LBRACKET nonArrayType COMMA expressionList RBRACKET;
arrayReferenceTypeDimensionSpecifier: (
    expressionList
    | DIM EQUALS expression
);
arrayReferenceType:
    ARRAY
    LBRACKET
    nonArrayType
    COMMA arrayReferenceTypeDimensionSpecifier
    RBRACKET;

classicalType
    : nonArrayType
    | arrayType
    ;

// numeric OpenQASM types
numericType
    : singleDesignatorType designator
    ;

constantDeclaration
    : CONST classicalType Identifier equalsExpression
    ;

// if multiple variables declared at once, either none are assigned or all are assigned
// prevents ambiguity w/ qubit arguments in subroutine calls
singleDesignatorDeclaration
    : singleDesignatorType designator Identifier equalsExpression?
    ;

noDesignatorDeclaration
    : noDesignatorType Identifier equalsExpression?
    ;

bitDeclaration
    : ( 'creg' Identifier designator? | 'bit' designator? Identifier ) equalsExpression?
    ;

complexDeclaration
    : COMPLEX LBRACKET numericType RBRACKET Identifier equalsExpression?
    ;

arrayInitializer: LBRACE (
        (expression | arrayInitializer) (COMMA (expression | arrayInitializer))*
    ) RBRACE;
arrayDeclaration: arrayType Identifier (EQUALS (arrayInitializer | expression))?;

classicalDeclaration
    : singleDesignatorDeclaration
    | noDesignatorDeclaration
    | bitDeclaration
    | complexDeclaration
    | arrayDeclaration
    ;

classicalTypeList
    : ( classicalType COMMA )* classicalType
    ;

classicalArgument
    : (singleDesignatorType designator | noDesignatorType) Identifier
    | 'creg' Identifier designator?
    | 'bit' designator? Identifier
    | COMPLEX LBRACKET numericType RBRACKET Identifier
    | (CONST | MUTABLE) arrayReferenceType Identifier
    ;

classicalArgumentList
    : classicalArgument ( COMMA classicalArgument )*
    ;

anyTypeArgument
    : classicalArgument
    | quantumArgument
    ;

anyTypeArgumentList
    : ( anyTypeArgument COMMA )* anyTypeArgument
    ;

/** Aliasing **/
aliasStatement
    : 'let' Identifier EQUALS aliasInitializer SEMICOLON
    ;

/** Register Concatenation and Slicing **/

aliasInitializer
    : expression
    | aliasInitializer '++' aliasInitializer
    ;

rangeDefinition
    : expression? COLON expression? ( COLON expression )?
    ;

/*** Gates and Built-in Quantum Instructions ***/

quantumGateDefinition
    : 'gate' quantumGateSignature quantumBlock
    ;

quantumGateSignature
    : quantumGateName ( LPAREN identifierList? RPAREN )? identifierList
    ;

quantumGateName
    : 'U'
    | 'CX'
    | Identifier
    ;

quantumBlock
    : LBRACE ( quantumStatement | quantumLoop )* RBRACE
    ;

// loops containing only quantum statements allowed in gates
quantumLoop
    : loopSignature quantumLoopBlock
    ;

quantumLoopBlock
    : quantumStatement
    | LBRACE quantumStatement* RBRACE
    ;

quantumStatement
    : quantumInstruction SEMICOLON
    | timingStatement
    ;

quantumInstruction
    : quantumGateCall
    | quantumPhase
    | quantumMeasurement
    | quantumReset
    | quantumBarrier
    ;

quantumPhase
    : quantumGateModifier* 'gphase' LPAREN expression RPAREN (indexedIdentifier (COMMA indexedIdentifier)*)?
    ;

quantumReset
    : 'reset' indexedIdentifier
    ;

quantumMeasurement
    : 'measure' indexedIdentifier
    ;

quantumMeasurementAssignment
    : quantumMeasurement ( ARROW indexedIdentifier )?
    | indexedIdentifier EQUALS quantumMeasurement
    ;

quantumBarrier
    : 'barrier' (indexedIdentifier (COMMA indexedIdentifier)*)?
    ;

quantumGateModifier
    : ( 'inv' | powModifier | ctrlModifier ) '@'
    ;

powModifier
    : 'pow' LPAREN expression RPAREN
    ;

ctrlModifier
    : ( 'ctrl' | 'negctrl' ) ( LPAREN expression RPAREN )?
    ;

quantumGateCall
    : quantumGateModifier* quantumGateName ( LPAREN expressionList RPAREN )? indexedIdentifier (COMMA indexedIdentifier)*
    ;

/*** Classical Instructions ***/

unaryOperator
    : '~' | '!' | '-'
    ;

comparisonOperator
    : '>'
    | '<'
    | '>='
    | '<='
    ;

equalityOperator
    : '=='
    | '!='
    ;

logicalOperator
    : '&&'
    | '||'
    ;

expressionStatement
    : expression SEMICOLON
    ;

expression
    // include terminator/unary as base cases to simplify parsing
    : expressionTerminator
    | unaryExpression
    // expression hierarchy
    | logicalAndExpression
    | expression '||' logicalAndExpression
    ;

/**  Expression hierarchy for non-terminators. Adapted from ANTLR4 C
  *  grammar: https://github.com/antlr/grammars-v4/blob/master/c/C.g4
  * Order (first to last evaluation):
    Terminator (including Parens),
    Unary Op,
    Multiplicative
    Additive
    Bit Shift
    Comparison
    Equality
    Bit And
    Exlusive Or (xOr)
    Bit Or
    Logical And
    Logical Or
**/

logicalAndExpression
    : bitOrExpression
    | logicalAndExpression '&&' bitOrExpression
    ;

bitOrExpression
    : xOrExpression
    | bitOrExpression '|' xOrExpression
    ;

xOrExpression
    : bitAndExpression
    | xOrExpression '^' bitAndExpression
    ;

bitAndExpression
    : equalityExpression
    | bitAndExpression '&' equalityExpression
    ;

equalityExpression
    : comparisonExpression
    | equalityExpression equalityOperator comparisonExpression
    ;

comparisonExpression
    : bitShiftExpression
    | comparisonExpression comparisonOperator bitShiftExpression
    ;

bitShiftExpression
    : additiveExpression
    | bitShiftExpression ( '<<' | '>>' ) additiveExpression
    ;

additiveExpression
    : multiplicativeExpression
    | additiveExpression ( PLUS | MINUS ) multiplicativeExpression
    ;

multiplicativeExpression
    // base case either terminator or unary
    : unaryExpression
    | multiplicativeExpression ( MUL | DIV | MOD ) unaryExpression
    ;

unaryExpression
    : unaryOperator? powerExpression
    ;

powerExpression
    : indexExpression
    | powerExpression '**' indexExpression
    ;

// The general form is a comma-separated list of indexing entities.
// `discreteSet` is only valid when being used as a single index: registers can
// support it for creating aliases, but arrays cannot.
indexOperator:
    LBRACKET
    (
        discreteSet
        | (expression | rangeDefinition) (COMMA (expression | rangeDefinition))*
    )
    RBRACKET;
indexExpression
    : expressionTerminator
    | indexExpression indexOperator
    ;

// Alternative form to `indexExpression` for cases where an obvious l-value is
// better grammatically than a generic expression.  Some current uses of this
// rule may be better as `expression`, leaving the semantic analysis to later
// (for example in gate calls).
indexedIdentifier: Identifier indexOperator*;

expressionTerminator
    : Constant
    | Integer
    | RealNumber
    | ImagNumber
    | booleanLiteral
    | Identifier
    | StringLiteral
    | builtInCall
    | externOrSubroutineCall
    | timingIdentifier
    | LPAREN expression RPAREN
    ;
/** End expression hierarchy **/

booleanLiteral
    : 'true' | 'false'
    ;

builtInCall
    : ( builtInMath | castOperator | SIZEOF) LPAREN expressionList RPAREN
    ;

builtInMath
    : 'arcsin'
    | 'sin'
    | 'arccos'
    | 'cos'
    | 'arctan'
    | 'tan'
    | 'exp'
    | 'ln'
    | 'sqrt'
    | 'rotl'
    | 'rotr'
    | 'popcount'
    ;

castOperator
    : classicalType
    ;

expressionList
    : expression ( COMMA expression )*
    ;

equalsExpression
    : EQUALS expression
    ;

assignmentOperator
    : EQUALS
    | '+=' | '-=' | '*=' | '/=' | '&=' | '|=' | '~=' | '^=' | '<<=' | '>>=' | '%=' | '**='
    ;

discreteSet: LBRACE expression (COMMA expression)* RBRACE;

setDeclaration
    : discreteSet
    | LBRACKET rangeDefinition RBRACKET
    | Identifier
    ;

programBlock
    : statement | controlDirective
    | LBRACE ( statement | controlDirective )* RBRACE
    ;

branchingStatement
    : 'if' LPAREN expression RPAREN programBlock ( 'else' programBlock )?
    ;

loopSignature
    : 'for' Identifier 'in' setDeclaration
    | 'while' LPAREN expression RPAREN
    ;

loopStatement: loopSignature programBlock ;

endStatement
    : 'end' SEMICOLON
    ;

returnStatement
    : 'return' ( expression | quantumMeasurement )? SEMICOLON;

controlDirective
    : ('break' | 'continue') SEMICOLON
    | endStatement
    | returnStatement
    ;

externDeclaration
    : 'extern' Identifier LPAREN classicalTypeList? RPAREN returnSignature? SEMICOLON
    ;

// if have function call w/ out args, is ambiguous; may get matched as identifier
externOrSubroutineCall
    : Identifier LPAREN expressionList? RPAREN
    ;

/*** Subroutines ***/

subroutineDefinition
    : 'def' Identifier LPAREN anyTypeArgumentList? RPAREN
    returnSignature? subroutineBlock
    ;

subroutineBlock
    : LBRACE statement* returnStatement? RBRACE
    ;

/*** Directives ***/

pragma
    : '#pragma' LBRACE statement* RBRACE  // match any valid openqasm statement
    ;

/*** Circuit Timing ***/

timingType
    : 'duration'
    | 'stretch'
    ;

timingBox
    : 'box' designator? quantumBlock
    ;

timingIdentifier
    : TimingLiteral
    | 'durationof' LPAREN ( Identifier | quantumBlock ) RPAREN
    ;

timingInstructionName
    : 'delay'
    | 'rotary'
    ;

timingInstruction
    : timingInstructionName (LPAREN expressionList? RPAREN)? designator indexedIdentifier (COMMA indexedIdentifier)*
    ;

timingStatement
    : timingInstruction SEMICOLON
    | timingBox
    ;

/*** Pulse Level Descriptions of Gates and Measurement ***/
// TODO: Update when pulse grammar is formalized

calibration
    : calibrationGrammarDeclaration
    | calibrationDefinition
    ;

calibrationGrammarDeclaration
    : 'defcalgrammar' calibrationGrammar SEMICOLON
    ;

calibrationDefinition
    : 'defcal' Identifier
    ( LPAREN calibrationArgumentList? RPAREN )? identifierList
    returnSignature? LBRACE .*? RBRACE  // for now, match anything inside body
    ;

calibrationGrammar
    : '"openpulse"' | StringLiteral  // currently: pulse grammar string can be anything
    ;

calibrationArgumentList
    : classicalArgumentList | expressionList
    ;

/**** Lexer grammar ****/

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

PLUS : '+';
MINUS : '-' ;
MUL : '*';
DIV : '/';
MOD : '%';

IMAG: 'im';
ImagNumber : ( Integer | RealNumber ) IMAG ;

COMPLEX: 'complex';

HASH: '#';
CONST: 'const';
MUTABLE: 'mutable';
ARRAY: 'array';
SIZEOF: 'sizeof';
DIM: '#dim';

Constant : ( 'pi' | 'π' | 'tau' | '𝜏' | 'euler' | 'ℇ' );

Whitespace : [ \t]+ -> skip ;
Newline : [\r\n]+ -> skip ;

fragment Digit : [0-9] ;
Integer : Digit+ ;

fragment ValidUnicode : [\p{Lu}\p{Ll}\p{Lt}\p{Lm}\p{Lo}\p{Nl}] ; // valid unicode chars
fragment Letter : [A-Za-z] ;
fragment FirstIdCharacter : '_' | '$' | ValidUnicode | Letter ;
fragment GeneralIdCharacter : FirstIdCharacter | Integer;

Identifier : FirstIdCharacter GeneralIdCharacter* ;

fragment SciNotation : [eE] ;
fragment PlusMinus : PLUS | MINUS ;
fragment Float : Digit+ DOT Digit* ;
RealNumber : (Integer | Float ) (SciNotation PlusMinus? Integer )? ;

fragment TimeUnit : 'dt' | 'ns' | 'us' | 'µs' | 'ms' | 's' ;
// represents explicit time value in SI or backend units
TimingLiteral : (Integer | RealNumber ) TimeUnit ;

// allow ``"str"`` and ``'str'``
StringLiteral
    : '"' ~["\r\t\n]+? '"'
    | '\'' ~['\r\t\n]+? '\''
    ;

// skip comments
LineComment : '//' ~[\r\n]* -> skip;
BlockComment : '/*' .*? '*/' -> skip;
