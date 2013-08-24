"""Implementation of base class for thermo objects"""

from Thermo.search import (pressureSearch, temperatureSearch,
    qualitySearch)

class State(object):
    def __init__(self, **kwargs):
        r"""
        This represents a base class for all State objects. Depending on the
        arguments given, pressureSearch, temperatureSearch or qualitySearch 
        are run, giving the required outputs.
        """
        otherstate = None
        othervalue = None
        statekeys = kwargs.keys()
        statevalues = [value for value in kwargs.values() if value]

        if len(statekeys) != 2:
            raise ValueError("Enter two of T, P, v, h, u, s, x"
                " as keyword arguments")
        if len(statevalues) != 2:
            raise ValueError("Enter two values of T, P, v, h, u, s, x")

        for key in statekeys:
            if key not in ['T', 'P', 'v', 'h', 'u', 's', 'x']:
                raise ValueError("Enter two of T, P, v, h, u, s, x"
                    " as keyword arguments")

        self.T  =  kwargs.get('T')
        self.P  =  kwargs.get('P')
        self.v  =  kwargs.get('v')
        self.h  =  kwargs.get('h')
        self.u  =  kwargs.get('u')
        self.s  =  kwargs.get('s')
        self.x  =  kwargs.get('x')
        stateList = {'P': self.P, 'T': self.T, 'v': self.v, 'u': self.u, 'h': self.h,
            's': self.s, 'x': self.x}

        if self.T is None and self.P is None:
            raise ValueError("Enter either one of Temperature and Pressure")
        
        if self.T and not self.P:
            stateList.pop('T')
        elif self.P:
            stateList.pop('P')

        for key in stateList:
            if stateList[key] is not None:
                otherstate = key
                othervalue = stateList[otherstate]
                break

        # If pressure is given as input , perform this function
        if self.P:
            if not self.x:
                finallist = pressureSearch({'P': self.P, otherstate: othervalue})
            else:
                if self.x >= 0 and self.x <= 1:
                    finallist = qualitySearch({'P': self.P, 'x': self.x})
                else:
                    raise ValueError("Quality should be between zero and one")
        
        elif self.T:   
            if not self.x:
                finallist = temperatureSearch({'T': self.T, otherstate: othervalue})
            else:
                if self.x >= 0 and self.x <= 1:  
                    finallist = qualitySearch({'T': self.T, 'x': self.x})
                else:
                    raise ValueError("Quality should be between zero and one")

        if not finallist:
            raise NotImplementedError("Thermo cannot find the state properties ",
                " for the given states")

        self.finallist = finallist

    def getTemp(self):
        """Returns Temperature"""
        return self.finallist[1]

    def getPressure(self):
        """Returns Pressure"""
        return self.finallist[0]

    def getEnthalpy(self):
        """Returns enthalpy"""
        return self.finallist[4]

    def getEnergy(self):
        """Returns energy"""
        return self.finallist[3]

    def getVolume(self):
        """Returns volume"""
        return self.finallist[2]

    def getEntropy(self):
        """Returns entropy"""
        return self.finallist[5]

    def getQuality(self):
        """Returns quality"""
        return self.finallist[6]

    def getFinallist(self):
        r"""
        Returns list of the form [Pressure, Temperature, Volume, Energy,
        Enthalpy, Entropy, Quality]
        """
        return self.finallist
