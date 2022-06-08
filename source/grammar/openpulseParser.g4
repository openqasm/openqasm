/***** ANTLRv4  grammar for OpenPulse. *****/
// This grammar is OpenPulse extension for QOpenQASM3.0
// We introduce several new types for OpenPulse.
// We override several nodes in qasm3 to consume the new types.
// The OpenPulse grammar can be used inside cal or defcal blocks.

parser grammar openpulseParser;
import qasm3Parser;

options {
    tokenVocab = openpulseLexer;
}

/**** OpenQASM3.0 overrides ****/
defcalStatement: DEFCAL Identifier (LPAREN argumentDefinitionList? RPAREN)? hardwareQubitList returnSignature? LBRACE statement* RBRACE;

// cal statement is not yet defined in OpenQASM3.0. 
// If it is defined in the future, this will be an override
calStatement: CAL LBRACE statement* RBRACE;

/** In the following we extend existing OpenQASM nodes. Need to refresh whenever OpenQASM is updated. **/
// We extend the scalarType with WAVEFORM, PORT and FRAME
scalarType:
    BIT designator?
    | INT designator?
    | UINT designator?
    | FLOAT designator?
    | ANGLE designator?
    | BOOL
    | DURATION
    | STRETCH
    | COMPLEX LBRACKET scalarType RBRACKET
    | WAVEFORM
    | PORT
    | FRAME
    ;

// we extend the statement with the calStatement
statement:
    pragma
    // All the actual statements of the language.
    | aliasDeclarationStatement
    | assignmentStatement
    | barrierStatement
    | boxStatement
    | breakStatement
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
    | calStatement
;
