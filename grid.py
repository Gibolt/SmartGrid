class Task:
    """An entire task, containing one or more tasklets"""
    tasklets = array()
	id = 0				# Unique identifier
	timeStart = 0		# Start time for the task
	timeEnd = 0			# Derived, time of completion
	taskEnergyMin = 0	# Minimum power consumed over course
	taskEnergyMax = 0	# Maximum power consumed over course
	usedEnergy = 0		# Actual energy used
#	taskUrgency = 0
	def __init__(self, tasklets):
		self.tasklets = tasklets
    def f(self):
        return 1

class Tasklet:
    """One component of a cycle"""
	timeStart = 0		# Planned time to begin Tasklet
	timeEnd = 0			# Derived, time of completion
	energy = 0			# Amount consumed per unit/total
#	interrupt = false	# Can be interrupted?
	def __init__(self, start, length):
		self.timeStart = start
		self.timeEnd = start + length
    def f(self):
        return 1
		
class Schedule:
    """Not Important"""
	tasks = array()		# List of the tasks that are being scheduled
	energy = 100		# Available Energy of the current system time
	time = 0  			# Current time of the system
	def __init__(selfh):
		i = 0
	def addTask(self,task):
		self.tasks.append(task)
	def completeTask(self,task)
		self.tasks.remove(task)
		self.energy -= task.usedEnergy
	def schedule(self):
		#Do work here
    def f(self):
        return 1
		
x = Task()