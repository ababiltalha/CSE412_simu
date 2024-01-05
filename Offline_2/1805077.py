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
DEMAND = 2
END = 3
EVALUATE = 4

InFilePath = "in.txt"
OutFilePath = "out.txt"

class InventorySystem:
    def __init__(self, InFile, OutFile, numEvents=4):
        self.inFile = InFile
        self.outFile = OutFile
        
        self.amount = 0
        self.bigs = 0
        self.initialInvLevel = 0
        self.invLevel = 0
        self.nextEventType = NONE        
        self.numEvents = numEvents
        self.numMonths = 0
        self.numValuesDemand = 0
        self.smalls = 0
        
        self.areaHolding = 0.0
        self.areaShortage = 0.0
        self.holdingCost = 0.0
        self.incrementalCost = 0.0
        self.maxLag = 0.0
        self.meanInterDemand = 0.0
        self.minLag = 0.0
        self.setupCost = 0.0
        self.shortageCost = 0.0
        self.simTime = 0.0
        self.timeLastEvent = 0.0
        self.timeNextEvent = [0.0] * (self.numEvents + 1)
        self.totalOrderingCost = 0.0
        self.probDistribDemand = [0.0] * (self.numValuesDemand + 1)
        
        self.numPolicies = 0
        self.policies = []      # list of [s, S]
        
        self.generator = lcgrand()

    def input(self):        
        with self.inFile as file:
            line = file.readline()
            self.initialInvLevel, self.numMonths, self.numPolicies = map(int, line.split())
            
            line = file.readline()
            self.numValuesDemand, self.meanInterDemand = map(float, line.split())
            self.numValuesDemand = int(self.numValuesDemand)
            
            line = file.readline()
            self.setupCost, self.incrementalCost, self.holdingCost, self.shortageCost = map(float, line.split())
            
            line = file.readline()
            self.minLag, self.maxLag = map(float, line.split())
            
            line = file.readline()
            self.probDistribDemand = list(map(float, line.split()))
            
            self.policies = []
            for i in range(self.numPolicies):
                line = file.readline()
                self.policies.append(list(map(int, line.split())))

    def reportHeader(self):
        self.outFile.write("------Single-Product Inventory System------\n\n")
        self.outFile.write("Initial inventory level: %d items\n\n" % (self.initialInvLevel))
        self.outFile.write("Number of demand sizes: %d\n\n" % (self.numValuesDemand))
        self.outFile.write("Distribution function of demand sizes: ")
        for i in range(self.numValuesDemand):
            self.outFile.write("%.2f " % (self.probDistribDemand[i]))
        self.outFile.write("\n\n")
        self.outFile.write("Mean inter-demand time: %.2f months\n\n" % (self.meanInterDemand))
        self.outFile.write("Delivery lag range: %.2f to %.2f months\n\n" % (self.minLag, self.maxLag))
        self.outFile.write("Length of simulation: %d months\n\n" % (self.numMonths))
        self.outFile.write("Costs:\n")
        self.outFile.write("K = %.2f\n" % (self.setupCost))
        self.outFile.write("i = %.2f\n" % (self.incrementalCost))
        self.outFile.write("h = %.2f\n" % (self.holdingCost))
        self.outFile.write("pi = %.2f\n\n" % (self.shortageCost))
        self.outFile.write("Number of policies: %d\n\n" % (self.numPolicies))
        self.outFile.write("Policies:\n")
        self.outFile.write("--------------------------------------------------------------------------------------------------\n")
        self.outFile.write(" Policy        Avg_total_cost     Avg_ordering_cost      Avg_holding_cost     Avg_shortage_cost\n")
        self.outFile.write("--------------------------------------------------------------------------------------------------\n\n")
    
    def report(self):
        avgOrderingCost = self.totalOrderingCost / self.numMonths
        avgHoldingCost = self.areaHolding * self.holdingCost / self.numMonths
        avgShortageCost = self.areaShortage * self.shortageCost / self.numMonths
        str = "(%2d,%3d)              %6.2f              %6.2f               %6.2f               %6.2f\n\n" % (self.smalls, self.bigs, avgOrderingCost + avgHoldingCost + avgShortageCost, avgOrderingCost, avgHoldingCost, avgShortageCost)
        self.outFile.write(str)
        
    
    def simulate(self):
        for i in range(self.numPolicies):
            self.simulatePolicy(self.policies[i][0], self.policies[i][1])
            # print(self.simTime)
        self.outFile.write("--------------------------------------------------------------------------------------------------")        

    def simulatePolicy(self, s, S):
        self.smalls = s
        self.bigs = S
        self.initialize()
        
        while True:
            self.timing()
            self.updateTimeAvgStats()
            
            if self.nextEventType == ARRIVAL:
                self.arrival()
            elif self.nextEventType == DEMAND:
                self.demand()
            elif self.nextEventType == EVALUATE:
                self.evaluate()
            elif self.nextEventType == END:
                self.report()
                
            if self.nextEventType == END:
                break
                
    def initialize(self):
        self.simTime = 0.0
        self.invLevel = self.initialInvLevel
        self.timeLastEvent = 0.0
        
        self.totalOrderingCost = 0.0
        self.areaHolding = 0.0
        self.areaShortage = 0.0
        
        self.timeNextEvent[ARRIVAL] = 1.0e+30
        self.timeNextEvent[DEMAND] = self.simTime + self.exponential(self.meanInterDemand)
        self.timeNextEvent[END] = self.numMonths
        self.timeNextEvent[EVALUATE] = 0.0
        
    def arrival(self):
        self.invLevel = self.invLevel + self.amount
        self.timeNextEvent[ARRIVAL] = 1.0e+30
        
    def demand(self):
        self.invLevel = self.invLevel - self.randomInt(self.probDistribDemand)
        self.timeNextEvent[DEMAND] = self.simTime + self.exponential(self.meanInterDemand)
        
    def randomInt(self, probDistrib):
        u = self.generator.lcgrand(1)
        i = 0
        while u > probDistrib[i]:
            i = i + 1
        return i
    
    def exponential(self, mean):
        return -mean * math.log(self.generator.lcgrand(1))
        
    def evaluate(self):
        if self.invLevel < self.smalls:
            self.amount = self.bigs - self.invLevel
            self.totalOrderingCost += self.setupCost + self.incrementalCost * self.amount
            self.timeNextEvent[ARRIVAL] = self.simTime + self.uniform(self.minLag, self.maxLag)
        self.timeNextEvent[EVALUATE] = self.simTime + 1.0
        
    def uniform(self, a, b):
        return a + (b - a) * self.generator.lcgrand(1)
    
    def updateTimeAvgStats(self):
        timeSinceLastEvent = self.simTime - self.timeLastEvent
        self.timeLastEvent = self.simTime
        
        if self.invLevel < 0:
            self.areaShortage -= self.invLevel * timeSinceLastEvent
        elif self.invLevel > 0:
            self.areaHolding += self.invLevel * timeSinceLastEvent
        

    def timing(self):
        minTimeNextEvent = 1.0e+29
        self.nextEventType = NONE
        
        for i in range(1, self.numEvents + 1):
            if self.timeNextEvent[i] < minTimeNextEvent:
                minTimeNextEvent= self.timeNextEvent[i]
                self.nextEventType = i
        
        if self.nextEventType == NONE:
            print("Event list empty at time", self.simTime)
            exit()
        self.simTime = minTimeNextEvent

def main():
    inFile = open(InFilePath, "r")
    outFile = open(OutFilePath, "w")
    inventorySystem = InventorySystem(inFile, outFile)
    inventorySystem.input()
    inventorySystem.reportHeader()
    inventorySystem.simulate()
    inFile.close()
    outFile.close()
 
if __name__ == "__main__":
    main()
    