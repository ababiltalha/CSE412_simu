import numpy as np

QLimit = 100
IsBusy : bool
Events = ["Arrival", "Departure", "EndSimulation"]

NextEventType : str

NumCustsDelayed : int
NumDelaysRequired : int
NumEvents : int
NumInQ : int
ServerStatus : int

AreaNumInQ : float
AreaServerStatus : float
MeanInterArrival : float
MeanService : float
Time : float
TimeLastEvent : float
TotalOfDelays : float

TimeArrival : [float] * (QLimit + 1)
TimeNextEvent : [float] * 3

InFile = open("in.txt", "r")
# OutFile = open("out.txt", "w")


def input():
    with InFile as file:
        line = file.readline()

    A, S, N = map(float, line.split())

    # print("Mean inter-arrival time:", A)
    # print("Mean service time:", S)
    # print("Total number of delays:", N)
    
    return A, S, N

def initialize():
    MeanInterArrival, MeanService, NumDelaysRequired = input()
    print("Mean inter-arrival time:", MeanInterArrival)
    print("Mean service time:", MeanService)
    print("Total number of delays:", NumDelaysRequired)
    
def timing():
    pass

def arrive():
    pass

def depart():
    pass

def report():
    pass

def updateTimeAvgStats():
    pass

def exponential(mean):
    pass

def main():
    initialize()
    
    
    
if __name__ == "__main__":
    main()
    