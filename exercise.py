import operator

'''
tasks = {}  # {number: (spec, [utilities]), ...}
nCycles = 0


def updateUtility(number, utility):
    if tasks[number][0]:
        tasks[number][1] = [utility, ]
        tasks[number][0] = False
    else:
        tasks[number][1].append(utility)


def createTask(number, specUtility):
    tasks[number] = (True, [specUtility, ])


def createUpdateTask(number, utility):
    if number in tasks.keys():
        updateUtility(number, utility)
    else:
        createTask(number, utility)


def getTaskUtility(number):
    return sum(tasks[number][1])/len(tasks[number][1])

def getBestTask():
    return max(tasks, key=lambda key: getTaskUtility(tasks[key]))


def parser(string):
    if string.find("cycle=") != -1:
        nCycles = int(string.replace("cycle=", "").replace(" decision=rationale", ""))


'''
