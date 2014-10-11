# -*- coding: utf-8 -*-
"""
Created on Fri Oct 10 20:18:24 2014

@author: Noah
"""
import numpy as np
import itertools as it
import matplotlib.pyplot as plt


class Task(object):
    def __init__(self,ID,priority,minStartTime,maxStartTime):
        self.ID = ID
        self.priority = priority
        self.minStartTime = minStartTime
        self.maxStartTime = maxStartTime
        self.powerConsumption = []
        
    def setTaskLength(self):
        self.taskLength = len(self.powerConsumption)
              

def generatePossibleAllowableSchedules(taskList,lengthOfTimeUnderStudy):
    # come up with a list of possible start times for each task
    allTaskStartTimes = []
    for task in taskList:
        allowableTaskStartTimes = []
        lastAllowableStartTime = min([task.maxStartTime,lengthOfTimeUnderStudy-task.taskLength])
        for startTime in range(task.minStartTime,lastAllowableStartTime + 1):
            allowableTaskStartTimes.append((task,startTime))
        allTaskStartTimes.append(allowableTaskStartTimes)
        
    # now create matrices of possible combinations of start times for all tasks
    combinedAllowableStartTimes = list(it.product(*allTaskStartTimes))
    allowableSchedules = []
    for combinedAllowableStartTime in combinedAllowableStartTimes:
        taskLevel = 0
        scheduleMatrix = np.zeros((len(taskList),lengthOfTimeUnderStudy))
        for taskStartTime in combinedAllowableStartTime:
            task = taskStartTime[0]
            startTime = taskStartTime[1]           
            timePeriodStep = 0
            for time in range(startTime,startTime + task.taskLength):
                scheduleMatrix[taskLevel,time] = task.powerConsumption[timePeriodStep]
                timePeriodStep += 1
            taskLevel += 1
        allowableSchedules.append(scheduleMatrix)
        
    return allowableSchedules
    
    
def evaluateSchedule(schedule,renewablePowerSchedule):
    print(schedule)
    energyConsumptionSchedule = schedule.sum(axis=0)
    for timeStep in range(0,len(energyConsumptionSchedule)):
        if energyConsumptionSchedule[timeStep] > renewablePowerSchedule[timeStep]:
            print("Schedule rejected!")
            return 100000000000000 # because we never want to pick this in the minimization
    powerDifference = renewablePowerSchedule - energyConsumptionSchedule
    score = powerDifference.sum()
    print("Schedule accepted with score of " + str(score))
    return score
    
    
def optimizePowerSchedules(allowableSchedules,lengthOfTimeUnderStudy,renewablePowerSchedule):
    bestScheduleScore = 100000000000000 # goal is to minimize the score
    bestEnergyConsumptionSchedule = []
    for scheduleIndex,schedule  in enumerate(allowableSchedules):
        scheduleScore = evaluateSchedule(schedule,renewablePowerSchedule)
        if scheduleScore < bestScheduleScore:
            bestScheduleScore = scheduleScore
            bestEnergyConsumptionSchedule = schedule
            
    # handle if no match is found
    if len(bestEnergyConsumptionSchedule) > 0:
        # present the results
        timeRange = np.arange(0,lengthOfTimeUnderStudy)
        print("Renewable power available: " + str(renewablePowerSchedule))
        print("Power consumed by the best selected schedule: " + str(bestEnergyConsumptionSchedule))
        print("Unused available renewable power: " + str(renewablePowerSchedule - bestEnergyConsumptionSchedule.sum(axis=0)))
        plt.figure()
        plt.suptitle("Comparison of renewable energy available and optimum schedule")
        supply, = plt.plot(timeRange,renewablePowerSchedule,label="Renewable Supply Schedule",color="blue",marker='*')  
        plt.hold()
        demand, = plt.plot(timeRange,bestEnergyConsumptionSchedule.sum(axis=0),':k',label="Energy Consumption Schedule",color="red",marker="o")
#        plt.legend([supply,demand])   
        plt.legend([supply,demand],["Renewable Supply Schedule","Energy Consumption Schedule"])
        plt.show()
        return bestEnergyConsumptionSchedule
    else:
        print("A schedule match was not found!  We'll need to use some non-renewable energy :(")
        return("A schedule match was not found!  We'll need to use some non-renewable energy :(")
    
    
def test_PerfectFit():
    """
    Values are slected to perfectly line up, with only one suitable solution.
    """
    task1 = Task(1,0.5,0,9)
    task1.powerConsumption = [5,5,5,5,4,4]
    task1.setTaskLength()
    task2 = Task(2,0.5,0,9)
    task2.powerConsumption = [1,1,5,5,5,5]
    task2.setTaskLength()
    taskList = [task1,task2]
    lengthOfTimeUnderStudy=10
    allowableSchedules = generatePossibleAllowableSchedules(taskList,lengthOfTimeUnderStudy)
    renewablePowerSchedule = np.ones((lengthOfTimeUnderStudy)) * 5
    bestEnergyConsumptionSchedule = optimizePowerSchedules(allowableSchedules,lengthOfTimeUnderStudy,renewablePowerSchedule)
    return renewablePowerSchedule,bestEnergyConsumptionSchedule


def test_NoFit_TooLowCapacity():
    """
    Should return a failure, by modifying test_PerfectFit up at one bit
    """
    task1 = Task(1,0.5,0,9)
    task1.powerConsumption = [5,5,5,5,4,4]
    task1.setTaskLength()
    task2 = Task(2,0.5,0,9)
    task2.powerConsumption = [2,1,5,5,5,5]
    task2.setTaskLength()
    taskList = [task1,task2]
    lengthOfTimeUnderStudy=10
    allowableSchedules = generatePossibleAllowableSchedules(taskList,lengthOfTimeUnderStudy)
    renewablePowerSchedule = np.ones((lengthOfTimeUnderStudy)) * 5
    bestEnergyConsumptionSchedule = optimizePowerSchedules(allowableSchedules,lengthOfTimeUnderStudy,renewablePowerSchedule)
    return renewablePowerSchedule,bestEnergyConsumptionSchedule   
    
    
def test_NoFit_TooLittleTime():
    """
    Should return a failure, by shortening the time available in test_PerfectFit
    """
    task1 = Task(1,0.5,0,9)
    task1.powerConsumption = [5,5,5,5,4,4]
    task1.setTaskLength()
    task2 = Task(2,0.5,0,9)
    task2.powerConsumption = [1,1,5,5,5,5]
    task2.setTaskLength()
    taskList = [task1,task2]
    lengthOfTimeUnderStudy=9
    allowableSchedules = generatePossibleAllowableSchedules(taskList,lengthOfTimeUnderStudy)
    renewablePowerSchedule = np.ones((lengthOfTimeUnderStudy)) * 5
    bestEnergyConsumptionSchedule = optimizePowerSchedules(allowableSchedules,lengthOfTimeUnderStudy,renewablePowerSchedule)
    return renewablePowerSchedule,bestEnergyConsumptionSchedule
    
    
def test_Random():
    """
    May or may not fit.  Keep running until it does.  Best for illustration.
    """
    lengthOfTimeUnderStudy=20
    task1 = Task(1,0.5,0,9)
    task1.powerConsumption = np.random.randint(3,7,(8))
    task1.setTaskLength()
    task2 = Task(2,0.5,3,4)
    task2.powerConsumption = np.random.randint(4,9,(4))
    task2.setTaskLength()
    task3 = Task(3,0.5,7,7)
    task3.powerConsumption = np.random.randint(1,3,(2))
    task3.setTaskLength()
    task4 = Task(4,0.5,0,lengthOfTimeUnderStudy)
    task4.powerConsumption = np.random.randint(1,6,(np.random.randint(0,lengthOfTimeUnderStudy)))
    task4.setTaskLength()
    taskList = [task1,task2,task3,task4]
    allowableSchedules = generatePossibleAllowableSchedules(taskList,lengthOfTimeUnderStudy)
    renewablePowerSchedule = np.random.randint(5,15,(lengthOfTimeUnderStudy))
    bestEnergyConsumptionSchedule = optimizePowerSchedules(allowableSchedules,lengthOfTimeUnderStudy,renewablePowerSchedule)
    return renewablePowerSchedule,bestEnergyConsumptionSchedule