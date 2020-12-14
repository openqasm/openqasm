# Generated from source/grammar/qasm3.g4 by ANTLR 4.9
# encoding: utf-8
from antlr4 import *
from io import StringIO
import sys
if sys.version_info[1] > 5:
	from typing import TextIO
else:
	from typing.io import TextIO


def serializedATN():
    with StringIO() as buf:
        buf.write("\3\u608b\ua72a\u8133\ub9ed\u417c\u3be7\u7786\u5964\3u")
        buf.write("\u02d1\4\2\t\2\4\3\t\3\4\4\t\4\4\5\t\5\4\6\t\6\4\7\t\7")
        buf.write("\4\b\t\b\4\t\t\t\4\n\t\n\4\13\t\13\4\f\t\f\4\r\t\r\4\16")
        buf.write("\t\16\4\17\t\17\4\20\t\20\4\21\t\21\4\22\t\22\4\23\t\23")
        buf.write("\4\24\t\24\4\25\t\25\4\26\t\26\4\27\t\27\4\30\t\30\4\31")
        buf.write("\t\31\4\32\t\32\4\33\t\33\4\34\t\34\4\35\t\35\4\36\t\36")
        buf.write("\4\37\t\37\4 \t \4!\t!\4\"\t\"\4#\t#\4$\t$\4%\t%\4&\t")
        buf.write("&\4\'\t\'\4(\t(\4)\t)\4*\t*\4+\t+\4,\t,\4-\t-\4.\t.\4")
        buf.write("/\t/\4\60\t\60\4\61\t\61\4\62\t\62\4\63\t\63\4\64\t\64")
        buf.write("\4\65\t\65\4\66\t\66\4\67\t\67\48\t8\49\t9\4:\t:\4;\t")
        buf.write(";\4<\t<\4=\t=\4>\t>\4?\t?\4@\t@\4A\tA\4B\tB\4C\tC\4D\t")
        buf.write("D\4E\tE\4F\tF\4G\tG\4H\tH\4I\tI\4J\tJ\4K\tK\4L\tL\4M\t")
        buf.write("M\4N\tN\4O\tO\4P\tP\4Q\tQ\4R\tR\4S\tS\4T\tT\4U\tU\4V\t")
        buf.write("V\3\2\3\2\7\2\u00af\n\2\f\2\16\2\u00b2\13\2\3\3\5\3\u00b5")
        buf.write("\n\3\3\3\7\3\u00b8\n\3\f\3\16\3\u00bb\13\3\3\4\3\4\3\4")
        buf.write("\3\4\5\4\u00c1\n\4\3\4\3\4\3\5\3\5\3\5\3\5\3\6\3\6\3\6")
        buf.write("\3\6\3\6\3\6\3\6\3\6\3\6\3\6\3\6\5\6\u00d4\n\6\3\7\3\7")
        buf.write("\3\7\3\7\5\7\u00da\n\7\3\b\3\b\3\b\5\b\u00df\n\b\3\b\3")
        buf.write("\b\3\t\3\t\3\n\3\n\3\n\3\13\3\13\3\13\5\13\u00eb\n\13")
        buf.write("\3\13\3\13\3\f\3\f\3\f\3\f\3\r\3\r\3\r\3\r\3\r\3\r\3\16")
        buf.write("\3\16\7\16\u00fb\n\16\f\16\16\16\u00fe\13\16\3\16\3\16")
        buf.write("\3\17\3\17\5\17\u0104\n\17\3\20\3\20\3\20\7\20\u0109\n")
        buf.write("\20\f\20\16\20\u010c\13\20\3\20\3\20\3\21\3\21\3\21\3")
        buf.write("\22\3\22\3\23\3\23\3\23\3\23\3\24\3\24\5\24\u011b\n\24")
        buf.write("\3\24\3\24\3\25\3\25\3\25\7\25\u0122\n\25\f\25\16\25\u0125")
        buf.write("\13\25\3\25\3\25\3\26\3\26\3\27\3\27\3\30\3\30\3\31\3")
        buf.write("\31\5\31\u0131\n\31\3\32\3\32\5\32\u0135\n\32\3\32\3\32")
        buf.write("\5\32\u0139\n\32\3\32\3\32\3\32\5\32\u013e\n\32\5\32\u0140")
        buf.write("\n\32\3\33\3\33\3\33\3\33\3\33\3\34\3\34\3\34\3\34\3\35")
        buf.write("\3\35\3\35\3\35\3\36\3\36\3\36\3\37\3\37\3\37\5\37\u0155")
        buf.write("\n\37\3 \3 \5 \u0159\n \3!\3!\3!\7!\u015e\n!\f!\16!\u0161")
        buf.write("\13!\3!\3!\3\"\3\"\3\"\3#\3#\3#\7#\u016b\n#\f#\16#\u016e")
        buf.write("\13#\3#\3#\3$\3$\3$\3$\3$\3%\3%\3%\3%\3%\3%\3%\3%\3%\3")
        buf.write("%\3%\5%\u0182\n%\3&\3&\5&\u0186\n&\3&\3&\5&\u018a\n&\3")
        buf.write("&\3&\5&\u018e\n&\3&\3&\3\'\3\'\3\'\3\'\3(\3(\3(\5(\u0199")
        buf.write("\n(\3(\5(\u019c\n(\3(\3(\3)\3)\3)\5)\u01a3\n)\3)\3)\3")
        buf.write("*\3*\5*\u01a9\n*\3*\3*\3+\3+\3+\5+\u01b0\n+\3,\3,\3,\3")
        buf.write("-\3-\3-\3-\3-\3-\3-\3-\5-\u01bd\n-\3.\3.\3.\3/\3/\3/\3")
        buf.write("/\3/\3/\5/\u01c8\n/\3/\3/\3\60\3\60\3\60\5\60\u01cf\n")
        buf.write("\60\3\60\5\60\u01d2\n\60\3\60\3\60\3\61\3\61\3\61\3\61")
        buf.write("\3\61\3\61\3\61\5\61\u01dd\n\61\3\62\3\62\3\62\5\62\u01e2")
        buf.write("\n\62\3\63\3\63\3\64\3\64\3\64\3\64\3\64\5\64\u01eb\n")
        buf.write("\64\3\65\3\65\3\65\3\65\3\65\3\65\3\65\3\65\5\65\u01f5")
        buf.write("\n\65\3\65\3\65\3\65\3\65\5\65\u01fb\n\65\3\65\3\65\3")
        buf.write("\65\3\65\3\65\3\65\3\65\3\65\3\65\3\65\3\65\7\65\u0208")
        buf.write("\n\65\f\65\16\65\u020b\13\65\3\66\3\66\3\66\3\66\3\66")
        buf.write("\5\66\u0212\n\66\3\67\3\67\3\67\7\67\u0217\n\67\f\67\16")
        buf.write("\67\u021a\13\67\3\67\3\67\38\38\38\58\u0221\n8\39\39\3")
        buf.write(":\3:\3;\3;\3<\3<\3<\3=\3=\3>\3>\3>\3>\3?\3?\3?\3?\3?\5")
        buf.write("?\u0237\n?\3@\3@\5@\u023b\n@\3A\3A\3A\3A\3A\3A\3A\5A\u0244")
        buf.write("\nA\3B\3B\3B\3B\3B\3B\3B\5B\u024d\nB\3B\3B\3C\3C\3C\3")
        buf.write("D\3D\3E\3E\3E\3E\5E\u025a\nE\3E\5E\u025d\nE\3E\5E\u0260")
        buf.write("\nE\3E\5E\u0263\nE\3E\3E\3F\3F\3F\3F\5F\u026b\nF\3F\5")
        buf.write("F\u026e\nF\3F\5F\u0271\nF\3F\3F\3G\3G\5G\u0277\nG\3H\3")
        buf.write("H\3H\3I\3I\3J\3J\3J\5J\u0281\nJ\5J\u0283\nJ\3K\3K\3K\3")
        buf.write("K\3K\3K\3K\5K\u028c\nK\3L\3L\5L\u0290\nL\3M\3M\5M\u0294")
        buf.write("\nM\3M\3M\3M\3M\5M\u029a\nM\3N\3N\3O\3O\3O\5O\u02a1\n")
        buf.write("O\3O\5O\u02a4\nO\3O\3O\3O\5O\u02a9\nO\3P\3P\3P\3P\5P\u02af")
        buf.write("\nP\3Q\3Q\5Q\u02b3\nQ\3R\3R\3R\3R\3S\3S\5S\u02bb\nS\3")
        buf.write("S\3S\3S\5S\u02c0\nS\3S\5S\u02c3\nS\3S\3S\3S\3S\3T\3T\3")
        buf.write("U\3U\5U\u02cd\nU\3V\3V\3V\2\3hW\2\4\6\b\n\f\16\20\22\24")
        buf.write("\26\30\32\34\36 \"$&(*,.\60\62\64\668:<>@BDFHJLNPRTVX")
        buf.write("Z\\^`bdfhjlnprtvxz|~\u0080\u0082\u0084\u0086\u0088\u008a")
        buf.write("\u008c\u008e\u0090\u0092\u0094\u0096\u0098\u009a\u009c")
        buf.write("\u009e\u00a0\u00a2\u00a4\u00a6\u00a8\u00aa\2\16\3\2st")
        buf.write("\3\2\5\6\3\2\7\b\3\2\t\f\4\2\21\21\36/\3\2\618\3\29:\4")
        buf.write("\2;Dij\3\2JL\3\2PT\3\2Z[\4\2^^qq\2\u02e1\2\u00ac\3\2\2")
        buf.write("\2\4\u00b4\3\2\2\2\6\u00bc\3\2\2\2\b\u00c4\3\2\2\2\n\u00d3")
        buf.write("\3\2\2\2\f\u00d9\3\2\2\2\16\u00de\3\2\2\2\20\u00e2\3\2")
        buf.write("\2\2\22\u00e4\3\2\2\2\24\u00e7\3\2\2\2\26\u00ee\3\2\2")
        buf.write("\2\30\u00f2\3\2\2\2\32\u00fc\3\2\2\2\34\u0101\3\2\2\2")
        buf.write("\36\u010a\3\2\2\2 \u010f\3\2\2\2\"\u0112\3\2\2\2$\u0114")
        buf.write("\3\2\2\2&\u0118\3\2\2\2(\u0123\3\2\2\2*\u0128\3\2\2\2")
        buf.write(",\u012a\3\2\2\2.\u012c\3\2\2\2\60\u0130\3\2\2\2\62\u013f")
        buf.write("\3\2\2\2\64\u0141\3\2\2\2\66\u0146\3\2\2\28\u014a\3\2")
        buf.write("\2\2:\u014e\3\2\2\2<\u0154\3\2\2\2>\u0156\3\2\2\2@\u015f")
        buf.write("\3\2\2\2B\u0164\3\2\2\2D\u016c\3\2\2\2F\u0171\3\2\2\2")
        buf.write("H\u0176\3\2\2\2J\u0183\3\2\2\2L\u0191\3\2\2\2N\u0195\3")
        buf.write("\2\2\2P\u019f\3\2\2\2R\u01a8\3\2\2\2T\u01af\3\2\2\2V\u01b1")
        buf.write("\3\2\2\2X\u01bc\3\2\2\2Z\u01be\3\2\2\2\\\u01c7\3\2\2\2")
        buf.write("^\u01cb\3\2\2\2`\u01dc\3\2\2\2b\u01e1\3\2\2\2d\u01e3\3")
        buf.write("\2\2\2f\u01ea\3\2\2\2h\u01fa\3\2\2\2j\u0211\3\2\2\2l\u0218")
        buf.write("\3\2\2\2n\u0220\3\2\2\2p\u0222\3\2\2\2r\u0224\3\2\2\2")
        buf.write("t\u0226\3\2\2\2v\u0228\3\2\2\2x\u022b\3\2\2\2z\u022d\3")
        buf.write("\2\2\2|\u0236\3\2\2\2~\u023a\3\2\2\2\u0080\u023c\3\2\2")
        buf.write("\2\u0082\u024c\3\2\2\2\u0084\u0250\3\2\2\2\u0086\u0253")
        buf.write("\3\2\2\2\u0088\u0255\3\2\2\2\u008a\u0266\3\2\2\2\u008c")
        buf.write("\u0276\3\2\2\2\u008e\u0278\3\2\2\2\u0090\u027b\3\2\2\2")
        buf.write("\u0092\u0282\3\2\2\2\u0094\u028b\3\2\2\2\u0096\u028f\3")
        buf.write("\2\2\2\u0098\u0299\3\2\2\2\u009a\u029b\3\2\2\2\u009c\u029d")
        buf.write("\3\2\2\2\u009e\u02ae\3\2\2\2\u00a0\u02b2\3\2\2\2\u00a2")
        buf.write("\u02b4\3\2\2\2\u00a4\u02b8\3\2\2\2\u00a6\u02c8\3\2\2\2")
        buf.write("\u00a8\u02cc\3\2\2\2\u00aa\u02ce\3\2\2\2\u00ac\u00b0\5")
        buf.write("\4\3\2\u00ad\u00af\5\n\6\2\u00ae\u00ad\3\2\2\2\u00af\u00b2")
        buf.write("\3\2\2\2\u00b0\u00ae\3\2\2\2\u00b0\u00b1\3\2\2\2\u00b1")
        buf.write("\3\3\2\2\2\u00b2\u00b0\3\2\2\2\u00b3\u00b5\5\6\4\2\u00b4")
        buf.write("\u00b3\3\2\2\2\u00b4\u00b5\3\2\2\2\u00b5\u00b9\3\2\2\2")
        buf.write("\u00b6\u00b8\5\b\5\2\u00b7\u00b6\3\2\2\2\u00b8\u00bb\3")
        buf.write("\2\2\2\u00b9\u00b7\3\2\2\2\u00b9\u00ba\3\2\2\2\u00ba\5")
        buf.write("\3\2\2\2\u00bb\u00b9\3\2\2\2\u00bc\u00bd\7\3\2\2\u00bd")
        buf.write("\u00c0\7n\2\2\u00be\u00bf\7g\2\2\u00bf\u00c1\7n\2\2\u00c0")
        buf.write("\u00be\3\2\2\2\u00c0\u00c1\3\2\2\2\u00c1\u00c2\3\2\2\2")
        buf.write("\u00c2\u00c3\7f\2\2\u00c3\7\3\2\2\2\u00c4\u00c5\7\4\2")
        buf.write("\2\u00c5\u00c6\7r\2\2\u00c6\u00c7\7f\2\2\u00c7\t\3\2\2")
        buf.write("\2\u00c8\u00d4\5\f\7\2\u00c9\u00d4\5f\64\2\u00ca\u00d4")
        buf.write("\5\16\b\2\u00cb\u00d4\5\u0080A\2\u00cc\u00d4\5\u0082B")
        buf.write("\2\u00cd\u00d4\5\u0084C\2\u00ce\u00d4\5F$\2\u00cf\u00d4")
        buf.write("\5R*\2\u00d0\u00d4\5\u009eP\2\u00d1\u00d4\5\u008eH\2\u00d2")
        buf.write("\u00d4\5\20\t\2\u00d3\u00c8\3\2\2\2\u00d3\u00c9\3\2\2")
        buf.write("\2\u00d3\u00ca\3\2\2\2\u00d3\u00cb\3\2\2\2\u00d3\u00cc")
        buf.write("\3\2\2\2\u00d3\u00cd\3\2\2\2\u00d3\u00ce\3\2\2\2\u00d3")
        buf.write("\u00cf\3\2\2\2\u00d3\u00d0\3\2\2\2\u00d3\u00d1\3\2\2\2")
        buf.write("\u00d3\u00d2\3\2\2\2\u00d4\13\3\2\2\2\u00d5\u00da\5\u008a")
        buf.write("F\2\u00d6\u00da\5\u0088E\2\u00d7\u00da\5L\'\2\u00d8\u00da")
        buf.write("\5\u00a4S\2\u00d9\u00d5\3\2\2\2\u00d9\u00d6\3\2\2\2\u00d9")
        buf.write("\u00d7\3\2\2\2\u00d9\u00d8\3\2\2\2\u00da\r\3\2\2\2\u00db")
        buf.write("\u00df\5$\23\2\u00dc\u00df\5> \2\u00dd\u00df\5\64\33\2")
        buf.write("\u00de\u00db\3\2\2\2\u00de\u00dc\3\2\2\2\u00de\u00dd\3")
        buf.write("\2\2\2\u00df\u00e0\3\2\2\2\u00e0\u00e1\7f\2\2\u00e1\17")
        buf.write("\3\2\2\2\u00e2\u00e3\t\2\2\2\u00e3\21\3\2\2\2\u00e4\u00e5")
        buf.write("\7j\2\2\u00e5\u00e6\5> \2\u00e6\23\3\2\2\2\u00e7\u00ea")
        buf.write("\7a\2\2\u00e8\u00eb\5\24\13\2\u00e9\u00eb\5\n\6\2\u00ea")
        buf.write("\u00e8\3\2\2\2\u00ea\u00e9\3\2\2\2\u00eb\u00ec\3\2\2\2")
        buf.write("\u00ec\u00ed\7b\2\2\u00ed\25\3\2\2\2\u00ee\u00ef\7_\2")
        buf.write("\2\u00ef\u00f0\5h\65\2\u00f0\u00f1\7`\2\2\u00f1\27\3\2")
        buf.write("\2\2\u00f2\u00f3\7_\2\2\u00f3\u00f4\5h\65\2\u00f4\u00f5")
        buf.write("\7h\2\2\u00f5\u00f6\5h\65\2\u00f6\u00f7\7`\2\2\u00f7\31")
        buf.write("\3\2\2\2\u00f8\u00f9\7q\2\2\u00f9\u00fb\7h\2\2\u00fa\u00f8")
        buf.write("\3\2\2\2\u00fb\u00fe\3\2\2\2\u00fc\u00fa\3\2\2\2\u00fc")
        buf.write("\u00fd\3\2\2\2\u00fd\u00ff\3\2\2\2\u00fe\u00fc\3\2\2\2")
        buf.write("\u00ff\u0100\7q\2\2\u0100\33\3\2\2\2\u0101\u0103\7q\2")
        buf.write("\2\u0102\u0104\5\26\f\2\u0103\u0102\3\2\2\2\u0103\u0104")
        buf.write("\3\2\2\2\u0104\35\3\2\2\2\u0105\u0106\5\34\17\2\u0106")
        buf.write("\u0107\7h\2\2\u0107\u0109\3\2\2\2\u0108\u0105\3\2\2\2")
        buf.write("\u0109\u010c\3\2\2\2\u010a\u0108\3\2\2\2\u010a\u010b\3")
        buf.write("\2\2\2\u010b\u010d\3\2\2\2\u010c\u010a\3\2\2\2\u010d\u010e")
        buf.write("\5\34\17\2\u010e\37\3\2\2\2\u010f\u0110\7e\2\2\u0110\u0111")
        buf.write("\7q\2\2\u0111!\3\2\2\2\u0112\u0113\t\3\2\2\u0113#\3\2")
        buf.write("\2\2\u0114\u0115\5\"\22\2\u0115\u0116\7q\2\2\u0116\u0117")
        buf.write("\5\26\f\2\u0117%\3\2\2\2\u0118\u011a\5\"\22\2\u0119\u011b")
        buf.write("\5\26\f\2\u011a\u0119\3\2\2\2\u011a\u011b\3\2\2\2\u011b")
        buf.write("\u011c\3\2\2\2\u011c\u011d\5 \21\2\u011d\'\3\2\2\2\u011e")
        buf.write("\u011f\5&\24\2\u011f\u0120\7h\2\2\u0120\u0122\3\2\2\2")
        buf.write("\u0121\u011e\3\2\2\2\u0122\u0125\3\2\2\2\u0123\u0121\3")
        buf.write("\2\2\2\u0123\u0124\3\2\2\2\u0124\u0126\3\2\2\2\u0125\u0123")
        buf.write("\3\2\2\2\u0126\u0127\5&\24\2\u0127)\3\2\2\2\u0128\u0129")
        buf.write("\t\4\2\2\u0129+\3\2\2\2\u012a\u012b\t\5\2\2\u012b-\3\2")
        buf.write("\2\2\u012c\u012d\7\r\2\2\u012d/\3\2\2\2\u012e\u0131\7")
        buf.write("\16\2\2\u012f\u0131\5\u0092J\2\u0130\u012e\3\2\2\2\u0130")
        buf.write("\u012f\3\2\2\2\u0131\61\3\2\2\2\u0132\u0134\5,\27\2\u0133")
        buf.write("\u0135\5\26\f\2\u0134\u0133\3\2\2\2\u0134\u0135\3\2\2")
        buf.write("\2\u0135\u0140\3\2\2\2\u0136\u0138\5.\30\2\u0137\u0139")
        buf.write("\5\30\r\2\u0138\u0137\3\2\2\2\u0138\u0139\3\2\2\2\u0139")
        buf.write("\u0140\3\2\2\2\u013a\u0140\5\60\31\2\u013b\u013d\5*\26")
        buf.write("\2\u013c\u013e\5\26\f\2\u013d\u013c\3\2\2\2\u013d\u013e")
        buf.write("\3\2\2\2\u013e\u0140\3\2\2\2\u013f\u0132\3\2\2\2\u013f")
        buf.write("\u0136\3\2\2\2\u013f\u013a\3\2\2\2\u013f\u013b\3\2\2\2")
        buf.write("\u0140\63\3\2\2\2\u0141\u0142\7\17\2\2\u0142\u0143\7q")
        buf.write("\2\2\u0143\u0144\7i\2\2\u0144\u0145\5h\65\2\u0145\65\3")
        buf.write("\2\2\2\u0146\u0147\5,\27\2\u0147\u0148\5\26\f\2\u0148")
        buf.write("\u0149\7q\2\2\u0149\67\3\2\2\2\u014a\u014b\5.\30\2\u014b")
        buf.write("\u014c\5\30\r\2\u014c\u014d\7q\2\2\u014d9\3\2\2\2\u014e")
        buf.write("\u014f\5\60\31\2\u014f\u0150\7q\2\2\u0150;\3\2\2\2\u0151")
        buf.write("\u0155\5\66\34\2\u0152\u0155\58\35\2\u0153\u0155\5:\36")
        buf.write("\2\u0154\u0151\3\2\2\2\u0154\u0152\3\2\2\2\u0154\u0153")
        buf.write("\3\2\2\2\u0155=\3\2\2\2\u0156\u0158\5<\37\2\u0157\u0159")
        buf.write("\5v<\2\u0158\u0157\3\2\2\2\u0158\u0159\3\2\2\2\u0159?")
        buf.write("\3\2\2\2\u015a\u015b\5\62\32\2\u015b\u015c\7h\2\2\u015c")
        buf.write("\u015e\3\2\2\2\u015d\u015a\3\2\2\2\u015e\u0161\3\2\2\2")
        buf.write("\u015f\u015d\3\2\2\2\u015f\u0160\3\2\2\2\u0160\u0162\3")
        buf.write("\2\2\2\u0161\u015f\3\2\2\2\u0162\u0163\5\62\32\2\u0163")
        buf.write("A\3\2\2\2\u0164\u0165\5\62\32\2\u0165\u0166\5 \21\2\u0166")
        buf.write("C\3\2\2\2\u0167\u0168\5B\"\2\u0168\u0169\7h\2\2\u0169")
        buf.write("\u016b\3\2\2\2\u016a\u0167\3\2\2\2\u016b\u016e\3\2\2\2")
        buf.write("\u016c\u016a\3\2\2\2\u016c\u016d\3\2\2\2\u016d\u016f\3")
        buf.write("\2\2\2\u016e\u016c\3\2\2\2\u016f\u0170\5B\"\2\u0170E\3")
        buf.write("\2\2\2\u0171\u0172\7\20\2\2\u0172\u0173\7q\2\2\u0173\u0174")
        buf.write("\7i\2\2\u0174\u0175\5H%\2\u0175G\3\2\2\2\u0176\u0181\7")
        buf.write("i\2\2\u0177\u0178\7q\2\2\u0178\u0182\5J&\2\u0179\u017a")
        buf.write("\7q\2\2\u017a\u017b\7\21\2\2\u017b\u0182\7q\2\2\u017c")
        buf.write("\u017d\7q\2\2\u017d\u017e\7_\2\2\u017e\u017f\5l\67\2\u017f")
        buf.write("\u0180\7`\2\2\u0180\u0182\3\2\2\2\u0181\u0177\3\2\2\2")
        buf.write("\u0181\u0179\3\2\2\2\u0181\u017c\3\2\2\2\u0182I\3\2\2")
        buf.write("\2\u0183\u0185\7_\2\2\u0184\u0186\5h\65\2\u0185\u0184")
        buf.write("\3\2\2\2\u0185\u0186\3\2\2\2\u0186\u0187\3\2\2\2\u0187")
        buf.write("\u0189\7e\2\2\u0188\u018a\5h\65\2\u0189\u0188\3\2\2\2")
        buf.write("\u0189\u018a\3\2\2\2\u018a\u018d\3\2\2\2\u018b\u018c\7")
        buf.write("e\2\2\u018c\u018e\5h\65\2\u018d\u018b\3\2\2\2\u018d\u018e")
        buf.write("\3\2\2\2\u018e\u018f\3\2\2\2\u018f\u0190\7`\2\2\u0190")
        buf.write("K\3\2\2\2\u0191\u0192\7\22\2\2\u0192\u0193\5N(\2\u0193")
        buf.write("\u0194\5P)\2\u0194M\3\2\2\2\u0195\u019b\7q\2\2\u0196\u0198")
        buf.write("\7c\2\2\u0197\u0199\5D#\2\u0198\u0197\3\2\2\2\u0198\u0199")
        buf.write("\3\2\2\2\u0199\u019a\3\2\2\2\u019a\u019c\7d\2\2\u019b")
        buf.write("\u0196\3\2\2\2\u019b\u019c\3\2\2\2\u019c\u019d\3\2\2\2")
        buf.write("\u019d\u019e\5\32\16\2\u019eO\3\2\2\2\u019f\u01a2\7a\2")
        buf.write("\2\u01a0\u01a3\5P)\2\u01a1\u01a3\5R*\2\u01a2\u01a0\3\2")
        buf.write("\2\2\u01a2\u01a1\3\2\2\2\u01a3\u01a4\3\2\2\2\u01a4\u01a5")
        buf.write("\7b\2\2\u01a5Q\3\2\2\2\u01a6\u01a9\5T+\2\u01a7\u01a9\5")
        buf.write("X-\2\u01a8\u01a6\3\2\2\2\u01a8\u01a7\3\2\2\2\u01a9\u01aa")
        buf.write("\3\2\2\2\u01aa\u01ab\7f\2\2\u01abS\3\2\2\2\u01ac\u01b0")
        buf.write("\5^\60\2\u01ad\u01b0\5V,\2\u01ae\u01b0\5Z.\2\u01af\u01ac")
        buf.write("\3\2\2\2\u01af\u01ad\3\2\2\2\u01af\u01ae\3\2\2\2\u01b0")
        buf.write("U\3\2\2\2\u01b1\u01b2\7\23\2\2\u01b2\u01b3\5\36\20\2\u01b3")
        buf.write("W\3\2\2\2\u01b4\u01b5\5V,\2\u01b5\u01b6\7j\2\2\u01b6\u01b7")
        buf.write("\5\36\20\2\u01b7\u01bd\3\2\2\2\u01b8\u01b9\5\36\20\2\u01b9")
        buf.write("\u01ba\7i\2\2\u01ba\u01bb\5V,\2\u01bb\u01bd\3\2\2\2\u01bc")
        buf.write("\u01b4\3\2\2\2\u01bc\u01b8\3\2\2\2\u01bdY\3\2\2\2\u01be")
        buf.write("\u01bf\7\24\2\2\u01bf\u01c0\5\36\20\2\u01c0[\3\2\2\2\u01c1")
        buf.write("\u01c8\7\25\2\2\u01c2\u01c3\7\26\2\2\u01c3\u01c4\7c\2")
        buf.write("\2\u01c4\u01c5\7n\2\2\u01c5\u01c8\7d\2\2\u01c6\u01c8\7")
        buf.write("\27\2\2\u01c7\u01c1\3\2\2\2\u01c7\u01c2\3\2\2\2\u01c7")
        buf.write("\u01c6\3\2\2\2\u01c8\u01c9\3\2\2\2\u01c9\u01ca\7\30\2")
        buf.write("\2\u01ca]\3\2\2\2\u01cb\u01d1\5`\61\2\u01cc\u01ce\7c\2")
        buf.write("\2\u01cd\u01cf\5l\67\2\u01ce\u01cd\3\2\2\2\u01ce\u01cf")
        buf.write("\3\2\2\2\u01cf\u01d0\3\2\2\2\u01d0\u01d2\7d\2\2\u01d1")
        buf.write("\u01cc\3\2\2\2\u01d1\u01d2\3\2\2\2\u01d2\u01d3\3\2\2\2")
        buf.write("\u01d3\u01d4\5\36\20\2\u01d4_\3\2\2\2\u01d5\u01dd\7\31")
        buf.write("\2\2\u01d6\u01dd\7\32\2\2\u01d7\u01dd\7\33\2\2\u01d8\u01dd")
        buf.write("\7q\2\2\u01d9\u01da\5\\/\2\u01da\u01db\5`\61\2\u01db\u01dd")
        buf.write("\3\2\2\2\u01dc\u01d5\3\2\2\2\u01dc\u01d6\3\2\2\2\u01dc")
        buf.write("\u01d7\3\2\2\2\u01dc\u01d8\3\2\2\2\u01dc\u01d9\3\2\2\2")
        buf.write("\u01dda\3\2\2\2\u01de\u01e2\7\34\2\2\u01df\u01e2\7\35")
        buf.write("\2\2\u01e0\u01e2\5p9\2\u01e1\u01de\3\2\2\2\u01e1\u01df")
        buf.write("\3\2\2\2\u01e1\u01e0\3\2\2\2\u01e2c\3\2\2\2\u01e3\u01e4")
        buf.write("\t\6\2\2\u01e4e\3\2\2\2\u01e5\u01e6\5h\65\2\u01e6\u01e7")
        buf.write("\7f\2\2\u01e7\u01eb\3\2\2\2\u01e8\u01e9\7\60\2\2\u01e9")
        buf.write("\u01eb\5f\64\2\u01ea\u01e5\3\2\2\2\u01ea\u01e8\3\2\2\2")
        buf.write("\u01ebg\3\2\2\2\u01ec\u01ed\b\65\1\2\u01ed\u01ee\5b\62")
        buf.write("\2\u01ee\u01ef\5h\65\t\u01ef\u01fb\3\2\2\2\u01f0\u01fb")
        buf.write("\5z>\2\u01f1\u01f2\5n8\2\u01f2\u01f4\7c\2\2\u01f3\u01f5")
        buf.write("\5l\67\2\u01f4\u01f3\3\2\2\2\u01f4\u01f5\3\2\2\2\u01f5")
        buf.write("\u01f6\3\2\2\2\u01f6\u01f7\7d\2\2\u01f7\u01fb\3\2\2\2")
        buf.write("\u01f8\u01fb\5V,\2\u01f9\u01fb\5j\66\2\u01fa\u01ec\3\2")
        buf.write("\2\2\u01fa\u01f0\3\2\2\2\u01fa\u01f1\3\2\2\2\u01fa\u01f8")
        buf.write("\3\2\2\2\u01fa\u01f9\3\2\2\2\u01fb\u0209\3\2\2\2\u01fc")
        buf.write("\u01fd\f\n\2\2\u01fd\u01fe\5d\63\2\u01fe\u01ff\5h\65\13")
        buf.write("\u01ff\u0208\3\2\2\2\u0200\u0201\f\7\2\2\u0201\u0202\7")
        buf.write("_\2\2\u0202\u0203\5h\65\2\u0203\u0204\7`\2\2\u0204\u0208")
        buf.write("\3\2\2\2\u0205\u0206\f\5\2\2\u0206\u0208\5t;\2\u0207\u01fc")
        buf.write("\3\2\2\2\u0207\u0200\3\2\2\2\u0207\u0205\3\2\2\2\u0208")
        buf.write("\u020b\3\2\2\2\u0209\u0207\3\2\2\2\u0209\u020a\3\2\2\2")
        buf.write("\u020ai\3\2\2\2\u020b\u0209\3\2\2\2\u020c\u0212\7k\2\2")
        buf.write("\u020d\u0212\7n\2\2\u020e\u0212\7p\2\2\u020f\u0212\7q")
        buf.write("\2\2\u0210\u0212\5\u0096L\2\u0211\u020c\3\2\2\2\u0211")
        buf.write("\u020d\3\2\2\2\u0211\u020e\3\2\2\2\u0211\u020f\3\2\2\2")
        buf.write("\u0211\u0210\3\2\2\2\u0212k\3\2\2\2\u0213\u0214\5h\65")
        buf.write("\2\u0214\u0215\7h\2\2\u0215\u0217\3\2\2\2\u0216\u0213")
        buf.write("\3\2\2\2\u0217\u021a\3\2\2\2\u0218\u0216\3\2\2\2\u0218")
        buf.write("\u0219\3\2\2\2\u0219\u021b\3\2\2\2\u021a\u0218\3\2\2\2")
        buf.write("\u021b\u021c\5h\65\2\u021cm\3\2\2\2\u021d\u0221\7q\2\2")
        buf.write("\u021e\u0221\5p9\2\u021f\u0221\5r:\2\u0220\u021d\3\2\2")
        buf.write("\2\u0220\u021e\3\2\2\2\u0220\u021f\3\2\2\2\u0221o\3\2")
        buf.write("\2\2\u0222\u0223\t\7\2\2\u0223q\3\2\2\2\u0224\u0225\5")
        buf.write("\62\32\2\u0225s\3\2\2\2\u0226\u0227\t\b\2\2\u0227u\3\2")
        buf.write("\2\2\u0228\u0229\5x=\2\u0229\u022a\5h\65\2\u022aw\3\2")
        buf.write("\2\2\u022b\u022c\t\t\2\2\u022cy\3\2\2\2\u022d\u022e\7")
        buf.write("q\2\2\u022e\u022f\7E\2\2\u022f\u0230\5|?\2\u0230{\3\2")
        buf.write("\2\2\u0231\u0232\7a\2\2\u0232\u0233\5l\67\2\u0233\u0234")
        buf.write("\7b\2\2\u0234\u0237\3\2\2\2\u0235\u0237\5J&\2\u0236\u0231")
        buf.write("\3\2\2\2\u0236\u0235\3\2\2\2\u0237}\3\2\2\2\u0238\u023b")
        buf.write("\5\n\6\2\u0239\u023b\5\24\13\2\u023a\u0238\3\2\2\2\u023a")
        buf.write("\u0239\3\2\2\2\u023b\177\3\2\2\2\u023c\u023d\7F\2\2\u023d")
        buf.write("\u023e\7c\2\2\u023e\u023f\5h\65\2\u023f\u0240\7d\2\2\u0240")
        buf.write("\u0243\5~@\2\u0241\u0242\7G\2\2\u0242\u0244\5~@\2\u0243")
        buf.write("\u0241\3\2\2\2\u0243\u0244\3\2\2\2\u0244\u0081\3\2\2\2")
        buf.write("\u0245\u0246\7H\2\2\u0246\u024d\5z>\2\u0247\u0248\7I\2")
        buf.write("\2\u0248\u0249\7c\2\2\u0249\u024a\5h\65\2\u024a\u024b")
        buf.write("\7d\2\2\u024b\u024d\3\2\2\2\u024c\u0245\3\2\2\2\u024c")
        buf.write("\u0247\3\2\2\2\u024d\u024e\3\2\2\2\u024e\u024f\5~@\2\u024f")
        buf.write("\u0083\3\2\2\2\u0250\u0251\5\u0086D\2\u0251\u0252\7f\2")
        buf.write("\2\u0252\u0085\3\2\2\2\u0253\u0254\t\n\2\2\u0254\u0087")
        buf.write("\3\2\2\2\u0255\u0256\7M\2\2\u0256\u025c\7q\2\2\u0257\u0259")
        buf.write("\7c\2\2\u0258\u025a\5@!\2\u0259\u0258\3\2\2\2\u0259\u025a")
        buf.write("\3\2\2\2\u025a\u025b\3\2\2\2\u025b\u025d\7d\2\2\u025c")
        buf.write("\u0257\3\2\2\2\u025c\u025d\3\2\2\2\u025d\u025f\3\2\2\2")
        buf.write("\u025e\u0260\5\22\n\2\u025f\u025e\3\2\2\2\u025f\u0260")
        buf.write("\3\2\2\2\u0260\u0262\3\2\2\2\u0261\u0263\5\62\32\2\u0262")
        buf.write("\u0261\3\2\2\2\u0262\u0263\3\2\2\2\u0263\u0264\3\2\2\2")
        buf.write("\u0264\u0265\7f\2\2\u0265\u0089\3\2\2\2\u0266\u0267\7")
        buf.write("N\2\2\u0267\u026d\7q\2\2\u0268\u026a\7c\2\2\u0269\u026b")
        buf.write("\5\u008cG\2\u026a\u0269\3\2\2\2\u026a\u026b\3\2\2\2\u026b")
        buf.write("\u026c\3\2\2\2\u026c\u026e\7d\2\2\u026d\u0268\3\2\2\2")
        buf.write("\u026d\u026e\3\2\2\2\u026e\u0270\3\2\2\2\u026f\u0271\5")
        buf.write("\22\n\2\u0270\u026f\3\2\2\2\u0270\u0271\3\2\2\2\u0271")
        buf.write("\u0272\3\2\2\2\u0272\u0273\5\24\13\2\u0273\u008b\3\2\2")
        buf.write("\2\u0274\u0277\5D#\2\u0275\u0277\5(\25\2\u0276\u0274\3")
        buf.write("\2\2\2\u0276\u0275\3\2\2\2\u0277\u008d\3\2\2\2\u0278\u0279")
        buf.write("\7O\2\2\u0279\u027a\7u\2\2\u027a\u008f\3\2\2\2\u027b\u027c")
        buf.write("\t\13\2\2\u027c\u0091\3\2\2\2\u027d\u0283\7U\2\2\u027e")
        buf.write("\u0280\7V\2\2\u027f\u0281\7n\2\2\u0280\u027f\3\2\2\2\u0280")
        buf.write("\u0281\3\2\2\2\u0281\u0283\3\2\2\2\u0282\u027d\3\2\2\2")
        buf.write("\u0282\u027e\3\2\2\2\u0283\u0093\3\2\2\2\u0284\u0285\7")
        buf.write("W\2\2\u0285\u0286\7q\2\2\u0286\u028c\5P)\2\u0287\u0288")
        buf.write("\7X\2\2\u0288\u0289\5\u0090I\2\u0289\u028a\5P)\2\u028a")
        buf.write("\u028c\3\2\2\2\u028b\u0284\3\2\2\2\u028b\u0287\3\2\2\2")
        buf.write("\u028c\u0095\3\2\2\2\u028d\u0290\5\u0098M\2\u028e\u0290")
        buf.write("\7Y\2\2\u028f\u028d\3\2\2\2\u028f\u028e\3\2\2\2\u0290")
        buf.write("\u0097\3\2\2\2\u0291\u0293\7q\2\2\u0292\u0294\5\u0090")
        buf.write("I\2\u0293\u0292\3\2\2\2\u0293\u0294\3\2\2\2\u0294\u029a")
        buf.write("\3\2\2\2\u0295\u0296\78\2\2\u0296\u0297\7c\2\2\u0297\u0298")
        buf.write("\7q\2\2\u0298\u029a\7d\2\2\u0299\u0291\3\2\2\2\u0299\u0295")
        buf.write("\3\2\2\2\u029a\u0099\3\2\2\2\u029b\u029c\t\f\2\2\u029c")
        buf.write("\u009b\3\2\2\2\u029d\u02a3\5\u009aN\2\u029e\u02a0\7c\2")
        buf.write("\2\u029f\u02a1\5l\67\2\u02a0\u029f\3\2\2\2\u02a0\u02a1")
        buf.write("\3\2\2\2\u02a1\u02a2\3\2\2\2\u02a2\u02a4\7d\2\2\u02a3")
        buf.write("\u029e\3\2\2\2\u02a3\u02a4\3\2\2\2\u02a4\u02a5\3\2\2\2")
        buf.write("\u02a5\u02a8\5\26\f\2\u02a6\u02a9\5J&\2\u02a7\u02a9\5")
        buf.write("\36\20\2\u02a8\u02a6\3\2\2\2\u02a8\u02a7\3\2\2\2\u02a9")
        buf.write("\u009d\3\2\2\2\u02aa\u02ab\5\u009cO\2\u02ab\u02ac\7f\2")
        buf.write("\2\u02ac\u02af\3\2\2\2\u02ad\u02af\5\u0094K\2\u02ae\u02aa")
        buf.write("\3\2\2\2\u02ae\u02ad\3\2\2\2\u02af\u009f\3\2\2\2\u02b0")
        buf.write("\u02b3\5\u00a2R\2\u02b1\u02b3\5\u00a4S\2\u02b2\u02b0\3")
        buf.write("\2\2\2\u02b2\u02b1\3\2\2\2\u02b3\u00a1\3\2\2\2\u02b4\u02b5")
        buf.write("\7\\\2\2\u02b5\u02b6\5\u00a6T\2\u02b6\u02b7\7f\2\2\u02b7")
        buf.write("\u00a3\3\2\2\2\u02b8\u02ba\7]\2\2\u02b9\u02bb\5\u00a6")
        buf.write("T\2\u02ba\u02b9\3\2\2\2\u02ba\u02bb\3\2\2\2\u02bb\u02bc")
        buf.write("\3\2\2\2\u02bc\u02c2\7q\2\2\u02bd\u02bf\7c\2\2\u02be\u02c0")
        buf.write("\5\u00a8U\2\u02bf\u02be\3\2\2\2\u02bf\u02c0\3\2\2\2\u02c0")
        buf.write("\u02c1\3\2\2\2\u02c1\u02c3\7d\2\2\u02c2\u02bd\3\2\2\2")
        buf.write("\u02c2\u02c3\3\2\2\2\u02c3\u02c4\3\2\2\2\u02c4\u02c5\5")
        buf.write("\32\16\2\u02c5\u02c6\5\22\n\2\u02c6\u02c7\5\u00aaV\2\u02c7")
        buf.write("\u00a5\3\2\2\2\u02c8\u02c9\t\r\2\2\u02c9\u00a7\3\2\2\2")
        buf.write("\u02ca\u02cd\5D#\2\u02cb\u02cd\5l\67\2\u02cc\u02ca\3\2")
        buf.write("\2\2\u02cc\u02cb\3\2\2\2\u02cd\u00a9\3\2\2\2\u02ce\u02cf")
        buf.write("\7u\2\2\u02cf\u00ab\3\2\2\2J\u00b0\u00b4\u00b9\u00c0\u00d3")
        buf.write("\u00d9\u00de\u00ea\u00fc\u0103\u010a\u011a\u0123\u0130")
        buf.write("\u0134\u0138\u013d\u013f\u0154\u0158\u015f\u016c\u0181")
        buf.write("\u0185\u0189\u018d\u0198\u019b\u01a2\u01a8\u01af\u01bc")
        buf.write("\u01c7\u01ce\u01d1\u01dc\u01e1\u01ea\u01f4\u01fa\u0207")
        buf.write("\u0209\u0211\u0218\u0220\u0236\u023a\u0243\u024c\u0259")
        buf.write("\u025c\u025f\u0262\u026a\u026d\u0270\u0276\u0280\u0282")
        buf.write("\u028b\u028f\u0293\u0299\u02a0\u02a3\u02a8\u02ae\u02b2")
        buf.write("\u02ba\u02bf\u02c2\u02cc")
        return buf.getvalue()


class qasm3Parser ( Parser ):

    grammarFileName = "qasm3.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "'OPENQASM'", "'include'", "'qubit'", 
                     "'qreg'", "'bit'", "'creg'", "'int'", "'uint'", "'float'", 
                     "'angle'", "'fixed'", "'bool'", "'const'", "'let'", 
                     "'||'", "'gate'", "'measure'", "'barrier'", "'inv'", 
                     "'pow'", "'ctrl'", "'@'", "'CX'", "'U'", "'reset'", 
                     "'~'", "'!'", "'+'", "'-'", "'*'", "'/'", "'<<'", "'>>'", 
                     "'rotl'", "'rotr'", "'&&'", "'&'", "'|'", "'^'", "'>'", 
                     "'<'", "'>='", "'<='", "'=='", "'!='", "'return'", 
                     "'sin'", "'cos'", "'tan'", "'exp'", "'ln'", "'sqrt'", 
                     "'popcount'", "'lengthof'", "'++'", "'--'", "'+='", 
                     "'-='", "'*='", "'/='", "'&='", "'|='", "'~='", "'^='", 
                     "'<<='", "'>>='", "'in'", "'if'", "'else'", "'for'", 
                     "'while'", "'break'", "'continue'", "'end'", "'kernel'", 
                     "'def'", "'#pragma'", "'dt'", "'ns'", "'us'", "'ms'", 
                     "'s'", "'length'", "'stretch'", "'boxas'", "'boxto'", 
                     "'stretchinf'", "'delay'", "'rotary'", "'defcalgrammar'", 
                     "'defcal'", "'openpulse'", "'['", "']'", "'{'", "'}'", 
                     "'('", "')'", "':'", "';'", "'.'", "','", "'='", "'->'" ]

    symbolicNames = [ "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "LBRACKET", "RBRACKET", "LBRACE", "RBRACE", 
                      "LPAREN", "RPAREN", "COLON", "SEMICOLON", "DOT", "COMMA", 
                      "ASSIGN", "ARROW", "Constant", "Whitespace", "Newline", 
                      "Integer", "Float", "RealNumber", "Identifier", "StringLiteral", 
                      "LineComment", "BlockComment", "AnyBlock" ]

    RULE_program = 0
    RULE_header = 1
    RULE_version = 2
    RULE_include = 3
    RULE_statement = 4
    RULE_globalStatement = 5
    RULE_declarationStatement = 6
    RULE_comment = 7
    RULE_returnSignature = 8
    RULE_programBlock = 9
    RULE_designator = 10
    RULE_doubleDesignator = 11
    RULE_identifierList = 12
    RULE_indexIdentifier = 13
    RULE_indexIdentifierList = 14
    RULE_association = 15
    RULE_quantumType = 16
    RULE_quantumDeclaration = 17
    RULE_quantumArgument = 18
    RULE_quantumArgumentList = 19
    RULE_bitType = 20
    RULE_singleDesignatorType = 21
    RULE_doubleDesignatorType = 22
    RULE_noDesignatorType = 23
    RULE_classicalType = 24
    RULE_constantDeclaration = 25
    RULE_singleDesignatorDeclaration = 26
    RULE_doubleDesignatorDeclaration = 27
    RULE_noDesignatorDeclaration = 28
    RULE_classicalVariableDeclaration = 29
    RULE_classicalDeclaration = 30
    RULE_classicalTypeList = 31
    RULE_classicalArgument = 32
    RULE_classicalArgumentList = 33
    RULE_aliasStatement = 34
    RULE_concatenateExpression = 35
    RULE_rangeDefinition = 36
    RULE_quantumGateDefinition = 37
    RULE_quantumGateSignature = 38
    RULE_quantumBlock = 39
    RULE_quantumStatement = 40
    RULE_quantumInstruction = 41
    RULE_quantumMeasurement = 42
    RULE_quantumMeasurementDeclaration = 43
    RULE_quantumBarrier = 44
    RULE_quantumGateModifier = 45
    RULE_quantumGateCall = 46
    RULE_quantumGateName = 47
    RULE_unaryOperator = 48
    RULE_binaryOperator = 49
    RULE_expressionStatement = 50
    RULE_expression = 51
    RULE_expressionTerminator = 52
    RULE_expressionList = 53
    RULE_call = 54
    RULE_builtInMath = 55
    RULE_castOperator = 56
    RULE_incrementor = 57
    RULE_assignmentExpression = 58
    RULE_assignmentOperator = 59
    RULE_membershipTest = 60
    RULE_setDeclaration = 61
    RULE_loopBranchBlock = 62
    RULE_branchingStatement = 63
    RULE_loopStatement = 64
    RULE_controlDirectiveStatement = 65
    RULE_controlDirective = 66
    RULE_kernelDeclaration = 67
    RULE_subroutineDefinition = 68
    RULE_subroutineArgumentList = 69
    RULE_pragma = 70
    RULE_timeUnit = 71
    RULE_timingType = 72
    RULE_timingBox = 73
    RULE_timeTerminator = 74
    RULE_timeIdentifier = 75
    RULE_timeInstructionName = 76
    RULE_timeInstruction = 77
    RULE_timeStatement = 78
    RULE_calibration = 79
    RULE_calibrationGrammarDeclaration = 80
    RULE_calibrationDefinition = 81
    RULE_calibrationGrammar = 82
    RULE_calibrationArgumentList = 83
    RULE_calibrationBody = 84

    ruleNames =  [ "program", "header", "version", "include", "statement", 
                   "globalStatement", "declarationStatement", "comment", 
                   "returnSignature", "programBlock", "designator", "doubleDesignator", 
                   "identifierList", "indexIdentifier", "indexIdentifierList", 
                   "association", "quantumType", "quantumDeclaration", "quantumArgument", 
                   "quantumArgumentList", "bitType", "singleDesignatorType", 
                   "doubleDesignatorType", "noDesignatorType", "classicalType", 
                   "constantDeclaration", "singleDesignatorDeclaration", 
                   "doubleDesignatorDeclaration", "noDesignatorDeclaration", 
                   "classicalVariableDeclaration", "classicalDeclaration", 
                   "classicalTypeList", "classicalArgument", "classicalArgumentList", 
                   "aliasStatement", "concatenateExpression", "rangeDefinition", 
                   "quantumGateDefinition", "quantumGateSignature", "quantumBlock", 
                   "quantumStatement", "quantumInstruction", "quantumMeasurement", 
                   "quantumMeasurementDeclaration", "quantumBarrier", "quantumGateModifier", 
                   "quantumGateCall", "quantumGateName", "unaryOperator", 
                   "binaryOperator", "expressionStatement", "expression", 
                   "expressionTerminator", "expressionList", "call", "builtInMath", 
                   "castOperator", "incrementor", "assignmentExpression", 
                   "assignmentOperator", "membershipTest", "setDeclaration", 
                   "loopBranchBlock", "branchingStatement", "loopStatement", 
                   "controlDirectiveStatement", "controlDirective", "kernelDeclaration", 
                   "subroutineDefinition", "subroutineArgumentList", "pragma", 
                   "timeUnit", "timingType", "timingBox", "timeTerminator", 
                   "timeIdentifier", "timeInstructionName", "timeInstruction", 
                   "timeStatement", "calibration", "calibrationGrammarDeclaration", 
                   "calibrationDefinition", "calibrationGrammar", "calibrationArgumentList", 
                   "calibrationBody" ]

    EOF = Token.EOF
    T__0=1
    T__1=2
    T__2=3
    T__3=4
    T__4=5
    T__5=6
    T__6=7
    T__7=8
    T__8=9
    T__9=10
    T__10=11
    T__11=12
    T__12=13
    T__13=14
    T__14=15
    T__15=16
    T__16=17
    T__17=18
    T__18=19
    T__19=20
    T__20=21
    T__21=22
    T__22=23
    T__23=24
    T__24=25
    T__25=26
    T__26=27
    T__27=28
    T__28=29
    T__29=30
    T__30=31
    T__31=32
    T__32=33
    T__33=34
    T__34=35
    T__35=36
    T__36=37
    T__37=38
    T__38=39
    T__39=40
    T__40=41
    T__41=42
    T__42=43
    T__43=44
    T__44=45
    T__45=46
    T__46=47
    T__47=48
    T__48=49
    T__49=50
    T__50=51
    T__51=52
    T__52=53
    T__53=54
    T__54=55
    T__55=56
    T__56=57
    T__57=58
    T__58=59
    T__59=60
    T__60=61
    T__61=62
    T__62=63
    T__63=64
    T__64=65
    T__65=66
    T__66=67
    T__67=68
    T__68=69
    T__69=70
    T__70=71
    T__71=72
    T__72=73
    T__73=74
    T__74=75
    T__75=76
    T__76=77
    T__77=78
    T__78=79
    T__79=80
    T__80=81
    T__81=82
    T__82=83
    T__83=84
    T__84=85
    T__85=86
    T__86=87
    T__87=88
    T__88=89
    T__89=90
    T__90=91
    T__91=92
    LBRACKET=93
    RBRACKET=94
    LBRACE=95
    RBRACE=96
    LPAREN=97
    RPAREN=98
    COLON=99
    SEMICOLON=100
    DOT=101
    COMMA=102
    ASSIGN=103
    ARROW=104
    Constant=105
    Whitespace=106
    Newline=107
    Integer=108
    Float=109
    RealNumber=110
    Identifier=111
    StringLiteral=112
    LineComment=113
    BlockComment=114
    AnyBlock=115

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.9")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class ProgramContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def header(self):
            return self.getTypedRuleContext(qasm3Parser.HeaderContext,0)


        def statement(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(qasm3Parser.StatementContext)
            else:
                return self.getTypedRuleContext(qasm3Parser.StatementContext,i)


        def getRuleIndex(self):
            return qasm3Parser.RULE_program

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterProgram" ):
                listener.enterProgram(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitProgram" ):
                listener.exitProgram(self)




    def program(self):

        localctx = qasm3Parser.ProgramContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_program)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 170
            self.header()
            self.state = 174
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while (((_la) & ~0x3f) == 0 and ((1 << _la) & ((1 << qasm3Parser.T__2) | (1 << qasm3Parser.T__3) | (1 << qasm3Parser.T__4) | (1 << qasm3Parser.T__5) | (1 << qasm3Parser.T__6) | (1 << qasm3Parser.T__7) | (1 << qasm3Parser.T__8) | (1 << qasm3Parser.T__9) | (1 << qasm3Parser.T__10) | (1 << qasm3Parser.T__11) | (1 << qasm3Parser.T__12) | (1 << qasm3Parser.T__13) | (1 << qasm3Parser.T__15) | (1 << qasm3Parser.T__16) | (1 << qasm3Parser.T__17) | (1 << qasm3Parser.T__18) | (1 << qasm3Parser.T__19) | (1 << qasm3Parser.T__20) | (1 << qasm3Parser.T__22) | (1 << qasm3Parser.T__23) | (1 << qasm3Parser.T__24) | (1 << qasm3Parser.T__25) | (1 << qasm3Parser.T__26) | (1 << qasm3Parser.T__45) | (1 << qasm3Parser.T__46) | (1 << qasm3Parser.T__47) | (1 << qasm3Parser.T__48) | (1 << qasm3Parser.T__49) | (1 << qasm3Parser.T__50) | (1 << qasm3Parser.T__51) | (1 << qasm3Parser.T__52) | (1 << qasm3Parser.T__53))) != 0) or ((((_la - 68)) & ~0x3f) == 0 and ((1 << (_la - 68)) & ((1 << (qasm3Parser.T__67 - 68)) | (1 << (qasm3Parser.T__69 - 68)) | (1 << (qasm3Parser.T__70 - 68)) | (1 << (qasm3Parser.T__71 - 68)) | (1 << (qasm3Parser.T__72 - 68)) | (1 << (qasm3Parser.T__73 - 68)) | (1 << (qasm3Parser.T__74 - 68)) | (1 << (qasm3Parser.T__75 - 68)) | (1 << (qasm3Parser.T__76 - 68)) | (1 << (qasm3Parser.T__82 - 68)) | (1 << (qasm3Parser.T__83 - 68)) | (1 << (qasm3Parser.T__84 - 68)) | (1 << (qasm3Parser.T__85 - 68)) | (1 << (qasm3Parser.T__86 - 68)) | (1 << (qasm3Parser.T__87 - 68)) | (1 << (qasm3Parser.T__88 - 68)) | (1 << (qasm3Parser.T__90 - 68)) | (1 << (qasm3Parser.Constant - 68)) | (1 << (qasm3Parser.Integer - 68)) | (1 << (qasm3Parser.RealNumber - 68)) | (1 << (qasm3Parser.Identifier - 68)) | (1 << (qasm3Parser.LineComment - 68)) | (1 << (qasm3Parser.BlockComment - 68)))) != 0):
                self.state = 171
                self.statement()
                self.state = 176
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class HeaderContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def version(self):
            return self.getTypedRuleContext(qasm3Parser.VersionContext,0)


        def include(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(qasm3Parser.IncludeContext)
            else:
                return self.getTypedRuleContext(qasm3Parser.IncludeContext,i)


        def getRuleIndex(self):
            return qasm3Parser.RULE_header

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterHeader" ):
                listener.enterHeader(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitHeader" ):
                listener.exitHeader(self)




    def header(self):

        localctx = qasm3Parser.HeaderContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_header)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 178
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==qasm3Parser.T__0:
                self.state = 177
                self.version()


            self.state = 183
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==qasm3Parser.T__1:
                self.state = 180
                self.include()
                self.state = 185
                self._errHandler.sync(self)
                _la = self._input.LA(1)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class VersionContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def Integer(self, i:int=None):
            if i is None:
                return self.getTokens(qasm3Parser.Integer)
            else:
                return self.getToken(qasm3Parser.Integer, i)

        def SEMICOLON(self):
            return self.getToken(qasm3Parser.SEMICOLON, 0)

        def DOT(self):
            return self.getToken(qasm3Parser.DOT, 0)

        def getRuleIndex(self):
            return qasm3Parser.RULE_version

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterVersion" ):
                listener.enterVersion(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitVersion" ):
                listener.exitVersion(self)




    def version(self):

        localctx = qasm3Parser.VersionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_version)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 186
            self.match(qasm3Parser.T__0)
            self.state = 187
            self.match(qasm3Parser.Integer)
            self.state = 190
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==qasm3Parser.DOT:
                self.state = 188
                self.match(qasm3Parser.DOT)
                self.state = 189
                self.match(qasm3Parser.Integer)


            self.state = 192
            self.match(qasm3Parser.SEMICOLON)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class IncludeContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def StringLiteral(self):
            return self.getToken(qasm3Parser.StringLiteral, 0)

        def SEMICOLON(self):
            return self.getToken(qasm3Parser.SEMICOLON, 0)

        def getRuleIndex(self):
            return qasm3Parser.RULE_include

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterInclude" ):
                listener.enterInclude(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitInclude" ):
                listener.exitInclude(self)




    def include(self):

        localctx = qasm3Parser.IncludeContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_include)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 194
            self.match(qasm3Parser.T__1)
            self.state = 195
            self.match(qasm3Parser.StringLiteral)
            self.state = 196
            self.match(qasm3Parser.SEMICOLON)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class StatementContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def globalStatement(self):
            return self.getTypedRuleContext(qasm3Parser.GlobalStatementContext,0)


        def expressionStatement(self):
            return self.getTypedRuleContext(qasm3Parser.ExpressionStatementContext,0)


        def declarationStatement(self):
            return self.getTypedRuleContext(qasm3Parser.DeclarationStatementContext,0)


        def branchingStatement(self):
            return self.getTypedRuleContext(qasm3Parser.BranchingStatementContext,0)


        def loopStatement(self):
            return self.getTypedRuleContext(qasm3Parser.LoopStatementContext,0)


        def controlDirectiveStatement(self):
            return self.getTypedRuleContext(qasm3Parser.ControlDirectiveStatementContext,0)


        def aliasStatement(self):
            return self.getTypedRuleContext(qasm3Parser.AliasStatementContext,0)


        def quantumStatement(self):
            return self.getTypedRuleContext(qasm3Parser.QuantumStatementContext,0)


        def timeStatement(self):
            return self.getTypedRuleContext(qasm3Parser.TimeStatementContext,0)


        def pragma(self):
            return self.getTypedRuleContext(qasm3Parser.PragmaContext,0)


        def comment(self):
            return self.getTypedRuleContext(qasm3Parser.CommentContext,0)


        def getRuleIndex(self):
            return qasm3Parser.RULE_statement

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterStatement" ):
                listener.enterStatement(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitStatement" ):
                listener.exitStatement(self)




    def statement(self):

        localctx = qasm3Parser.StatementContext(self, self._ctx, self.state)
        self.enterRule(localctx, 8, self.RULE_statement)
        try:
            self.state = 209
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,4,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 198
                self.globalStatement()
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 199
                self.expressionStatement()
                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 200
                self.declarationStatement()
                pass

            elif la_ == 4:
                self.enterOuterAlt(localctx, 4)
                self.state = 201
                self.branchingStatement()
                pass

            elif la_ == 5:
                self.enterOuterAlt(localctx, 5)
                self.state = 202
                self.loopStatement()
                pass

            elif la_ == 6:
                self.enterOuterAlt(localctx, 6)
                self.state = 203
                self.controlDirectiveStatement()
                pass

            elif la_ == 7:
                self.enterOuterAlt(localctx, 7)
                self.state = 204
                self.aliasStatement()
                pass

            elif la_ == 8:
                self.enterOuterAlt(localctx, 8)
                self.state = 205
                self.quantumStatement()
                pass

            elif la_ == 9:
                self.enterOuterAlt(localctx, 9)
                self.state = 206
                self.timeStatement()
                pass

            elif la_ == 10:
                self.enterOuterAlt(localctx, 10)
                self.state = 207
                self.pragma()
                pass

            elif la_ == 11:
                self.enterOuterAlt(localctx, 11)
                self.state = 208
                self.comment()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class GlobalStatementContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def subroutineDefinition(self):
            return self.getTypedRuleContext(qasm3Parser.SubroutineDefinitionContext,0)


        def kernelDeclaration(self):
            return self.getTypedRuleContext(qasm3Parser.KernelDeclarationContext,0)


        def quantumGateDefinition(self):
            return self.getTypedRuleContext(qasm3Parser.QuantumGateDefinitionContext,0)


        def calibrationDefinition(self):
            return self.getTypedRuleContext(qasm3Parser.CalibrationDefinitionContext,0)


        def getRuleIndex(self):
            return qasm3Parser.RULE_globalStatement

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterGlobalStatement" ):
                listener.enterGlobalStatement(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitGlobalStatement" ):
                listener.exitGlobalStatement(self)




    def globalStatement(self):

        localctx = qasm3Parser.GlobalStatementContext(self, self._ctx, self.state)
        self.enterRule(localctx, 10, self.RULE_globalStatement)
        try:
            self.state = 215
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [qasm3Parser.T__75]:
                self.enterOuterAlt(localctx, 1)
                self.state = 211
                self.subroutineDefinition()
                pass
            elif token in [qasm3Parser.T__74]:
                self.enterOuterAlt(localctx, 2)
                self.state = 212
                self.kernelDeclaration()
                pass
            elif token in [qasm3Parser.T__15]:
                self.enterOuterAlt(localctx, 3)
                self.state = 213
                self.quantumGateDefinition()
                pass
            elif token in [qasm3Parser.T__90]:
                self.enterOuterAlt(localctx, 4)
                self.state = 214
                self.calibrationDefinition()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class DeclarationStatementContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def SEMICOLON(self):
            return self.getToken(qasm3Parser.SEMICOLON, 0)

        def quantumDeclaration(self):
            return self.getTypedRuleContext(qasm3Parser.QuantumDeclarationContext,0)


        def classicalDeclaration(self):
            return self.getTypedRuleContext(qasm3Parser.ClassicalDeclarationContext,0)


        def constantDeclaration(self):
            return self.getTypedRuleContext(qasm3Parser.ConstantDeclarationContext,0)


        def getRuleIndex(self):
            return qasm3Parser.RULE_declarationStatement

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterDeclarationStatement" ):
                listener.enterDeclarationStatement(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitDeclarationStatement" ):
                listener.exitDeclarationStatement(self)




    def declarationStatement(self):

        localctx = qasm3Parser.DeclarationStatementContext(self, self._ctx, self.state)
        self.enterRule(localctx, 12, self.RULE_declarationStatement)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 220
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [qasm3Parser.T__2, qasm3Parser.T__3]:
                self.state = 217
                self.quantumDeclaration()
                pass
            elif token in [qasm3Parser.T__6, qasm3Parser.T__7, qasm3Parser.T__8, qasm3Parser.T__9, qasm3Parser.T__10, qasm3Parser.T__11, qasm3Parser.T__82, qasm3Parser.T__83]:
                self.state = 218
                self.classicalDeclaration()
                pass
            elif token in [qasm3Parser.T__12]:
                self.state = 219
                self.constantDeclaration()
                pass
            else:
                raise NoViableAltException(self)

            self.state = 222
            self.match(qasm3Parser.SEMICOLON)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class CommentContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def LineComment(self):
            return self.getToken(qasm3Parser.LineComment, 0)

        def BlockComment(self):
            return self.getToken(qasm3Parser.BlockComment, 0)

        def getRuleIndex(self):
            return qasm3Parser.RULE_comment

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterComment" ):
                listener.enterComment(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitComment" ):
                listener.exitComment(self)




    def comment(self):

        localctx = qasm3Parser.CommentContext(self, self._ctx, self.state)
        self.enterRule(localctx, 14, self.RULE_comment)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 224
            _la = self._input.LA(1)
            if not(_la==qasm3Parser.LineComment or _la==qasm3Parser.BlockComment):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ReturnSignatureContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def ARROW(self):
            return self.getToken(qasm3Parser.ARROW, 0)

        def classicalDeclaration(self):
            return self.getTypedRuleContext(qasm3Parser.ClassicalDeclarationContext,0)


        def getRuleIndex(self):
            return qasm3Parser.RULE_returnSignature

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterReturnSignature" ):
                listener.enterReturnSignature(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitReturnSignature" ):
                listener.exitReturnSignature(self)




    def returnSignature(self):

        localctx = qasm3Parser.ReturnSignatureContext(self, self._ctx, self.state)
        self.enterRule(localctx, 16, self.RULE_returnSignature)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 226
            self.match(qasm3Parser.ARROW)
            self.state = 227
            self.classicalDeclaration()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ProgramBlockContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def LBRACE(self):
            return self.getToken(qasm3Parser.LBRACE, 0)

        def RBRACE(self):
            return self.getToken(qasm3Parser.RBRACE, 0)

        def programBlock(self):
            return self.getTypedRuleContext(qasm3Parser.ProgramBlockContext,0)


        def statement(self):
            return self.getTypedRuleContext(qasm3Parser.StatementContext,0)


        def getRuleIndex(self):
            return qasm3Parser.RULE_programBlock

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterProgramBlock" ):
                listener.enterProgramBlock(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitProgramBlock" ):
                listener.exitProgramBlock(self)




    def programBlock(self):

        localctx = qasm3Parser.ProgramBlockContext(self, self._ctx, self.state)
        self.enterRule(localctx, 18, self.RULE_programBlock)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 229
            self.match(qasm3Parser.LBRACE)
            self.state = 232
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [qasm3Parser.LBRACE]:
                self.state = 230
                self.programBlock()
                pass
            elif token in [qasm3Parser.T__2, qasm3Parser.T__3, qasm3Parser.T__4, qasm3Parser.T__5, qasm3Parser.T__6, qasm3Parser.T__7, qasm3Parser.T__8, qasm3Parser.T__9, qasm3Parser.T__10, qasm3Parser.T__11, qasm3Parser.T__12, qasm3Parser.T__13, qasm3Parser.T__15, qasm3Parser.T__16, qasm3Parser.T__17, qasm3Parser.T__18, qasm3Parser.T__19, qasm3Parser.T__20, qasm3Parser.T__22, qasm3Parser.T__23, qasm3Parser.T__24, qasm3Parser.T__25, qasm3Parser.T__26, qasm3Parser.T__45, qasm3Parser.T__46, qasm3Parser.T__47, qasm3Parser.T__48, qasm3Parser.T__49, qasm3Parser.T__50, qasm3Parser.T__51, qasm3Parser.T__52, qasm3Parser.T__53, qasm3Parser.T__67, qasm3Parser.T__69, qasm3Parser.T__70, qasm3Parser.T__71, qasm3Parser.T__72, qasm3Parser.T__73, qasm3Parser.T__74, qasm3Parser.T__75, qasm3Parser.T__76, qasm3Parser.T__82, qasm3Parser.T__83, qasm3Parser.T__84, qasm3Parser.T__85, qasm3Parser.T__86, qasm3Parser.T__87, qasm3Parser.T__88, qasm3Parser.T__90, qasm3Parser.Constant, qasm3Parser.Integer, qasm3Parser.RealNumber, qasm3Parser.Identifier, qasm3Parser.LineComment, qasm3Parser.BlockComment]:
                self.state = 231
                self.statement()
                pass
            else:
                raise NoViableAltException(self)

            self.state = 234
            self.match(qasm3Parser.RBRACE)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class DesignatorContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def LBRACKET(self):
            return self.getToken(qasm3Parser.LBRACKET, 0)

        def expression(self):
            return self.getTypedRuleContext(qasm3Parser.ExpressionContext,0)


        def RBRACKET(self):
            return self.getToken(qasm3Parser.RBRACKET, 0)

        def getRuleIndex(self):
            return qasm3Parser.RULE_designator

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterDesignator" ):
                listener.enterDesignator(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitDesignator" ):
                listener.exitDesignator(self)




    def designator(self):

        localctx = qasm3Parser.DesignatorContext(self, self._ctx, self.state)
        self.enterRule(localctx, 20, self.RULE_designator)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 236
            self.match(qasm3Parser.LBRACKET)
            self.state = 237
            self.expression(0)
            self.state = 238
            self.match(qasm3Parser.RBRACKET)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class DoubleDesignatorContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def LBRACKET(self):
            return self.getToken(qasm3Parser.LBRACKET, 0)

        def expression(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(qasm3Parser.ExpressionContext)
            else:
                return self.getTypedRuleContext(qasm3Parser.ExpressionContext,i)


        def COMMA(self):
            return self.getToken(qasm3Parser.COMMA, 0)

        def RBRACKET(self):
            return self.getToken(qasm3Parser.RBRACKET, 0)

        def getRuleIndex(self):
            return qasm3Parser.RULE_doubleDesignator

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterDoubleDesignator" ):
                listener.enterDoubleDesignator(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitDoubleDesignator" ):
                listener.exitDoubleDesignator(self)




    def doubleDesignator(self):

        localctx = qasm3Parser.DoubleDesignatorContext(self, self._ctx, self.state)
        self.enterRule(localctx, 22, self.RULE_doubleDesignator)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 240
            self.match(qasm3Parser.LBRACKET)
            self.state = 241
            self.expression(0)
            self.state = 242
            self.match(qasm3Parser.COMMA)
            self.state = 243
            self.expression(0)
            self.state = 244
            self.match(qasm3Parser.RBRACKET)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class IdentifierListContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def Identifier(self, i:int=None):
            if i is None:
                return self.getTokens(qasm3Parser.Identifier)
            else:
                return self.getToken(qasm3Parser.Identifier, i)

        def COMMA(self, i:int=None):
            if i is None:
                return self.getTokens(qasm3Parser.COMMA)
            else:
                return self.getToken(qasm3Parser.COMMA, i)

        def getRuleIndex(self):
            return qasm3Parser.RULE_identifierList

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterIdentifierList" ):
                listener.enterIdentifierList(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitIdentifierList" ):
                listener.exitIdentifierList(self)




    def identifierList(self):

        localctx = qasm3Parser.IdentifierListContext(self, self._ctx, self.state)
        self.enterRule(localctx, 24, self.RULE_identifierList)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 250
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,8,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 246
                    self.match(qasm3Parser.Identifier)
                    self.state = 247
                    self.match(qasm3Parser.COMMA) 
                self.state = 252
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,8,self._ctx)

            self.state = 253
            self.match(qasm3Parser.Identifier)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class IndexIdentifierContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def Identifier(self):
            return self.getToken(qasm3Parser.Identifier, 0)

        def designator(self):
            return self.getTypedRuleContext(qasm3Parser.DesignatorContext,0)


        def getRuleIndex(self):
            return qasm3Parser.RULE_indexIdentifier

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterIndexIdentifier" ):
                listener.enterIndexIdentifier(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitIndexIdentifier" ):
                listener.exitIndexIdentifier(self)




    def indexIdentifier(self):

        localctx = qasm3Parser.IndexIdentifierContext(self, self._ctx, self.state)
        self.enterRule(localctx, 26, self.RULE_indexIdentifier)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 255
            self.match(qasm3Parser.Identifier)
            self.state = 257
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,9,self._ctx)
            if la_ == 1:
                self.state = 256
                self.designator()


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class IndexIdentifierListContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def indexIdentifier(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(qasm3Parser.IndexIdentifierContext)
            else:
                return self.getTypedRuleContext(qasm3Parser.IndexIdentifierContext,i)


        def COMMA(self, i:int=None):
            if i is None:
                return self.getTokens(qasm3Parser.COMMA)
            else:
                return self.getToken(qasm3Parser.COMMA, i)

        def getRuleIndex(self):
            return qasm3Parser.RULE_indexIdentifierList

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterIndexIdentifierList" ):
                listener.enterIndexIdentifierList(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitIndexIdentifierList" ):
                listener.exitIndexIdentifierList(self)




    def indexIdentifierList(self):

        localctx = qasm3Parser.IndexIdentifierListContext(self, self._ctx, self.state)
        self.enterRule(localctx, 28, self.RULE_indexIdentifierList)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 264
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,10,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 259
                    self.indexIdentifier()
                    self.state = 260
                    self.match(qasm3Parser.COMMA) 
                self.state = 266
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,10,self._ctx)

            self.state = 267
            self.indexIdentifier()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class AssociationContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def COLON(self):
            return self.getToken(qasm3Parser.COLON, 0)

        def Identifier(self):
            return self.getToken(qasm3Parser.Identifier, 0)

        def getRuleIndex(self):
            return qasm3Parser.RULE_association

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterAssociation" ):
                listener.enterAssociation(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitAssociation" ):
                listener.exitAssociation(self)




    def association(self):

        localctx = qasm3Parser.AssociationContext(self, self._ctx, self.state)
        self.enterRule(localctx, 30, self.RULE_association)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 269
            self.match(qasm3Parser.COLON)
            self.state = 270
            self.match(qasm3Parser.Identifier)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class QuantumTypeContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return qasm3Parser.RULE_quantumType

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterQuantumType" ):
                listener.enterQuantumType(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitQuantumType" ):
                listener.exitQuantumType(self)




    def quantumType(self):

        localctx = qasm3Parser.QuantumTypeContext(self, self._ctx, self.state)
        self.enterRule(localctx, 32, self.RULE_quantumType)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 272
            _la = self._input.LA(1)
            if not(_la==qasm3Parser.T__2 or _la==qasm3Parser.T__3):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class QuantumDeclarationContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def quantumType(self):
            return self.getTypedRuleContext(qasm3Parser.QuantumTypeContext,0)


        def Identifier(self):
            return self.getToken(qasm3Parser.Identifier, 0)

        def designator(self):
            return self.getTypedRuleContext(qasm3Parser.DesignatorContext,0)


        def getRuleIndex(self):
            return qasm3Parser.RULE_quantumDeclaration

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterQuantumDeclaration" ):
                listener.enterQuantumDeclaration(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitQuantumDeclaration" ):
                listener.exitQuantumDeclaration(self)




    def quantumDeclaration(self):

        localctx = qasm3Parser.QuantumDeclarationContext(self, self._ctx, self.state)
        self.enterRule(localctx, 34, self.RULE_quantumDeclaration)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 274
            self.quantumType()
            self.state = 275
            self.match(qasm3Parser.Identifier)
            self.state = 276
            self.designator()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class QuantumArgumentContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def quantumType(self):
            return self.getTypedRuleContext(qasm3Parser.QuantumTypeContext,0)


        def association(self):
            return self.getTypedRuleContext(qasm3Parser.AssociationContext,0)


        def designator(self):
            return self.getTypedRuleContext(qasm3Parser.DesignatorContext,0)


        def getRuleIndex(self):
            return qasm3Parser.RULE_quantumArgument

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterQuantumArgument" ):
                listener.enterQuantumArgument(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitQuantumArgument" ):
                listener.exitQuantumArgument(self)




    def quantumArgument(self):

        localctx = qasm3Parser.QuantumArgumentContext(self, self._ctx, self.state)
        self.enterRule(localctx, 36, self.RULE_quantumArgument)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 278
            self.quantumType()
            self.state = 280
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==qasm3Parser.LBRACKET:
                self.state = 279
                self.designator()


            self.state = 282
            self.association()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class QuantumArgumentListContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def quantumArgument(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(qasm3Parser.QuantumArgumentContext)
            else:
                return self.getTypedRuleContext(qasm3Parser.QuantumArgumentContext,i)


        def COMMA(self, i:int=None):
            if i is None:
                return self.getTokens(qasm3Parser.COMMA)
            else:
                return self.getToken(qasm3Parser.COMMA, i)

        def getRuleIndex(self):
            return qasm3Parser.RULE_quantumArgumentList

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterQuantumArgumentList" ):
                listener.enterQuantumArgumentList(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitQuantumArgumentList" ):
                listener.exitQuantumArgumentList(self)




    def quantumArgumentList(self):

        localctx = qasm3Parser.QuantumArgumentListContext(self, self._ctx, self.state)
        self.enterRule(localctx, 38, self.RULE_quantumArgumentList)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 289
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,12,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 284
                    self.quantumArgument()
                    self.state = 285
                    self.match(qasm3Parser.COMMA) 
                self.state = 291
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,12,self._ctx)

            self.state = 292
            self.quantumArgument()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class BitTypeContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return qasm3Parser.RULE_bitType

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterBitType" ):
                listener.enterBitType(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitBitType" ):
                listener.exitBitType(self)




    def bitType(self):

        localctx = qasm3Parser.BitTypeContext(self, self._ctx, self.state)
        self.enterRule(localctx, 40, self.RULE_bitType)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 294
            _la = self._input.LA(1)
            if not(_la==qasm3Parser.T__4 or _la==qasm3Parser.T__5):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class SingleDesignatorTypeContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return qasm3Parser.RULE_singleDesignatorType

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterSingleDesignatorType" ):
                listener.enterSingleDesignatorType(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitSingleDesignatorType" ):
                listener.exitSingleDesignatorType(self)




    def singleDesignatorType(self):

        localctx = qasm3Parser.SingleDesignatorTypeContext(self, self._ctx, self.state)
        self.enterRule(localctx, 42, self.RULE_singleDesignatorType)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 296
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & ((1 << qasm3Parser.T__6) | (1 << qasm3Parser.T__7) | (1 << qasm3Parser.T__8) | (1 << qasm3Parser.T__9))) != 0)):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class DoubleDesignatorTypeContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return qasm3Parser.RULE_doubleDesignatorType

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterDoubleDesignatorType" ):
                listener.enterDoubleDesignatorType(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitDoubleDesignatorType" ):
                listener.exitDoubleDesignatorType(self)




    def doubleDesignatorType(self):

        localctx = qasm3Parser.DoubleDesignatorTypeContext(self, self._ctx, self.state)
        self.enterRule(localctx, 44, self.RULE_doubleDesignatorType)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 298
            self.match(qasm3Parser.T__10)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class NoDesignatorTypeContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def timingType(self):
            return self.getTypedRuleContext(qasm3Parser.TimingTypeContext,0)


        def getRuleIndex(self):
            return qasm3Parser.RULE_noDesignatorType

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterNoDesignatorType" ):
                listener.enterNoDesignatorType(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitNoDesignatorType" ):
                listener.exitNoDesignatorType(self)




    def noDesignatorType(self):

        localctx = qasm3Parser.NoDesignatorTypeContext(self, self._ctx, self.state)
        self.enterRule(localctx, 46, self.RULE_noDesignatorType)
        try:
            self.state = 302
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [qasm3Parser.T__11]:
                self.enterOuterAlt(localctx, 1)
                self.state = 300
                self.match(qasm3Parser.T__11)
                pass
            elif token in [qasm3Parser.T__82, qasm3Parser.T__83]:
                self.enterOuterAlt(localctx, 2)
                self.state = 301
                self.timingType()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ClassicalTypeContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def singleDesignatorType(self):
            return self.getTypedRuleContext(qasm3Parser.SingleDesignatorTypeContext,0)


        def designator(self):
            return self.getTypedRuleContext(qasm3Parser.DesignatorContext,0)


        def doubleDesignatorType(self):
            return self.getTypedRuleContext(qasm3Parser.DoubleDesignatorTypeContext,0)


        def doubleDesignator(self):
            return self.getTypedRuleContext(qasm3Parser.DoubleDesignatorContext,0)


        def noDesignatorType(self):
            return self.getTypedRuleContext(qasm3Parser.NoDesignatorTypeContext,0)


        def bitType(self):
            return self.getTypedRuleContext(qasm3Parser.BitTypeContext,0)


        def getRuleIndex(self):
            return qasm3Parser.RULE_classicalType

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterClassicalType" ):
                listener.enterClassicalType(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitClassicalType" ):
                listener.exitClassicalType(self)




    def classicalType(self):

        localctx = qasm3Parser.ClassicalTypeContext(self, self._ctx, self.state)
        self.enterRule(localctx, 48, self.RULE_classicalType)
        self._la = 0 # Token type
        try:
            self.state = 317
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [qasm3Parser.T__6, qasm3Parser.T__7, qasm3Parser.T__8, qasm3Parser.T__9]:
                self.enterOuterAlt(localctx, 1)
                self.state = 304
                self.singleDesignatorType()
                self.state = 306
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==qasm3Parser.LBRACKET:
                    self.state = 305
                    self.designator()


                pass
            elif token in [qasm3Parser.T__10]:
                self.enterOuterAlt(localctx, 2)
                self.state = 308
                self.doubleDesignatorType()
                self.state = 310
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==qasm3Parser.LBRACKET:
                    self.state = 309
                    self.doubleDesignator()


                pass
            elif token in [qasm3Parser.T__11, qasm3Parser.T__82, qasm3Parser.T__83]:
                self.enterOuterAlt(localctx, 3)
                self.state = 312
                self.noDesignatorType()
                pass
            elif token in [qasm3Parser.T__4, qasm3Parser.T__5]:
                self.enterOuterAlt(localctx, 4)
                self.state = 313
                self.bitType()
                self.state = 315
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==qasm3Parser.LBRACKET:
                    self.state = 314
                    self.designator()


                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ConstantDeclarationContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def Identifier(self):
            return self.getToken(qasm3Parser.Identifier, 0)

        def ASSIGN(self):
            return self.getToken(qasm3Parser.ASSIGN, 0)

        def expression(self):
            return self.getTypedRuleContext(qasm3Parser.ExpressionContext,0)


        def getRuleIndex(self):
            return qasm3Parser.RULE_constantDeclaration

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterConstantDeclaration" ):
                listener.enterConstantDeclaration(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitConstantDeclaration" ):
                listener.exitConstantDeclaration(self)




    def constantDeclaration(self):

        localctx = qasm3Parser.ConstantDeclarationContext(self, self._ctx, self.state)
        self.enterRule(localctx, 50, self.RULE_constantDeclaration)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 319
            self.match(qasm3Parser.T__12)
            self.state = 320
            self.match(qasm3Parser.Identifier)
            self.state = 321
            self.match(qasm3Parser.ASSIGN)
            self.state = 322
            self.expression(0)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class SingleDesignatorDeclarationContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def singleDesignatorType(self):
            return self.getTypedRuleContext(qasm3Parser.SingleDesignatorTypeContext,0)


        def designator(self):
            return self.getTypedRuleContext(qasm3Parser.DesignatorContext,0)


        def Identifier(self):
            return self.getToken(qasm3Parser.Identifier, 0)

        def getRuleIndex(self):
            return qasm3Parser.RULE_singleDesignatorDeclaration

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterSingleDesignatorDeclaration" ):
                listener.enterSingleDesignatorDeclaration(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitSingleDesignatorDeclaration" ):
                listener.exitSingleDesignatorDeclaration(self)




    def singleDesignatorDeclaration(self):

        localctx = qasm3Parser.SingleDesignatorDeclarationContext(self, self._ctx, self.state)
        self.enterRule(localctx, 52, self.RULE_singleDesignatorDeclaration)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 324
            self.singleDesignatorType()
            self.state = 325
            self.designator()
            self.state = 326
            self.match(qasm3Parser.Identifier)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class DoubleDesignatorDeclarationContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def doubleDesignatorType(self):
            return self.getTypedRuleContext(qasm3Parser.DoubleDesignatorTypeContext,0)


        def doubleDesignator(self):
            return self.getTypedRuleContext(qasm3Parser.DoubleDesignatorContext,0)


        def Identifier(self):
            return self.getToken(qasm3Parser.Identifier, 0)

        def getRuleIndex(self):
            return qasm3Parser.RULE_doubleDesignatorDeclaration

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterDoubleDesignatorDeclaration" ):
                listener.enterDoubleDesignatorDeclaration(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitDoubleDesignatorDeclaration" ):
                listener.exitDoubleDesignatorDeclaration(self)




    def doubleDesignatorDeclaration(self):

        localctx = qasm3Parser.DoubleDesignatorDeclarationContext(self, self._ctx, self.state)
        self.enterRule(localctx, 54, self.RULE_doubleDesignatorDeclaration)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 328
            self.doubleDesignatorType()
            self.state = 329
            self.doubleDesignator()
            self.state = 330
            self.match(qasm3Parser.Identifier)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class NoDesignatorDeclarationContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def noDesignatorType(self):
            return self.getTypedRuleContext(qasm3Parser.NoDesignatorTypeContext,0)


        def Identifier(self):
            return self.getToken(qasm3Parser.Identifier, 0)

        def getRuleIndex(self):
            return qasm3Parser.RULE_noDesignatorDeclaration

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterNoDesignatorDeclaration" ):
                listener.enterNoDesignatorDeclaration(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitNoDesignatorDeclaration" ):
                listener.exitNoDesignatorDeclaration(self)




    def noDesignatorDeclaration(self):

        localctx = qasm3Parser.NoDesignatorDeclarationContext(self, self._ctx, self.state)
        self.enterRule(localctx, 56, self.RULE_noDesignatorDeclaration)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 332
            self.noDesignatorType()
            self.state = 333
            self.match(qasm3Parser.Identifier)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ClassicalVariableDeclarationContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def singleDesignatorDeclaration(self):
            return self.getTypedRuleContext(qasm3Parser.SingleDesignatorDeclarationContext,0)


        def doubleDesignatorDeclaration(self):
            return self.getTypedRuleContext(qasm3Parser.DoubleDesignatorDeclarationContext,0)


        def noDesignatorDeclaration(self):
            return self.getTypedRuleContext(qasm3Parser.NoDesignatorDeclarationContext,0)


        def getRuleIndex(self):
            return qasm3Parser.RULE_classicalVariableDeclaration

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterClassicalVariableDeclaration" ):
                listener.enterClassicalVariableDeclaration(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitClassicalVariableDeclaration" ):
                listener.exitClassicalVariableDeclaration(self)




    def classicalVariableDeclaration(self):

        localctx = qasm3Parser.ClassicalVariableDeclarationContext(self, self._ctx, self.state)
        self.enterRule(localctx, 58, self.RULE_classicalVariableDeclaration)
        try:
            self.state = 338
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [qasm3Parser.T__6, qasm3Parser.T__7, qasm3Parser.T__8, qasm3Parser.T__9]:
                self.enterOuterAlt(localctx, 1)
                self.state = 335
                self.singleDesignatorDeclaration()
                pass
            elif token in [qasm3Parser.T__10]:
                self.enterOuterAlt(localctx, 2)
                self.state = 336
                self.doubleDesignatorDeclaration()
                pass
            elif token in [qasm3Parser.T__11, qasm3Parser.T__82, qasm3Parser.T__83]:
                self.enterOuterAlt(localctx, 3)
                self.state = 337
                self.noDesignatorDeclaration()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ClassicalDeclarationContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def classicalVariableDeclaration(self):
            return self.getTypedRuleContext(qasm3Parser.ClassicalVariableDeclarationContext,0)


        def assignmentExpression(self):
            return self.getTypedRuleContext(qasm3Parser.AssignmentExpressionContext,0)


        def getRuleIndex(self):
            return qasm3Parser.RULE_classicalDeclaration

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterClassicalDeclaration" ):
                listener.enterClassicalDeclaration(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitClassicalDeclaration" ):
                listener.exitClassicalDeclaration(self)




    def classicalDeclaration(self):

        localctx = qasm3Parser.ClassicalDeclarationContext(self, self._ctx, self.state)
        self.enterRule(localctx, 60, self.RULE_classicalDeclaration)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 340
            self.classicalVariableDeclaration()
            self.state = 342
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if ((((_la - 57)) & ~0x3f) == 0 and ((1 << (_la - 57)) & ((1 << (qasm3Parser.T__56 - 57)) | (1 << (qasm3Parser.T__57 - 57)) | (1 << (qasm3Parser.T__58 - 57)) | (1 << (qasm3Parser.T__59 - 57)) | (1 << (qasm3Parser.T__60 - 57)) | (1 << (qasm3Parser.T__61 - 57)) | (1 << (qasm3Parser.T__62 - 57)) | (1 << (qasm3Parser.T__63 - 57)) | (1 << (qasm3Parser.T__64 - 57)) | (1 << (qasm3Parser.T__65 - 57)) | (1 << (qasm3Parser.ASSIGN - 57)) | (1 << (qasm3Parser.ARROW - 57)))) != 0):
                self.state = 341
                self.assignmentExpression()


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ClassicalTypeListContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def classicalType(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(qasm3Parser.ClassicalTypeContext)
            else:
                return self.getTypedRuleContext(qasm3Parser.ClassicalTypeContext,i)


        def COMMA(self, i:int=None):
            if i is None:
                return self.getTokens(qasm3Parser.COMMA)
            else:
                return self.getToken(qasm3Parser.COMMA, i)

        def getRuleIndex(self):
            return qasm3Parser.RULE_classicalTypeList

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterClassicalTypeList" ):
                listener.enterClassicalTypeList(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitClassicalTypeList" ):
                listener.exitClassicalTypeList(self)




    def classicalTypeList(self):

        localctx = qasm3Parser.ClassicalTypeListContext(self, self._ctx, self.state)
        self.enterRule(localctx, 62, self.RULE_classicalTypeList)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 349
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,20,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 344
                    self.classicalType()
                    self.state = 345
                    self.match(qasm3Parser.COMMA) 
                self.state = 351
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,20,self._ctx)

            self.state = 352
            self.classicalType()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ClassicalArgumentContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def classicalType(self):
            return self.getTypedRuleContext(qasm3Parser.ClassicalTypeContext,0)


        def association(self):
            return self.getTypedRuleContext(qasm3Parser.AssociationContext,0)


        def getRuleIndex(self):
            return qasm3Parser.RULE_classicalArgument

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterClassicalArgument" ):
                listener.enterClassicalArgument(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitClassicalArgument" ):
                listener.exitClassicalArgument(self)




    def classicalArgument(self):

        localctx = qasm3Parser.ClassicalArgumentContext(self, self._ctx, self.state)
        self.enterRule(localctx, 64, self.RULE_classicalArgument)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 354
            self.classicalType()
            self.state = 355
            self.association()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ClassicalArgumentListContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def classicalArgument(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(qasm3Parser.ClassicalArgumentContext)
            else:
                return self.getTypedRuleContext(qasm3Parser.ClassicalArgumentContext,i)


        def COMMA(self, i:int=None):
            if i is None:
                return self.getTokens(qasm3Parser.COMMA)
            else:
                return self.getToken(qasm3Parser.COMMA, i)

        def getRuleIndex(self):
            return qasm3Parser.RULE_classicalArgumentList

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterClassicalArgumentList" ):
                listener.enterClassicalArgumentList(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitClassicalArgumentList" ):
                listener.exitClassicalArgumentList(self)




    def classicalArgumentList(self):

        localctx = qasm3Parser.ClassicalArgumentListContext(self, self._ctx, self.state)
        self.enterRule(localctx, 66, self.RULE_classicalArgumentList)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 362
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,21,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 357
                    self.classicalArgument()
                    self.state = 358
                    self.match(qasm3Parser.COMMA) 
                self.state = 364
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,21,self._ctx)

            self.state = 365
            self.classicalArgument()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class AliasStatementContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def Identifier(self):
            return self.getToken(qasm3Parser.Identifier, 0)

        def ASSIGN(self):
            return self.getToken(qasm3Parser.ASSIGN, 0)

        def concatenateExpression(self):
            return self.getTypedRuleContext(qasm3Parser.ConcatenateExpressionContext,0)


        def getRuleIndex(self):
            return qasm3Parser.RULE_aliasStatement

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterAliasStatement" ):
                listener.enterAliasStatement(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitAliasStatement" ):
                listener.exitAliasStatement(self)




    def aliasStatement(self):

        localctx = qasm3Parser.AliasStatementContext(self, self._ctx, self.state)
        self.enterRule(localctx, 68, self.RULE_aliasStatement)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 367
            self.match(qasm3Parser.T__13)
            self.state = 368
            self.match(qasm3Parser.Identifier)
            self.state = 369
            self.match(qasm3Parser.ASSIGN)
            self.state = 370
            self.concatenateExpression()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ConcatenateExpressionContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def ASSIGN(self):
            return self.getToken(qasm3Parser.ASSIGN, 0)

        def Identifier(self, i:int=None):
            if i is None:
                return self.getTokens(qasm3Parser.Identifier)
            else:
                return self.getToken(qasm3Parser.Identifier, i)

        def rangeDefinition(self):
            return self.getTypedRuleContext(qasm3Parser.RangeDefinitionContext,0)


        def LBRACKET(self):
            return self.getToken(qasm3Parser.LBRACKET, 0)

        def expressionList(self):
            return self.getTypedRuleContext(qasm3Parser.ExpressionListContext,0)


        def RBRACKET(self):
            return self.getToken(qasm3Parser.RBRACKET, 0)

        def getRuleIndex(self):
            return qasm3Parser.RULE_concatenateExpression

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterConcatenateExpression" ):
                listener.enterConcatenateExpression(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitConcatenateExpression" ):
                listener.exitConcatenateExpression(self)




    def concatenateExpression(self):

        localctx = qasm3Parser.ConcatenateExpressionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 70, self.RULE_concatenateExpression)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 372
            self.match(qasm3Parser.ASSIGN)
            self.state = 383
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,22,self._ctx)
            if la_ == 1:
                self.state = 373
                self.match(qasm3Parser.Identifier)
                self.state = 374
                self.rangeDefinition()
                pass

            elif la_ == 2:
                self.state = 375
                self.match(qasm3Parser.Identifier)
                self.state = 376
                self.match(qasm3Parser.T__14)
                self.state = 377
                self.match(qasm3Parser.Identifier)
                pass

            elif la_ == 3:
                self.state = 378
                self.match(qasm3Parser.Identifier)
                self.state = 379
                self.match(qasm3Parser.LBRACKET)
                self.state = 380
                self.expressionList()
                self.state = 381
                self.match(qasm3Parser.RBRACKET)
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class RangeDefinitionContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def LBRACKET(self):
            return self.getToken(qasm3Parser.LBRACKET, 0)

        def COLON(self, i:int=None):
            if i is None:
                return self.getTokens(qasm3Parser.COLON)
            else:
                return self.getToken(qasm3Parser.COLON, i)

        def RBRACKET(self):
            return self.getToken(qasm3Parser.RBRACKET, 0)

        def expression(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(qasm3Parser.ExpressionContext)
            else:
                return self.getTypedRuleContext(qasm3Parser.ExpressionContext,i)


        def getRuleIndex(self):
            return qasm3Parser.RULE_rangeDefinition

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterRangeDefinition" ):
                listener.enterRangeDefinition(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitRangeDefinition" ):
                listener.exitRangeDefinition(self)




    def rangeDefinition(self):

        localctx = qasm3Parser.RangeDefinitionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 72, self.RULE_rangeDefinition)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 385
            self.match(qasm3Parser.LBRACKET)
            self.state = 387
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if (((_la) & ~0x3f) == 0 and ((1 << _la) & ((1 << qasm3Parser.T__4) | (1 << qasm3Parser.T__5) | (1 << qasm3Parser.T__6) | (1 << qasm3Parser.T__7) | (1 << qasm3Parser.T__8) | (1 << qasm3Parser.T__9) | (1 << qasm3Parser.T__10) | (1 << qasm3Parser.T__11) | (1 << qasm3Parser.T__16) | (1 << qasm3Parser.T__25) | (1 << qasm3Parser.T__26) | (1 << qasm3Parser.T__46) | (1 << qasm3Parser.T__47) | (1 << qasm3Parser.T__48) | (1 << qasm3Parser.T__49) | (1 << qasm3Parser.T__50) | (1 << qasm3Parser.T__51) | (1 << qasm3Parser.T__52) | (1 << qasm3Parser.T__53))) != 0) or ((((_la - 83)) & ~0x3f) == 0 and ((1 << (_la - 83)) & ((1 << (qasm3Parser.T__82 - 83)) | (1 << (qasm3Parser.T__83 - 83)) | (1 << (qasm3Parser.T__86 - 83)) | (1 << (qasm3Parser.Constant - 83)) | (1 << (qasm3Parser.Integer - 83)) | (1 << (qasm3Parser.RealNumber - 83)) | (1 << (qasm3Parser.Identifier - 83)))) != 0):
                self.state = 386
                self.expression(0)


            self.state = 389
            self.match(qasm3Parser.COLON)
            self.state = 391
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if (((_la) & ~0x3f) == 0 and ((1 << _la) & ((1 << qasm3Parser.T__4) | (1 << qasm3Parser.T__5) | (1 << qasm3Parser.T__6) | (1 << qasm3Parser.T__7) | (1 << qasm3Parser.T__8) | (1 << qasm3Parser.T__9) | (1 << qasm3Parser.T__10) | (1 << qasm3Parser.T__11) | (1 << qasm3Parser.T__16) | (1 << qasm3Parser.T__25) | (1 << qasm3Parser.T__26) | (1 << qasm3Parser.T__46) | (1 << qasm3Parser.T__47) | (1 << qasm3Parser.T__48) | (1 << qasm3Parser.T__49) | (1 << qasm3Parser.T__50) | (1 << qasm3Parser.T__51) | (1 << qasm3Parser.T__52) | (1 << qasm3Parser.T__53))) != 0) or ((((_la - 83)) & ~0x3f) == 0 and ((1 << (_la - 83)) & ((1 << (qasm3Parser.T__82 - 83)) | (1 << (qasm3Parser.T__83 - 83)) | (1 << (qasm3Parser.T__86 - 83)) | (1 << (qasm3Parser.Constant - 83)) | (1 << (qasm3Parser.Integer - 83)) | (1 << (qasm3Parser.RealNumber - 83)) | (1 << (qasm3Parser.Identifier - 83)))) != 0):
                self.state = 390
                self.expression(0)


            self.state = 395
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==qasm3Parser.COLON:
                self.state = 393
                self.match(qasm3Parser.COLON)
                self.state = 394
                self.expression(0)


            self.state = 397
            self.match(qasm3Parser.RBRACKET)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class QuantumGateDefinitionContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def quantumGateSignature(self):
            return self.getTypedRuleContext(qasm3Parser.QuantumGateSignatureContext,0)


        def quantumBlock(self):
            return self.getTypedRuleContext(qasm3Parser.QuantumBlockContext,0)


        def getRuleIndex(self):
            return qasm3Parser.RULE_quantumGateDefinition

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterQuantumGateDefinition" ):
                listener.enterQuantumGateDefinition(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitQuantumGateDefinition" ):
                listener.exitQuantumGateDefinition(self)




    def quantumGateDefinition(self):

        localctx = qasm3Parser.QuantumGateDefinitionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 74, self.RULE_quantumGateDefinition)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 399
            self.match(qasm3Parser.T__15)
            self.state = 400
            self.quantumGateSignature()
            self.state = 401
            self.quantumBlock()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class QuantumGateSignatureContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def Identifier(self):
            return self.getToken(qasm3Parser.Identifier, 0)

        def identifierList(self):
            return self.getTypedRuleContext(qasm3Parser.IdentifierListContext,0)


        def LPAREN(self):
            return self.getToken(qasm3Parser.LPAREN, 0)

        def RPAREN(self):
            return self.getToken(qasm3Parser.RPAREN, 0)

        def classicalArgumentList(self):
            return self.getTypedRuleContext(qasm3Parser.ClassicalArgumentListContext,0)


        def getRuleIndex(self):
            return qasm3Parser.RULE_quantumGateSignature

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterQuantumGateSignature" ):
                listener.enterQuantumGateSignature(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitQuantumGateSignature" ):
                listener.exitQuantumGateSignature(self)




    def quantumGateSignature(self):

        localctx = qasm3Parser.QuantumGateSignatureContext(self, self._ctx, self.state)
        self.enterRule(localctx, 76, self.RULE_quantumGateSignature)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 403
            self.match(qasm3Parser.Identifier)
            self.state = 409
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==qasm3Parser.LPAREN:
                self.state = 404
                self.match(qasm3Parser.LPAREN)
                self.state = 406
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if (((_la) & ~0x3f) == 0 and ((1 << _la) & ((1 << qasm3Parser.T__4) | (1 << qasm3Parser.T__5) | (1 << qasm3Parser.T__6) | (1 << qasm3Parser.T__7) | (1 << qasm3Parser.T__8) | (1 << qasm3Parser.T__9) | (1 << qasm3Parser.T__10) | (1 << qasm3Parser.T__11))) != 0) or _la==qasm3Parser.T__82 or _la==qasm3Parser.T__83:
                    self.state = 405
                    self.classicalArgumentList()


                self.state = 408
                self.match(qasm3Parser.RPAREN)


            self.state = 411
            self.identifierList()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class QuantumBlockContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def LBRACE(self):
            return self.getToken(qasm3Parser.LBRACE, 0)

        def RBRACE(self):
            return self.getToken(qasm3Parser.RBRACE, 0)

        def quantumBlock(self):
            return self.getTypedRuleContext(qasm3Parser.QuantumBlockContext,0)


        def quantumStatement(self):
            return self.getTypedRuleContext(qasm3Parser.QuantumStatementContext,0)


        def getRuleIndex(self):
            return qasm3Parser.RULE_quantumBlock

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterQuantumBlock" ):
                listener.enterQuantumBlock(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitQuantumBlock" ):
                listener.exitQuantumBlock(self)




    def quantumBlock(self):

        localctx = qasm3Parser.QuantumBlockContext(self, self._ctx, self.state)
        self.enterRule(localctx, 78, self.RULE_quantumBlock)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 413
            self.match(qasm3Parser.LBRACE)
            self.state = 416
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [qasm3Parser.LBRACE]:
                self.state = 414
                self.quantumBlock()
                pass
            elif token in [qasm3Parser.T__16, qasm3Parser.T__17, qasm3Parser.T__18, qasm3Parser.T__19, qasm3Parser.T__20, qasm3Parser.T__22, qasm3Parser.T__23, qasm3Parser.T__24, qasm3Parser.Identifier]:
                self.state = 415
                self.quantumStatement()
                pass
            else:
                raise NoViableAltException(self)

            self.state = 418
            self.match(qasm3Parser.RBRACE)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class QuantumStatementContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def SEMICOLON(self):
            return self.getToken(qasm3Parser.SEMICOLON, 0)

        def quantumInstruction(self):
            return self.getTypedRuleContext(qasm3Parser.QuantumInstructionContext,0)


        def quantumMeasurementDeclaration(self):
            return self.getTypedRuleContext(qasm3Parser.QuantumMeasurementDeclarationContext,0)


        def getRuleIndex(self):
            return qasm3Parser.RULE_quantumStatement

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterQuantumStatement" ):
                listener.enterQuantumStatement(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitQuantumStatement" ):
                listener.exitQuantumStatement(self)




    def quantumStatement(self):

        localctx = qasm3Parser.QuantumStatementContext(self, self._ctx, self.state)
        self.enterRule(localctx, 80, self.RULE_quantumStatement)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 422
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,29,self._ctx)
            if la_ == 1:
                self.state = 420
                self.quantumInstruction()
                pass

            elif la_ == 2:
                self.state = 421
                self.quantumMeasurementDeclaration()
                pass


            self.state = 424
            self.match(qasm3Parser.SEMICOLON)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class QuantumInstructionContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def quantumGateCall(self):
            return self.getTypedRuleContext(qasm3Parser.QuantumGateCallContext,0)


        def quantumMeasurement(self):
            return self.getTypedRuleContext(qasm3Parser.QuantumMeasurementContext,0)


        def quantumBarrier(self):
            return self.getTypedRuleContext(qasm3Parser.QuantumBarrierContext,0)


        def getRuleIndex(self):
            return qasm3Parser.RULE_quantumInstruction

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterQuantumInstruction" ):
                listener.enterQuantumInstruction(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitQuantumInstruction" ):
                listener.exitQuantumInstruction(self)




    def quantumInstruction(self):

        localctx = qasm3Parser.QuantumInstructionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 82, self.RULE_quantumInstruction)
        try:
            self.state = 429
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [qasm3Parser.T__18, qasm3Parser.T__19, qasm3Parser.T__20, qasm3Parser.T__22, qasm3Parser.T__23, qasm3Parser.T__24, qasm3Parser.Identifier]:
                self.enterOuterAlt(localctx, 1)
                self.state = 426
                self.quantumGateCall()
                pass
            elif token in [qasm3Parser.T__16]:
                self.enterOuterAlt(localctx, 2)
                self.state = 427
                self.quantumMeasurement()
                pass
            elif token in [qasm3Parser.T__17]:
                self.enterOuterAlt(localctx, 3)
                self.state = 428
                self.quantumBarrier()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class QuantumMeasurementContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def indexIdentifierList(self):
            return self.getTypedRuleContext(qasm3Parser.IndexIdentifierListContext,0)


        def getRuleIndex(self):
            return qasm3Parser.RULE_quantumMeasurement

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterQuantumMeasurement" ):
                listener.enterQuantumMeasurement(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitQuantumMeasurement" ):
                listener.exitQuantumMeasurement(self)




    def quantumMeasurement(self):

        localctx = qasm3Parser.QuantumMeasurementContext(self, self._ctx, self.state)
        self.enterRule(localctx, 84, self.RULE_quantumMeasurement)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 431
            self.match(qasm3Parser.T__16)
            self.state = 432
            self.indexIdentifierList()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class QuantumMeasurementDeclarationContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def quantumMeasurement(self):
            return self.getTypedRuleContext(qasm3Parser.QuantumMeasurementContext,0)


        def ARROW(self):
            return self.getToken(qasm3Parser.ARROW, 0)

        def indexIdentifierList(self):
            return self.getTypedRuleContext(qasm3Parser.IndexIdentifierListContext,0)


        def ASSIGN(self):
            return self.getToken(qasm3Parser.ASSIGN, 0)

        def getRuleIndex(self):
            return qasm3Parser.RULE_quantumMeasurementDeclaration

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterQuantumMeasurementDeclaration" ):
                listener.enterQuantumMeasurementDeclaration(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitQuantumMeasurementDeclaration" ):
                listener.exitQuantumMeasurementDeclaration(self)




    def quantumMeasurementDeclaration(self):

        localctx = qasm3Parser.QuantumMeasurementDeclarationContext(self, self._ctx, self.state)
        self.enterRule(localctx, 86, self.RULE_quantumMeasurementDeclaration)
        try:
            self.state = 442
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [qasm3Parser.T__16]:
                self.enterOuterAlt(localctx, 1)
                self.state = 434
                self.quantumMeasurement()
                self.state = 435
                self.match(qasm3Parser.ARROW)
                self.state = 436
                self.indexIdentifierList()
                pass
            elif token in [qasm3Parser.Identifier]:
                self.enterOuterAlt(localctx, 2)
                self.state = 438
                self.indexIdentifierList()
                self.state = 439
                self.match(qasm3Parser.ASSIGN)
                self.state = 440
                self.quantumMeasurement()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class QuantumBarrierContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def indexIdentifierList(self):
            return self.getTypedRuleContext(qasm3Parser.IndexIdentifierListContext,0)


        def getRuleIndex(self):
            return qasm3Parser.RULE_quantumBarrier

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterQuantumBarrier" ):
                listener.enterQuantumBarrier(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitQuantumBarrier" ):
                listener.exitQuantumBarrier(self)




    def quantumBarrier(self):

        localctx = qasm3Parser.QuantumBarrierContext(self, self._ctx, self.state)
        self.enterRule(localctx, 88, self.RULE_quantumBarrier)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 444
            self.match(qasm3Parser.T__17)
            self.state = 445
            self.indexIdentifierList()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class QuantumGateModifierContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def LPAREN(self):
            return self.getToken(qasm3Parser.LPAREN, 0)

        def Integer(self):
            return self.getToken(qasm3Parser.Integer, 0)

        def RPAREN(self):
            return self.getToken(qasm3Parser.RPAREN, 0)

        def getRuleIndex(self):
            return qasm3Parser.RULE_quantumGateModifier

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterQuantumGateModifier" ):
                listener.enterQuantumGateModifier(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitQuantumGateModifier" ):
                listener.exitQuantumGateModifier(self)




    def quantumGateModifier(self):

        localctx = qasm3Parser.QuantumGateModifierContext(self, self._ctx, self.state)
        self.enterRule(localctx, 90, self.RULE_quantumGateModifier)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 453
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [qasm3Parser.T__18]:
                self.state = 447
                self.match(qasm3Parser.T__18)
                pass
            elif token in [qasm3Parser.T__19]:
                self.state = 448
                self.match(qasm3Parser.T__19)
                self.state = 449
                self.match(qasm3Parser.LPAREN)
                self.state = 450
                self.match(qasm3Parser.Integer)
                self.state = 451
                self.match(qasm3Parser.RPAREN)
                pass
            elif token in [qasm3Parser.T__20]:
                self.state = 452
                self.match(qasm3Parser.T__20)
                pass
            else:
                raise NoViableAltException(self)

            self.state = 455
            self.match(qasm3Parser.T__21)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class QuantumGateCallContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def quantumGateName(self):
            return self.getTypedRuleContext(qasm3Parser.QuantumGateNameContext,0)


        def indexIdentifierList(self):
            return self.getTypedRuleContext(qasm3Parser.IndexIdentifierListContext,0)


        def LPAREN(self):
            return self.getToken(qasm3Parser.LPAREN, 0)

        def RPAREN(self):
            return self.getToken(qasm3Parser.RPAREN, 0)

        def expressionList(self):
            return self.getTypedRuleContext(qasm3Parser.ExpressionListContext,0)


        def getRuleIndex(self):
            return qasm3Parser.RULE_quantumGateCall

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterQuantumGateCall" ):
                listener.enterQuantumGateCall(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitQuantumGateCall" ):
                listener.exitQuantumGateCall(self)




    def quantumGateCall(self):

        localctx = qasm3Parser.QuantumGateCallContext(self, self._ctx, self.state)
        self.enterRule(localctx, 92, self.RULE_quantumGateCall)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 457
            self.quantumGateName()
            self.state = 463
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==qasm3Parser.LPAREN:
                self.state = 458
                self.match(qasm3Parser.LPAREN)
                self.state = 460
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if (((_la) & ~0x3f) == 0 and ((1 << _la) & ((1 << qasm3Parser.T__4) | (1 << qasm3Parser.T__5) | (1 << qasm3Parser.T__6) | (1 << qasm3Parser.T__7) | (1 << qasm3Parser.T__8) | (1 << qasm3Parser.T__9) | (1 << qasm3Parser.T__10) | (1 << qasm3Parser.T__11) | (1 << qasm3Parser.T__16) | (1 << qasm3Parser.T__25) | (1 << qasm3Parser.T__26) | (1 << qasm3Parser.T__46) | (1 << qasm3Parser.T__47) | (1 << qasm3Parser.T__48) | (1 << qasm3Parser.T__49) | (1 << qasm3Parser.T__50) | (1 << qasm3Parser.T__51) | (1 << qasm3Parser.T__52) | (1 << qasm3Parser.T__53))) != 0) or ((((_la - 83)) & ~0x3f) == 0 and ((1 << (_la - 83)) & ((1 << (qasm3Parser.T__82 - 83)) | (1 << (qasm3Parser.T__83 - 83)) | (1 << (qasm3Parser.T__86 - 83)) | (1 << (qasm3Parser.Constant - 83)) | (1 << (qasm3Parser.Integer - 83)) | (1 << (qasm3Parser.RealNumber - 83)) | (1 << (qasm3Parser.Identifier - 83)))) != 0):
                    self.state = 459
                    self.expressionList()


                self.state = 462
                self.match(qasm3Parser.RPAREN)


            self.state = 465
            self.indexIdentifierList()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class QuantumGateNameContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def Identifier(self):
            return self.getToken(qasm3Parser.Identifier, 0)

        def quantumGateModifier(self):
            return self.getTypedRuleContext(qasm3Parser.QuantumGateModifierContext,0)


        def quantumGateName(self):
            return self.getTypedRuleContext(qasm3Parser.QuantumGateNameContext,0)


        def getRuleIndex(self):
            return qasm3Parser.RULE_quantumGateName

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterQuantumGateName" ):
                listener.enterQuantumGateName(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitQuantumGateName" ):
                listener.exitQuantumGateName(self)




    def quantumGateName(self):

        localctx = qasm3Parser.QuantumGateNameContext(self, self._ctx, self.state)
        self.enterRule(localctx, 94, self.RULE_quantumGateName)
        try:
            self.state = 474
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [qasm3Parser.T__22]:
                self.enterOuterAlt(localctx, 1)
                self.state = 467
                self.match(qasm3Parser.T__22)
                pass
            elif token in [qasm3Parser.T__23]:
                self.enterOuterAlt(localctx, 2)
                self.state = 468
                self.match(qasm3Parser.T__23)
                pass
            elif token in [qasm3Parser.T__24]:
                self.enterOuterAlt(localctx, 3)
                self.state = 469
                self.match(qasm3Parser.T__24)
                pass
            elif token in [qasm3Parser.Identifier]:
                self.enterOuterAlt(localctx, 4)
                self.state = 470
                self.match(qasm3Parser.Identifier)
                pass
            elif token in [qasm3Parser.T__18, qasm3Parser.T__19, qasm3Parser.T__20]:
                self.enterOuterAlt(localctx, 5)
                self.state = 471
                self.quantumGateModifier()
                self.state = 472
                self.quantumGateName()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class UnaryOperatorContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def builtInMath(self):
            return self.getTypedRuleContext(qasm3Parser.BuiltInMathContext,0)


        def getRuleIndex(self):
            return qasm3Parser.RULE_unaryOperator

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterUnaryOperator" ):
                listener.enterUnaryOperator(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitUnaryOperator" ):
                listener.exitUnaryOperator(self)




    def unaryOperator(self):

        localctx = qasm3Parser.UnaryOperatorContext(self, self._ctx, self.state)
        self.enterRule(localctx, 96, self.RULE_unaryOperator)
        try:
            self.state = 479
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [qasm3Parser.T__25]:
                self.enterOuterAlt(localctx, 1)
                self.state = 476
                self.match(qasm3Parser.T__25)
                pass
            elif token in [qasm3Parser.T__26]:
                self.enterOuterAlt(localctx, 2)
                self.state = 477
                self.match(qasm3Parser.T__26)
                pass
            elif token in [qasm3Parser.T__46, qasm3Parser.T__47, qasm3Parser.T__48, qasm3Parser.T__49, qasm3Parser.T__50, qasm3Parser.T__51, qasm3Parser.T__52, qasm3Parser.T__53]:
                self.enterOuterAlt(localctx, 3)
                self.state = 478
                self.builtInMath()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class BinaryOperatorContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return qasm3Parser.RULE_binaryOperator

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterBinaryOperator" ):
                listener.enterBinaryOperator(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitBinaryOperator" ):
                listener.exitBinaryOperator(self)




    def binaryOperator(self):

        localctx = qasm3Parser.BinaryOperatorContext(self, self._ctx, self.state)
        self.enterRule(localctx, 98, self.RULE_binaryOperator)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 481
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & ((1 << qasm3Parser.T__14) | (1 << qasm3Parser.T__27) | (1 << qasm3Parser.T__28) | (1 << qasm3Parser.T__29) | (1 << qasm3Parser.T__30) | (1 << qasm3Parser.T__31) | (1 << qasm3Parser.T__32) | (1 << qasm3Parser.T__33) | (1 << qasm3Parser.T__34) | (1 << qasm3Parser.T__35) | (1 << qasm3Parser.T__36) | (1 << qasm3Parser.T__37) | (1 << qasm3Parser.T__38) | (1 << qasm3Parser.T__39) | (1 << qasm3Parser.T__40) | (1 << qasm3Parser.T__41) | (1 << qasm3Parser.T__42) | (1 << qasm3Parser.T__43) | (1 << qasm3Parser.T__44))) != 0)):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ExpressionStatementContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def expression(self):
            return self.getTypedRuleContext(qasm3Parser.ExpressionContext,0)


        def SEMICOLON(self):
            return self.getToken(qasm3Parser.SEMICOLON, 0)

        def expressionStatement(self):
            return self.getTypedRuleContext(qasm3Parser.ExpressionStatementContext,0)


        def getRuleIndex(self):
            return qasm3Parser.RULE_expressionStatement

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterExpressionStatement" ):
                listener.enterExpressionStatement(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitExpressionStatement" ):
                listener.exitExpressionStatement(self)




    def expressionStatement(self):

        localctx = qasm3Parser.ExpressionStatementContext(self, self._ctx, self.state)
        self.enterRule(localctx, 100, self.RULE_expressionStatement)
        try:
            self.state = 488
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [qasm3Parser.T__4, qasm3Parser.T__5, qasm3Parser.T__6, qasm3Parser.T__7, qasm3Parser.T__8, qasm3Parser.T__9, qasm3Parser.T__10, qasm3Parser.T__11, qasm3Parser.T__16, qasm3Parser.T__25, qasm3Parser.T__26, qasm3Parser.T__46, qasm3Parser.T__47, qasm3Parser.T__48, qasm3Parser.T__49, qasm3Parser.T__50, qasm3Parser.T__51, qasm3Parser.T__52, qasm3Parser.T__53, qasm3Parser.T__82, qasm3Parser.T__83, qasm3Parser.T__86, qasm3Parser.Constant, qasm3Parser.Integer, qasm3Parser.RealNumber, qasm3Parser.Identifier]:
                self.enterOuterAlt(localctx, 1)
                self.state = 483
                self.expression(0)
                self.state = 484
                self.match(qasm3Parser.SEMICOLON)
                pass
            elif token in [qasm3Parser.T__45]:
                self.enterOuterAlt(localctx, 2)
                self.state = 486
                self.match(qasm3Parser.T__45)
                self.state = 487
                self.expressionStatement()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ExpressionContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def unaryOperator(self):
            return self.getTypedRuleContext(qasm3Parser.UnaryOperatorContext,0)


        def expression(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(qasm3Parser.ExpressionContext)
            else:
                return self.getTypedRuleContext(qasm3Parser.ExpressionContext,i)


        def membershipTest(self):
            return self.getTypedRuleContext(qasm3Parser.MembershipTestContext,0)


        def call(self):
            return self.getTypedRuleContext(qasm3Parser.CallContext,0)


        def LPAREN(self):
            return self.getToken(qasm3Parser.LPAREN, 0)

        def RPAREN(self):
            return self.getToken(qasm3Parser.RPAREN, 0)

        def expressionList(self):
            return self.getTypedRuleContext(qasm3Parser.ExpressionListContext,0)


        def quantumMeasurement(self):
            return self.getTypedRuleContext(qasm3Parser.QuantumMeasurementContext,0)


        def expressionTerminator(self):
            return self.getTypedRuleContext(qasm3Parser.ExpressionTerminatorContext,0)


        def binaryOperator(self):
            return self.getTypedRuleContext(qasm3Parser.BinaryOperatorContext,0)


        def LBRACKET(self):
            return self.getToken(qasm3Parser.LBRACKET, 0)

        def RBRACKET(self):
            return self.getToken(qasm3Parser.RBRACKET, 0)

        def incrementor(self):
            return self.getTypedRuleContext(qasm3Parser.IncrementorContext,0)


        def getRuleIndex(self):
            return qasm3Parser.RULE_expression

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterExpression" ):
                listener.enterExpression(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitExpression" ):
                listener.exitExpression(self)



    def expression(self, _p:int=0):
        _parentctx = self._ctx
        _parentState = self.state
        localctx = qasm3Parser.ExpressionContext(self, self._ctx, _parentState)
        _prevctx = localctx
        _startState = 102
        self.enterRecursionRule(localctx, 102, self.RULE_expression, _p)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 504
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,39,self._ctx)
            if la_ == 1:
                self.state = 491
                self.unaryOperator()
                self.state = 492
                self.expression(7)
                pass

            elif la_ == 2:
                self.state = 494
                self.membershipTest()
                pass

            elif la_ == 3:
                self.state = 495
                self.call()
                self.state = 496
                self.match(qasm3Parser.LPAREN)
                self.state = 498
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if (((_la) & ~0x3f) == 0 and ((1 << _la) & ((1 << qasm3Parser.T__4) | (1 << qasm3Parser.T__5) | (1 << qasm3Parser.T__6) | (1 << qasm3Parser.T__7) | (1 << qasm3Parser.T__8) | (1 << qasm3Parser.T__9) | (1 << qasm3Parser.T__10) | (1 << qasm3Parser.T__11) | (1 << qasm3Parser.T__16) | (1 << qasm3Parser.T__25) | (1 << qasm3Parser.T__26) | (1 << qasm3Parser.T__46) | (1 << qasm3Parser.T__47) | (1 << qasm3Parser.T__48) | (1 << qasm3Parser.T__49) | (1 << qasm3Parser.T__50) | (1 << qasm3Parser.T__51) | (1 << qasm3Parser.T__52) | (1 << qasm3Parser.T__53))) != 0) or ((((_la - 83)) & ~0x3f) == 0 and ((1 << (_la - 83)) & ((1 << (qasm3Parser.T__82 - 83)) | (1 << (qasm3Parser.T__83 - 83)) | (1 << (qasm3Parser.T__86 - 83)) | (1 << (qasm3Parser.Constant - 83)) | (1 << (qasm3Parser.Integer - 83)) | (1 << (qasm3Parser.RealNumber - 83)) | (1 << (qasm3Parser.Identifier - 83)))) != 0):
                    self.state = 497
                    self.expressionList()


                self.state = 500
                self.match(qasm3Parser.RPAREN)
                pass

            elif la_ == 4:
                self.state = 502
                self.quantumMeasurement()
                pass

            elif la_ == 5:
                self.state = 503
                self.expressionTerminator()
                pass


            self._ctx.stop = self._input.LT(-1)
            self.state = 519
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,41,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    if self._parseListeners is not None:
                        self.triggerExitRuleEvent()
                    _prevctx = localctx
                    self.state = 517
                    self._errHandler.sync(self)
                    la_ = self._interp.adaptivePredict(self._input,40,self._ctx)
                    if la_ == 1:
                        localctx = qasm3Parser.ExpressionContext(self, _parentctx, _parentState)
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_expression)
                        self.state = 506
                        if not self.precpred(self._ctx, 8):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 8)")
                        self.state = 507
                        self.binaryOperator()
                        self.state = 508
                        self.expression(9)
                        pass

                    elif la_ == 2:
                        localctx = qasm3Parser.ExpressionContext(self, _parentctx, _parentState)
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_expression)
                        self.state = 510
                        if not self.precpred(self._ctx, 5):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 5)")
                        self.state = 511
                        self.match(qasm3Parser.LBRACKET)
                        self.state = 512
                        self.expression(0)
                        self.state = 513
                        self.match(qasm3Parser.RBRACKET)
                        pass

                    elif la_ == 3:
                        localctx = qasm3Parser.ExpressionContext(self, _parentctx, _parentState)
                        self.pushNewRecursionContext(localctx, _startState, self.RULE_expression)
                        self.state = 515
                        if not self.precpred(self._ctx, 3):
                            from antlr4.error.Errors import FailedPredicateException
                            raise FailedPredicateException(self, "self.precpred(self._ctx, 3)")
                        self.state = 516
                        self.incrementor()
                        pass

             
                self.state = 521
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,41,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.unrollRecursionContexts(_parentctx)
        return localctx


    class ExpressionTerminatorContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def Constant(self):
            return self.getToken(qasm3Parser.Constant, 0)

        def Integer(self):
            return self.getToken(qasm3Parser.Integer, 0)

        def RealNumber(self):
            return self.getToken(qasm3Parser.RealNumber, 0)

        def Identifier(self):
            return self.getToken(qasm3Parser.Identifier, 0)

        def timeTerminator(self):
            return self.getTypedRuleContext(qasm3Parser.TimeTerminatorContext,0)


        def getRuleIndex(self):
            return qasm3Parser.RULE_expressionTerminator

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterExpressionTerminator" ):
                listener.enterExpressionTerminator(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitExpressionTerminator" ):
                listener.exitExpressionTerminator(self)




    def expressionTerminator(self):

        localctx = qasm3Parser.ExpressionTerminatorContext(self, self._ctx, self.state)
        self.enterRule(localctx, 104, self.RULE_expressionTerminator)
        try:
            self.state = 527
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,42,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 522
                self.match(qasm3Parser.Constant)
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 523
                self.match(qasm3Parser.Integer)
                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 524
                self.match(qasm3Parser.RealNumber)
                pass

            elif la_ == 4:
                self.enterOuterAlt(localctx, 4)
                self.state = 525
                self.match(qasm3Parser.Identifier)
                pass

            elif la_ == 5:
                self.enterOuterAlt(localctx, 5)
                self.state = 526
                self.timeTerminator()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ExpressionListContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def expression(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(qasm3Parser.ExpressionContext)
            else:
                return self.getTypedRuleContext(qasm3Parser.ExpressionContext,i)


        def COMMA(self, i:int=None):
            if i is None:
                return self.getTokens(qasm3Parser.COMMA)
            else:
                return self.getToken(qasm3Parser.COMMA, i)

        def getRuleIndex(self):
            return qasm3Parser.RULE_expressionList

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterExpressionList" ):
                listener.enterExpressionList(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitExpressionList" ):
                listener.exitExpressionList(self)




    def expressionList(self):

        localctx = qasm3Parser.ExpressionListContext(self, self._ctx, self.state)
        self.enterRule(localctx, 106, self.RULE_expressionList)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 534
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,43,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 529
                    self.expression(0)
                    self.state = 530
                    self.match(qasm3Parser.COMMA) 
                self.state = 536
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,43,self._ctx)

            self.state = 537
            self.expression(0)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class CallContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def Identifier(self):
            return self.getToken(qasm3Parser.Identifier, 0)

        def builtInMath(self):
            return self.getTypedRuleContext(qasm3Parser.BuiltInMathContext,0)


        def castOperator(self):
            return self.getTypedRuleContext(qasm3Parser.CastOperatorContext,0)


        def getRuleIndex(self):
            return qasm3Parser.RULE_call

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterCall" ):
                listener.enterCall(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitCall" ):
                listener.exitCall(self)




    def call(self):

        localctx = qasm3Parser.CallContext(self, self._ctx, self.state)
        self.enterRule(localctx, 108, self.RULE_call)
        try:
            self.state = 542
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [qasm3Parser.Identifier]:
                self.enterOuterAlt(localctx, 1)
                self.state = 539
                self.match(qasm3Parser.Identifier)
                pass
            elif token in [qasm3Parser.T__46, qasm3Parser.T__47, qasm3Parser.T__48, qasm3Parser.T__49, qasm3Parser.T__50, qasm3Parser.T__51, qasm3Parser.T__52, qasm3Parser.T__53]:
                self.enterOuterAlt(localctx, 2)
                self.state = 540
                self.builtInMath()
                pass
            elif token in [qasm3Parser.T__4, qasm3Parser.T__5, qasm3Parser.T__6, qasm3Parser.T__7, qasm3Parser.T__8, qasm3Parser.T__9, qasm3Parser.T__10, qasm3Parser.T__11, qasm3Parser.T__82, qasm3Parser.T__83]:
                self.enterOuterAlt(localctx, 3)
                self.state = 541
                self.castOperator()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class BuiltInMathContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return qasm3Parser.RULE_builtInMath

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterBuiltInMath" ):
                listener.enterBuiltInMath(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitBuiltInMath" ):
                listener.exitBuiltInMath(self)




    def builtInMath(self):

        localctx = qasm3Parser.BuiltInMathContext(self, self._ctx, self.state)
        self.enterRule(localctx, 110, self.RULE_builtInMath)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 544
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & ((1 << qasm3Parser.T__46) | (1 << qasm3Parser.T__47) | (1 << qasm3Parser.T__48) | (1 << qasm3Parser.T__49) | (1 << qasm3Parser.T__50) | (1 << qasm3Parser.T__51) | (1 << qasm3Parser.T__52) | (1 << qasm3Parser.T__53))) != 0)):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class CastOperatorContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def classicalType(self):
            return self.getTypedRuleContext(qasm3Parser.ClassicalTypeContext,0)


        def getRuleIndex(self):
            return qasm3Parser.RULE_castOperator

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterCastOperator" ):
                listener.enterCastOperator(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitCastOperator" ):
                listener.exitCastOperator(self)




    def castOperator(self):

        localctx = qasm3Parser.CastOperatorContext(self, self._ctx, self.state)
        self.enterRule(localctx, 112, self.RULE_castOperator)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 546
            self.classicalType()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class IncrementorContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return qasm3Parser.RULE_incrementor

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterIncrementor" ):
                listener.enterIncrementor(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitIncrementor" ):
                listener.exitIncrementor(self)




    def incrementor(self):

        localctx = qasm3Parser.IncrementorContext(self, self._ctx, self.state)
        self.enterRule(localctx, 114, self.RULE_incrementor)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 548
            _la = self._input.LA(1)
            if not(_la==qasm3Parser.T__54 or _la==qasm3Parser.T__55):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class AssignmentExpressionContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def assignmentOperator(self):
            return self.getTypedRuleContext(qasm3Parser.AssignmentOperatorContext,0)


        def expression(self):
            return self.getTypedRuleContext(qasm3Parser.ExpressionContext,0)


        def getRuleIndex(self):
            return qasm3Parser.RULE_assignmentExpression

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterAssignmentExpression" ):
                listener.enterAssignmentExpression(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitAssignmentExpression" ):
                listener.exitAssignmentExpression(self)




    def assignmentExpression(self):

        localctx = qasm3Parser.AssignmentExpressionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 116, self.RULE_assignmentExpression)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 550
            self.assignmentOperator()
            self.state = 551
            self.expression(0)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class AssignmentOperatorContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def ASSIGN(self):
            return self.getToken(qasm3Parser.ASSIGN, 0)

        def ARROW(self):
            return self.getToken(qasm3Parser.ARROW, 0)

        def getRuleIndex(self):
            return qasm3Parser.RULE_assignmentOperator

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterAssignmentOperator" ):
                listener.enterAssignmentOperator(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitAssignmentOperator" ):
                listener.exitAssignmentOperator(self)




    def assignmentOperator(self):

        localctx = qasm3Parser.AssignmentOperatorContext(self, self._ctx, self.state)
        self.enterRule(localctx, 118, self.RULE_assignmentOperator)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 553
            _la = self._input.LA(1)
            if not(((((_la - 57)) & ~0x3f) == 0 and ((1 << (_la - 57)) & ((1 << (qasm3Parser.T__56 - 57)) | (1 << (qasm3Parser.T__57 - 57)) | (1 << (qasm3Parser.T__58 - 57)) | (1 << (qasm3Parser.T__59 - 57)) | (1 << (qasm3Parser.T__60 - 57)) | (1 << (qasm3Parser.T__61 - 57)) | (1 << (qasm3Parser.T__62 - 57)) | (1 << (qasm3Parser.T__63 - 57)) | (1 << (qasm3Parser.T__64 - 57)) | (1 << (qasm3Parser.T__65 - 57)) | (1 << (qasm3Parser.ASSIGN - 57)) | (1 << (qasm3Parser.ARROW - 57)))) != 0)):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class MembershipTestContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def Identifier(self):
            return self.getToken(qasm3Parser.Identifier, 0)

        def setDeclaration(self):
            return self.getTypedRuleContext(qasm3Parser.SetDeclarationContext,0)


        def getRuleIndex(self):
            return qasm3Parser.RULE_membershipTest

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterMembershipTest" ):
                listener.enterMembershipTest(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitMembershipTest" ):
                listener.exitMembershipTest(self)




    def membershipTest(self):

        localctx = qasm3Parser.MembershipTestContext(self, self._ctx, self.state)
        self.enterRule(localctx, 120, self.RULE_membershipTest)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 555
            self.match(qasm3Parser.Identifier)
            self.state = 556
            self.match(qasm3Parser.T__66)
            self.state = 557
            self.setDeclaration()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class SetDeclarationContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def LBRACE(self):
            return self.getToken(qasm3Parser.LBRACE, 0)

        def expressionList(self):
            return self.getTypedRuleContext(qasm3Parser.ExpressionListContext,0)


        def RBRACE(self):
            return self.getToken(qasm3Parser.RBRACE, 0)

        def rangeDefinition(self):
            return self.getTypedRuleContext(qasm3Parser.RangeDefinitionContext,0)


        def getRuleIndex(self):
            return qasm3Parser.RULE_setDeclaration

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterSetDeclaration" ):
                listener.enterSetDeclaration(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitSetDeclaration" ):
                listener.exitSetDeclaration(self)




    def setDeclaration(self):

        localctx = qasm3Parser.SetDeclarationContext(self, self._ctx, self.state)
        self.enterRule(localctx, 122, self.RULE_setDeclaration)
        try:
            self.state = 564
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [qasm3Parser.LBRACE]:
                self.enterOuterAlt(localctx, 1)
                self.state = 559
                self.match(qasm3Parser.LBRACE)
                self.state = 560
                self.expressionList()
                self.state = 561
                self.match(qasm3Parser.RBRACE)
                pass
            elif token in [qasm3Parser.LBRACKET]:
                self.enterOuterAlt(localctx, 2)
                self.state = 563
                self.rangeDefinition()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class LoopBranchBlockContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def statement(self):
            return self.getTypedRuleContext(qasm3Parser.StatementContext,0)


        def programBlock(self):
            return self.getTypedRuleContext(qasm3Parser.ProgramBlockContext,0)


        def getRuleIndex(self):
            return qasm3Parser.RULE_loopBranchBlock

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterLoopBranchBlock" ):
                listener.enterLoopBranchBlock(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitLoopBranchBlock" ):
                listener.exitLoopBranchBlock(self)




    def loopBranchBlock(self):

        localctx = qasm3Parser.LoopBranchBlockContext(self, self._ctx, self.state)
        self.enterRule(localctx, 124, self.RULE_loopBranchBlock)
        try:
            self.state = 568
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [qasm3Parser.T__2, qasm3Parser.T__3, qasm3Parser.T__4, qasm3Parser.T__5, qasm3Parser.T__6, qasm3Parser.T__7, qasm3Parser.T__8, qasm3Parser.T__9, qasm3Parser.T__10, qasm3Parser.T__11, qasm3Parser.T__12, qasm3Parser.T__13, qasm3Parser.T__15, qasm3Parser.T__16, qasm3Parser.T__17, qasm3Parser.T__18, qasm3Parser.T__19, qasm3Parser.T__20, qasm3Parser.T__22, qasm3Parser.T__23, qasm3Parser.T__24, qasm3Parser.T__25, qasm3Parser.T__26, qasm3Parser.T__45, qasm3Parser.T__46, qasm3Parser.T__47, qasm3Parser.T__48, qasm3Parser.T__49, qasm3Parser.T__50, qasm3Parser.T__51, qasm3Parser.T__52, qasm3Parser.T__53, qasm3Parser.T__67, qasm3Parser.T__69, qasm3Parser.T__70, qasm3Parser.T__71, qasm3Parser.T__72, qasm3Parser.T__73, qasm3Parser.T__74, qasm3Parser.T__75, qasm3Parser.T__76, qasm3Parser.T__82, qasm3Parser.T__83, qasm3Parser.T__84, qasm3Parser.T__85, qasm3Parser.T__86, qasm3Parser.T__87, qasm3Parser.T__88, qasm3Parser.T__90, qasm3Parser.Constant, qasm3Parser.Integer, qasm3Parser.RealNumber, qasm3Parser.Identifier, qasm3Parser.LineComment, qasm3Parser.BlockComment]:
                self.enterOuterAlt(localctx, 1)
                self.state = 566
                self.statement()
                pass
            elif token in [qasm3Parser.LBRACE]:
                self.enterOuterAlt(localctx, 2)
                self.state = 567
                self.programBlock()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class BranchingStatementContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def LPAREN(self):
            return self.getToken(qasm3Parser.LPAREN, 0)

        def expression(self):
            return self.getTypedRuleContext(qasm3Parser.ExpressionContext,0)


        def RPAREN(self):
            return self.getToken(qasm3Parser.RPAREN, 0)

        def loopBranchBlock(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(qasm3Parser.LoopBranchBlockContext)
            else:
                return self.getTypedRuleContext(qasm3Parser.LoopBranchBlockContext,i)


        def getRuleIndex(self):
            return qasm3Parser.RULE_branchingStatement

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterBranchingStatement" ):
                listener.enterBranchingStatement(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitBranchingStatement" ):
                listener.exitBranchingStatement(self)




    def branchingStatement(self):

        localctx = qasm3Parser.BranchingStatementContext(self, self._ctx, self.state)
        self.enterRule(localctx, 126, self.RULE_branchingStatement)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 570
            self.match(qasm3Parser.T__67)
            self.state = 571
            self.match(qasm3Parser.LPAREN)
            self.state = 572
            self.expression(0)
            self.state = 573
            self.match(qasm3Parser.RPAREN)
            self.state = 574
            self.loopBranchBlock()
            self.state = 577
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,47,self._ctx)
            if la_ == 1:
                self.state = 575
                self.match(qasm3Parser.T__68)
                self.state = 576
                self.loopBranchBlock()


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class LoopStatementContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def loopBranchBlock(self):
            return self.getTypedRuleContext(qasm3Parser.LoopBranchBlockContext,0)


        def membershipTest(self):
            return self.getTypedRuleContext(qasm3Parser.MembershipTestContext,0)


        def LPAREN(self):
            return self.getToken(qasm3Parser.LPAREN, 0)

        def expression(self):
            return self.getTypedRuleContext(qasm3Parser.ExpressionContext,0)


        def RPAREN(self):
            return self.getToken(qasm3Parser.RPAREN, 0)

        def getRuleIndex(self):
            return qasm3Parser.RULE_loopStatement

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterLoopStatement" ):
                listener.enterLoopStatement(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitLoopStatement" ):
                listener.exitLoopStatement(self)




    def loopStatement(self):

        localctx = qasm3Parser.LoopStatementContext(self, self._ctx, self.state)
        self.enterRule(localctx, 128, self.RULE_loopStatement)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 586
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [qasm3Parser.T__69]:
                self.state = 579
                self.match(qasm3Parser.T__69)
                self.state = 580
                self.membershipTest()
                pass
            elif token in [qasm3Parser.T__70]:
                self.state = 581
                self.match(qasm3Parser.T__70)
                self.state = 582
                self.match(qasm3Parser.LPAREN)
                self.state = 583
                self.expression(0)
                self.state = 584
                self.match(qasm3Parser.RPAREN)
                pass
            else:
                raise NoViableAltException(self)

            self.state = 588
            self.loopBranchBlock()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ControlDirectiveStatementContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def controlDirective(self):
            return self.getTypedRuleContext(qasm3Parser.ControlDirectiveContext,0)


        def SEMICOLON(self):
            return self.getToken(qasm3Parser.SEMICOLON, 0)

        def getRuleIndex(self):
            return qasm3Parser.RULE_controlDirectiveStatement

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterControlDirectiveStatement" ):
                listener.enterControlDirectiveStatement(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitControlDirectiveStatement" ):
                listener.exitControlDirectiveStatement(self)




    def controlDirectiveStatement(self):

        localctx = qasm3Parser.ControlDirectiveStatementContext(self, self._ctx, self.state)
        self.enterRule(localctx, 130, self.RULE_controlDirectiveStatement)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 590
            self.controlDirective()
            self.state = 591
            self.match(qasm3Parser.SEMICOLON)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ControlDirectiveContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return qasm3Parser.RULE_controlDirective

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterControlDirective" ):
                listener.enterControlDirective(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitControlDirective" ):
                listener.exitControlDirective(self)




    def controlDirective(self):

        localctx = qasm3Parser.ControlDirectiveContext(self, self._ctx, self.state)
        self.enterRule(localctx, 132, self.RULE_controlDirective)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 593
            _la = self._input.LA(1)
            if not(((((_la - 72)) & ~0x3f) == 0 and ((1 << (_la - 72)) & ((1 << (qasm3Parser.T__71 - 72)) | (1 << (qasm3Parser.T__72 - 72)) | (1 << (qasm3Parser.T__73 - 72)))) != 0)):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class KernelDeclarationContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def Identifier(self):
            return self.getToken(qasm3Parser.Identifier, 0)

        def SEMICOLON(self):
            return self.getToken(qasm3Parser.SEMICOLON, 0)

        def LPAREN(self):
            return self.getToken(qasm3Parser.LPAREN, 0)

        def RPAREN(self):
            return self.getToken(qasm3Parser.RPAREN, 0)

        def returnSignature(self):
            return self.getTypedRuleContext(qasm3Parser.ReturnSignatureContext,0)


        def classicalType(self):
            return self.getTypedRuleContext(qasm3Parser.ClassicalTypeContext,0)


        def classicalTypeList(self):
            return self.getTypedRuleContext(qasm3Parser.ClassicalTypeListContext,0)


        def getRuleIndex(self):
            return qasm3Parser.RULE_kernelDeclaration

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterKernelDeclaration" ):
                listener.enterKernelDeclaration(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitKernelDeclaration" ):
                listener.exitKernelDeclaration(self)




    def kernelDeclaration(self):

        localctx = qasm3Parser.KernelDeclarationContext(self, self._ctx, self.state)
        self.enterRule(localctx, 134, self.RULE_kernelDeclaration)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 595
            self.match(qasm3Parser.T__74)
            self.state = 596
            self.match(qasm3Parser.Identifier)
            self.state = 602
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==qasm3Parser.LPAREN:
                self.state = 597
                self.match(qasm3Parser.LPAREN)
                self.state = 599
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if (((_la) & ~0x3f) == 0 and ((1 << _la) & ((1 << qasm3Parser.T__4) | (1 << qasm3Parser.T__5) | (1 << qasm3Parser.T__6) | (1 << qasm3Parser.T__7) | (1 << qasm3Parser.T__8) | (1 << qasm3Parser.T__9) | (1 << qasm3Parser.T__10) | (1 << qasm3Parser.T__11))) != 0) or _la==qasm3Parser.T__82 or _la==qasm3Parser.T__83:
                    self.state = 598
                    self.classicalTypeList()


                self.state = 601
                self.match(qasm3Parser.RPAREN)


            self.state = 605
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==qasm3Parser.ARROW:
                self.state = 604
                self.returnSignature()


            self.state = 608
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if (((_la) & ~0x3f) == 0 and ((1 << _la) & ((1 << qasm3Parser.T__4) | (1 << qasm3Parser.T__5) | (1 << qasm3Parser.T__6) | (1 << qasm3Parser.T__7) | (1 << qasm3Parser.T__8) | (1 << qasm3Parser.T__9) | (1 << qasm3Parser.T__10) | (1 << qasm3Parser.T__11))) != 0) or _la==qasm3Parser.T__82 or _la==qasm3Parser.T__83:
                self.state = 607
                self.classicalType()


            self.state = 610
            self.match(qasm3Parser.SEMICOLON)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class SubroutineDefinitionContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def Identifier(self):
            return self.getToken(qasm3Parser.Identifier, 0)

        def programBlock(self):
            return self.getTypedRuleContext(qasm3Parser.ProgramBlockContext,0)


        def LPAREN(self):
            return self.getToken(qasm3Parser.LPAREN, 0)

        def RPAREN(self):
            return self.getToken(qasm3Parser.RPAREN, 0)

        def returnSignature(self):
            return self.getTypedRuleContext(qasm3Parser.ReturnSignatureContext,0)


        def subroutineArgumentList(self):
            return self.getTypedRuleContext(qasm3Parser.SubroutineArgumentListContext,0)


        def getRuleIndex(self):
            return qasm3Parser.RULE_subroutineDefinition

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterSubroutineDefinition" ):
                listener.enterSubroutineDefinition(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitSubroutineDefinition" ):
                listener.exitSubroutineDefinition(self)




    def subroutineDefinition(self):

        localctx = qasm3Parser.SubroutineDefinitionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 136, self.RULE_subroutineDefinition)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 612
            self.match(qasm3Parser.T__75)
            self.state = 613
            self.match(qasm3Parser.Identifier)
            self.state = 619
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==qasm3Parser.LPAREN:
                self.state = 614
                self.match(qasm3Parser.LPAREN)
                self.state = 616
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if (((_la) & ~0x3f) == 0 and ((1 << _la) & ((1 << qasm3Parser.T__2) | (1 << qasm3Parser.T__3) | (1 << qasm3Parser.T__4) | (1 << qasm3Parser.T__5) | (1 << qasm3Parser.T__6) | (1 << qasm3Parser.T__7) | (1 << qasm3Parser.T__8) | (1 << qasm3Parser.T__9) | (1 << qasm3Parser.T__10) | (1 << qasm3Parser.T__11))) != 0) or _la==qasm3Parser.T__82 or _la==qasm3Parser.T__83:
                    self.state = 615
                    self.subroutineArgumentList()


                self.state = 618
                self.match(qasm3Parser.RPAREN)


            self.state = 622
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==qasm3Parser.ARROW:
                self.state = 621
                self.returnSignature()


            self.state = 624
            self.programBlock()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class SubroutineArgumentListContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def classicalArgumentList(self):
            return self.getTypedRuleContext(qasm3Parser.ClassicalArgumentListContext,0)


        def quantumArgumentList(self):
            return self.getTypedRuleContext(qasm3Parser.QuantumArgumentListContext,0)


        def getRuleIndex(self):
            return qasm3Parser.RULE_subroutineArgumentList

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterSubroutineArgumentList" ):
                listener.enterSubroutineArgumentList(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitSubroutineArgumentList" ):
                listener.exitSubroutineArgumentList(self)




    def subroutineArgumentList(self):

        localctx = qasm3Parser.SubroutineArgumentListContext(self, self._ctx, self.state)
        self.enterRule(localctx, 138, self.RULE_subroutineArgumentList)
        try:
            self.state = 628
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [qasm3Parser.T__4, qasm3Parser.T__5, qasm3Parser.T__6, qasm3Parser.T__7, qasm3Parser.T__8, qasm3Parser.T__9, qasm3Parser.T__10, qasm3Parser.T__11, qasm3Parser.T__82, qasm3Parser.T__83]:
                self.enterOuterAlt(localctx, 1)
                self.state = 626
                self.classicalArgumentList()
                pass
            elif token in [qasm3Parser.T__2, qasm3Parser.T__3]:
                self.enterOuterAlt(localctx, 2)
                self.state = 627
                self.quantumArgumentList()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class PragmaContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def AnyBlock(self):
            return self.getToken(qasm3Parser.AnyBlock, 0)

        def getRuleIndex(self):
            return qasm3Parser.RULE_pragma

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterPragma" ):
                listener.enterPragma(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitPragma" ):
                listener.exitPragma(self)




    def pragma(self):

        localctx = qasm3Parser.PragmaContext(self, self._ctx, self.state)
        self.enterRule(localctx, 140, self.RULE_pragma)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 630
            self.match(qasm3Parser.T__76)
            self.state = 631
            self.match(qasm3Parser.AnyBlock)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class TimeUnitContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return qasm3Parser.RULE_timeUnit

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterTimeUnit" ):
                listener.enterTimeUnit(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitTimeUnit" ):
                listener.exitTimeUnit(self)




    def timeUnit(self):

        localctx = qasm3Parser.TimeUnitContext(self, self._ctx, self.state)
        self.enterRule(localctx, 142, self.RULE_timeUnit)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 633
            _la = self._input.LA(1)
            if not(((((_la - 78)) & ~0x3f) == 0 and ((1 << (_la - 78)) & ((1 << (qasm3Parser.T__77 - 78)) | (1 << (qasm3Parser.T__78 - 78)) | (1 << (qasm3Parser.T__79 - 78)) | (1 << (qasm3Parser.T__80 - 78)) | (1 << (qasm3Parser.T__81 - 78)))) != 0)):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class TimingTypeContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def Integer(self):
            return self.getToken(qasm3Parser.Integer, 0)

        def getRuleIndex(self):
            return qasm3Parser.RULE_timingType

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterTimingType" ):
                listener.enterTimingType(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitTimingType" ):
                listener.exitTimingType(self)




    def timingType(self):

        localctx = qasm3Parser.TimingTypeContext(self, self._ctx, self.state)
        self.enterRule(localctx, 144, self.RULE_timingType)
        self._la = 0 # Token type
        try:
            self.state = 640
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [qasm3Parser.T__82]:
                self.enterOuterAlt(localctx, 1)
                self.state = 635
                self.match(qasm3Parser.T__82)
                pass
            elif token in [qasm3Parser.T__83]:
                self.enterOuterAlt(localctx, 2)
                self.state = 636
                self.match(qasm3Parser.T__83)
                self.state = 638
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==qasm3Parser.Integer:
                    self.state = 637
                    self.match(qasm3Parser.Integer)


                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class TimingBoxContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def Identifier(self):
            return self.getToken(qasm3Parser.Identifier, 0)

        def quantumBlock(self):
            return self.getTypedRuleContext(qasm3Parser.QuantumBlockContext,0)


        def timeUnit(self):
            return self.getTypedRuleContext(qasm3Parser.TimeUnitContext,0)


        def getRuleIndex(self):
            return qasm3Parser.RULE_timingBox

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterTimingBox" ):
                listener.enterTimingBox(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitTimingBox" ):
                listener.exitTimingBox(self)




    def timingBox(self):

        localctx = qasm3Parser.TimingBoxContext(self, self._ctx, self.state)
        self.enterRule(localctx, 146, self.RULE_timingBox)
        try:
            self.state = 649
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [qasm3Parser.T__84]:
                self.enterOuterAlt(localctx, 1)
                self.state = 642
                self.match(qasm3Parser.T__84)
                self.state = 643
                self.match(qasm3Parser.Identifier)
                self.state = 644
                self.quantumBlock()
                pass
            elif token in [qasm3Parser.T__85]:
                self.enterOuterAlt(localctx, 2)
                self.state = 645
                self.match(qasm3Parser.T__85)
                self.state = 646
                self.timeUnit()
                self.state = 647
                self.quantumBlock()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class TimeTerminatorContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def timeIdentifier(self):
            return self.getTypedRuleContext(qasm3Parser.TimeIdentifierContext,0)


        def getRuleIndex(self):
            return qasm3Parser.RULE_timeTerminator

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterTimeTerminator" ):
                listener.enterTimeTerminator(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitTimeTerminator" ):
                listener.exitTimeTerminator(self)




    def timeTerminator(self):

        localctx = qasm3Parser.TimeTerminatorContext(self, self._ctx, self.state)
        self.enterRule(localctx, 148, self.RULE_timeTerminator)
        try:
            self.state = 653
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [qasm3Parser.T__53, qasm3Parser.Identifier]:
                self.enterOuterAlt(localctx, 1)
                self.state = 651
                self.timeIdentifier()
                pass
            elif token in [qasm3Parser.T__86]:
                self.enterOuterAlt(localctx, 2)
                self.state = 652
                self.match(qasm3Parser.T__86)
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class TimeIdentifierContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def Identifier(self):
            return self.getToken(qasm3Parser.Identifier, 0)

        def timeUnit(self):
            return self.getTypedRuleContext(qasm3Parser.TimeUnitContext,0)


        def LPAREN(self):
            return self.getToken(qasm3Parser.LPAREN, 0)

        def RPAREN(self):
            return self.getToken(qasm3Parser.RPAREN, 0)

        def getRuleIndex(self):
            return qasm3Parser.RULE_timeIdentifier

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterTimeIdentifier" ):
                listener.enterTimeIdentifier(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitTimeIdentifier" ):
                listener.exitTimeIdentifier(self)




    def timeIdentifier(self):

        localctx = qasm3Parser.TimeIdentifierContext(self, self._ctx, self.state)
        self.enterRule(localctx, 150, self.RULE_timeIdentifier)
        try:
            self.state = 663
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [qasm3Parser.Identifier]:
                self.enterOuterAlt(localctx, 1)
                self.state = 655
                self.match(qasm3Parser.Identifier)
                self.state = 657
                self._errHandler.sync(self)
                la_ = self._interp.adaptivePredict(self._input,61,self._ctx)
                if la_ == 1:
                    self.state = 656
                    self.timeUnit()


                pass
            elif token in [qasm3Parser.T__53]:
                self.enterOuterAlt(localctx, 2)
                self.state = 659
                self.match(qasm3Parser.T__53)
                self.state = 660
                self.match(qasm3Parser.LPAREN)
                self.state = 661
                self.match(qasm3Parser.Identifier)
                self.state = 662
                self.match(qasm3Parser.RPAREN)
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class TimeInstructionNameContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return qasm3Parser.RULE_timeInstructionName

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterTimeInstructionName" ):
                listener.enterTimeInstructionName(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitTimeInstructionName" ):
                listener.exitTimeInstructionName(self)




    def timeInstructionName(self):

        localctx = qasm3Parser.TimeInstructionNameContext(self, self._ctx, self.state)
        self.enterRule(localctx, 152, self.RULE_timeInstructionName)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 665
            _la = self._input.LA(1)
            if not(_la==qasm3Parser.T__87 or _la==qasm3Parser.T__88):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class TimeInstructionContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def timeInstructionName(self):
            return self.getTypedRuleContext(qasm3Parser.TimeInstructionNameContext,0)


        def designator(self):
            return self.getTypedRuleContext(qasm3Parser.DesignatorContext,0)


        def rangeDefinition(self):
            return self.getTypedRuleContext(qasm3Parser.RangeDefinitionContext,0)


        def indexIdentifierList(self):
            return self.getTypedRuleContext(qasm3Parser.IndexIdentifierListContext,0)


        def LPAREN(self):
            return self.getToken(qasm3Parser.LPAREN, 0)

        def RPAREN(self):
            return self.getToken(qasm3Parser.RPAREN, 0)

        def expressionList(self):
            return self.getTypedRuleContext(qasm3Parser.ExpressionListContext,0)


        def getRuleIndex(self):
            return qasm3Parser.RULE_timeInstruction

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterTimeInstruction" ):
                listener.enterTimeInstruction(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitTimeInstruction" ):
                listener.exitTimeInstruction(self)




    def timeInstruction(self):

        localctx = qasm3Parser.TimeInstructionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 154, self.RULE_timeInstruction)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 667
            self.timeInstructionName()
            self.state = 673
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==qasm3Parser.LPAREN:
                self.state = 668
                self.match(qasm3Parser.LPAREN)
                self.state = 670
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if (((_la) & ~0x3f) == 0 and ((1 << _la) & ((1 << qasm3Parser.T__4) | (1 << qasm3Parser.T__5) | (1 << qasm3Parser.T__6) | (1 << qasm3Parser.T__7) | (1 << qasm3Parser.T__8) | (1 << qasm3Parser.T__9) | (1 << qasm3Parser.T__10) | (1 << qasm3Parser.T__11) | (1 << qasm3Parser.T__16) | (1 << qasm3Parser.T__25) | (1 << qasm3Parser.T__26) | (1 << qasm3Parser.T__46) | (1 << qasm3Parser.T__47) | (1 << qasm3Parser.T__48) | (1 << qasm3Parser.T__49) | (1 << qasm3Parser.T__50) | (1 << qasm3Parser.T__51) | (1 << qasm3Parser.T__52) | (1 << qasm3Parser.T__53))) != 0) or ((((_la - 83)) & ~0x3f) == 0 and ((1 << (_la - 83)) & ((1 << (qasm3Parser.T__82 - 83)) | (1 << (qasm3Parser.T__83 - 83)) | (1 << (qasm3Parser.T__86 - 83)) | (1 << (qasm3Parser.Constant - 83)) | (1 << (qasm3Parser.Integer - 83)) | (1 << (qasm3Parser.RealNumber - 83)) | (1 << (qasm3Parser.Identifier - 83)))) != 0):
                    self.state = 669
                    self.expressionList()


                self.state = 672
                self.match(qasm3Parser.RPAREN)


            self.state = 675
            self.designator()
            self.state = 678
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [qasm3Parser.LBRACKET]:
                self.state = 676
                self.rangeDefinition()
                pass
            elif token in [qasm3Parser.Identifier]:
                self.state = 677
                self.indexIdentifierList()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class TimeStatementContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def timeInstruction(self):
            return self.getTypedRuleContext(qasm3Parser.TimeInstructionContext,0)


        def SEMICOLON(self):
            return self.getToken(qasm3Parser.SEMICOLON, 0)

        def timingBox(self):
            return self.getTypedRuleContext(qasm3Parser.TimingBoxContext,0)


        def getRuleIndex(self):
            return qasm3Parser.RULE_timeStatement

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterTimeStatement" ):
                listener.enterTimeStatement(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitTimeStatement" ):
                listener.exitTimeStatement(self)




    def timeStatement(self):

        localctx = qasm3Parser.TimeStatementContext(self, self._ctx, self.state)
        self.enterRule(localctx, 156, self.RULE_timeStatement)
        try:
            self.state = 684
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [qasm3Parser.T__87, qasm3Parser.T__88]:
                self.enterOuterAlt(localctx, 1)
                self.state = 680
                self.timeInstruction()
                self.state = 681
                self.match(qasm3Parser.SEMICOLON)
                pass
            elif token in [qasm3Parser.T__84, qasm3Parser.T__85]:
                self.enterOuterAlt(localctx, 2)
                self.state = 683
                self.timingBox()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class CalibrationContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def calibrationGrammarDeclaration(self):
            return self.getTypedRuleContext(qasm3Parser.CalibrationGrammarDeclarationContext,0)


        def calibrationDefinition(self):
            return self.getTypedRuleContext(qasm3Parser.CalibrationDefinitionContext,0)


        def getRuleIndex(self):
            return qasm3Parser.RULE_calibration

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterCalibration" ):
                listener.enterCalibration(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitCalibration" ):
                listener.exitCalibration(self)




    def calibration(self):

        localctx = qasm3Parser.CalibrationContext(self, self._ctx, self.state)
        self.enterRule(localctx, 158, self.RULE_calibration)
        try:
            self.state = 688
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [qasm3Parser.T__89]:
                self.enterOuterAlt(localctx, 1)
                self.state = 686
                self.calibrationGrammarDeclaration()
                pass
            elif token in [qasm3Parser.T__90]:
                self.enterOuterAlt(localctx, 2)
                self.state = 687
                self.calibrationDefinition()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class CalibrationGrammarDeclarationContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def calibrationGrammar(self):
            return self.getTypedRuleContext(qasm3Parser.CalibrationGrammarContext,0)


        def SEMICOLON(self):
            return self.getToken(qasm3Parser.SEMICOLON, 0)

        def getRuleIndex(self):
            return qasm3Parser.RULE_calibrationGrammarDeclaration

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterCalibrationGrammarDeclaration" ):
                listener.enterCalibrationGrammarDeclaration(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitCalibrationGrammarDeclaration" ):
                listener.exitCalibrationGrammarDeclaration(self)




    def calibrationGrammarDeclaration(self):

        localctx = qasm3Parser.CalibrationGrammarDeclarationContext(self, self._ctx, self.state)
        self.enterRule(localctx, 160, self.RULE_calibrationGrammarDeclaration)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 690
            self.match(qasm3Parser.T__89)
            self.state = 691
            self.calibrationGrammar()
            self.state = 692
            self.match(qasm3Parser.SEMICOLON)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class CalibrationDefinitionContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def Identifier(self):
            return self.getToken(qasm3Parser.Identifier, 0)

        def identifierList(self):
            return self.getTypedRuleContext(qasm3Parser.IdentifierListContext,0)


        def returnSignature(self):
            return self.getTypedRuleContext(qasm3Parser.ReturnSignatureContext,0)


        def calibrationBody(self):
            return self.getTypedRuleContext(qasm3Parser.CalibrationBodyContext,0)


        def calibrationGrammar(self):
            return self.getTypedRuleContext(qasm3Parser.CalibrationGrammarContext,0)


        def LPAREN(self):
            return self.getToken(qasm3Parser.LPAREN, 0)

        def RPAREN(self):
            return self.getToken(qasm3Parser.RPAREN, 0)

        def calibrationArgumentList(self):
            return self.getTypedRuleContext(qasm3Parser.CalibrationArgumentListContext,0)


        def getRuleIndex(self):
            return qasm3Parser.RULE_calibrationDefinition

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterCalibrationDefinition" ):
                listener.enterCalibrationDefinition(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitCalibrationDefinition" ):
                listener.exitCalibrationDefinition(self)




    def calibrationDefinition(self):

        localctx = qasm3Parser.CalibrationDefinitionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 162, self.RULE_calibrationDefinition)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 694
            self.match(qasm3Parser.T__90)
            self.state = 696
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,68,self._ctx)
            if la_ == 1:
                self.state = 695
                self.calibrationGrammar()


            self.state = 698
            self.match(qasm3Parser.Identifier)
            self.state = 704
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==qasm3Parser.LPAREN:
                self.state = 699
                self.match(qasm3Parser.LPAREN)
                self.state = 701
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if (((_la) & ~0x3f) == 0 and ((1 << _la) & ((1 << qasm3Parser.T__4) | (1 << qasm3Parser.T__5) | (1 << qasm3Parser.T__6) | (1 << qasm3Parser.T__7) | (1 << qasm3Parser.T__8) | (1 << qasm3Parser.T__9) | (1 << qasm3Parser.T__10) | (1 << qasm3Parser.T__11) | (1 << qasm3Parser.T__16) | (1 << qasm3Parser.T__25) | (1 << qasm3Parser.T__26) | (1 << qasm3Parser.T__46) | (1 << qasm3Parser.T__47) | (1 << qasm3Parser.T__48) | (1 << qasm3Parser.T__49) | (1 << qasm3Parser.T__50) | (1 << qasm3Parser.T__51) | (1 << qasm3Parser.T__52) | (1 << qasm3Parser.T__53))) != 0) or ((((_la - 83)) & ~0x3f) == 0 and ((1 << (_la - 83)) & ((1 << (qasm3Parser.T__82 - 83)) | (1 << (qasm3Parser.T__83 - 83)) | (1 << (qasm3Parser.T__86 - 83)) | (1 << (qasm3Parser.Constant - 83)) | (1 << (qasm3Parser.Integer - 83)) | (1 << (qasm3Parser.RealNumber - 83)) | (1 << (qasm3Parser.Identifier - 83)))) != 0):
                    self.state = 700
                    self.calibrationArgumentList()


                self.state = 703
                self.match(qasm3Parser.RPAREN)


            self.state = 706
            self.identifierList()
            self.state = 707
            self.returnSignature()
            self.state = 708
            self.calibrationBody()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class CalibrationGrammarContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def Identifier(self):
            return self.getToken(qasm3Parser.Identifier, 0)

        def getRuleIndex(self):
            return qasm3Parser.RULE_calibrationGrammar

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterCalibrationGrammar" ):
                listener.enterCalibrationGrammar(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitCalibrationGrammar" ):
                listener.exitCalibrationGrammar(self)




    def calibrationGrammar(self):

        localctx = qasm3Parser.CalibrationGrammarContext(self, self._ctx, self.state)
        self.enterRule(localctx, 164, self.RULE_calibrationGrammar)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 710
            _la = self._input.LA(1)
            if not(_la==qasm3Parser.T__91 or _la==qasm3Parser.Identifier):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class CalibrationArgumentListContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def classicalArgumentList(self):
            return self.getTypedRuleContext(qasm3Parser.ClassicalArgumentListContext,0)


        def expressionList(self):
            return self.getTypedRuleContext(qasm3Parser.ExpressionListContext,0)


        def getRuleIndex(self):
            return qasm3Parser.RULE_calibrationArgumentList

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterCalibrationArgumentList" ):
                listener.enterCalibrationArgumentList(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitCalibrationArgumentList" ):
                listener.exitCalibrationArgumentList(self)




    def calibrationArgumentList(self):

        localctx = qasm3Parser.CalibrationArgumentListContext(self, self._ctx, self.state)
        self.enterRule(localctx, 166, self.RULE_calibrationArgumentList)
        try:
            self.state = 714
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,71,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 712
                self.classicalArgumentList()
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 713
                self.expressionList()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class CalibrationBodyContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def AnyBlock(self):
            return self.getToken(qasm3Parser.AnyBlock, 0)

        def getRuleIndex(self):
            return qasm3Parser.RULE_calibrationBody

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterCalibrationBody" ):
                listener.enterCalibrationBody(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitCalibrationBody" ):
                listener.exitCalibrationBody(self)




    def calibrationBody(self):

        localctx = qasm3Parser.CalibrationBodyContext(self, self._ctx, self.state)
        self.enterRule(localctx, 168, self.RULE_calibrationBody)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 716
            self.match(qasm3Parser.AnyBlock)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx



    def sempred(self, localctx:RuleContext, ruleIndex:int, predIndex:int):
        if self._predicates == None:
            self._predicates = dict()
        self._predicates[51] = self.expression_sempred
        pred = self._predicates.get(ruleIndex, None)
        if pred is None:
            raise Exception("No predicate with index:" + str(ruleIndex))
        else:
            return pred(localctx, predIndex)

    def expression_sempred(self, localctx:ExpressionContext, predIndex:int):
            if predIndex == 0:
                return self.precpred(self._ctx, 8)
         

            if predIndex == 1:
                return self.precpred(self._ctx, 5)
         

            if predIndex == 2:
                return self.precpred(self._ctx, 3)
         




