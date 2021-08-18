# OpenQASM Working Groups

As outlined in the OpenQASM [governance document](governance.md), the Technical Steering Committee (TSC)
will, from time to time, elect to create **Working Groups** (WG) to study issues. The TSC will appoint a **Contributor**
as **Chair** for each WG. A WG shall submit a language RFC or pull request to the OpenQASM specification
for review by the TSC at an agreed upon date. A WG will be automatically disbanded upon acceptance or
(final) rejection of the RFC/pull request.

## Current Working Groups

### Generics and circuit families

**Objective**: ...

Chair: Niel de Beaudrap  
Members: Colm Ryan, Andrew Cross, Ali Javadi, Blake Johnson

### Grammar

**Objective**: 

Chair: Li Chen  
Members: Hiroshi Horii, Michael Healy, Luciano Bello, Jeff Heckey, Yunong Shi, Steven Heidel

### Types and casting

**Objective**: Define type hierarchy and implicit casting rules.  
**Questions**:

 * Any implicit casts?
 * What explicit casts are allowed?
 * Registers vs arrays?
 * Can you index into integers and get bit value?
 * Is an int equivalent to an array of bits?

Chair: Michael Healy (IBM Quantum)  
Members: Niel de Beaudrap, Hiroshi Horii, Blake Johnson, Colm Ryan, Luciano Bello, Prasahnt Sivarajah, Yunong Shi



### OpenPulse

**Objective**: Define a pulse grammar "openpulse" to be used for microcoding of gate instructions with
OpenQASM `defcal`'s.

Chair: Thomas Alexander (IBM Quantum)  
Members: Blake Johnson, Colm Ryan, Derek Bolt, Peter Karalekas, Lauren Capelluto, Michael Healy, Prasahnt Sivarajah, Yunong Shi, Steven Heidel, Zachary Schoenfeld


## Past Working Groups
