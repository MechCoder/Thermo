'''Thermo

A python module used to retrieve information corresponding to various states .

Author = S.Manoj Kumar

'''



import shelve

import bisect


class State:
    def GetTemp(self):
        return self.T

    def GetPressure(self):
        return self.P

    def GetEnthalpy(self):
        return self.h

    def GetEnergy(self):
        return self.u

    def GetVolume(self):
        return self.v

    def GetEntropy(self):
        return self.s

    def GetQuality(self):
        return self.x



    def __init__(self ,T = None , P = None , h = None , u = None , s = None , x = None , v = None):

        '''initializing all the variables'''

        self.T  =  T
        self.P  =  P
        self.v  =  v
        self.h  =  h
        self.u  =  u
        self.s  =  s
        self.x  =  x
        
        self.StateList = {'pressure' : [self.P , 0] , 'temp' : [self.T ,1] , 'volume' : [self.v ,2 ] , 'energy': [self.u ,3] , 'enthalpy' : [self.h ,4 ], 'entropy' : [self.s, 5 ], 'quality' : [self.x , 6]}
          
        self.SatList =  ['pressure' , 'temp' , 'vf' , 'vg' , 'uf' , 'ug' ,'hf' , 'hg' , 'sf' , 'sg']

        self.GivenStates = []

        for key in self.StateList:
            if self.StateList[key][0] != None:
                self.GivenStates.append(key)

        #If input is less than one , raise an error     
        assert(len(self.GivenStates) == 2) , 'Please input two values'

 
        #If pressure is given as input , perform this function  
        if 'pressure' in self.GivenStates:
            if 'quality' not in self.GivenStates:  
                self._PressureSearch()
            
            else:
                if self.x >= 0 and self.x <= 1:
                    self._QualitySearch(0)
                     
        
        elif 'temp' in self.GivenStates:   
            if 'quality' not in self.GivenStates :
                self._TemperatureSearch()

            else:
                if self.x >= 0 and self.x <= 1:  
                    self._QualitySearch(1)
    def _QualitySearch(self , TorP):
       #Searches for given pressure or temperature and quality.
        


        if TorP == 0:
 
            Data = shelve.open('ptables.dat')
            Property = 'pressure'
            Value = self.P
            UpperValue = 22064.0

            LowerValue = 1.0


        elif TorP == 1:
            Data = shelve.open('Temptables.dat')
            Property = 'temp'
            Value = self.T
            UpperValue = 373.95

            LowerValue = 0.01    


        if Value >= LowerValue and Value <= UpperValue:
    
            TorpInd = bisect.bisect_left(Data[Property] , Value)
            Isotherm1 = [Data['pressure'][TorpInd - 1] , Data['temp'][TorpInd - 1] , Data['vf'][TorpInd - 1] , Data['vg'][TorpInd - 1] , Data['uf'][TorpInd - 1] , Data['ug'][TorpInd - 1] , Data['hf'][TorpInd - 1] , Data['hg'][TorpInd - 1] , Data['sf'][TorpInd - 1] , Data['sg'][TorpInd - 1]]

            Isotherm2 = [Data['pressure'][TorpInd], Data['temp'][TorpInd] , Data['vf'][TorpInd] , Data['vg'][TorpInd] , Data['uf'][TorpInd] , Data['ug'][TorpInd] , Data['hf'][TorpInd] , Data['hg'][TorpInd] , Data['sf'][TorpInd] , Data['sg'][TorpInd]]

            Isotherm = self.interpolate(Value,TorP,Isotherm1 , Isotherm2)
        

            self.P = Isotherm[0] 
            self.T = Isotherm[1]
            self.v = Isotherm[2] + self.x * (Isotherm[3] - Isotherm[2])
            self.u = Isotherm[4] + self.x * (Isotherm[5] - Isotherm[4])
            self.h = Isotherm[6] + self.x * (Isotherm[7] - Isotherm[6])
            self.s = Isotherm[8] + self.x * (Isotherm[9] - Isotherm[8])    



    def interpolate(self ,state, index ,lowerlimit ,upperlimit ):
        '''Interpolate is a function used to find the other properties for a given state, provided one property is given. The arguments needed are two lists which are close to each other , and the index of the known property in the list'''
       
        slope = float(state - upperlimit[index]) / (upperlimit[index] - lowerlimit[index])                 
         
        difference = [x - y for x, y in zip(upperlimit , lowerlimit)]
        
        dx = [slope * x for x in difference] 
 
        interpolatedvalue = [x + y for x , y in zip(upperlimit , dx)] 
        
        return interpolatedvalue

    def _helper(self , Isotherm):
        '''This is a private function used to find the corresponding other values when a given pressure and other state is given.This function is used because the block of code below has to be repeated many times for multiple interpolations'''
        

        OtherState = self.GivenStates[0]

        #These are the beginning and ending values for the given pressure and other state
        OtherPropValue =  self.StateList[OtherState][0]

        OtherIndex = self.StateList[OtherState][1]
                
        StartingValue = Isotherm[0][OtherIndex - 1]  

        EndingValue =   Isotherm[-1][OtherIndex - 1]


        #Checking if for a given pressure value , the other state is between the starting and ending values     

        if  OtherPropValue >= StartingValue and EndingValue >= OtherPropValue:
           
            OtherStateList = []


            #Extracting the values required for a given pressure and storing it in a temporary list
            for isotherm in Isotherm:

                OtherStateList.append(isotherm[OtherIndex - 1])
                
            if OtherPropValue in OtherStateList:
                     
                TempList = Isotherm[OtherStateList.index(OtherPropValue)]

                return TempList


            else:
                    #Search the list for two properties which are relatively close to the user input

                OtherStateIndex = bisect.bisect_left(OtherStateList , OtherPropValue)

                PrevIndex = OtherStateIndex - 1
    
                TempList = self.interpolate(OtherPropValue ,OtherIndex - 1, Isotherm[PrevIndex], Isotherm[OtherStateIndex])
                return TempList
   
    def _QualityHelper(self , torp):

        '''Quality is a private function that helps in finding the quality when the state of water is saturated'''

        if torp == 1:

            SatData = shelve.open('ptables.dat')                 
 
            TorpList = SatData['pressure']

            Torp = self.P

            UpperValue = 22064.0

            LowerValue = 1.0

        elif torp == 0:
            SatData = shelve.open('Temptables.dat')                 
 
            TorpList = SatData['temp']

            Torp = self.T

            UpperValue = 373.95

            LowerValue = 0.01     

        List1 = ['volume' , 'energy' , 'enthalpy' , 'entropy']

        List2 = ['vf' , 'vg' , 'uf' , 'ug' , 'hf' , 'hg' , 'sf' , 'sg']
 
        OtherState = self.GivenStates[0]

        OtherValue = self.StateList[OtherState][0]

        TempIndex = List1.index(OtherState)

        if Torp in TorpList:
       
            TempList = [] 
    
            index = TorpList.index(Torp)
 
            for state in self.SatList:

                TempList.append(SatData[state][index])
                                                     
            VapourState = SatData[List2[2 * TempIndex + 1]][index]

            FluidState = SatData[List2[2 * TempIndex]][index]

            if OtherValue >=FluidState and VapourState >= OtherValue:          

                x = (OtherValue - FluidState) / (VapourState - FluidState)
        
                self.x = x
            
                self.T = SatData['temp'][index]
          
                self.v = SatData['vf'][index] + x * (SatData['vg'][index] - SatData['vf'][index])

                self.u = SatData['uf'][index] + x * (SatData['ug'][index] -SatData['uf'][index])
     
                self.h = SatData['hf'][index] + x * (SatData['hg'][index] -SatData['hf'][index])
          
                self.s = SatData['sf'][index] + x * (SatData['sg'][index] -SatData['sf'][index])

                SatData.close()
                return     

        elif Torp >= LowerValue and UpperValue >= Torp: 

            #If P lies in between 1 and 22064 kPa , use the Saturated Pressure Tables to interpolate for a given pressure and follow the same procedure as above. 
                                     
            index = bisect.bisect_left(TorpList , Torp)     

            Isobar = [SatData['temp'][index - 1] , SatData['pressure'][index - 1] ,SatData['vf'][index - 1] , SatData['vg'][index - 1] , SatData['uf'][index - 1] ,
SatData['ug'][index - 1] , SatData['hf'][index - 1] , SatData['hg'][index - 1] ,SatData['sf'][index - 1] , SatData['sg'][index - 1]]

            Isobar2 =  [SatData['temp'][index] , SatData['pressure'][index] ,SatData['vf'][index] , SatData['vg'][index] , SatData['uf'][index] ,
SatData['ug'][index] , SatData['hf'][index] , SatData['hg'][index] ,SatData['sf'][index] , SatData['sg'][index]]

            TempList = self.interpolate(Torp , torp ,Isobar , Isobar2)
  
            if TempList: 
                self.T = TempList[0]
                self.P = TempList[1]             

                TempList.remove(self.T)

                TempList.remove(self.P)

                if OtherValue >= TempList[TempIndex * 2] and TempList[TempIndex * 2 + 1] >= OtherValue:               

                    x = (OtherValue - TempList[TempIndex * 2]) / (TempList[TempIndex * 2 + 1] - TempList[TempIndex * 2])
        
                    self.x = x
           
                    self.v = TempList[0] + x * (TempList[1] - TempList[0])

                    self.u = TempList[2] + x * (TempList[3] - TempList[2])
     
                    self.h = TempList[4] + x * (TempList[5] - TempList[4])
          
                    self.s = TempList[6] + x * (TempList[7] - TempList[6])

                    SatData.close() 
                    return   



    def _PressureSearch(self):
       #super.dat is a database file containing the superheated tables which was scraped from this website 'http://www.ohio.edu/mechanical/thermo/property_tables/H2O/' It opens a dictionary having pressure as the key value and the other values stored as lists of lists.For example data['20'] will give the entire superheated data for the pressure 20 kPa

        self.GivenStates.remove('pressure')

        SuperheatedData = shelve.open('super.dat')

        #Storing it as float numbers because the user can input float also
        
        PressureList = map(lambda x : float(x) ,SuperheatedData.keys())
        
        
        #Storing the Pressure values in a sorted list , since in a dictionary it is kept in a random order
        PressureList.sort()

        #Checking if the input Pressure is present in the super.dat file
       
        if self.P in PressureList:

            #If present find out the corresponding subtables for the given pressure
            PressureIndex = PressureList.index(self.P)
            
            Isotherm = SuperheatedData[str(int(self.P))]

            TempList = self._helper(Isotherm)
 
            if TempList:
                self.T  =  TempList[0]
                self.v  =  TempList[1]
                self.h  =  TempList[3]
                self.u  =  TempList[2]
                self.s  =  TempList[4]
                self.x  =  1
                SuperheatedData.close() 
                return  
        
        elif self.P > 10.0 and self.P < 20000.0:

            '''If pressure is not present in between 10 and 20000 kPa , then interpolate once to find the pressure between two pressures , and then interpolate again to find the values for the corresponding states'''

            OtherState = self.GivenStates[0]
          
            PressureIndex = bisect.bisect_left(PressureList , self.P)

            PrevIndex = PressureIndex - 1  
        
            Isotherm1 = SuperheatedData[str(int(PressureList[PressureIndex]))] 

            Isotherm2 = SuperheatedData[str(int(PressureList[PrevIndex]))]

            TempList1 = self._helper(Isotherm1)
           
            TempList2 = self._helper(Isotherm2)
            if TempList1 and TempList2:
                del TempList1[self.StateList[OtherState][1] - 1]

                TempList1.insert(0 , PressureList[PressureIndex])

                TempList2 = self._helper(Isotherm2)
 
                del TempList2[self.StateList[OtherState][1] - 1]

                TempList2.insert(0 , PressureList[PrevIndex])

                TempList = self.interpolate(self.P , 0 ,TempList2 , TempList1)
                self.v  =  TempList[1]
                self.h  =  TempList[3]
                self.u  =  TempList[2]
                self.s  =  TempList[4]
                self.x  =  1  
                SuperheatedData.close()

       #ptables.dat is a database file consisting of saturated data for pressure values ranging from 1kPa to 22064 kPa 

        if 'temp' not in self.GivenStates[0]:
            self._QualityHelper(1)
        
    def _TemperatureSearch(self):

        '''TemperatureSearch is a private function used to search for other properties when temperature and any other property is given.'''
        self.GivenStates.remove('temp')

        SuperheatedData = shelve.open('super.dat')
                
        PressureList = map(lambda x : int(x) ,SuperheatedData.keys())
                        
        PressureList.sort()

        TemperatureList = []

        #Storing the values corresponding to a given temperature for all pressure

        for pressure in PressureList:
            TempList = [] 

            Isobars= SuperheatedData[str(pressure)]

            for Isobar in Isobars:

                TempList.append(Isobar[0])
 
            if self.T in TempList:

                index = TempList.index(self.T)
                 
                List = Isobars[index]
            
                List.insert(0 , pressure)
 
                TemperatureList.append(List)

            elif self.T >= TempList[0] and TempList[-1] >= self.T:
                index = bisect.bisect_left(TempList , self.T)

                PrevIndex = index - 1 

                Isobar1 = Isobars[index] 

                Isobar2 = Isobars[PrevIndex]

                List = self.interpolate(self.T, 0 ,Isobar2,Isobar1)

                List.insert(0 , pressure)

                TemperatureList.append(List)

        OtherStateIndex =  self.StateList[self.GivenStates[0]][1]

        OtherValue = self.StateList[self.GivenStates[0]][0]

        OtherValueList = []

        if TemperatureList and OtherValueList:    

            for Temperature in TemperatureList:
              
                OtherValueList.append(Temperature[OtherStateIndex]) 
 
            if OtherValue in OtherValueList:
           
                ValueFlag = OtherValueList.index(OtherValue)

                Answer = TemperatureList[ValueFlag]

                self.x = 1

                self.P = Answer[0]

                self.v = Answer[2]

                self.u = Answer[3]

                self.h = Answer[4]

                self.s = Answer[5]

                SuperheatedData.close()
                return             

            elif OtherValue <= OtherValueList[0] and OtherValue >= OtherValueList[-1]:

                length = len(OtherValueList)
            
                OtherValueList.reverse()

                temp = bisect.bisect_left(OtherValueList , OtherValue)
            
                ValueFlag1 = length  -1 -temp

                ValueFlag2 = ValueFlag1 + 1

                Answer = self.interpolate(OtherValue,OtherStateIndex,TemperatureList[ValueFlag2] , TemperatureList[ValueFlag1])

                self.x = 1

                self.P = Answer[0]

                self.v = Answer[2]

                self.u = Answer[3]

                self.h = Answer[4]

                self.s = Answer[5]

                SuperheatedData.close()
                return

        if 'pressure' not in self.GivenStates:
            self._QualityHelper(0)
  
