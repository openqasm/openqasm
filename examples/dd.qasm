/* CPMG XY4 decoupling w/ boxing
 * This example demonstrates the use of referential delays
 * and time alignment.
*/
OPENQASM 3.0;
include "stdgates.inc";

stretch s;
length start_stretch = -0.5 * lengthof({x %q0;}) + s;
length middle_stretch = -0.5 * lengthof({x %q0;}) - 5 * lengthof({y %q0;}) + s;
length end_stretch = -0.5 * lengthof({y %q0;}) + s;

boxas dd_circ {
  delay[start_stretch] %q0;
  x %q0;
  delay[middle_stretch] %q0;
  y %q0;
  delay[middle_stretch] %q0;
  x %q0;
  delay[middle_stretch] %q0;
  y %q0;
  delay[end_stretch] %q0;

  cx %q2, %q3;
  cx %q1, %q2;
  u %q3;
}
