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
INCLUDE: 'include';
DEFCALGRAMMAR: 'defcalgrammar';
DEF: 'def';
DEFCAL: 'defcal';
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

PRAGMA: '#pragma';


/* Types. */

INPUT: 'input';
OUTPUT: 'output';
CONST: 'const';
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
ImaginaryLiteral: (DecimalIntegerLiteral | FloatLiteral) IMAG;

BinaryIntegerLiteral: ('0b' | '0B') ([01] '_'?)* [01];
OctalIntegerLiteral: '0o' ([0-7] '_'?)* [0-7];
DecimalIntegerLiteral: ([0-9] '_'?)* [0-9];
HexIntegerLiteral: ('0x' | '0X') ([0-9a-fA-F] '_'?)* [0-9a-fA-F];

fragment ValidUnicode: [\p{Lu}\p{Ll}\p{Lt}\p{Lm}\p{Lo}\p{Nl}]; // valid unicode chars
fragment Letter: [A-Za-z];
fragment FirstIdCharacter: '_' | ValidUnicode | Letter;
fragment GeneralIdCharacter: FirstIdCharacter | [0-9];

Identifier: FirstIdCharacter GeneralIdCharacter*;
// TODO: OpenPulse asks for identifiers like '$q' in the argument list of
// 'defcal' statements, though this is not a valid identifier by the OpenQASM 3
// specification.  For now, we allow it as a special case.
HardwareQubit: '$' ([0-9]+ | Identifier);

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
// allow ``"str"`` and ``'str'``
StringLiteral
    : '"' ~["\r\t\n]+? '"'
    | '\'' ~['\r\t\n]+? '\''
    ;

// Ignore whitespace between tokens, and define C++-style comments.
Whitespace: [ \t]+ -> skip ;
Newline: [\r\n]+ -> skip ;
LineComment : '//' ~[\r\n]* -> skip;
BlockComment : '/*' .*? '*/' -> skip;


// The version identifier token would be ambiguous between itself and
// integer/floating-point literals (if there's no patch version), so we use a
// special mode to ensure it's lexed correctly.
mode VERSION_IDENTIFIER;
    VERSION_IDENTIFER_WHITESPACE: [ \t\r\n]+ -> skip;
    VersionSpecifier: [0-9]+ ('.' [0-9]+ ('.' [0-9]+)?)? -> popMode;
