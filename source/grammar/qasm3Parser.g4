parser grammar qasm3Parser;

options {
    tokenVocab = qasm3Lexer;
}

program: version? statement* EOF;
version: OPENQASM VersionSpecifier SEMICOLON;

// A statement is any valid single statement of an OpenQASM 3 program, with the
// exception of the version-definition statement (which must be unique, and the
// first statement of the file if present).  This file just defines rules for
// parsing; we leave semantic analysis and rejection of invalid scopes for
// compiler implementations.
statement:
    pragma
    // All the actual statements of the language.
    | annotation* (
        aliasDeclarationStatement
        | assignmentStatement
        | barrierStatement
        | boxStatement
        | breakStatement
        | calStatement
        | calibrationGrammarStatement
        | classicalDeclarationStatement
        | constDeclarationStatement
        | continueStatement
        | defStatement
        | defcalStatement
        | delayStatement
        | endStatement
        | expressionStatement
        | externStatement
        | forStatement
        | gateCallStatement
        | gateStatement
        | ifStatement
        | includeStatement
        | ioDeclarationStatement
        | measureArrowAssignmentStatement
        | oldStyleDeclarationStatement
        | quantumDeclarationStatement
        | resetStatement
        | returnStatement
        | whileStatement
    )
;
annotation: AnnotationKeyword RemainingLineContent?;
scope: LBRACE statement* RBRACE;
pragma: PRAGMA RemainingLineContent;

statementOrScope: statement | scope;


/* Start top-level statement definitions. */

// Inclusion statements.
calibrationGrammarStatement: DEFCALGRAMMAR StringLiteral SEMICOLON;
includeStatement: INCLUDE StringLiteral SEMICOLON;

// Control-flow statements.
breakStatement: BREAK SEMICOLON;
continueStatement: CONTINUE SEMICOLON;
endStatement: END SEMICOLON;
forStatement: FOR scalarType Identifier IN (setExpression | LBRACKET rangeExpression RBRACKET | expression) body=statementOrScope;
ifStatement: IF LPAREN expression RPAREN if_body=statementOrScope (ELSE else_body=statementOrScope)?;
returnStatement: RETURN (expression | measureExpression)? SEMICOLON;
whileStatement: WHILE LPAREN expression RPAREN body=statementOrScope;

// Quantum directive statements.
barrierStatement: BARRIER gateOperandList? SEMICOLON;
boxStatement: BOX designator? scope;
delayStatement: DELAY designator gateOperandList? SEMICOLON;
/* `gateCallStatement`  is split in two to avoid a potential ambiguity with an
 * `expressionStatement` that consists of a single function call.  The only
 * "gate" that can have no operands is `gphase` with no control modifiers, and
 * `gphase(pi);` looks grammatically identical to `fn(pi);`.  We disambiguate by
 * having `gphase` be its own token, and requiring that all other gate calls
 * grammatically have at least one qubit.  Strictly, as long as `gphase` is a
 * separate token, ANTLR can disambiguate the statements by the definition
 * order, but this is more robust. */
gateCallStatement:
    gateModifier* Identifier (LPAREN expressionList? RPAREN)? designator? gateOperandList SEMICOLON
    | gateModifier* GPHASE (LPAREN expressionList? RPAREN)? designator? gateOperandList? SEMICOLON
;
// measureArrowAssignmentStatement also permits the case of not assigning the
// result to any classical value too.
measureArrowAssignmentStatement: measureExpression (ARROW indexedIdentifier)? SEMICOLON;
resetStatement: RESET gateOperand SEMICOLON;

// Primitive declaration statements.
aliasDeclarationStatement: LET Identifier EQUALS aliasExpression SEMICOLON;
classicalDeclarationStatement: (scalarType | arrayType) Identifier (EQUALS declarationExpression)? SEMICOLON;
constDeclarationStatement: CONST scalarType Identifier EQUALS declarationExpression SEMICOLON;
ioDeclarationStatement: (INPUT | OUTPUT) (scalarType | arrayType) Identifier SEMICOLON;
oldStyleDeclarationStatement: (CREG | QREG) Identifier designator? SEMICOLON;
quantumDeclarationStatement: qubitType Identifier SEMICOLON;

// Declarations and definitions of higher-order objects.
defStatement: DEF Identifier LPAREN argumentDefinitionList? RPAREN returnSignature? scope;
externStatement: EXTERN Identifier LPAREN externArgumentList? RPAREN returnSignature? SEMICOLON;
gateStatement: GATE Identifier (LPAREN params=identifierList? RPAREN)? qubits=identifierList scope;

// Non-declaration assignments and calculations.
assignmentStatement: indexedIdentifier op=(EQUALS | CompoundAssignmentOperator) (expression | measureExpression) SEMICOLON;
expressionStatement: expression SEMICOLON;

// Statements where the bulk is in the calibration language.
calStatement: CAL LBRACE CalibrationBlock? RBRACE;
defcalStatement: DEFCAL defcalTarget (LPAREN defcalArgumentDefinitionList? RPAREN)? defcalOperandList returnSignature? LBRACE CalibrationBlock? RBRACE;


/* End top-level statement definitions. */
/* Start expression definitions. */


// ANTLR4 can handle direct left-recursive rules, and ambiguities are guaranteed
// to resolve in the order of definition.  This means that the order of rules
// here defines the precedence table, from most tightly binding to least.
expression:
    LPAREN expression RPAREN                                  # parenthesisExpression
    | expression indexOperator                                # indexExpression
    | <assoc=right> expression op=DOUBLE_ASTERISK expression  # powerExpression
    | op=(TILDE | EXCLAMATION_POINT | MINUS) expression       # unaryExpression
    | expression op=(ASTERISK | SLASH | PERCENT) expression   # multiplicativeExpression
    | expression op=(PLUS | MINUS) expression                 # additiveExpression
    | expression op=BitshiftOperator expression               # bitshiftExpression
    | expression op=ComparisonOperator expression             # comparisonExpression
    | expression op=EqualityOperator expression               # equalityExpression
    | expression op=AMPERSAND expression                      # bitwiseAndExpression
    | expression op=CARET expression                          # bitwiseXorExpression
    | expression op=PIPE expression                           # bitwiseOrExpression
    | expression op=DOUBLE_AMPERSAND expression               # logicalAndExpression
    | expression op=DOUBLE_PIPE expression                    # logicalOrExpression
    | (scalarType | arrayType) LPAREN expression RPAREN       # castExpression
    | DURATIONOF LPAREN scope RPAREN                          # durationofExpression
    | Identifier LPAREN expressionList? RPAREN                # callExpression
    | (
        Identifier
        | BinaryIntegerLiteral
        | OctalIntegerLiteral
        | DecimalIntegerLiteral
        | HexIntegerLiteral
        | FloatLiteral
        | ImaginaryLiteral
        | BooleanLiteral
        | BitstringLiteral
        | TimingLiteral
        | HardwareQubit
      )                                                       # literalExpression
;

// Special-case expressions that are only valid in certain contexts.  These are
// not in the expression tree, but can contain elements that are within it.
aliasExpression: expression (DOUBLE_PLUS expression)*;
declarationExpression: arrayLiteral | expression | measureExpression;
measureExpression: MEASURE gateOperand;
rangeExpression: expression? COLON expression? (COLON expression)?;
setExpression: LBRACE expression (COMMA expression)* COMMA? RBRACE;
arrayLiteral: LBRACE (expression | arrayLiteral) (COMMA (expression | arrayLiteral))* COMMA? RBRACE;

// The general form is a comma-separated list of indexing entities.
// `setExpression` is only valid when being used as a single index: registers
// can support it for creating aliases, but arrays cannot.
indexOperator:
    LBRACKET
    (
        setExpression
        | (expression | rangeExpression) (COMMA (expression | rangeExpression))* COMMA?
    )
    RBRACKET;
// Alternative form to `indexExpression` for cases where an obvious l-value is
// better grammatically than a generic expression.  Some current uses of this
// rule may be better as `expression`, leaving the semantic analysis to later
// (for example in gate calls).
indexedIdentifier: Identifier indexOperator*;

/* End expression definitions. */
/* Start type definitions. */

returnSignature: ARROW scalarType;
gateModifier: (
    INV
    | POW LPAREN expression RPAREN
    | (CTRL | NEGCTRL) (LPAREN expression RPAREN)?
) AT;

scalarType:
    BIT designator?
    | INT designator?
    | UINT designator?
    | FLOAT designator?
    | ANGLE designator?
    | BOOL
    | DURATION
    | STRETCH
    | COMPLEX (LBRACKET scalarType RBRACKET)?
;
qubitType: QUBIT designator?;
arrayType: ARRAY LBRACKET scalarType COMMA expressionList RBRACKET;
arrayReferenceType: (READONLY | MUTABLE) ARRAY LBRACKET scalarType COMMA (expressionList | DIM EQUALS expression) RBRACKET;

designator: LBRACKET expression RBRACKET;

defcalTarget: MEASURE | RESET | DELAY | Identifier;
defcalArgumentDefinition: expression | argumentDefinition;
defcalOperand: HardwareQubit | Identifier;
gateOperand: indexedIdentifier | HardwareQubit;
externArgument: scalarType | arrayReferenceType | CREG designator?;
argumentDefinition:
    scalarType Identifier
    | qubitType Identifier
    | (CREG | QREG) Identifier designator?
    | arrayReferenceType Identifier
;

argumentDefinitionList: argumentDefinition (COMMA argumentDefinition)* COMMA?;
defcalArgumentDefinitionList: defcalArgumentDefinition (COMMA defcalArgumentDefinition)* COMMA?;
defcalOperandList: defcalOperand (COMMA defcalOperand)* COMMA?;
expressionList: expression (COMMA expression)* COMMA?;
identifierList: Identifier (COMMA Identifier)* COMMA?;
gateOperandList: gateOperand (COMMA gateOperand)* COMMA?;
externArgumentList: externArgument (COMMA externArgument)* COMMA?;
