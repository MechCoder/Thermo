from bisect import bisect_left
import shelve
import os

current = os.getcwd()
def pressureSearch(match):
    r"""
    This function outputs the other state values provided pressure and
    any other state is given.
    """
    P = match.get('P')
    statelist = ['T', 'v', 'h', 'u', 's', 'x']
    statedict = {'P': 0, 'T': 1, 'v': 2, 'u': 3, 'h': 4, 's': 5, 'x': 6}

    for key in statelist:
        if match.get(key):
            otherstate = key
            othervalue = match[key]
            break

    stateindex = statedict[otherstate]
    superheateddata = shelve.open(current + '/Thermo/super.dat')
    # Storing it as float numbers because the user input is float
    pressurelist = map(lambda x : float(x) ,superheateddata.keys())        
    # Storing the Pressure values in a sorted list , since in a dictionary it is kept in a random order
    pressurelist.sort()    

    if P in pressurelist:
        pressureindex = pressurelist.index(P)
        isotherm = superheateddata[str(int(P))]
        superheateddata.close()
        templist = _helper(isotherm, {otherstate: othervalue})
        if templist:
            templist.append(1)  # Quality
            templist.insert(0, P)
            return templist

    else:
        # If pressure is not present in between 10 and 20000 kPa,
        # then interpolate once to find the pressure between two pressures,
        # and then interpolate again to find the values for the corresponding states
        pressureind = bisect_left(pressurelist , P)
        prevind = pressureind - 1
        isotherm1 = superheateddata[str(int(pressurelist[pressureind]))] 
        isotherm2 = superheateddata[str(int(pressurelist[prevind]))]
        templist1 = _helper(isotherm1, {otherstate: othervalue})
        if templist1:
            templist1.insert(0, pressurelist[pressureind])
            del templist1[stateindex]
            templist2 = _helper(isotherm2, {otherstate: othervalue})
            if templist2:
                templist2.insert(0, pressurelist[prevind])
                del templist2[stateindex]
                templist = interpolate(P, 0, templist2, templist1)
                templist.insert(stateindex, othervalue)
                templist.append(1)  # Quality
                if templist:
                    return templist

    # In saturated state
    if otherstate != 'T':
        templist = _qualityHelper({'P': P, otherstate: othervalue})
        if templist:
            return templist

def _helper(isotherm, match):
    statelist = ['T', 'v', 'h', 'u', 's', 'x']
    for key in statelist:
        if match.get(key):
            otherstate = key
            othervalue = match[key]

    statedict = {'P': 0, 'T': 1, 'v': 2, 'u': 3, 'h': 4, 's': 5, 'x': 6}
    stateindex = statedict[otherstate]
    startvalue = isotherm[0][stateindex - 1]  
    endvalue =   isotherm[-1][stateindex - 1]

    if othervalue >= startvalue and othervalue <= endvalue:
        otherstatelist = [iso[stateindex - 1] for iso in isotherm]
        if othervalue in otherstatelist:
            return isotherm[otherstatelist.index(othervalue)]
        else:
            afterindex = bisect_left(otherstatelist, othervalue)
            beforeindex = afterindex - 1
            return interpolate(othervalue, stateindex - 1,
                isotherm[beforeindex], isotherm[afterindex])

def interpolate(state, index, lowerlimit, upperlimit):
    r"""
    Interpolate is a function used to find the other properties for a given state,
    provided one property is given, and the arguments needed are two statelists
    between which the given property exists and the index of the known property
    in the list
    """
       
    slope = float(state - upperlimit[index]) / (upperlimit[index] - lowerlimit[index])                      
    difference = [x - y for x, y in zip(upperlimit , lowerlimit)]    
    dx = [slope * x for x in difference]
    interpolatedvalue = [x + y for x , y in zip(upperlimit , dx)]     
    return interpolatedvalue

def _qualityHelper(match):
    r"""
    Quality Helper is a private function that helps to find the quality when the
    water is saturated
    """
    statelist = ['v', 'h', 'u', 's', 'x']

    P = match.get('P')
    if P:
        satdata = shelve.open(current + '/Thermo/ptables.dat')
        torplist = satdata['pressure']
        dummy = 0
        torp = match.pop('P')
        for key in statelist:
            if match.get(key):
                otherstate = key
                othervalue = match[key]
        upperval = 22064.0
        lowerval = 1.0

    else:
        satdata = shelve.open(current + '/Thermo/Temptables.dat')
        torplist = satdata['temp']
        dummy = 1
        torp = match.pop('T')
        for key in statelist:
            if match.get(key):
                otherstate = key
                othervalue = match[key]
        upperval = 373.95
        lowerval = 0.01

    list1 = ['vf', 'vg', 'uf', 'ug', 'hf', 'hg', 'sf', 'sg']
    statedict = {'v': 0, 'u': 1, 'h': 2, 's': 3}
    satlist =  ['pressure', 'temp', 'vf', 'vg', 'uf', 'ug', 'hf', 'hg', 'sf', 'sg']
    stateind = statedict[otherstate]

    if torp in torplist:
        templist = [] 
        tindex = torplist.index(torp)
        for state in satlist[2: ]:
            templist.append(satdata[state][tindex])                                                
        vapstate = satdata[list1[2*stateind + 1]][tindex]
        fluidstate = satdata[list1[2*stateind]][tindex]
        if othervalue >=fluidstate and vapstate >= othervalue:
            newlist = []
            x = (othervalue - fluidstate)/(vapstate - fluidstate)
            newlist.append(satdata['pressure'][tindex])
            newlist.append(satdata['temp'][tindex])
            newlist.append(satdata['vf'][tindex] +
                x*(satdata['vg'][tindex] - satdata['vf'][tindex]))
            newlist.append(satdata['uf'][tindex] +
                x*(satdata['ug'][tindex] - satdata['uf'][tindex]))
            newlist.append(satdata['hf'][tindex] +
                x*(satdata['hg'][tindex] - satdata['hf'][tindex]))
            newlist.append(satdata['sf'][tindex] +
                x*(satdata['sg'][tindex] - satdata['sf'][tindex]))
            newlist.append(x)
            satdata.close()
            return newlist

    elif torp >= lowerval and upperval >= torp: 
        # If P lies in between 1 and 22064 kPa, or if temperatue is between
        # 0.01 and 395C use the Saturated Pressure or temperature
        # Tables to interpolate for a given pressure and follow the
        # same procedure as above. 
                                     
        tindex = bisect_left(torplist, torp)
        preindex = tindex - 1
        pisobar = [satdata[state][preindex] for state in satlist]
        nisobar = [satdata[state][tindex] for state in satlist]
        templist = interpolate(torp, dummy, pisobar, nisobar)
        if templist:
            newlist = []
            newlist.append(templist.pop(0))
            newlist.append(templist.pop(0))
            fluidstate = templist[stateind*2]
            vapstate = templist[stateind*2 + 1]
            if othervalue >= fluidstate and vapstate >= othervalue:               
                x = (othervalue - fluidstate)/(vapstate - fluidstate)
                newlist.append(templist[0] + x*(templist[1] - templist[0]))
                newlist.append(templist[2] + x*(templist[3] - templist[2]))
                newlist.append(templist[4] + x*(templist[5] - templist[4]))
                newlist.append(templist[6] + x*(templist[7] - templist[6]))
                newlist.append(x)
                satdata.close() 
                return newlist

def temperatureSearch(match):
    r"""
    temperatureSearch is a function used to search for other properties
    when temperature and any other property is given.
    """
    T = match.get('T')
    statelist = ['P', 'v', 'h', 'u', 's', 'x']
    statedict = {'P': 0, 'T': 1, 'v': 2, 'u': 3, 'h': 4, 's': 5, 'x': 6}

    for key in statelist:
        if match.get(key):
            otherstate = key
            othervalue = match[key]
            break

    stateindex = statedict[otherstate]
    superheateddata = shelve.open(current + '/Thermo/super.dat')            
    pressurelist = map(lambda x: int(x), superheateddata.keys())
    pressurelist.sort()
    isotherm = []

    # Storing the values corresponding to a given temperature for all pressures
    for pressure in pressurelist:
        isobars= superheateddata[str(pressure)]
        templist = [isobar[0] for isobar in isobars]
        if T in templist:
           tindex = templist.index(T)
           list_ = isobars[tindex]
           list_.insert(0, pressure)
           isotherm.append(list_)
        elif T >= templist[0] and templist[-1] >= T:
           tindex = bisect_left(templist , T)
           previndex = tindex - 1 
           nisobar = isobars[tindex] 
           pisobar = isobars[previndex]
           list_ = (interpolate(T, 0, pisobar, nisobar))
           list_.insert(0 , pressure)
           isotherm.append(list_)

    if isotherm:    
        othvallist = [temp[stateindex] for temp in isotherm]
        inival = othvallist[0]
        finval = othvallist[-1]
        if othervalue in othvallist:
            valflag = othvallist.index(othervalue)
            isotherm[valflag].append(1)
            superheateddata.close()
            return isotherm
        elif othervalue <= inival and othervalue >= finval:
            othvallist.reverse()  # It is in decreasing order 
            temp = bisect_left(othvallist, othervalue)
            niso = isotherm[-temp]
            piso = isotherm[-temp - 1]
            templist = interpolate(othervalue, stateindex, piso, niso)
            if templist:
                templist.append(1)
                superheateddata.close()
                return templist

    if otherstate != 'P':
        templist = _qualityHelper({'T': T, otherstate: othervalue})
        if templist:
            return templist

def qualitySearch(match):
    r"""
    This is a function when used to find the other states when quality and one of
    temperature and pressure are given
    """
    satlist =  ['pressure', 'temp', 'vf', 'vg', 'uf', 'ug',
        'hf', 'hg', 'sf', 'sg']
    x = match.get('x')
    if match.get('P'):
        dummy = 0
        data = shelve.open(current + '/Thermo/ptables.dat')
        property_ = 'pressure'
        value = match.get('P')
        upperValue = 22064.0
        lowerValue = 1.0

    else:
        dummy = 1
        data = shelve.open(current + '/Thermo/Temptables.dat')
        property_ = 'temp'
        value = match.get('T')
        upperValue = 373.95
        lowerValue = 0.01


    if value >= lowerValue and value <= upperValue:
        torpInd = bisect_left(data[property_], value)
        piso = [data[prop][torpInd - 1] for prop in satlist]
        niso = [data[prop][torpInd] for prop in satlist]
        finallist = interpolate(value, dummy, piso, niso)
        if finallist:
            newlist = []
            newlist.append(finallist[0])
            newlist.append(finallist[1])
            newlist.append(finallist[2] + x*(finallist[3] - finallist[2]))
            newlist.append(finallist[4] + x*(finallist[5] - finallist[4]))
            newlist.append(finallist[6] + x*(finallist[7] - finallist[6]))
            newlist.append(finallist[8] + x*(finallist[9] - finallist[8]))
            newlist.append(x)
            return newlist
