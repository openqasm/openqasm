/**** ANTLRv4  grammar for OpenQASM3.0. ****/

grammar qasm3;

/** Parser grammar **/

program
    : header (globalStatement | statement)*
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

globalStatement
    : subroutineDefinition
    | kernelDeclaration
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
    | controlDirectiveStatement
    | aliasStatement
    | quantumStatement
    ;

quantumDeclarationStatement : quantumDeclaration SEMICOLON ;

classicalDeclarationStatement
    : ( classicalDeclaration | constantDeclaration ) SEMICOLON
    ;

classicalAssignment
    : indexIdentifier assignmentOperator ( expression | indexIdentifier )
    ;

assignmentStatement : ( classicalAssignment | quantumMeasurementAssignment ) SEMICOLON ;

returnSignature
    : ARROW classicalType
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
    : 'const' equalsAssignmentList
    ;

// if multiple variables declared at once, either none are assigned or all are assigned
// prevents ambiguity w/ qubit arguments in subroutine calls
singleDesignatorDeclaration
    : singleDesignatorType designator ( identifierList | equalsAssignmentList )
    ;

doubleDesignatorDeclaration
    : doubleDesignatorType doubleDesignator ( identifierList | equalsAssignmentList )
    ;

noDesignatorDeclaration
    : noDesignatorType ( identifierList | equalsAssignmentList )
    ;

bitDeclaration
    : bitType (indexIdentifierList | indexEqualsAssignmentList )
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
    : 'let' Identifier EQUALS indexIdentifier SEMICOLON
    ;

// Register Concatenation and Slicing

indexIdentifier
    : Identifier rangeDefinition
    | Identifier ( LBRACKET expressionList RBRACKET )?
    | indexIdentifier '||' indexIdentifier
    ;

indexIdentifierList
    : ( indexIdentifier COMMA )* indexIdentifier
    ;

indexEqualsAssignmentList
    : ( indexIdentifier equalsExpression COMMA)* indexIdentifier equalsExpression
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
    | quantumBarrier
    ;

quantumPhase
    : 'gphase' LPAREN Identifier RPAREN
    ;

quantumMeasurement
    : 'measure' indexIdentifierList
    ;

quantumMeasurementAssignment
    : quantumMeasurement ( ARROW indexIdentifierList)?
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
    ;

expression
    : expression binaryOperator expression
    | unaryOperator expression
    | expression incrementor
    | expression LBRACKET expression RBRACKET
    | LPAREN expression RPAREN
    | membershipTest
    | builtInCall
    | subroutineCall
    | kernelCall
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

builtInCall
    : ( builtInMath | castOperator ) LPAREN expressionList RPAREN
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
    : ( Identifier equalsExpression COMMA)* Identifier equalsExpression
    ;

membershipTest
    : Identifier 'in' setDeclaration
    ;

setDeclaration
    : LBRACE expressionList RBRACE
    | rangeDefinition
    | Identifier
    ;

programBlock
    : statement
    | LBRACE statement* RBRACE
    ;

branchingStatement
    : 'if' LPAREN expression RPAREN programBlock ( 'else' programBlock )?
    ;

loopSignature
    : 'for' membershipTest
    | 'while' LPAREN expression RPAREN
    ;

loopStatement: loopSignature programBlock ;

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

// if have kernel w/ out args, is ambiguous; may get matched as identifier
kernelCall
    : Identifier LPAREN expressionList? RPAREN
    ;

/* Subroutines */

subroutineDefinition
    : 'def' Identifier ( LPAREN classicalArgumentList? RPAREN )? quantumArgumentList?
    returnSignature? subroutineBlock
    ;

returnStatement : 'return' statement;

subroutineBlock
    : LBRACE statement* returnStatement? RBRACE
    ;

// if have subroutine w/ out args, is ambiguous; may get matched as identifier
subroutineCall
    : Identifier ( LPAREN expressionList? RPAREN )? expressionList
    ;

/* Directives */

pragma
    : '#pragma' LBRACE statement* RBRACE  // match any valid openqasm statement
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

Constant : MINUS? ( 'pi' | 'π' | 'tau' | '𝜏' | 'euler' | 'ℇ' );

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
RealNumber : Float (SciNotation PlusMinus? Integer )? ;

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
