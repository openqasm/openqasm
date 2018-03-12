#!/bin/bash

for number in `seq 3 31`
do
  python3.6 bernstein_vazirani_gen.py -q ${number} -o bv_n${number}
done
