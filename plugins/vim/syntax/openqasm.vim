" Syntax highlighting for OpenQASM files.  This version of the syntax
" highlighter is written for OpenQASM 3.0, but should work fine in principle for
" previous versions (with some extraneous highlighting).
"
" Language:     OpenQASM
" Author:       Jake Lishman <jake.lishman@ibm.com>
" Version:      0.1

if exists("b:current_syntax")
    finish
endif
let b:current_syntax = "openqasm"

let s:openqasm_version = openqasm#get_version()

" Spelling only occurs in comments.
syntax spell default

if s:openqasm_version < 3
    " Simple ASCII letters, numbers and underscore.
    syntax iskeyword a-z,A-Z,48-57,_
else
    " Unicode classes Ll, Lm, Lo, Lt, Lu, Nl, digits (48-57), underscore (95), and
    " dollar (36).  Vim doesn't have a nice way of matching these classes (at least
    " as of Vim 8.2), so we just have to be explicit.
    syntax iskeyword
        \36,48-57,65-90,95,97-122,170,181,186,192-214,216-246,248-705,710-721,736-740,748,750
        \,880-884,886-887,890-893,895,902,904-906,908,910-929,931-1013,1015-1153,1162-1327
        \,1329-1366,1369,1376-1416,1488-1514,1519-1522,1568-1610,1646-1647,1649-1747,1749
        \,1765-1766,1774-1775,1786-1788,1791,1808,1810-1839,1869-1957,1969,1994-2026,2036-2037
        \,2042,2048-2069,2074,2084,2088,2112-2136,2144-2154,2208-2228,2230-2247,2308-2361,2365
        \,2384,2392-2401,2417-2432,2437-2444,2447-2448,2451-2472,2474-2480,2482,2486-2489,2493
        \,2510,2524-2525,2527-2529,2544-2545,2556,2565-2570,2575-2576,2579-2600,2602-2608
        \,2610-2611,2613-2614,2616-2617,2649-2652,2654,2674-2676,2693-2701,2703-2705,2707-2728
        \,2730-2736,2738-2739,2741-2745,2749,2768,2784-2785,2809,2821-2828,2831-2832,2835-2856
        \,2858-2864,2866-2867,2869-2873,2877,2908-2909,2911-2913,2929,2947,2949-2954,2958-2960
        \,2962-2965,2969-2970,2972,2974-2975,2979-2980,2984-2986,2990-3001,3024,3077-3084
        \,3086-3088,3090-3112,3114-3129,3133,3160-3162,3168-3169,3200,3205-3212,3214-3216
        \,3218-3240,3242-3251,3253-3257,3261,3294,3296-3297,3313-3314,3332-3340,3342-3344
        \,3346-3386,3389,3406,3412-3414,3423-3425,3450-3455,3461-3478,3482-3505,3507-3515,3517
        \,3520-3526,3585-3632,3634-3635,3648-3654,3713-3714,3716,3718-3722,3724-3747,3749
        \,3751-3760,3762-3763,3773,3776-3780,3782,3804-3807,3840,3904-3911,3913-3948,3976-3980
        \,4096-4138,4159,4176-4181,4186-4189,4193,4197-4198,4206-4208,4213-4225,4238,4256-4293
        \,4295,4301,4304-4346,4348-4680,4682-4685,4688-4694,4696,4698-4701,4704-4744,4746-4749
        \,4752-4784,4786-4789,4792-4798,4800,4802-4805,4808-4822,4824-4880,4882-4885,4888-4954
        \,4992-5007,5024-5109,5112-5117,5121-5740,5743-5759,5761-5786,5792-5866,5870-5880
        \,5888-5900,5902-5905,5920-5937,5952-5969,5984-5996,5998-6000,6016-6067,6103,6108
        \,6176-6264,6272-6276,6279-6312,6314,6320-6389,6400-6430,6480-6509,6512-6516,6528-6571
        \,6576-6601,6656-6678,6688-6740,6823,6917-6963,6981-6987,7043-7072,7086-7087,7098-7141
        \,7168-7203,7245-7247,7258-7293,7296-7304,7312-7354,7357-7359,7401-7404,7406-7411
        \,7413-7414,7418,7424-7615,7680-7957,7960-7965,7968-8005,8008-8013,8016-8023,8025,8027
        \,8029,8031-8061,8064-8116,8118-8124,8126,8130-8132,8134-8140,8144-8147,8150-8155
        \,8160-8172,8178-8180,8182-8188,8305,8319,8336-8348,8450,8455,8458-8467,8469,8473-8477
        \,8484,8486,8488,8490-8493,8495-8505,8508-8511,8517-8521,8526,8544-8584,11264-11310
        \,11312-11358,11360-11492,11499-11502,11506-11507,11520-11557,11559,11565,11568-11623
        \,11631,11648-11670,11680-11686,11688-11694,11696-11702,11704-11710,11712-11718
        \,11720-11726,11728-11734,11736-11742,11823,12293-12295,12321-12329,12337-12341
        \,12344-12348,12353-12438,12445-12447,12449-12538,12540-12543,12549-12591,12593-12686
        \,12704-12735,12784-12799,13312,19903,19968,40956,40960-42124,42192-42237,42240-42508
        \,42512-42527,42538-42539,42560-42606,42623-42653,42656-42735,42775-42783,42786-42888
        \,42891-42943,42946-42954,42997-43009,43011-43013,43015-43018,43020-43042,43072-43123
        \,43138-43187,43250-43255,43259,43261-43262,43274-43301,43312-43334,43360-43388
        \,43396-43442,43471,43488-43492,43494-43503,43514-43518,43520-43560,43584-43586
        \,43588-43595,43616-43638,43642,43646-43695,43697,43701-43702,43705-43709,43712,43714
        \,43739-43741,43744-43754,43762-43764,43777-43782,43785-43790,43793-43798,43808-43814
        \,43816-43822,43824-43866,43868-43881,43888-44002,44032,55203,55216-55238,55243-55291
        \,63744-64109,64112-64217,64256-64262,64275-64279,64285,64287-64296,64298-64310
        \,64312-64316,64318,64320-64321,64323-64324,64326-64433,64467-64829,64848-64911
        \,64914-64967,65008-65019,65136-65140,65142-65276,65313-65338,65345-65370,65382-65470
        \,65474-65479,65482-65487,65490-65495,65498-65500,65536-65547,65549-65574,65576-65594
        \,65596-65597,65599-65613,65616-65629,65664-65786,65856-65908,66176-66204,66208-66256
        \,66304-66335,66349-66378,66384-66421,66432-66461,66464-66499,66504-66511,66513-66517
        \,66560-66717,66736-66771,66776-66811,66816-66855,66864-66915,67072-67382,67392-67413
        \,67424-67431,67584-67589,67592,67594-67637,67639-67640,67644,67647-67669,67680-67702
        \,67712-67742,67808-67826,67828-67829,67840-67861,67872-67897,67968-68023,68030-68031
        \,68096,68112-68115,68117-68119,68121-68149,68192-68220,68224-68252,68288-68295
        \,68297-68324,68352-68405,68416-68437,68448-68466,68480-68497,68608-68680,68736-68786
        \,68800-68850,68864-68899,69248-69289,69296-69297,69376-69404,69415,69424-69445
        \,69552-69572,69600-69622,69635-69687,69763-69807,69840-69864,69891-69926,69956,69959
        \,69968-70002,70006,70019-70066,70081-70084,70106,70108,70144-70161,70163-70187
        \,70272-70278,70280,70282-70285,70287-70301,70303-70312,70320-70366,70405-70412
        \,70415-70416,70419-70440,70442-70448,70450-70451,70453-70457,70461,70480,70493-70497
        \,70656-70708,70727-70730,70751-70753,70784-70831,70852-70853,70855,71040-71086
        \,71128-71131,71168-71215,71236,71296-71338,71352,71424-71450,71680-71723,71840-71903
        \,71935-71942,71945,71948-71955,71957-71958,71960-71983,71999,72001,72096-72103
        \,72106-72144,72161,72163,72192,72203-72242,72250,72272,72284-72329,72349,72384-72440
        \,72704-72712,72714-72750,72768,72818-72847,72960-72966,72968-72969,72971-73008,73030
        \,73056-73061,73063-73064,73066-73097,73112,73440-73458,73648,73728-74649,74752-74862
        \,74880-75075,77824-78894,82944-83526,92160-92728,92736-92766,92880-92909,92928-92975
        \,92992-92995,93027-93047,93053-93071,93760-93823,93952-94026,94032,94099-94111
        \,94176-94177,94179,94208,100343,100352-101589,101632,101640,110592-110878
        \,110928-110930,110948-110951,110960-111355,113664-113770,113776-113788,113792-113800
        \,113808-113817,119808-119892,119894-119964,119966-119967,119970,119973-119974
        \,119977-119980,119982-119993,119995,119997-120003,120005-120069,120071-120074
        \,120077-120084,120086-120092,120094-120121,120123-120126,120128-120132,120134
        \,120138-120144,120146-120485,120488-120512,120514-120538,120540-120570,120572-120596
        \,120598-120628,120630-120654,120656-120686,120688-120712,120714-120744,120746-120770
        \,120772-120779,123136-123180,123191-123197,123214,123584-123627,124928-125124
        \,125184-125251,125259,126464-126467,126469-126495,126497-126498,126500,126503
        \,126505-126514,126516-126519,126521,126523,126530,126535,126537,126539,126541-126543
        \,126545-126546,126548,126551,126553,126555,126557,126559,126561-126562,126564
        \,126567-126570,126572-126578,126580-126583,126585-126588,126590,126592-126601
        \,126603-126619,126625-126627,126629-126633,126635-126651,131072,173789,173824,177972
        \,177984,178205,178208,183969,183984,191456,194560-195101,196608,201546
endif

" The function is contained, and only tested as the very last chance at the
" start of a statement - this is more straightforwards than trying to regex
" match the first word of a sequence, where it may be followed by arbitrarily
" many nested braces.
syntax match qasmFunction #\v\K\k*\ze\s*(\(|\s\K)# contained nextgroup=qasmParams skipwhite skipempty

syntax match qasmIdentifier #\v<\K\k*>#

syntax region qasmIndex matchgroup=qasmOperator start=#\v\[# end=#\v\]# transparent

" This parameters syntax item is necessary to allow "if" and "while" single-line
" statements to be matched correctly, when the test includes a function call.
syntax region qasmParams start="(" end=")" transparent contained
syntax region qasmDesignator start=#\v\[# end=#\v\]# transparent contained
    \ contains=qasmType,qasmOperator,qasmInteger,qasmReal,qasmIdentifier nextgroup=qasmParams skipwhite skipempty

" General keywords.
syntax keyword qasmInclude include
syntax keyword qasmVersion OPENQASM
syntax keyword qasmBuiltinGate U CX
syntax keyword qasmBuiltinQuantum reset measure barrier
syntax keyword qasmBuiltinClassical sin cos tan exp ln sqrt
syntax keyword qasmBuiltinConstant pi
syntax keyword qasmDefine gate nextgroup=qasmFunction skipwhite skipempty


" For historical reasons, the designator from a register defined by "qreg" (as
" opposed to "qubit") comes _after_ the identifier, unlike every other type.
syntax keyword qasmType qreg creg
    \ nextgroup=qasmRegIdentifier skipwhite skipempty
syntax match qasmRegIdentifier #\v<\K\k*># contained nextgroup=qasmDesignator skipwhite skipempty

highlight link qasmRegIdentifier qasmIdentifier

if s:openqasm_version < 3
    syntax keyword qasmDefine opaque nextgroup=qasmFunction skipwhite skipempty
else
    syntax keyword qasmInclude defcalgrammar
    " The current OpenQASM 3 grammar has 'creg' behave like other classical
    " types (i.e. with the designator immediately after the type name), even
    " though this clashes with OpenQASM 2.
    syntax keyword qasmType bit qubit int uint float bool angle duration stretch creg complex
        \ nextgroup=qasmDesignator skipwhite skipempty
    syntax keyword qasmIO input output
    syntax keyword qasmBuiltinQuantum durationof box
    syntax keyword qasmBuiltinClassical rotl rotr popcount
    syntax keyword qasmBuiltinConstant tau euler π 𝜏 ℇ
    syntax keyword qasmBuiltinPulse delay nextgroup=qasmDesignator skipwhite skipempty
    syntax keyword qasmDefine let const
    syntax keyword qasmDefine def gate defcal nextgroup=qasmFunction skipwhite skipempty
    syntax keyword qasmExtern extern nextgroup=qasmFunction skipwhite skipempty
    syntax keyword qasmJump break continue return
endif


syntax region qasmTest start=#\V(# end=#\V)# contained transparent
    \ nextgroup=@qasmStatementStart skipwhite skipempty

"" Looping constructs.
if s:openqasm_version >= 3
    " for
    syntax keyword qasmRepeat for nextgroup=qasmLoopVariable skipwhite skipempty
    syntax match qasmLoopVariable #\v<\K\k*># contained nextgroup=qasmLoopIn skipwhite skipempty
    syntax keyword qasmLoopIn in contained
        \ nextgroup=qasmLoopSet,qasmLoopRange,qasmLoopIdentifier skipwhite skipempty
    syntax region qasmLoopSet start=#\v\{# end=#\v\}# contained transparent
        \ nextgroup=@qasmStatementStart skipwhite skipempty
    syntax region qasmLoopRange start=#\v\[# end=#\v\]# contained transparent
        \ nextgroup=@qasmStatementStart skipwhite skipempty
        \ contains=TOP,qasmIndex
    syntax match qasmLoopIdentifier #\v<\K\k*># contained
        \ nextgroup=@qasmStatementStart skipwhite skipempty
    highlight link qasmLoopVariable qasmIdentifier
    highlight link qasmLoopIdentifier qasmIdentifier
    highlight link qasmLoopIn qasmOperator
    " while
    syntax keyword qasmRepeat while nextgroup=qasmTest skipwhite skipempty
endif

"" Branching constructs.
syntax keyword qasmConditional if nextgroup=qasmTest skipwhite skipempty
if s:openqasm_version >= 3
    syntax keyword qasmConditional else
        \ nextgroup=@qasmStatementStart skipwhite skipempty
endif


" This cluster is to force the matching of statements to do the "function" last.
" The function highlight can only occur as the first element of a sequence of
" space-separated entries, and only at the start of a statement.  This is a
" little tricky to match, so the aim is to match every other possibility first,
" and anything successful left over gets displayed as a function.
syntax cluster qasmStatementStart
    \ contains=qasmConditional,qasmJump,qasmIO,qasmType,qasmBuiltinQuantum,qasmBuiltinClassical,qasmBuiltinConstant,qasmBuiltinPulse,qasmDefine,qasmExtern,qasmModifier,qasmBlock,qasmRepeat,qasmFunction
syntax match qasmStatementEnd #;#
    \ nextgroup=@qasmStatementStart skipwhite skipempty

"" All types of operators.
if s:openqasm_version < 3
    let s:comparison_operators = ['==']
else
    let s:comparison_operators = [
        \'', '==', '!=', '<', '>',
    \ '', ]
endif
execute 'syntax match qasmComparisonOperator #\V\\(' . join(s:comparison_operators, '\|') . '\\)#'

if s:openqasm_version >= 3
    let s:general_operators = [ '',
        \ '~', ':', '||', '|', '&&', '&', '^', '*', '/', '>>', '<<', '%', '**',
        \ '+', '-',
    \ '', ]
    execute 'syntax match qasmOperator #\V\\('
        \ . join(s:general_operators, '\|')
        \ . '\\)#'
    syntax keyword qasmOperator in
    " Assignment operators start a new sentence in their r-value, so can have a
    " function call in that position.
    let s:assignment_operators = [ '',
        \ '=', '+=', '-=', '*=', '/=', '&=', '|=', '~=', '^=', '<<=', '>>=', '%=', '**=',
    \ '', ]
    execute 'syntax match qasmAssignmentOperator'
        \ . ' #\V\\(' . join(s:assignment_operators, '\|') . '\\)#'
        \ . ' nextgroup=@qasmStatementStart skipwhite skipempty'
endif
" The "->" assignment operator has the l-value on the right instead of the left,
" so cannot be followed by a function.
syntax match qasmAssignmentOperator #\V->#

"" Modifiers for quantum functions.  These must be followed by a function.
if s:openqasm_version >= 3
    syntax keyword qasmModifier inv
        \ nextgroup=qasmModifierSigil skipwhite skipempty
    syntax keyword qasmModifier pow ctrl negctrl
        \ nextgroup=qasmModifierParams,qasmModifierSigil skipwhite skipempty
    syntax region qasmModifierParams start=#(# end=#)# contained transparent
        \ nextgroup=qasmModifierSigil skipwhite skipempty
    syntax match qasmModifierSigil #@# contained
        \ nextgroup=qasmModifier,qasmFunction skipwhite skipempty
endif

"" Language literals.
syntax region qasmString start=#"# end=#"#
syntax region qasmString start=#'# end=#'#
syntax match qasmInteger #\v<\d+# nextgroup=qasmTimeUnit
syntax match qasmReal #\v<\d+\.\d*([eE][+-]?\d+)?# nextgroup=qasmTimeUnit skipwhite skipempty
if s:openqasm_version >= 3
    syntax match qasmTimeUnit #\v(dt|ns|us|μs|ms|s)># contained display
endif
syntax cluster qasmNumber contains=qasmInteger,qasmReal
syntax cluster qasmLiteral contains=@qasmNumber,qasmString

syntax match qasmBlockStart #{# containedin=qasmBlock,qasmPragmaBlock
    \ nextgroup=@qasmStatementStart skipwhite skipempty
syntax region qasmBlock start=#\V{# end=#\V}# transparent
    \ nextgroup=@qasmStatementStart skipwhite skipempty

if s:openqasm_version >= 3
    syntax match qasmHardwareQubit #\V$\k\*#
endif

"" Comments
" "skipwhite" is still needed after the single-line comment to allow function
" calls which don't start in the first column of the next input line.
syntax region qasmComment start=#//# end=#$# contains=@Spell
    \ nextgroup=@qasmStatementStart skipwhite skipempty
if s:openqasm_version >= 3
    syntax region qasmComment start=#/\*# end=#\*/# contains=@Spell
        \ nextgroup=@qasmStatementStart skipwhite skipempty
endif

if s:openqasm_version >= 3
    " Allow the {} characters denoted #pragma blocks to be highlighted differently.
    syntax match qasmPragma "#pragma" nextgroup=qasmPragmaBlock skipwhite skipempty
    syntax region qasmPragmaBlock matchgroup=qasmPragma start=#\V{# end=#\V}# transparent contained
endif


" Finally, set up all highlighting links.

highlight default link qasmIdentifier           Identifier
highlight default link qasmComment              Comment

highlight default link qasmType                 Type
highlight default link qasmIO                   StorageClass

highlight default link qasmStatementEnd         Operator
highlight default link qasmBuiltinQuantum       Operator
highlight default link qasmBuiltinPulse         Operator

highlight default link qasmVersion              PreProc
highlight default link qasmInclude              Include
highlight default link qasmPragma               PreProc

highlight default link qasmOperator             Operator
highlight default link qasmAssignmentOperator   Operator
highlight default link qasmComparisonOperator   Operator

highlight default link qasmRepeat               Repeat
highlight default link qasmJump                 Statement
highlight default link qasmConditional          Conditional

highlight default link qasmHardwareQubit        Special
highlight default link qasmInteger              Number
highlight default link qasmReal                 Float
highlight default link qasmTimeUnit             Number
highlight default link qasmBuiltinConstant      Constant
highlight default link qasmString               String

highlight default link qasmDefine               Statement
highlight default link qasmExtern               Statement
highlight default link qasmModifier             Function
highlight default link qasmModifierSigil        Special

highlight default link qasmFunction             Function
highlight default link qasmBuiltinGate          Function
highlight default link qasmBuiltinClassical     Function
