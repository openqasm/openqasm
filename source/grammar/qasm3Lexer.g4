lexer grammar qasm3Lexer;

/* Naming conventions in this lexer grammar
 *
 * - Keywords and exact symbols that have only one possible value are written in
 *   all caps.  There is no more information in the parsed text than in the name
 *   of the lexeme.  For example, `INCLUDE` is only ever the string `'include'`.
 *
 * - Lexemes with information in the string form are in PascalCase.  This
 *   indicates there is more information in the token than just the name.  For
 *   example, `Identifier` has a payload containing the name of the identifier.
 */

/* Language keywords. */

OPENQASM: 'OPENQASM' -> pushMode(VERSION_IDENTIFIER);
INCLUDE: 'include' -> pushMode(ARBITRARY_STRING);
DEFCALGRAMMAR: 'defcalgrammar' -> pushMode(ARBITRARY_STRING);
DEF: 'def';
CAL: 'cal' -> mode(CAL_PRELUDE);
DEFCAL: 'defcal' -> mode(DEFCAL_PRELUDE);
GATE: 'gate';
EXTERN: 'extern';
BOX: 'box';
LET: 'let';

BREAK: 'break';
CONTINUE: 'continue';
IF: 'if';
ELSE: 'else';
END: 'end';
RETURN: 'return';
FOR: 'for';
WHILE: 'while';
IN: 'in';

PRAGMA: '#'? 'pragma' -> pushMode(EAT_TO_LINE_END);
AnnotationKeyword: '@' Identifier ->  pushMode(EAT_TO_LINE_END);


/* Types. */

INPUT: 'input';
OUTPUT: 'output';
CONST: 'const';
READONLY: 'readonly';
MUTABLE: 'mutable';

QREG: 'qreg';
QUBIT: 'qubit';

CREG: 'creg';
BOOL: 'bool';
BIT: 'bit';
INT: 'int';
UINT: 'uint';
FLOAT: 'float';
ANGLE: 'angle';
COMPLEX: 'complex';
ARRAY: 'array';
VOID: 'void';

DURATION:  'duration';
STRETCH: 'stretch';


/* Builtin identifiers and operations */

GPHASE: 'gphase';
INV: 'inv';
POW: 'pow';
CTRL: 'ctrl';
NEGCTRL: 'negctrl';

DIM: '#dim';

DURATIONOF: 'durationof';

DELAY: 'delay';
RESET: 'reset';
MEASURE: 'measure';
BARRIER: 'barrier';

BooleanLiteral: 'true' | 'false';


/* Symbols */

LBRACKET: '[';
RBRACKET: ']';
LBRACE: '{';
RBRACE: '}';
LPAREN: '(';
RPAREN: ')';

COLON: ':';
SEMICOLON: ';';

DOT: '.';
COMMA: ',';

EQUALS: '=';
ARROW: '->';
PLUS: '+';
DOUBLE_PLUS: '++';
MINUS: '-';
ASTERISK: '*';
DOUBLE_ASTERISK: '**';
SLASH: '/';
PERCENT: '%';
PIPE: '|';
DOUBLE_PIPE: '||';
AMPERSAND: '&';
DOUBLE_AMPERSAND: '&&';
CARET: '^';
AT: '@';
TILDE: '~';
EXCLAMATION_POINT: '!';

EqualityOperator: '==' | '!=';
CompoundAssignmentOperator: '+=' | '-=' | '*=' | '/=' | '&=' | '|=' | '~=' | '^=' | '<<=' | '>>=' | '%=' | '**=';
ComparisonOperator: '>' | '<' | '>=' | '<=';
BitshiftOperator: '>>' | '<<';

IMAG: 'im';
ImaginaryLiteral: (DecimalIntegerLiteral | FloatLiteral) ' '* IMAG;

BinaryIntegerLiteral: ('0b' | '0B') ([01] '_'?)* [01];
OctalIntegerLiteral: '0o' ([0-7] '_'?)* [0-7];
DecimalIntegerLiteral: ([0-9] '_'?)* [0-9];
HexIntegerLiteral: ('0x' | '0X') ([0-9a-fA-F] '_'?)* [0-9a-fA-F];

fragment ValidUnicode: [\p{Lu}\p{Ll}\p{Lt}\p{Lm}\p{Lo}\p{Nl}]; // valid unicode chars
fragment Letter: [A-Za-z];
fragment FirstIdCharacter: '_' | ValidUnicode | Letter;
fragment GeneralIdCharacter: FirstIdCharacter | [0-9];

Identifier: FirstIdCharacter GeneralIdCharacter*;
HardwareQubit: '$' [0-9]+;

fragment FloatLiteralExponent: [eE] (PLUS | MINUS)? DecimalIntegerLiteral;
FloatLiteral:
    // 1_123e-3, 123e+4 or 123E5 (needs the exponent or it's just an integer)
    DecimalIntegerLiteral FloatLiteralExponent
    // .1234_5678 or .1e3 (no digits before the dot)
    | DOT DecimalIntegerLiteral FloatLiteralExponent?
    // 123.456, 123. or 145.32e+1_00
    | DecimalIntegerLiteral DOT DecimalIntegerLiteral? FloatLiteralExponent?;

fragment TimeUnit: 'dt' | 'ns' | 'us' | 'µs' | 'ms' | 's';
// represents explicit time value in SI or backend units
TimingLiteral: (DecimalIntegerLiteral | FloatLiteral) TimeUnit;

BitstringLiteral: '"' ([01] '_'?)* [01] '"';

// Ignore whitespace between tokens, and define C++-style comments.
Whitespace: [ \t]+ -> skip ;
Newline: [\r\n]+ -> skip ;
LineComment : '//' ~[\r\n]* -> skip;
BlockComment : '/*' .*? '*/' -> skip;


// The version identifier token would be ambiguous between itself and
// integer/floating-point literals, so we use a special mode to ensure it's
// lexed correctly.
mode VERSION_IDENTIFIER;
    VERSION_IDENTIFER_WHITESPACE: [ \t\r\n]+ -> skip;
    VersionSpecifier: [0-9]+ ('.' [0-9]+)? -> popMode;

// An include statement's path or defcalgrammar target is potentially ambiguous
// with `BitstringLiteral`.
mode ARBITRARY_STRING;
    ARBITRARY_STRING_WHITESPACE: [ \t\r\n]+ -> skip;
    // allow ``"str"`` and ``'str'``;
    StringLiteral: ('"' ~["\r\t\n]+? '"' | '\'' ~['\r\t\n]+? '\'') -> popMode;


// A different lexer mode to swap to when we need handle tokens on a line basis
// rather than the default arbitrary-whitespace-based tokenisation.  This is
// used by the annotation and pragma rules.
mode EAT_TO_LINE_END;
    EAT_INITIAL_SPACE: [ \t]+ -> skip;
    EAT_LINE_END: [\r\n] -> popMode, skip;

    // The line content must be a non-empty token to satisfy ANTLR (otherwise it
    // would be able to produce an infinite number of tokens).  We could include
    // the line ending to guarantee that this is always non-empty, but that just
    // puts an annoying burden on consumers to remove it again.
    RemainingLineContent: ~[ \t\r\n] ~[\r\n]*;


// We need to do a little context-aware lexing when we hit a `cal` or `defcal`
// token.  In both cases, there's a small interlude before the pulse grammar
// block starts, and we need to be able to lex our way through that.  We don't
// want to tie this grammar to one host language by injecting host code to
// manage the state of the lexer, so instead we need to do a little duplication
// of the tokens, because ANTLR doesn't allow us to inherit rules directly.
mode CAL_PRELUDE;
    CAL_PRELUDE_WHITESPACE: [ \t\r\n]+ -> skip;
    CAL_PRELUDE_COMMENT: (LineComment | BlockComment) -> skip;
    CAL_PRELUDE_LBRACE: LBRACE -> type(LBRACE), mode(CAL_BLOCK);

mode DEFCAL_PRELUDE;
    DEFCAL_PRELUDE_WHITESPACE: [ \t\r\n]+ -> skip;
    DEFCAL_PRELUDE_COMMENT: (LineComment | BlockComment) -> skip;
    DEFCAL_PRELUDE_LBRACE: LBRACE -> type(LBRACE), mode(CAL_BLOCK);

    // Duplications of valid constant expression tokens that may appear in the
    // argument list.  This is an unfortunately large number of duplications.

    // Types.
    DEFCAL_PRELUDE_QREG: QREG -> type(QREG);
    DEFCAL_PRELUDE_QUBIT: QUBIT -> type(QUBIT);
    DEFCAL_PRELUDE_CREG: CREG -> type(CREG);
    DEFCAL_PRELUDE_BOOL: BOOL -> type(BOOL);
    DEFCAL_PRELUDE_BIT: BIT -> type(BIT);
    DEFCAL_PRELUDE_INT: INT -> type(INT);
    DEFCAL_PRELUDE_UINT: UINT -> type(UINT);
    DEFCAL_PRELUDE_ANGLE: ANGLE -> type(ANGLE);
    DEFCAL_PRELUDE_FLOAT: FLOAT -> type(FLOAT);
    DEFCAL_PRELUDE_COMPLEX: COMPLEX -> type(COMPLEX);
    DEFCAL_PRELUDE_ARRAY: ARRAY -> type(ARRAY);
    DEFCAL_PRELUDE_DURATION: DURATION -> type(DURATION);
    // Punctuation.
    DEFCAL_PRELUDE_LBRACKET: LBRACKET -> type(LBRACKET);
    DEFCAL_PRELUDE_RBRACKET: RBRACKET -> type(RBRACKET);
    DEFCAL_PRELUDE_LPAREN: LPAREN -> type(LPAREN);
    DEFCAL_PRELUDE_RPAREN: RPAREN -> type(RPAREN);
    DEFCAL_PRELUDE_ARROW: ARROW -> type(ARROW);
    DEFCAL_PRELUDE_COMMA: COMMA -> type(COMMA);
    DEFCAL_PRELUDE_PLUS: PLUS -> type(PLUS);
    DEFCAL_PRELUDE_MINUS: MINUS -> type(MINUS);
    DEFCAL_PRELUDE_ASTERISK: ASTERISK -> type(ASTERISK);
    DEFCAL_PRELUDE_SLASH: SLASH -> type(SLASH);
    DEFCAL_PRELUDE_BitshiftOperator: BitshiftOperator -> type(BitshiftOperator);
    // Literals and names.
    DEFCAL_PRELUDE_BitstringLiteral: BitstringLiteral -> type(BitstringLiteral);
    DEFCAL_PRELUDE_BinaryIntegerLiteral: BinaryIntegerLiteral -> type(BinaryIntegerLiteral);
    DEFCAL_PRELUDE_OctalIntegerLiteral: OctalIntegerLiteral -> type(OctalIntegerLiteral);
    DEFCAL_PRELUDE_DecimalIntegerLiteral: DecimalIntegerLiteral -> type(DecimalIntegerLiteral);
    DEFCAL_PRELUDE_HexIntegerLiteral: HexIntegerLiteral -> type(HexIntegerLiteral);
    DEFCAL_PRELUDE_FloatLiteral: FloatLiteral -> type(FloatLiteral);
    DEFCAL_PRELUDE_MEASURE: MEASURE -> type(MEASURE);
    DEFCAL_PRELUDE_DELAY: DELAY -> type(DELAY);
    DEFCAL_PRELUDE_RESET: RESET -> type(RESET);
    DEFCAL_PRELUDE_Identifier: Identifier -> type(Identifier);
    DEFCAL_PRELUDE_HardwareQubit: HardwareQubit -> type(HardwareQubit);


// The meat-and-potatoes of matching a calibration block with balanced inner
// braces.  We enter `CAL_BLOCK` with the opening brace already tokenised
// (that's how the lexer knew to swap modes to us), and with the token left open
// to continue to accumulate.  We want to tokenise until we hit the balancing
// brace.  Since we have _no_ knowledge of what the inner langauge is doing,
// things like unbalanced braces in comments will cause a failure, but there's
// not much we can do about that without greater spec restrictions.
mode CAL_BLOCK;
    fragment NestedCalibrationBlock: LBRACE (NestedCalibrationBlock | ~[{}])* RBRACE;
    CalibrationBlock: (NestedCalibrationBlock | ~[{}])+;
    CAL_BLOCK_RBRACE: RBRACE -> type(RBRACE), mode(DEFAULT_MODE);
