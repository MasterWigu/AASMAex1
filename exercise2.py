import sys


def getTaskUtility(tasks, number, memFactor):
    if tasks[number][0]:  # if the curr utility is speculated
        return tasks[number][1][0][0]

    ut = 0
    summation = 0
    for uPair in tasks[number][1]:
        summation += uPair[1]**memFactor

    for uPair in tasks[number][1]:
        ut += ((uPair[1]**memFactor) / summation) * uPair[0]

    return ut


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
        # print("AAAAA   "+ input)
        if input.find("A") != -1:
            ut = float(input.replace("A u=", ""))
            self.gain += ut
            updateUtility(self.tasks, self.lastDone, ut, self.currCycle)
        else:
            lst = input.replace("T", "").split(" u=")  # lst=[taskNo, specUt]
            self.tasks[int(lst[0])] = [True, [(float(lst[1]), 0), ]]

    def decide_act(self):
        act = max(self.tasks.keys(), key=(lambda k: getTaskUtility(self.tasks, k, self.memoryFactor)))
        if act != self.lastTask:
            self.prepLasting = self.restart
        if act == self.lastTask or self.restart == 0:
            if self.prepLasting > 0:
                self.prepLasting -= 1
            if self.prepLasting == 0:
                self.lastDone = act
        self.lastTask = act
        self.currCycle += 1

    def recharge(self):
        out = self.name + "={"
        for k in self.tasks.keys():
            if not self.tasks[k][0]:
                out += "T"+str(k)+"=" + "{0:.2f}".format(getTaskUtility(self.tasks, k, self.memoryFactor))+","
            else:
                out += "T"+str(k)+"=NA,"
        out = out[:-1]+"}"
        return out, self.gain


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
        aNames = opt.replace("agents={", "").replace("}", "").split(',')
    if opt.find("decision=") != -1:
        decision = opt.replace("decision=", "")

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


rech = "state={"
gain = 0
for agent in agents.keys():
    rech += agents[agent].recharge()[0] + ","
    gain += agents[agent].recharge()[1]
rech = rech[:-1]+"} gain=" + str(gain)
sys.stdout.write(rech+'\n')
