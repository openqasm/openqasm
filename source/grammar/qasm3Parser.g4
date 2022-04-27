parser grammar qasm3Parser;

options {
    tokenVocab = qasm3Lexer;
}

program: header (globalStatement | statement)*;
header: version? include* io*;
version: OPENQASM (Integer | RealNumber) SEMICOLON;
include: INCLUDE StringLiteral SEMICOLON;

ioIdentifier: INPUT | OUTPUT;
io: ioIdentifier classicalType Identifier SEMICOLON;

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
classicalDeclarationStatement: (classicalDeclaration | constantDeclaration) SEMICOLON;
classicalAssignment: indexedIdentifier assignmentOperator expression;
assignmentStatement: (classicalAssignment | quantumMeasurementAssignment) SEMICOLON;
returnSignature: ARROW classicalType;

/*** Types and Casting ***/

designator: LBRACKET expression RBRACKET;
identifierList: Identifier (COMMA Identifier)*;

/** Quantum Types **/
quantumDeclaration: QREG Identifier designator? | QUBIT designator? Identifier;
quantumArgument: QREG Identifier designator? | QUBIT designator? Identifier;

/** Classical Types **/
bitType: BIT | CREG;
singleDesignatorType: INT | UINT | FLOAT | ANGLE;
noDesignatorType: BOOL | DURATION | STRETCH;

nonArrayType
    : singleDesignatorType designator
    | noDesignatorType
    | bitType designator?
    | COMPLEX LBRACKET numericType RBRACKET
;

arrayType: ARRAY LBRACKET nonArrayType COMMA expressionList RBRACKET;
arrayReferenceTypeDimensionSpecifier
    : expressionList
    | DIM EQUALS expression
;
arrayReferenceType: ARRAY LBRACKET nonArrayType COMMA arrayReferenceTypeDimensionSpecifier RBRACKET;

classicalType
    : nonArrayType
    | arrayType
;

// numeric OpenQASM types
numericType: singleDesignatorType designator;

constantDeclaration: CONST classicalType Identifier equalsExpression;

// if multiple variables declared at once, either none are assigned or all are assigned
// prevents ambiguity w/ qubit arguments in subroutine calls
singleDesignatorDeclaration: singleDesignatorType designator Identifier equalsExpression?;

noDesignatorDeclaration: noDesignatorType Identifier equalsExpression?;

bitDeclaration: ( CREG Identifier designator? | BIT designator? Identifier ) equalsExpression?;
complexDeclaration: COMPLEX LBRACKET numericType RBRACKET Identifier equalsExpression?;

arrayInitializer:
    LBRACE
    (expression | arrayInitializer)
    (COMMA (expression | arrayInitializer))*
    RBRACE;
arrayDeclaration: arrayType Identifier (EQUALS (arrayInitializer | expression))?;

classicalDeclaration
    : singleDesignatorDeclaration
    | noDesignatorDeclaration
    | bitDeclaration
    | complexDeclaration
    | arrayDeclaration
;

classicalTypeList: classicalType (COMMA classicalType)*;
classicalArgument
    : (singleDesignatorType designator | noDesignatorType) Identifier
    | CREG Identifier designator?
    | BIT designator? Identifier
    | COMPLEX LBRACKET numericType RBRACKET Identifier
    | (CONST | MUTABLE) arrayReferenceType Identifier
;

classicalArgumentList: classicalArgument (COMMA classicalArgument)*;

anyTypeArgument: classicalArgument | quantumArgument;
anyTypeArgumentList: anyTypeArgument (COMMA anyTypeArgument)*;

/** Aliasing **/
aliasInitializer: expression (DOUBLE_PLUS expression)*;
aliasStatement: LET Identifier EQUALS aliasInitializer SEMICOLON;

/** Register Concatenation and Slicing **/

rangeDefinition: expression? COLON expression? (COLON expression)?;

/*** Gates and Built-in Quantum Instructions ***/

quantumGateDefinition
    : GATE quantumGateSignature quantumBlock
    ;

quantumGateSignature
    : quantumGateName ( LPAREN identifierList? RPAREN )? identifierList
    ;

quantumGateName: U_ | CX | Identifier;
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

quantumBarrier: BARRIER (indexedIdentifier (COMMA indexedIdentifier)*)?;
quantumMeasurement: MEASURE indexedIdentifier;
quantumPhase: quantumGateModifier* GPHASE LPAREN expression RPAREN (indexedIdentifier (COMMA indexedIdentifier)*)?;
quantumReset: RESET indexedIdentifier;

quantumMeasurementAssignment
    : quantumMeasurement (ARROW indexedIdentifier)?
    | indexedIdentifier EQUALS quantumMeasurement
;

powModifier: POW LPAREN expression RPAREN;
ctrlModifier: (CTRL | NEGCTRL) ( LPAREN expression RPAREN )?;
quantumGateModifier: (INV | powModifier | ctrlModifier) AT;
quantumGateCall: quantumGateModifier* quantumGateName (LPAREN expressionList RPAREN)? indexedIdentifier (COMMA indexedIdentifier)*;

/*** Classical Instructions ***/

unaryOperator: TILDE | EXCLAMATION_POINT | MINUS;

expressionStatement: expression SEMICOLON;

expression
    // include terminator/unary as base cases to simplify parsing
    : expressionTerminator
    | unaryExpression
    // expression hierarchy
    | logicalAndExpression
    | expression DOUBLE_PIPE logicalAndExpression
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
    | logicalAndExpression DOUBLE_AMPERSAND bitOrExpression
    ;

bitOrExpression
    : xOrExpression
    | bitOrExpression PIPE xOrExpression
    ;

xOrExpression
    : bitAndExpression
    | xOrExpression CARET bitAndExpression
    ;

bitAndExpression
    : equalityExpression
    | bitAndExpression AMPERSAND equalityExpression
    ;

equalityExpression
    : comparisonExpression
    | equalityExpression EqualityOperator comparisonExpression
    ;

comparisonExpression
    : bitShiftExpression
    | comparisonExpression ComparisonOperator bitShiftExpression
    ;

bitShiftExpression
    : additiveExpression
    | bitShiftExpression BitshiftOperator additiveExpression
    ;

additiveExpression
    : multiplicativeExpression
    | additiveExpression (PLUS | MINUS) multiplicativeExpression
    ;

multiplicativeExpression
    // base case either terminator or unary
    : unaryExpression
    | multiplicativeExpression (ASTERISK | SLASH | PERCENT) unaryExpression
    ;

unaryExpression: unaryOperator? powerExpression;

powerExpression
    : indexExpression
    | powerExpression DOUBLE_ASTERISK indexExpression
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
    | BooleanLiteral
    | Identifier
    | StringLiteral
    | builtInCall
    | externOrSubroutineCall
    | timingIdentifier
    | LPAREN expression RPAREN
;
/** End expression hierarchy **/

builtInCall: (BuiltinMath | castOperator | SIZEOF) LPAREN expressionList RPAREN;

castOperator: classicalType;

expressionList: expression (COMMA expression)*;

equalsExpression: EQUALS expression;
assignmentOperator : EQUALS | CompoundAssignmentOperator;

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

branchingStatement: IF LPAREN expression RPAREN programBlock (ELSE programBlock)?;

loopSignature
    : FOR Identifier IN setDeclaration
    | WHILE LPAREN expression RPAREN
    ;

loopStatement: loopSignature programBlock;
endStatement: END SEMICOLON;
returnStatement: RETURN (expression | quantumMeasurement)? SEMICOLON;

controlDirective
    : (BREAK| CONTINUE) SEMICOLON
    | endStatement
    | returnStatement
    ;

externDeclaration: EXTERN Identifier LPAREN classicalTypeList? RPAREN returnSignature? SEMICOLON;

// if have function call w/ out args, is ambiguous; may get matched as identifier
externOrSubroutineCall: Identifier LPAREN expressionList? RPAREN;

/*** Subroutines ***/
subroutineDefinition: DEF Identifier LPAREN anyTypeArgumentList? RPAREN returnSignature? subroutineBlock;
subroutineBlock: LBRACE statement* returnStatement? RBRACE;

/*** Directives ***/
pragma: PRAGMA LBRACE statement* RBRACE;

/*** Circuit Timing ***/
timingBox: BOX designator? quantumBlock;
timingIdentifier: TimingLiteral | DURATIONOF LPAREN (Identifier | quantumBlock) RPAREN;
timingInstruction: BuiltinTimingInstruction (LPAREN expressionList? RPAREN)?  designator indexedIdentifier (COMMA indexedIdentifier)*;
timingStatement: timingInstruction SEMICOLON | timingBox;

/*** Pulse Level Descriptions of Gates and Measurement ***/
// TODO: Update when pulse grammar is formalized
calibration: calibrationGrammarDeclaration | calibrationDefinition;
calibrationGrammarDeclaration: DEFCALGRAMMAR StringLiteral SEMICOLON;
// For now, the defcal parser just matches anything at all within the braces.
calibrationDefinition: DEFCAL Identifier (LPAREN calibrationArgumentList? RPAREN)? identifierList returnSignature? LBRACE .*? RBRACE;
calibrationArgumentList: classicalArgumentList | expressionList;
