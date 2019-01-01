import numpy as np
import random
import time


def fitness(solution, F, D):
    res = 0
    for i in range(0, len(F)):
        for j in range(0, len(F)):
            res += F[i, j] * D[solution[i], solution[j]]
    return res


def probs(P, F, D):
    fitnesses = [fitness(p, F, D) for p in P]
    mean = sum(fitnesses) / len(fitnesses)
    revertedFitnesses = [2 * mean - f for f in fitnesses]
    miniimum = min(revertedFitnesses)
    if (miniimum < 0):
        revertedFitnesses = [f - miniimum for f in revertedFitnesses]
    summ = sum(revertedFitnesses)
    return [f / summ for f in revertedFitnesses]


def mutate(sol):
    p1 = random.randrange(0, len(sol) - 1)
    p2 = random.randrange(0, len(sol) - 1)
    sol[p1], sol[p2] = sol[p2], sol[p1]

def fix(sol):
    n = len(sol)
    unused = set(range(n)) - set(sol)
    used = set()
    for i in range(len(sol)):
        if sol[i] in used:
            sol[i] = unused.pop()
        else:
            used.add(sol[i])


def reproduction(Pp):
    childs = []
    for i in range(len(Pp)):
        for j in range(len(Pp)):
            if i != j:
                split = random.randrange(0, len(Pp[i]) + 1)
                child = Pp[i][0:split] + Pp[j][split:len(Pp[j])]
                fix(child)
                if random.random() < 0.5:
                    mutate(child)
                childs.append(child)
    return childs


def ls(sol, F, D):
    prevScore = fitness(sol, F, D)
    prevSol = sol[:]
    minScrore = 9999999999
    minSol = []

    improved = True
    while improved:
        improved = False
        for i in range(len(prevSol) - 1):
            for j in range(len(prevSol) - 1):
                if i != j:
                    newSol = prevSol[:]
                    newSol[i], newSol[j] = newSol[j], newSol[i]
                    newScore = fitness(newSol, F, D)
                    if newScore < minScrore:
                        minScrore = newScore
                        minSol = newSol[:]
                        improved = True
        prevSol = minSol[:]
        prevScore = minScrore
    return prevSol


def evolve(file, seconds):
    with open(file) as f:
        lines = f.readlines()
    n = int(lines[0])
    if 2 != (len(lines) - 2) / n:
        raise OSError('broken input')
    D = np.empty((n, n), int)
    for i in range(1, n + 1):
        D[i - 1] = np.fromstring(lines[i], dtype=int, count=-1, sep=' ')
    F = np.empty((n, n), int)
    for i in range(n + 2, 2 * n + 2):
        F[i - n - 2] = np.fromstring(lines[i], dtype=int, count=-1, sep=' ')

    P = [list(range(n)) for _ in range(7 * 6)]
    print(min([fitness(p, F, D) for p in P]))
    for p in P:
        random.shuffle(p)

    start = time.perf_counter()
    try:
        while time.perf_counter() - start < seconds:
            Pp = np.random.choice(len(P), size=7, p=probs(P, F, D))
            Pp = [P[i] for i in Pp]
            P = reproduction(Pp)
        fitnesses = [fitness(p, F, D) for p in P]
        theKing = P[fitnesses.index(min(fitnesses))]
        theKing = ls(theKing, F, D)
        ft = fitness(theKing, F, D)
        print(theKing, ft)
        string = ""
        string += str(ft) + " "
        for i in theKing:
            string += str(i) + " "
        with open(file + ".sol", "w+") as f:
            f.write(string)
    except:
        fitnesses = [fitness(p, F, D) for p in P]
        theKing = P[fitnesses.index(min(fitnesses))]
        theKing = ls(theKing, F, D)
        print(theKing, fitness(theKing, F, D))
