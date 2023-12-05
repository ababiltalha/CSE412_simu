import math
import lcgrand

NONE = 0
ARRIVAL = 1
DEPARTURE = 2

InFilePath = "IOs/io3/in.txt"

class SingleServerQueueingSystem:
    def __init__(self, InFile, ResultsFile, EventOrdersFile, NumEvents=2):
        self.InFile = InFile
        self.ResultsFile = ResultsFile
        self.EventOrdersFile = EventOrdersFile
        
        self.QLimit = 100
        
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

        self.TimeArrival = [0.0] * (self.QLimit + 1)
        self.TimeNextEvent = [0.0] * 3
        
        self.EventCount = 0
        self.NumCustsArrived = 0
        self.NumCustsDeparted = 0
        self.lcgrand = lcgrand.lcgrand()

    def input(self):
        with self.InFile as file:
            line = file.readline()

        A, S, N = map(float, line.split())

        # print("Mean inter-arrival time:", A)
        # print("Mean service time:", S)
        # print("Total number of delays:", N)

        return A, S, N

    def initialize(self):
        self.MeanInterArrival, self.MeanService, self.NumDelaysRequired = self.input()

        self.ResultsFile.write("----Single-Server Queueing System----\n\n")
        self.ResultsFile.write("Mean inter-arrival time: {:.6f} minutes\n".format(self.MeanInterArrival))
        self.ResultsFile.write("Mean service time: {:.6f} minutes\n".format(self.MeanService))
        self.ResultsFile.write("Number of customers: {}\n".format(int(self.NumDelaysRequired)))

        self.Time = 0.0
        self.ServerBusy = False
        self.NumInQ = 0
        self.TimeLastEvent = 0.0

        self.NumCustsDelayed = 0
        self.TotalOfDelays = 0.0
        self.AreaNumInQ = 0.0
        self.AreaServerStatus = 0.0

        self.TimeNextEvent[ARRIVAL] = self.Time + self.exponential(self.MeanInterArrival)
        self.TimeNextEvent[DEPARTURE] = 1.0e+30

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
        self.EventOrdersFile.write("{}. Next event: ".format(self.EventCount))
        
        if self.NextEventType == ARRIVAL:
            self.NumCustsArrived = self.NumCustsArrived + 1
            self.EventOrdersFile.write("Customer {} Arrival\n".format(self.NumCustsArrived))
        elif self.NextEventType == DEPARTURE:
            self.NumCustsDeparted = self.NumCustsDeparted + 1
            self.EventOrdersFile.write("Customer {} Departure\n".format(self.NumCustsDeparted))
        
        self.Time = minTimeNextEvent

    def arrive(self):
        self.TimeNextEvent[ARRIVAL] = self.Time + self.exponential(self.MeanInterArrival)

        if self.ServerBusy:
            self.NumInQ = self.NumInQ + 1
            if self.NumInQ > self.QLimit:
                print("Queue overflow at time", self.Time)
                exit()
            self.TimeArrival[self.NumInQ] = self.Time

        else:
            self.NumCustsDelayed = self.NumCustsDelayed + 1
            self.EventOrdersFile.write("\n---------No. of customers delayed: {}--------\n\n".format(self.NumCustsDelayed))
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
            self.EventOrdersFile.write("\n---------No. of customers delayed: {}--------\n\n".format(self.NumCustsDelayed))
            self.TimeNextEvent[DEPARTURE] = self.Time + self.exponential(self.MeanService)

            for i in range(1, self.NumInQ + 1):
                self.TimeArrival[i] = self.TimeArrival[i + 1]

    def report(self):
        self.ResultsFile.write("\n")
        self.ResultsFile.write("Avg delay in queue: {:.6f} minutes\n".format(self.TotalOfDelays / self.NumCustsDelayed))
        self.ResultsFile.write("Avg number in queue: {:.6f}\n".format(self.AreaNumInQ / self.Time))
        self.ResultsFile.write("Server utilization: {:.6f}\n".format(self.AreaServerStatus / self.Time))
        self.ResultsFile.write("Time simulation ended: {:.6f} minutes\n".format(self.Time))

    def updateTimeAvgStats(self):
        timeSinceLastEvent = self.Time - self.TimeLastEvent
        self.TimeLastEvent = self.Time

        self.AreaNumInQ = self.AreaNumInQ + self.NumInQ * timeSinceLastEvent
        self.AreaServerStatus = self.AreaServerStatus + self.ServerBusy * timeSinceLastEvent

    def exponential(self, mean):
        return -mean * math.log(self.lcgrand.lcgrand(1))

    def simulate(self):
        self.initialize()

        while self.NumCustsDelayed < self.NumDelaysRequired:
            self.timing()
            self.updateTimeAvgStats()

            if self.NextEventType == ARRIVAL:
                self.arrive()
            elif self.NextEventType == DEPARTURE:
                self.depart()

        self.report()

def main():
    InFile = open(InFilePath, "r")
    ResultsFile = open("results.txt", "w")
    EventOrdersFile = open("event_orders.txt", "w")
    
    singleServerQueueingSystem = SingleServerQueueingSystem(InFile=InFile, ResultsFile=ResultsFile, EventOrdersFile=EventOrdersFile)
    singleServerQueueingSystem.simulate()
    
    InFile.close()
    ResultsFile.close()
    EventOrdersFile.close()
    
 
if __name__ == "__main__":
    main()
    