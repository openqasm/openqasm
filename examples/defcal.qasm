defcalgrammar "openpulse";

defcal x %q0 {
   play drive(%q0), gaussian(...);
}

defcal x %q1 {
  play drive(%q1), gaussian(...);
}

defcal rz(angle[20]:theta) q {
  shift_phase drive(q), -theta;
}

defcal measure %q0 -> bit {
  complex[int[24]] iq;
  bit state;
  complex[int[12]] k0[1024] = [i0 + q0*j, i1 + q1*j, i2 + q2*j, ...];
  play measure(%q0), flat_top_gaussian(...);
  iq = capture acquire(%q0), 2048, kernel(k0);
  return threshold(iq, 1234);
}

defcal zx90_ix %q0, %q1 {
  play drive(%q0, "cr1"), flat_top_gaussian(...);  // uses a non-default
                                                   // frame labeled "cr1"
}

defcal cx %q0, %q1 {
  zx90_ix %q0, %q1;
  x %q0;
  shift_phase drive(%q0, "cr1");
  zx90_ix %q0, %q1;
  x %q0;
  x %q1;
}
