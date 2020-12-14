/* CPMG XY4 decoupling 
 * This example demonstrates the use of referential delays
 * and time alignment.
*/
OPENQASM 3.0;
include "stdgates.inc";

length start_stretch = -0.5 * lengthof({x %0;}) + stretch
length middle_stretch = -0.5 * lengthof({x %0;}) - 5 * lengthof({y %0;} + stretch
length end_stretch = -0.5 * lengthof({y %0;}) + stretch

box {
  delay[start_stretch] %0;
  x %0;
  delay[middle_stretch] %0;
  y %0;
  delay[middle_stretch] %0;
  x %0;
  delay[middle_stretch] %0;
  y %0;
  delay[end_stretch] %0;

  cx %2, %3;
  cx %1, %2;
  u %3;
}