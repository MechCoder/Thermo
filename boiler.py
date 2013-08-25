from state import State

class SteadyState(object):
    r"""
    Base SteadyState class for stuff like Boilers to inherit from.
    """
    def t(self):
        return self.T1, self.T2

    def p(self):
        return self.P1, self.P2

    def h(self):
        return self.h1, self.h2

    def u(self):
        return self.u1, self.u2

    def v(self):
        return self.v1, self.v2

    def x(self):
        return self.x1, self.x2

    def s(self):
        return self.s1, self.s2

class Boiler(SteadyState):
    def __init__(self, P, H1= None, H2= None,
        T1=None, T2=None):
        self.P1 = self.P2 = P  # Pressure remains constant across boiler
        self.H1 = H1
        self.T1 = T1
        self.H2 = H2
        self.T2 = T2
        statedict = {'h1': H1, 'h2': H2, 't1': T1, 't2': T2}
        
        # Preprocessing
        knownprop = [key for key in statedict if statedict[key]]
        if len(knownprop) != 2:
            raise NotImplementedError("Any two of h1, h2, T1, T2, are required "
                "for steady state of turbine")
        self.__process()

    def __process(self):
        if self.H1 or self.T1:
            if self.H1 and self.T1:
                raise ValueError("Just enter one of initial enthalpy and temperature")
            elif self.H1:
                self.state1 = State(h=self.H1, P=self.P1)
            elif self.T1:
                self.state1 = State(T=self.T1, P=self.P1)

        else:
            raise ValueError("You need to enter one of initial enthalpy and temperature")

        if self.H2:
            self.state2 = State(h=self.H2, P=self.P2)
        elif self.T2:
            self.state2 = State(T=self.T2, P=self.P2)

        (self.P1, self.T1, self.v1, self.u1, self.h1,
           self.s1, self.x1) = / self.state1.finallist
        (self.P2, self.T2, self.v2, self.u2, self.h2,
           self.s1, self.x1) = / self.state2.finallist

    def heat(self):
        return self.h2 - self.h1
