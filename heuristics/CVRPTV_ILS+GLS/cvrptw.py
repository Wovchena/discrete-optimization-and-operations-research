import numpy as np
import re
import math
import time
import random

def isAnswerValid(answer, dists, demands, workTime, CAPACITY, SERVICE_TIME):
    for vehicleRout in range(len(answer) - 1):
        if not answer[vehicleRout]:
            continue
        timeStamp = 0
        vehicleCapacity = CAPACITY
        timeStamp = max(timeStamp + dists[0][answer[vehicleRout][0]], workTime[answer[vehicleRout][0]][0])
        timeStamp += SERVICE_TIME
        vehicleCapacity -= demands[answer[vehicleRout][0]]
        for nodeI in range(len(answer[vehicleRout]) - 1):
            timeStamp += dists[answer[vehicleRout][nodeI]][answer[vehicleRout][nodeI + 1]]
            timeStamp = max(timeStamp, workTime[answer[vehicleRout][nodeI + 1]][0])
            if timeStamp > workTime[answer[vehicleRout][nodeI + 1]][1]:
                return False
            timeStamp += SERVICE_TIME
            vehicleCapacity -= demands[answer[vehicleRout][nodeI + 1]]
            if vehicleCapacity < 0:
                return False
        timeStamp = timeStamp + dists[answer[vehicleRout][-1]][0]
        if timeStamp > workTime[0][1]:
            return False
    return True

def operate(answer, curO, p, dists, demands, workTime, VEHICLE_NUMBER, CAPACITY, SERVICE_TIME):
    bestAnswer = [x[:] for x in answer]
    bsetO = curO
    for veicleRout in range(len(answer) - 1): # 2-opt
        for firstNodeI in range(len(answer[veicleRout]) - 1):
            for secondeNodeI in range(firstNodeI + 1, len(answer[veicleRout])):
                curAnswer = [x[:] for x in answer]
                curAnswer[veicleRout] = answer[veicleRout][:firstNodeI] + list(reversed(answer[veicleRout][firstNodeI:secondeNodeI])) + answer[veicleRout][secondeNodeI:]
                if isAnswerValid(curAnswer, dists, demands, workTime, CAPACITY, SERVICE_TIME):
                    curO = O(curAnswer, p, dists)
                    if (curO < bsetO):
                        bestAnswer = [x[:] for x in curAnswer]
                        bsetO = curO

    for firstVeicleRout in range(len(answer)): # relocate
        for secondVehicleRout in range(len(answer) - 1):
            for nodeI in range(len(answer[firstVeicleRout])):
                for node2I in range(len(answer[secondVehicleRout])):
                    curAnswer = [x[:] for x in answer]
                    toMove =  curAnswer[firstVeicleRout][nodeI]
                    curAnswer[secondVehicleRout].insert(node2I+1, curAnswer[firstVeicleRout][nodeI])
                    curAnswer[firstVeicleRout].remove(toMove)
                    if isAnswerValid(curAnswer, dists, demands, workTime, CAPACITY, SERVICE_TIME):
                        curO = O(curAnswer, p, dists)
                        if (curO < bsetO): 
                            bestAnswer = [x[:] for x in curAnswer]
                            bsetO = curO
                
                if not answer[secondVehicleRout]:
                    curAnswer = [x[:] for x in answer]
                    
                    curAnswer[secondVehicleRout].append(curAnswer[firstVeicleRout].pop(nodeI))
                    
                    if isAnswerValid(curAnswer, dists, demands, workTime, CAPACITY, SERVICE_TIME):
                        curO = O(curAnswer, p, dists)
                        if (curO < bsetO):
                            bestAnswer = [x[:] for x in curAnswer]
                            bsetO = curO

    for firstVeicleRout in range(len(answer) - 1): # exchange
        for secondVeicleRout in range(len(answer) - 1):
            for nodeI in range(len(answer[firstVeicleRout])):
                for node2I in range(len(answer[secondVehicleRout])):
                    curAnswer =[x[:] for x in answer]
                    curAnswer[secondVeicleRout][node2I:node2I+1], curAnswer[firstVeicleRout][nodeI:nodeI+1] = curAnswer[firstVeicleRout][nodeI:nodeI+1], curAnswer[secondVeicleRout][node2I:node2I+1]
                    if isAnswerValid(curAnswer, dists, demands, workTime, CAPACITY, SERVICE_TIME):
                        curO = O(curAnswer, p, dists)
                        if (curO < bsetO):
                            bestAnswer = [x[:] for x in curAnswer]
                            bsetO = curO

    for firstVeicleRout in range(len(answer) - 1): # cross
        for secondVeicleRout in range(len(answer) - 1):
            for nodeI in range(max(len(answer[firstVeicleRout]), 1)):
                for node2I in range(max(len(answer[secondVehicleRout]), 1)):
                    curAnswer = [x[:] for x in answer]
                    curAnswer[secondVeicleRout][node2I:], curAnswer[secondVeicleRout][nodeI:] = curAnswer[secondVeicleRout][nodeI:], curAnswer[secondVeicleRout][node2I:]
                    if isAnswerValid(curAnswer, dists, demands, workTime, CAPACITY, SERVICE_TIME):
                        curO = O(curAnswer, p, dists)
                        if (curO < bsetO):
                            bestAnswer = [x[:] for x in curAnswer]
                            bsetO = curO
    return bestAnswer, bsetO
                            
def O(answer, p, dists):
    LAMB = 0.2
    objective = 0
    for routI in range(len(answer) - 1): # the last vehicle is virtual
        if answer[routI]:
            prevNode = answer[routI][0]
            objective += dists[0][prevNode] + LAMB * p[0][prevNode] * dists[0][prevNode]
            for i in range(0, len(answer[routI])):
                curNode = answer[routI][i]
                objective += dists[prevNode][curNode] + LAMB * p[prevNode][curNode] * dists[prevNode][curNode]
                prevNode = curNode
            objective += dists[curNode][0] + LAMB * p[curNode][0] * dists[curNode][0]
    ALPHA1 = 1.025
    ALPHA2 = 0.0005
    for node in answer[-1]:
        objective += ALPHA1 * (dists[0][node] + dists[node][0] + LAMB * p[0][node] * dists[0][node] + LAMB * p[node][0] * dists[node][node]) + ALPHA2 
    return objective

def ls(answer, p, dists, demands, workTime, VEHICLE_NUMBER, CAPACITY, SERVICE_TIME):
    curO = O(answer, p , dists)
    newAnswer, newO = operate(answer, curO, p, dists, demands, workTime, VEHICLE_NUMBER, CAPACITY, SERVICE_TIME)
    while newO < curO:
        answer = newAnswer
        curO = newO
        newAnswer, newO = operate(answer, curO, p, dists, demands, workTime, VEHICLE_NUMBER, CAPACITY, SERVICE_TIME)
    return answer

def gls(dists, demands, workTime, VEHICLE_NUMBER, CAPACITY, SERVICE_TIME, seconds):
    try:
        p = np.zeros(dists.shape, int) # penalites for directed arcs
        answer = [[] for _ in range(VEHICLE_NUMBER + 1)]
        answer[VEHICLE_NUMBER] = [i for i in range(1, len(dists))]
        answer = ls(answer, p, dists, demands, workTime, VEHICLE_NUMBER, CAPACITY, SERVICE_TIME)
        bestAnswer = [x[:] for x in answer]
        bestO = O(bestAnswer, p, dists)
        count = 0
        start = time.perf_counter()
        while time.perf_counter() - start < seconds:
            if count % 10 == 0:
                print(count, 'iteration')
            print(count)
            count += 1
            maxArc = None
            maxCost = 0
            for route in answer:
                if route:
                    curArk = (0, route[0])
                    curCost = dists[0][route[0]] / (p[0][route[0]] + 1)
                    if curCost > maxCost:
                        maxCost = curCost
                        maxArc = curArk
                    for nodeI in range(len(route) - 1):
                        curArk = (route[nodeI], route[nodeI+1])
                        curCost = dists[curArk[0]][curArk[1]] / (p[curArk[0]][curArk[1]] + 1)
                        if curCost > maxCost:
                            maxCost = curCost
                            maxArc = curArk
                    curArk = (route[-1], 0)
                    curCost = dists[curArk[0]][curArk[1]] / (p[curArk[0]][curArk[1]] + 1)
                    if curCost > maxCost:
                        maxCost = curCost
                        maxArc = curArk
            p[maxArc[0]][maxArc[1]] += 1
            answer = ls(answer, p, dists, demands, workTime, VEHICLE_NUMBER, CAPACITY, SERVICE_TIME)
            curO = O(answer, p, dists)
            if curO < bestO:
                bestO = curO
                bestAnswer = [x[:] for x in answer]
        return ls(bestAnswer, p, np.zeros(dists.shape, int), demands, workTime, VEHICLE_NUMBER, CAPACITY, SERVICE_TIME)
    except:
        print('KILLED')
        print(bestAnswer)
        return ls(bestAnswer, p, np.zeros(dists.shape, int), demands, workTime, VEHICLE_NUMBER, CAPACITY, SERVICE_TIME)

def ils(dists, demands, workTime, VEHICLE_NUMBER, CAPACITY, SERVICE_TIME, seconds):
    try:
        p = np.zeros(dists.shape, int) # penalites for directed arcs
        answer = [[] for _ in range(VEHICLE_NUMBER + 1)]
        answer[VEHICLE_NUMBER] = [i for i in range(1, len(dists))]
        answer = ls(answer, p, dists, demands, workTime, VEHICLE_NUMBER, CAPACITY, SERVICE_TIME)
        bestAnswer = [x[:] for x in answer]
        bestO = O(bestAnswer, p, dists)
        count = 0
        start = time.perf_counter()
        while time.perf_counter() - start < seconds:
            if count % 10 == 0:
                print(count, 'iteration')
            print(count)
            count += 1
            unemptyRoutes = []
            for route in answer:
                if route:
                    unemptyRoutes.appedn(route)
            annihilate = random.choice(unemptyRoutes)
            answer[-1].extend(annihilate)
            annihilate.clear()
            answer = ls(answer, p, dists, demands, workTime, VEHICLE_NUMBER, CAPACITY, SERVICE_TIME)
            curO = O(answer, p, dists)
            if curO < bestO:
                bestO = curO
                bestAnswer = [x[:] for x in answer]
        return ls(bestAnswer, p, np.zeros(dists.shape, int), demands, workTime, VEHICLE_NUMBER, CAPACITY, SERVICE_TIME)
    except:
        print('KILLED')
        print(bestAnswer)
        return bestAnswer

def print_answer(answer, dists, workTime, SERVICE_TIME):
    if answer[-1]:
        print('No solution is found!')
    for route in answer:
        if route:
            toPrint = [0, 0]
            prevNode = 0
            timeStamp = 0
            for node in route:
                toPrint.append(node)
                timeStamp += dists[prevNode][node]
                timeStamp = max(timeStamp, workTime[node][0])
                toPrint.append(timeStamp)
                timeStamp += SERVICE_TIME
                prevNode = node
            toPrint.extend([0, timeStamp + dists[prevNode][0]])
            print(*toPrint)
    
def solve(fileName, seconds, algo='gls'):
    VEHICLE_NUMBER = None
    CAPACITY = None
    SERVICE_TIME = None
    customers = []
    vehicleNumberCapacityRe = re.compile('^\\s+\\d+\\s+\\d+\\s+$')
    dataRe = re.compile('^\\s+(\\d+\\s+){7}$')
    with open(fileName) as f:
        lines = f.readlines()
    for line in lines:
        if dataRe.match(line):
            customers.append(np.fromstring(line, dtype=int, count=7, sep=' ')) 
        elif vehicleNumberCapacityRe.match(line):
            numberCapacity = np.fromstring(line, dtype=int, count=2, sep=' ')
            VEHICLE_NUMBER, CAPACITY = numberCapacity[0], numberCapacity[1]
    SERVICE_TIME = customers[1][6]
    dists = np.empty((len(customers), len(customers)), float)
    for i in range(len(customers)):
        for j in range(len(customers)):
            dists[i][j] = math.sqrt((customers[i][1] - customers[j][1]) ** 2 + (customers[i][2] - customers[j][2]) ** 2)
    demands = np.array([x[3] for x in customers], int)
    workTime = np.array([(x[4], x[5]) for x in customers])
    if 'gls' == algo:
        answer = gls(dists, demands, workTime, VEHICLE_NUMBER, CAPACITY, SERVICE_TIME, seconds)
    else:
        answer = ils(dists, demands, workTime, VEHICLE_NUMBER, CAPACITY, SERVICE_TIME, seconds)
    print('-' * 79)
    print(fileName)
    print(answer)
    print(O(answer, np.zeros(dists.shape, int), dists))
    print_answer(answer, dists, workTime, SERVICE_TIME)
