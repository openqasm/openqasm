#!/bin/bash

for number in `seq 3 31`
do
  filename=`expr $number + 1`
  python3.6 counterfeit_coin_gen.py -c ${number} -o cc_n${filename}
done
