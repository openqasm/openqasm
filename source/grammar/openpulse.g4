/***** ANTLRv4  grammar for OpenPulse. *****/
// This grammar is OpenPulse extension for QOpenQASM3.0
// We introduce several new types for OpenPulse.
// We override several nodes in qasm3 to consume the new types.
// The OpenPulse grammar can be used inside cal or defcal blocks.

grammar openpulse;
import qasm3;

/**** OpenQASM3.0 overrides ****/

// calBlock is the new addition
calibration
    : calibrationGrammarDeclaration
    | calibrationDefinition
    | calBlock
    ;

// defcal body uses openpulse grammar
calibrationDefinition
    : 'defcal' Identifier
    ( LPAREN calibrationArgumentList? RPAREN )? identifierList
    returnSignature? LBRACE calStatement* returnStatement? RBRACE
;

// cal block is not yet defined in OpenQASM3.0. 
// If it is defined in the future, this will be an override
calBlock
    : 'cal' LBRACE calStatement* RBRACE
    ;

/**** OpenPulse types ****/
// These types can only used inside cal and defcal blocks
pulseType
    : 'waveform'
    | 'port'
    | 'frame'
    ;

pulseDeclaration
    : pulseType Identifier equalsExpression? SEMICOLON
    ;

// A collection of existing OpenQASM3.0 statements that can be used in OpenPulse
// as well as the new OpenPulse statements.
calStatement
    : quantumStatement 
    | quantumLoop
    | pulseDeclaration
    | statement
    | calExternDeclaration
    ;

// calType extend the classicalType with pulseType
calType
    : classicalType
    | pulseType
    ;

calTypeList
    : ( calType COMMA )* calType
    ;

// calExternDeclaration extends the extern declation in OpenPulse
calExternDeclaration
    : 'extern' Identifier LPAREN calTypeList? RPAREN (ARROW calType)? SEMICOLON
    ;
