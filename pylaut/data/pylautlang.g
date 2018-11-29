%import common.STRING_INNER
%import common.DIGIT
%import common.SIGNED_INT
%import common.LETTER
%import common.UCASE_LETTER
%import common.WORD
%import common.WS
%ignore WS

start: (labelled|label)*

labelled: label? change
phoneme: "/" PHONEME_STR "/"
phoneme_list: "{" (phoneme ",")* phoneme "}"
?value: phoneme | phoneme_list | feat_expr
?expr: value | fcall
?change: unconditional
    | basic_conditional
    | conditional
    | fcall
unconditional: phoneme "->" phoneme -> simple_unconditional
    | phoneme_list "->" phoneme_list -> multiple_unconditional
    | feat_expr "->" feat_expr -> change_feature
    | feat_expr "->" phoneme -> replace_by_feature
basic_conditional: (unconditional | fcall) condition_list
conditional: phoneme ("=>" phoneme condition_list)+ "=>" phoneme -> simple_conditional
    | phoneme_list ("=>" phoneme_list condition_list)+ "=>" phoneme_list -> multiple_conditional
    | feat_expr ("=>" feat_expr condition_list)+ "=>" feat_expr -> change_feature_conditional
    | feat_expr ("=>" phoneme condition_list)+ "=>" phoneme -> replace_by_feature_conditional
condition_list: (condition)+
condition: "&" condition_body -> and_condition
    | "|" condition_body -> or_condition
?condition_body: relative_expr
    | inexpr
    | ifexpr
relative_expr: [BOUNDARY] value* RELATIVE value* [BOUNDARY]
inexpr: "in" entity
ifexpr: "if" boolexpr
?boolexpr: isexpr | bopexpr
isexpr: entity "is" value
bopexpr: (entity | value) "=" (entity | value) -> eqexpr
//    | (entity | value) ">" (entity | value) -> gtexpr
//    | (entity | value) "<" (entity | value) -> ltexpr
feat_expr: "[" finner+ "]"
words: (WORD ",")* WORD
finner: "+" words -> pos_feature
    |   "-" words -> neg_feature
fcall: IDENTIFIER "(" (value ",")* [value] ")"
index: entity "[" indexer "]"
member: entity "." IDENTIFIER
?entity: member | index | IDENTIFIER
label: "#" IDENTIFIER
offset: "@" SIGNED_INT
?indexer: SIGNED_INT | offset


IDENTIFIER: ("_"|LETTER) ("_"|LETTER|DIGIT)*
PHONEME_STR: /[^\/\\\_\n\t\[\]]+/
COMMENT: /%[^\n]*/
BOUNDARY: "#"
RELATIVE: "_"
%ignore COMMENT
