# -*- coding: utf-8 -*-
"""
Created on Fri Oct 10 20:18:24 2014

@author: Noah
"""
import numpy as np
import itertools as it
import matplotlib.pyplot as plt


class Task(object):
    def __init__(self,ID,priority,minStartTime,maxStartTime,maxEndTime=100):
        self.ID = ID
        self.priority = priority
        self.minStartTime = minStartTime
        self.maxEndTime = maxEndTime
        self.maxStartTime = maxStartTime
        self.powerConsumption = []
        
        # with tasklets
        self.tasklets = []
        
    def setTaskLength(self):
        self.taskLength = len(self.powerConsumption)

        
class Tasklet(object):
    def __init__(self,ID,maxGap=0):
        self.ID = ID
        self.maxGap = maxGap # this needs to be the max gap after, so the gap after the last tasklet shouldn't matter
        self.powerConsumption = []
        
    def setTaskletLength(self):
        self.taskletLength = len(self.powerConsumption)

def initializeTestTasklets():
    task1 = Task(1,0.5,0,9)
    tasklet11 = Tasklet(1,3)
    tasklet11.powerConsumption = [1,2,3]
    tasklet11.setTaskletLength()
    tasklet12 = Tasklet(2,0)
    tasklet12.powerConsumption = [4,5,6]
    tasklet12.setTaskletLength()
    task1.tasklets = [tasklet11,tasklet12]
    task2 = Task(2,0.5,2,6)
    task2.setTaskLength()
    tasklet21 = Tasklet(1,3)
    tasklet21.powerConsumption = [1,2,3]
    tasklet21.setTaskletLength()
    tasklet22 = Tasklet(2,0)
    tasklet22.powerConsumption = [4,5,6]
    tasklet22.setTaskletLength()
    task2.tasklets = [tasklet21,tasklet22]
    taskList = [task1,task2]
    return taskList
     
def generatePossibleAllowableSchedulesWithTasklets(taskList,lengthOfTimeUnderStudy):
    allProfilesForEachTask = []

    for task in taskList:
        taskProfiles = []
        # we want to add (taskID,start,[gap1,gap2,...,gapn])
        # create the list of possible task gaps
        
        #---------create allowable start times---------------        
        allowableTaskStartTimes = []
#        lastAllowableStartTime = min([task.maxStartTime,lengthOfTimeUnderStudy-task.taskLength])
        lastAllowableStartTime = task.maxStartTime
        for startTime in range(task.minStartTime,lastAllowableStartTime + 1):
            allowableTaskStartTimes.append(startTime)
        
        #---------create possible tasklet gaps---------------
        taskGaps = []
        for tasklet in task.tasklets:
            taskGap = []
            for gap in range(0,tasklet.maxGap + 1):
                taskGap.append(gap)
            taskGaps.append(taskGap)

        # combine one taskGap from each list, all possible permutations
        combinedTaskletGaps = list(it.product(*taskGaps))
        for startTime in allowableTaskStartTimes:
            for taskGap in combinedTaskletGaps:
                # check to make sure the combination doens't exceed the max end time
                taskEnd = startTime
                for i in range(0,len(task.tasklets)):
                    taskEnd += task.tasklets[i].taskletLength
                    for gap in taskGap:
                        taskEnd += gap
                if taskEnd <= task.maxEndTime and taskEnd <= lengthOfTimeUnderStudy:
                    taskProfile = (task,startTime,taskGap)
                    taskProfiles.append(taskProfile)
        allProfilesForEachTask.append(taskProfiles)
    
    combinedAllowableTaskSchedules = list(it.product(*allProfilesForEachTask))
#    return combinedAllowableTaskSchedules
    allowableSchedules = []
    
    for schedule in combinedAllowableTaskSchedules:
        taskLevel = 0
        scheduleMatrix = np.zeros((len(taskList),lengthOfTimeUnderStudy))
        for taskDetails in schedule:
            task = taskDetails[0]
            startTime = taskDetails[1]
            gaps = taskDetails[2]
            time = startTime
            taskletGap = 0
            for tasklet in task.tasklets:
                for step in tasklet.powerConsumption:
                    scheduleMatrix[taskLevel,time] = step
                    time += 1
                for stall in range(0,gaps[taskletGap]):
                    scheduleMatrix[taskLevel,time] = 0
                    time += 1
            taskLevel += 1
        allowableSchedules.append(scheduleMatrix)
        
    
    return allowableSchedules
        
        # now we can build matricies of all possible combinations of start times for all tasks
#        combinedAllowableTaskSchedules = list(it.product(*allProfilesForEachTask))
#        return combinedAllowableTaskSchedules
        




          

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


def evaluateSchedule_CooliPythonVersion(schedule,renewablePowerSchedule):
    """
    2 notes:
        1. only run using something like iPython
        2. takes much much longer, but looks kind of neat for demonstrations
    """
    #    print(schedule)
    print("Schedule under consideration:")
    plt.figure()
    plt.imshow(schedule,cmap="PuRd")
    plt.show()
    energyConsumptionSchedule = schedule.sum(axis=0)
    for timeStep in range(0,len(energyConsumptionSchedule)):
        if energyConsumptionSchedule[timeStep] > renewablePowerSchedule[timeStep]:
            print("Schedule rejected!")
            return 100000000000000 # because we never want to pick this in the minimization
    powerDifference = renewablePowerSchedule - energyConsumptionSchedule
    score = powerDifference.sum()
    print("Schedule accepted with score of " + str(score))
    return score

def evaluateSchedule(schedule,renewablePowerSchedule):
#    print("Schedule under consideration:")
#    print(schedule)
    energyConsumptionSchedule = schedule.sum(axis=0)
    for timeStep in range(0,len(energyConsumptionSchedule)):
        if energyConsumptionSchedule[timeStep] > renewablePowerSchedule[timeStep]:
#            print("Schedule rejected!")
            return 100000000000000 # because we never want to pick this in the minimization
    powerDifference = renewablePowerSchedule - energyConsumptionSchedule
    score = powerDifference.sum()
#    print("Schedule accepted with score of " + str(score))
    return score
    
    
def evaluateSchedule_NonRenewable(schedule,renewablePowerSchedule,totalCapacity=10):
    energyConsumptionSchedule = schedule.sum(axis=0)
    for energyConsumption in energyConsumptionSchedule:
        if energyConsumption > totalCapacity:
            return 100000000000000
    nonRenewableEnergyUsed = 0.0
    powerDifference = renewablePowerSchedule - energyConsumptionSchedule
    for difference in powerDifference:
        if difference < 0:
            nonRenewableEnergyUsed += abs(difference)
    return nonRenewableEnergyUsed
    
def optimizePowerSchedules(allowableSchedules,lengthOfTimeUnderStudy,renewablePowerSchedule):
    bestScheduleScore = 100000000000000 # goal is to minimize the score
    bestEnergyConsumptionSchedule = []
    for scheduleIndex,schedule  in enumerate(allowableSchedules):
        scheduleScore = evaluateSchedule_CooliPythonVersion(schedule,renewablePowerSchedule)
        if scheduleScore < bestScheduleScore:
            bestScheduleScore = scheduleScore
            bestEnergyConsumptionSchedule = schedule
            
    # handle if no match is found
    if len(bestEnergyConsumptionSchedule) > 0:
        # present the results
        timeRange = np.arange(0,lengthOfTimeUnderStudy)
        print("Renewable power available: " + str(renewablePowerSchedule))
        print("Power consumed by the best selected schedule: " + str(bestEnergyConsumptionSchedule))
#        print("Representation of the best schedule:")
        plt.figure()
        plt.suptitle("Representation of the best schedule")
        plt.imshow(bestEnergyConsumptionSchedule,cmap="PuRd",interpolation="nearest")
        plt.axis("off")
        plt.colorbar(orientation="horizontal")
        plt.tight_layout()
        plt.show()
        print("Unused available renewable power: " + str(renewablePowerSchedule - bestEnergyConsumptionSchedule.sum(axis=0)))
        plt.figure()
        plt.suptitle("Comparison of renewable energy available and optimum schedule")
        supply, = plt.plot(timeRange,renewablePowerSchedule,':k',label="Renewable Supply Schedule",color="blue",marker='*')  
        plt.hold()
        demand, = plt.plot(timeRange,bestEnergyConsumptionSchedule.sum(axis=0),label="Energy Consumption Schedule",color="red",marker="o")
        plt.fill_between(timeRange,bestEnergyConsumptionSchedule.sum(axis=0),color='red',alpha=0.5)
        plt.legend([supply,demand],["Renewable Supply Schedule","Energy Consumption Schedule"],loc='best', fancybox=True, framealpha=0.5)
        plt.show()
        return bestEnergyConsumptionSchedule
    else:
        print("A schedule match was not found!  We'll need to use some non-renewable energy :(")
        return("A schedule match was not found!  We'll need to use some non-renewable energy :(")


def optimizePowerSchedules_NonRenewable(allowableSchedules,lengthOfTimeUnderStudy,renewablePowerSchedule):
    bestScheduleScore = 100000000000000 # goal is to minimize the score
    bestEnergyConsumptionSchedule = []
    for scheduleIndex,schedule  in enumerate(allowableSchedules):
        scheduleScore = evaluateSchedule_NonRenewable(schedule,renewablePowerSchedule)
        if scheduleScore < bestScheduleScore:
            bestScheduleScore = scheduleScore
            bestEnergyConsumptionSchedule = schedule        

    # handle if no match is found
    if len(bestEnergyConsumptionSchedule) > 0:
        # present the results
        timeRange = np.arange(0,lengthOfTimeUnderStudy)
        print("Renewable power available: " + str(renewablePowerSchedule))
        print("Power consumed by the best selected schedule: " + str(bestEnergyConsumptionSchedule))
#        print("Representation of the best schedule:")
        plt.figure()
        plt.suptitle("Representation of the best schedule")
        plt.imshow(bestEnergyConsumptionSchedule,cmap="PuRd",interpolation="nearest")
        plt.axis("off")
        plt.colorbar(orientation="horizontal")
        plt.tight_layout()
        plt.show()
        print("Unused available renewable power: " + str(renewablePowerSchedule - bestEnergyConsumptionSchedule.sum(axis=0)))
        plt.figure()
        plt.suptitle("Comparison of renewable energy available and optimum schedule")
        supply, = plt.plot(timeRange,renewablePowerSchedule,':k',label="Renewable Supply Schedule",color="blue",marker='*')  
        plt.hold()
        demand, = plt.plot(timeRange,bestEnergyConsumptionSchedule.sum(axis=0),label="Energy Consumption Schedule",color="red",marker="o")
        plt.fill_between(timeRange,bestEnergyConsumptionSchedule.sum(axis=0),color='red',alpha=0.5)
        plt.legend([supply,demand],["Renewable Supply Schedule","Energy Consumption Schedule"],loc='best', fancybox=True, framealpha=0.5)
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
    
def test_VeryRandom():
    """
    Nothing is guaranteed here.  Should be fun.  Runtime may get long.
    """
    taskList = []
    lengthOfTimeUnderStudy = 20
    renewablePowerSchedule = np.random.randint(20,100,(lengthOfTimeUnderStudy))
    nTasks = np.random.randint(1,6)
    for taskToAdd in range(0,nTasks):
        taskID = taskToAdd
        fixedPriority = 0.5
        randomStart = np.random.randint(0,lengthOfTimeUnderStudy)
        randomEnd = np.random.randint(randomStart,lengthOfTimeUnderStudy)
        task = Task(taskID,fixedPriority,randomStart,randomEnd)
        maxTaskLengthPossible = lengthOfTimeUnderStudy - randomStart
        taskLength = np.random.randint(0,maxTaskLengthPossible)
        taskLow = np.random.randint(0,10)
        taskHigh = np.random.randint(taskLow+1,20)
        task.powerConsumption = np.random.randint(taskLow,taskHigh,(taskLength))
        task.setTaskLength()
        taskList.append(task)
        allowableSchedules = generatePossibleAllowableSchedules(taskList,lengthOfTimeUnderStudy)
    renewablePowerSchedule = np.random.randint(5,15,(lengthOfTimeUnderStudy))
    bestEnergyConsumptionSchedule = optimizePowerSchedules(allowableSchedules,lengthOfTimeUnderStudy,renewablePowerSchedule)
    return renewablePowerSchedule,bestEnergyConsumptionSchedule
        
        
# tests including non-renewables
def test_NonRenewable_TooLowCapacity():
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
    bestEnergyConsumptionSchedule = optimizePowerSchedules_NonRenewable(allowableSchedules,lengthOfTimeUnderStudy,renewablePowerSchedule)
    return renewablePowerSchedule,bestEnergyConsumptionSchedule   


def test_NonRenewable_Random():
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
    bestEnergyConsumptionSchedule = optimizePowerSchedules_NonRenewable(allowableSchedules,lengthOfTimeUnderStudy,renewablePowerSchedule)
    return renewablePowerSchedule,bestEnergyConsumptionSchedule
    
def test_NonRenewable_ConstantRenewable():
    """
    May or may not fit.  Keep running until it does.  Best for illustration.
    """
    lengthOfTimeUnderStudy=20
    task1 = Task(1,0.5,0,9)
    task1.powerConsumption = np.random.randint(6,7,(8))
    task1.setTaskLength()
    task2 = Task(2,0.5,3,4)
    task2.powerConsumption = np.random.randint(5,7,(4))
    task2.setTaskLength()
    task3 = Task(3,0.5,7,7)
    task3.powerConsumption = np.random.randint(1,3,(2))
    task3.setTaskLength()
    task4 = Task(4,0.5,0,lengthOfTimeUnderStudy)
    task4.powerConsumption = np.random.randint(1,6,(np.random.randint(0,lengthOfTimeUnderStudy)))
    task4.setTaskLength()
    taskList = [task1,task2,task3,task4]
    allowableSchedules = generatePossibleAllowableSchedules(taskList,lengthOfTimeUnderStudy)
    renewablePowerSchedule = np.ones(lengthOfTimeUnderStudy) * 15
    bestEnergyConsumptionSchedule = optimizePowerSchedules_NonRenewable(allowableSchedules,lengthOfTimeUnderStudy,renewablePowerSchedule)
    return renewablePowerSchedule,bestEnergyConsumptionSchedule

#-------------------Tasklets-------------------------
def test_NonRenewable_Tasklets():
    lengthOfTimeUnderStudy = 20
    task1 = Task(1,0.5,0,9)
    tasklet11 = Tasklet(1,5)
    tasklet11.powerConsumption = np.random.randint(5,9,(3))
    tasklet11.setTaskletLength()
    tasklet12 = Tasklet(2,0)
    tasklet12.powerConsumption = np.random.randint(2,7,(3))
    tasklet12.setTaskletLength()
    task1.tasklets = [tasklet11,tasklet12]
    task2 = Task(2,0.5,2,6)
    task2.setTaskLength()
    tasklet21 = Tasklet(1,3)
    tasklet21.powerConsumption = np.random.randint(1,4,(4))
    tasklet21.setTaskletLength()
    tasklet22 = Tasklet(2,2)
    tasklet22.powerConsumption = np.random.randint(3,8,(2))
    tasklet22.setTaskletLength()
    tasklet23 = Tasklet(3,0)
    tasklet23.powerConsumption = np.random.randint(3,5,(2))
    tasklet23.setTaskletLength()
    task2.tasklets = [tasklet21,tasklet22,tasklet23]
    taskList = [task1,task2]
    allowableSchedules = generatePossibleAllowableSchedulesWithTasklets(taskList,lengthOfTimeUnderStudy)
    renewablePowerSchedule = np.random.randint(5,10,(lengthOfTimeUnderStudy))
    bestEnergyConsumptionSchedule = optimizePowerSchedules_NonRenewable(allowableSchedules,lengthOfTimeUnderStudy,renewablePowerSchedule)
    return renewablePowerSchedule,bestEnergyConsumptionSchedule