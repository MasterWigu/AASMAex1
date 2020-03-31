import sys
from math import inf
from itertools import combinations_with_replacement


def getTaskUtility(tasks, number, memFactor):
    if tasks[number][0]:  # if the curr utility is speculated
        return tasks[number][1][0][0]

    ut = 0
    summation = 0
    for uPair in tasks[number][1]:
        summation += uPair[1]**memFactor

    for uPair in tasks[number][1]:
        ut += ((uPair[1]**memFactor) / summation) * uPair[0]

    return round(ut, 4)


def updateUtility(tasks, number, utility, cycle, memFactor):

    # print("Task: T"+ str(number) + " Old value: " + str(getTaskUtility(tasks, number, memFactor)))
    if tasks[number][0]:
        tasks[number][1] = [(utility, cycle), ]
        tasks[number][0] = False
    else:
        tasks[number][1].append((utility, cycle))
    # print("Task: T"+ str(number) + " New value: " + str(getTaskUtility(tasks, number, memFactor)))


def createTask(tasks, number, specUtility):
    tasks[number] = [True, [(specUtility, 0), ]]


#########################
### A: AGENT BEHAVIOR ###
#########################

class Agent:
    def __init__(self, options, aName):
        self.cycle = 1
        self.currCycle = 0
        self.decision = "rationale"
        self.memoryFactor = 0
        self.lastTask = -1
        self.lastDone = -1
        self.restart = 0
        self.prepLasting = self.restart
        self.gain = 0
        self.name = aName
        self.tasks = {}  # {number: [spec, [(utilities,cycle), ...]], ...}
        for i in options:
            if i.find("decision=") != -1:
                self.decision = i.replace("decision=", "")
            elif i.find("restart=") != -1:
                self.restart = int(i.replace("restart=", ""))
            elif i.find("cycle=") != -1:
                self.cycle = int(i.replace("cycle=", ""))
            elif i.find("memory-factor=") != -1:
                self.memoryFactor = float(i.replace("memory-factor=", ""))

    def perceive(self, input):
        if input.find("A") != -1:
            if self.lastDone != -1:
                ut = float(input.replace("A u=", ""))
                self.gain += ut
                updateUtility(self.tasks, self.lastDone, ut, self.currCycle, self.memoryFactor)
                self.lastDone = -1
        else:
            lst = input.replace("T", "").split(" u=")  # lst=[taskNo, specUt]
            self.tasks[int(lst[0])] = [True, [(float(lst[1]), 0), ]]

    def decide_act(self):
        taskMax = max(self.tasks.keys(), key=(lambda k: getTaskUtility(self.tasks, k, self.memoryFactor)))
        # print("tMax = " + str(taskMax) + " || lastTask = " + str(self.lastTask))
        # case change:
        utCh = getTaskUtility(self.tasks, taskMax, self.memoryFactor) * (self.cycle - self.currCycle - self.restart)
        # case stay:
        if self.lastTask != -1:
            utSt = getTaskUtility(self.tasks, self.lastTask, self.memoryFactor) * (self.cycle - self.currCycle - self.prepLasting)
        else:  # if none before
            utSt = -inf

        # print("utSt = " + str(utSt) + " || utCh = " + str(utCh))

        if self.restart == 0:
            self.lastDone = taskMax
            self.lastTask = taskMax
        elif utCh > utSt or ((utCh == utSt and min(taskMax, self.lastTask) == taskMax) and taskMax != self.lastTask):  # case change
            # print("CHANGE / PREP")
            self.lastTask = taskMax
            self.prepLasting = self.restart - 1
        else:  # case stay
            if self.prepLasting > 0:  # still preparing
                # print("STAY  / PREP")
                self.prepLasting -= 1
            else:  # execute task
                # print("STAY  / EXEC")
                self.lastDone = self.lastTask

        self.currCycle += 1
        # print("Chosen task: T" + str(self.lastTask))
        # print(self.recharge())

    def do_act(self):


    def recharge(self):
        out = self.name + "={"
        for k in self.tasks.keys():
            if not self.tasks[k][0]:
                out += "T"+str(k)+"=" + "{0:.2f}".format(getTaskUtility(self.tasks, k, self.memoryFactor))+","
            else:
                out += "T"+str(k)+"=NA,"
        out = out[:-1]+"}"
        return out, self.gain


def calculateGain(comb):





def chooseTasks():
    tempTasks = agents[agents.keys()[0]].tasks.keys()
    combs = combinations_with_replacement(tempTasks, len(agents))
    gain = -inf
    tempGain = 0
    finalComb = None
    for comb in combs:

        tempGain = calculateGain(comb)
        if gain > tempGain:
            finalComb = comb
        elif gain == tempGain:
            finalComb = chooseIndexBest(finalComb, comb)
    return finalComb











#####################
### B: MAIN UTILS ###
#####################
agents = {}

line = sys.stdin.readline()
aNames = ["A"]
decision = "homogeneous-society"
percUt = []

for opt in line.split(' '):
    if opt.find("agents=") != -1:
        aNames = opt.replace("agents={", "").replace("}", "").replace("agents=[", "").replace("]", "").split(',')
    if opt.find("decision=") != -1:
        decision = opt.replace("decision=", "")
        if decision == "flexible":
            exit(0)

for name in aNames:
    agents[name] = Agent(line.split(' '), name)
for line in sys.stdin:
    if line.startswith("end"):
        break
    elif line.startswith("TIK"):
        for agent in agents.keys():
            agents[agent].decide_act()
    elif line.startswith("T"):
        for agent in agents.keys():
            agents[agent].perceive(line)
    else:
        if decision != "homogeneous-society":
            agentUt = line.split(" u=")  # lst=[agent, Ut]
            agents[agentUt[0]].perceive("A u=" + agentUt[1])
        else:
            percUt.append(float(line.split(" u=")[1]))
            if len(percUt) == len(aNames):
                med = sum(percUt) / len(percUt)
                for agent in agents.keys():
                    agents[agent].perceive("A u=" + str(med))
                percUt = []


rech = ""
gain = 0
for agent in agents.keys():
    rech += agents[agent].recharge()[0] + ","
    if len(agents.keys()) == 1:  # if only 1 agent, dont output agent name
        rech = rech[3:-1]
    gain += agents[agent].recharge()[1]
rech = "state={" + rech[:-1]+"} gain=" + "{0:.2f}".format(gain)
sys.stdout.write(rech+'\n')
