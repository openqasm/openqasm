grammar qasm3;

program
    : header include* statement+ EOF
    ;

header
    : 'OPENQASM' Number (Dot Number)? SemiColon
    ;

include
    : 'include' StringLiteral SemiColon
    ;

statement
    : variableDeclarationStatement SemiColon
    | gateDefinition
    ;

variableDeclarationStatement
    : type variableDeclarationList
    ;

type
    : varType (OpenBracket Number (Comma Number)? CloseBracket)?
    ;

variableDeclarationList
    : variableDeclaration (Comma variableDeclaration)*
    ;

variableDeclaration
    : Identifier (OpenBracket Number CloseBracket)? (Assign value)?
    ;

gateDefinition
    : Gate Identifier (paramsList)? qargsList '{' expression+ '}'
    ;

paramsList
    : paramDeclaration (Comma paramDeclaration)*
    ;

// Why does it only accept angle parameters?
// Why are variables declared like angle[32] foo and params angle[32]:foo?
paramDeclaration
    : type OpenBracket Number CloseBracket Colon Identifier
    ;

qargsList
    : qargDeclaration (Comma qargDeclaration)*
    ;

qargDeclaration
    : Identifier (Comma Identifier)*
    ;

expression
    : // TODO
    ;

value
    : Number
    | StringLiteral
    ;

// Lexer variables needs some refactor
varType
    : 'qubit' | 'qreg' | 'bit' | 'creg' | 'bool' | 'const' | 'int' | 'uint' | 'angle' | 'fixed'
    ;

Gate
    : 'gate'
    ;

Assign : '=';

StringLiteral
    : '"' Identifier '"'
    ;

OpenBracket : '[';

CloseBracket : ']';

Colon: ':';

SemiColon : ';';

Dot : '.';

Comma : ',';

Identifier
    : ('a' .. 'z' | 'A' .. 'Z') ('a' .. 'z' | 'A' .. 'Z' | '0' .. '9' | '_')*
    ;

Number : [0-9]+;