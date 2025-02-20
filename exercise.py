import sys
from math import inf
from itertools import product


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


def taskMin(tasks, numTask):
    if tasks[numTask][0]:  # if the curr utility is speculated
        return tasks[numTask][1][0][0]
    minTask = inf
    for uPair in tasks[numTask][1]:
        if uPair[0] < minTask:
            minTask = uPair[0]
    return minTask


def updateUtility(tasks, number, utility, cycle):

    if tasks[number][0]:
        tasks[number][1] = [(utility, cycle), ]
        tasks[number][0] = False
    else:
        tasks[number][1].append((utility, cycle))


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
        self.lastDone2 = {}  # for flexible only
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
            if self.lastDone == -2:  # if last tik was flexible
                tempIn = input.replace("A u=", "").replace("T", "").replace("{", "").replace("}", "").replace("\n", "").split(",")
                for pairStr in tempIn:
                    pair = pairStr.split("=")
                    self.gain += self.lastDone2[int(pair[0])] * float(pair[1])
                    updateUtility(self.tasks, int(pair[0]), float(pair[1]), self.currCycle)
                self.lastDone = -1
                return self.tasks
            else:
                if self.lastDone != -1 and self.lastDone != -2:
                    ut = float(input.replace("A u=", ""))
                    self.gain += ut
                    updateUtility(self.tasks, self.lastDone, ut, self.currCycle)
                    #print(self.tasks)
                    self.lastDone = -1
                    return self.tasks
        else:
            lst = input.replace("T", "").split(" u=")  # lst=[taskNo, specUt]
            self.tasks[int(lst[0])] = [True, [(float(lst[1]), 0), ]]

    def gain_from_task(self, task, pen=0):
        if task == self.lastTask:
            return (getTaskUtility(self.tasks, self.lastTask, self.memoryFactor) - pen) * (self.cycle - self.currCycle - self.prepLasting)
        else:
            return (getTaskUtility(self.tasks, task, self.memoryFactor) - pen) * (self.cycle - self.currCycle - self.restart)

    def decide_act(self):
        taskMax = max(self.tasks.keys(), key=(lambda k: getTaskUtility(self.tasks, k, self.memoryFactor)))
        utCh = getTaskUtility(self.tasks, taskMax, self.memoryFactor) * (self.cycle - self.currCycle - self.restart)
        if self.restart == 0:
            return taskMax

        if self.lastTask != -1:  # case stay:
            utSt = getTaskUtility(self.tasks, self.lastTask, self.memoryFactor) * (self.cycle - self.currCycle - self.prepLasting)
        else:  # if none before
            utSt = -inf

        if utCh > utSt or ((utCh == utSt and min(taskMax, self.lastTask) == taskMax) and taskMax != self.lastTask):  # case change
            return taskMax
        else:  # case stay
            return self.lastTask

    def do_act(self, task):
        if self.decision == "flexible" and taskMin(self.tasks, task) < 0:
            bestTask2 = ""
            bestP = 0
            tempGain = -inf
            for t1 in self.tasks:
                for t2 in self.tasks:
                    if taskMin(self.tasks, t1) != taskMin(self.tasks, t2):
                        p = (-taskMin(self.tasks, t2))/(taskMin(self.tasks, t1)-taskMin(self.tasks, t2))
                        g = p*getTaskUtility(self.tasks, t1, self.memoryFactor) + (1-p)*getTaskUtility(self.tasks, t2, self.memoryFactor)
                        if g > tempGain and 0 < p < 1:
                            tempGain = g
                            bestP = p
                            bestTask2 = t2
                            task = t1

            self.lastTask = -1
            self.lastDone = -2
            self.lastDone2 = {task: bestP, bestTask2: (1-bestP)}
            #print("DECIDED: " + str(self.lastDone2)+ "\n")

            tempDone = list(self.lastDone2.keys())
            tempDone.sort()

            out = "{T" + str(tempDone[0]) + "=" + "{0:.2f}".format(self.lastDone2[tempDone[0]]) + ",T"
            out += str(tempDone[1]) + "=" + "{0:.2f}".format(self.lastDone2[tempDone[1]]) + "}"
            sys.stdout.write(out + '\n')

        else:  # if not flexible on current tik
            if self.restart == 0:
                self.lastDone = task
                self.lastTask = task
            elif task != self.lastTask:  # case change
                self.lastTask = task
                self.prepLasting = self.restart - 1
            else:  # case stay
                if self.prepLasting > 0:  # still preparing
                    self.prepLasting -= 1
                else:  # execute task
                    self.lastDone = self.lastTask

        self.currCycle += 1

    def decide_do_act(self):
        self.do_act(self.decide_act())

    def recharge(self):
        out = self.name + "={"
        for k in self.tasks.keys():
            if not self.tasks[k][0]:
                out += "T"+str(k)+"=" + "{0:.2f}".format(getTaskUtility(self.tasks, k, self.memoryFactor))+","
            else:
                out += "T"+str(k)+"=NA,"
        out = out[:-1]+"}"
        return out, self.gain


def calculateGain(comb, pen):
    gain = 0
    for i in range(len(comb)):
        currAgent = agents[list(agents.keys())[i]]
        if comb.count(comb[i]) > 1:
            gain += currAgent.gain_from_task(comb[i], pen)
        else:
            gain += currAgent.gain_from_task(comb[i], 0)
    return gain


def chooseIndexBest(comb1, comb2):
    def combPoints(comb):
        points = 0
        for i in range(len(comb)):
            points += i*comb[i]
        return points

    cp1 = combPoints(comb1)
    cp2 = combPoints(comb2)
    if cp1 < cp2:
        return comb2
    else:
        return comb1


def chooseTasks(pen):
    tempTasks = agents[list(agents.keys())[0]].tasks.keys()
    combs = product(tempTasks, repeat=len(agents))
    gain = -inf
    finalComb = None
    for comb in combs:
        tempGain = calculateGain(comb, pen)
        if gain < tempGain:
            finalComb = comb
            gain = tempGain
        elif gain == tempGain:
            finalComb = chooseIndexBest(finalComb, comb)
    print(finalComb)
    print(gain)
    return finalComb


def tikWithPen(pen):
    comb = chooseTasks(pen)
    for i in range(len(agents)):
        agents[list(agents.keys())[i]].do_act(comb[i])


def output():
    rech = ""
    gain = 0
    for a in agents.keys():
        rech += agents[a].recharge()[0] + ","
        if len(agents.keys()) == 1:  # if only 1 agent, dont output agent name
            rech = rech[3:-1]
        gain += agents[a].recharge()[1]
    rech = "state={" + rech[:-1]+"} gain=" + "{0:.2f}".format(gain)
    sys.stdout.write(rech+'\n')

    #print("AAAAA" + str(gain))


#####################
### B: MAIN UTILS ###
#####################
agents = {}

line = sys.stdin.readline()
aNames = ["A"]
decision = "homogeneous-society"
percUt = []
penalty = 0

for opt in line.split(' '):
    if opt.find("agents=") != -1:
        aNames = opt.replace("agents={", "").replace("}", "").replace("agents=[", "").replace("]", "").split(',')
    if opt.find("concurrency-penalty=") != -1:
        penalty = float(opt.replace("concurrency-penalty=", ""))
    if opt.find("decision=") != -1:
        decision = opt.replace("decision=", "")

for name in aNames:
    agents[name] = Agent(line.split(' '), name)
for line in sys.stdin:
    #print(line)
    if line.startswith("end"):
        break
    elif line.startswith("TIK"):
        if penalty == 0:
            #print("TIKTIK")
            for agent in agents.keys():
                agents[agent].decide_do_act()
        else:
            tikWithPen(penalty)
    elif line.startswith("T"):
        for agent in agents.keys():
            agents[agent].perceive(line)
    else:
        agentUt = line.split(" u=")  # lst=[agent, Ut]
        ts = agents[agentUt[0]].perceive("A u=" + agentUt[1])
        if decision == "homogeneous-society":
            for agent in agents.keys():
                agents[agent].tasks = ts
output()
