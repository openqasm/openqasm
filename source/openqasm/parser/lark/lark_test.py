GRAMMAR = r'''
'''
from lark import Lark
import time

qasm_parser = Lark(GRAMMAR, start='program', parser='lalr')

with open("ising.qasm", "r") as f:
    data = f.read()
st = time.time()
qasm_parser.parse(data)
ed = time.time()

print(ed - st)
