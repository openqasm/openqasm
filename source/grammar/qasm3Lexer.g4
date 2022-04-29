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

OPENQASM: 'OPENQASM';
INCLUDE: 'include';
PRAGMA: '#pragma';
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

U_: 'U';
CX: 'CX';

GPHASE: 'gphase';
INV: 'inv';
POW: 'pow';
CTRL: 'ctrl';
NEGCTRL: 'negctrl';

DIM: '#dim';
SIZEOF: 'sizeof';

BuiltinMath
    : 'arccos'
    | 'arcsin'
    | 'arctan'
    | 'cos'
    | 'exp'
    | 'ln'
    | 'popcount'
    | 'rotl'
    | 'rotr'
    | 'sin'
    | 'sqrt'
    | 'tan'
    ;
DURATIONOF: 'durationof';
BuiltinTimingInstruction: 'delay' | 'rotary';

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

/* There is no lexer rule for 'UnaryOperator' (~, ! or -) because the MINUS
 * lexeme is context-dependent as to whether it is unary or binary.
 */
EqualityOperator: '==' | '!=';
CompoundAssignmentOperator: '+=' | '-=' | '*=' | '/=' | '&=' | '|=' | '~=' | '^=' | '<<=' | '>>=' | '%=' | '**=';
ComparisonOperator: '>' | '<' | '>=' | '<=';
BitshiftOperator: '>>' | '<<';

IMAG: 'im';
ImagNumber : ( Integer | RealNumber ) IMAG ;

Constant: ('pi' | 'π' | 'tau' | '𝜏' | 'euler' | 'ℇ');

fragment Digit : [0-9] ;
Integer : Digit+ ;

fragment ValidUnicode: [\p{Lu}\p{Ll}\p{Lt}\p{Lm}\p{Lo}\p{Nl}] ; // valid unicode chars
fragment Letter: [A-Za-z] ;
fragment FirstIdCharacter : '_' | '$' | ValidUnicode | Letter ;
fragment GeneralIdCharacter : FirstIdCharacter | Digit;

Identifier: FirstIdCharacter GeneralIdCharacter*;

fragment SciNotation: [eE];
fragment PlusMinus: PLUS | MINUS;
fragment Float: Digit+ DOT Digit*;
RealNumber: (Integer | Float) (SciNotation PlusMinus? Integer)?;

fragment TimeUnit: 'dt' | 'ns' | 'us' | 'µs' | 'ms' | 's';
// represents explicit time value in SI or backend units
TimingLiteral : (Integer | RealNumber) TimeUnit;


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
