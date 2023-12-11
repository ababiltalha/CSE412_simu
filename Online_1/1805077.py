import math

class lcgrand:
    def __init__(self):
        self.MODLUS = 2147483647
        self.MULT1  = 24112
        self.MULT2  = 26143

        self.zrng = [1,
                1973272912, 281629770, 20006270,1280689831,2096730329,1933576050,
                913566091, 246780520,1363774876, 604901985,1511192140,1259851944,
                824064364, 150493284, 242708531, 75253171,1964472944,1202299975,
                233217322,1911216000, 726370533, 403498145, 993232223,1103205531,
                762430696,1922803170,1385516923, 76271663, 413682397, 726466604,
                336157058,1432650381,1120463904, 595778810, 877722890,1046574445,
                68911991,2088367019, 748545416, 622401386,2122378830, 640690903,
                1774806513,2132545692,2079249579, 78130110, 852776735,1187867272,
                1351423507,1645973084,1997049139, 922510944,2045512870, 898585771,
                243649545,1004818771, 773686062, 403188473, 372279877,1901633463,
                498067494,2087759558, 493157915, 597104727,1530940798,1814496276,
                536444882,1663153658, 855503735, 67784357,1432404475, 619691088,
                119025595, 880802310, 176192644,1116780070, 277854671,1366580350,
                1142483975,2026948561,1053920743, 786262391,1792203830,1494667770,
                1923011392,1433700034,1244184613,1147297105, 539712780,1545929719,
                190641742,1645390429, 264907697, 620389253,1502074852, 927711160,
                364849192,2049576050, 638580085, 547070247]
        
    def lcgrand(self, stream):
        zi = self.zrng[stream]
        lowprd = (zi & 65535) * self.MULT1
        hi31 = (zi >> 16) * self.MULT1 + (lowprd >> 16)
        zi = ((lowprd & 65535) - self.MODLUS) + ((hi31 & 32767) << 16) + (hi31 >> 15)
        if zi < 0:
            zi = zi + self.MODLUS
        
        lowprd = (zi & 65535) * self.MULT2
        hi31 = (zi >> 16) * self.MULT2 + (lowprd >> 16)
        zi = ((lowprd & 65535) - self.MODLUS) + ((hi31 & 32767) << 16) + (hi31 >> 15)
        if zi < 0:
            zi = zi + self.MODLUS
            
        self.zrng[stream] = zi
        return (zi >> 7 | 1) / 16777216.0

NONE = 0
ARRIVAL = 1
DEPARTURE = 2
END = 3

InFilePath = "OnlineB/IOs - OnlineB/io1/in.txt"

class SingleServerQueueingSystem:
    def __init__(self, InFile, ResultsFile, EventOrdersFile, NumEvents=2):
        self.InFile = InFile
        self.ResultsFile = ResultsFile
        # self.EventOrdersFile = EventOrdersFile
        
        self.QLimit = 0 
        
        self.NextEventType = NONE
        self.NumCustsDelayed = 0
        self.NumDelaysRequired = 0
        self.NumEvents = NumEvents
        self.NumInQ = 0
        self.ServerBusy = False
        self.EventCount = 0

        self.AreaNumInQ = 0.0
        self.AreaServerStatus = 0.0
        self.MeanInterArrival = 0.0
        self.MeanService = 0.0
        self.Time = 0.0
        self.TimeLastEvent = 0.0
        self.TotalOfDelays = 0.0

        self.TimeArrival = None
        self.TimeNextEvent = [0.0] * 4
        
        self.EventCount = 0
        self.NumCustsArrived = 0
        self.NumCustsDeparted = 0
        self.lcgrand = lcgrand()
        
        self.EndTime = 0.0
        self.BalkingCusts = 0

    def input(self):
        with self.InFile as file:
            line = file.readline()

        A, S, E, Q = map(float, line.split())

        print("Mean inter-arrival time:", A)
        print("Mean service time:", S)
        print("Maximum queue length:", Q)
        print("Simulation end time:", E)

        return A, S, E, Q

    def initialize(self):
        self.MeanInterArrival, self.MeanService, self.EndTime, Q = self.input()

        self.ResultsFile.write("----Single-Server Queueing System----\n\n")
        self.ResultsFile.write("Mean inter-arrival time: {:.6f} minutes\n".format(self.MeanInterArrival))
        self.ResultsFile.write("Mean service time: {:.6f} minutes\n".format(self.MeanService))
        # self.ResultsFile.write("Number of customers: {}\n".format(int(self.NumDelaysRequired)))
        self.ResultsFile.write("Maximum Queue Length: {}\n".format(int(Q)))

        self.Time = 0.0
        self.ServerBusy = False
        self.NumInQ = 0
        self.TimeLastEvent = 0.0
        # print(Q)
        self.QLimit = int(Q)
        # print(self.QLimit)
        self.TimeArrival = [0.0] * (self.QLimit + 1)

        self.NumCustsDelayed = 0
        self.TotalOfDelays = 0.0
        self.AreaNumInQ = 0.0
        self.AreaServerStatus = 0.0
        
        self.BalkingCusts = 0

        self.TimeNextEvent[ARRIVAL] = self.Time + self.exponential(self.MeanInterArrival)
        self.TimeNextEvent[DEPARTURE] = 1.0e+30
        self.TimeNextEvent[END] = self.EndTime

    def timing(self):
        minTimeNextEvent = 1.0e+29
        self.NextEventType = NONE

        for i in range(1, self.NumEvents + 1):
            if self.TimeNextEvent[i] < minTimeNextEvent:
                minTimeNextEvent = self.TimeNextEvent[i]
                self.NextEventType = i

        if self.NextEventType == NONE:
            print("Event list empty at time", self.Time)
            exit()
        
        self.EventCount = self.EventCount + 1
        # self.EventOrdersFile.write("{}. Next event: ".format(self.EventCount))
        
        if self.NextEventType == ARRIVAL:
            self.NumCustsArrived = self.NumCustsArrived + 1
            # self.EventOrdersFile.write("Customer {} Arrival\n".format(self.NumCustsArrived))
        elif self.NextEventType == DEPARTURE:
            self.NumCustsDeparted = self.NumCustsDeparted + 1
            # self.EventOrdersFile.write("Customer {} Departure\n".format(self.NumCustsDeparted))
        
        self.Time = minTimeNextEvent

    def arrive(self):
        self.TimeNextEvent[ARRIVAL] = self.Time + self.exponential(self.MeanInterArrival)

        if self.ServerBusy:
            self.NumInQ = self.NumInQ + 1
            if self.NumInQ > self.QLimit:
                # Balking
                self.NumInQ = self.NumInQ - 1
                self.BalkingCusts = self.BalkingCusts + 1
            else:
                self.TimeArrival[self.NumInQ] = self.Time

        else:
            self.NumCustsDelayed = self.NumCustsDelayed + 1
            # self.EventOrdersFile.write("\n---------No. of customers delayed: {}--------\n\n".format(self.NumCustsDelayed))
            self.ServerBusy = True
            self.TimeNextEvent[DEPARTURE] = self.Time + self.exponential(self.MeanService)

    def depart(self):
        if self.NumInQ == 0:
            self.ServerBusy = False
            self.TimeNextEvent[DEPARTURE] = 1.0e+30
        else:
            self.NumInQ = self.NumInQ - 1
            delay = self.Time - self.TimeArrival[1]
            self.TotalOfDelays = self.TotalOfDelays + delay

            self.NumCustsDelayed = self.NumCustsDelayed + 1
            # self.EventOrdersFile.write("\n---------No. of customers delayed: {}--------\n\n".format(self.NumCustsDelayed))
            self.TimeNextEvent[DEPARTURE] = self.Time + self.exponential(self.MeanService)

            for i in range(1, self.NumInQ + 1):
                self.TimeArrival[i] = self.TimeArrival[i + 1]

    def report(self):
        self.ResultsFile.write("\n")
        self.ResultsFile.write("Avg delay in queue: {:.6f} minutes\n".format(self.TotalOfDelays / self.NumCustsDelayed))
        self.ResultsFile.write("Avg number in queue: {:.6f}\n".format(self.AreaNumInQ / self.Time))
        self.ResultsFile.write("Server utilization: {:.6f}\n".format(self.AreaServerStatus / self.Time))
        self.ResultsFile.write("Time simulation ended: {:.6f} minutes\n".format(self.Time))
        
        self.ResultsFile.write("\n")
        self.ResultsFile.write("Total number of Balking customers: {}\n".format(self.BalkingCusts))
        self.ResultsFile.write("Total number of customers delayed: {}\n".format(self.NumCustsDelayed))
        self.ResultsFile.write("Percentage of Balking customers: {:.6f} %".format(self.BalkingCusts / (self.BalkingCusts + self.NumCustsDelayed) * 100))

    def updateTimeAvgStats(self):
        timeSinceLastEvent = self.Time - self.TimeLastEvent
        self.TimeLastEvent = self.Time

        self.AreaNumInQ = self.AreaNumInQ + self.NumInQ * timeSinceLastEvent
        self.AreaServerStatus = self.AreaServerStatus + self.ServerBusy * timeSinceLastEvent

    def exponential(self, mean):
        return -mean * math.log(self.lcgrand.lcgrand(1))

    def simulate(self):
        self.initialize()

        while self.NextEventType != END:
            self.timing()
            self.updateTimeAvgStats()

            if self.NextEventType == ARRIVAL:
                self.arrive()
            elif self.NextEventType == DEPARTURE:
                self.depart()
            elif self.NextEventType == END:
                break

        self.report()

def main():
    InFile = open(InFilePath, "r")
    if not InFile:
        print("Input file not found")
        exit()
    ResultsFile = open("results.txt", "w")
    # EventOrdersFile = open("event_orders.txt", "w")
    
    singleServerQueueingSystem = SingleServerQueueingSystem(InFile=InFile, ResultsFile=ResultsFile, EventOrdersFile=None, NumEvents=3)
    singleServerQueueingSystem.simulate()
    
    InFile.close()
    ResultsFile.close()
    # EventOrdersFile.close()
    
 
if __name__ == "__main__":
    main()
    