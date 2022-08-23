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
calStatement: CAL LBRACE statement* RBRACE;
defcalStatement: DEFCAL defcalTarget (LPAREN defcalArgumentDefinitionList? RPAREN)? defcalOperandList returnSignature? LBRACE statement* RBRACE;

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
