import numpy as np
import random
import time
from colors import cprint

def clustered_print(a, m, p):
    COLCODE = {
        'k': 0,  # black
        'r': 1,  # red
        'g': 2,  # green
        'y': 3,  # yellow
        'b': 4,  # blue
        'm': 5,  # magenta
        'c': 6,  # cyan
        'w': 7  # white
    }
    COLORS = [(c1, c2) for c1 in COLCODE for c2 in COLCODE if c1 != c2]
    mI = 0
    for machine in a:
        pI = 0
        for part in machine:
            if m[mI] == p[pI]:
                cprint(part, *COLORS[p[pI] % len(COLORS)])
            else:
                print(part, end='')
            pI += 1
        print()
        mI += 1
    print('-' * 79)

def move_m(m, p, mI, cI):
    mPrime = np.copy(m)
    pPrime = np.copy(p)
    oldI = mPrime[mI]
    mPrime[mI] = cI
    if 0 == len(np.where(mPrime == oldI)[0]):
        for i in range(len(pPrime)):
            if pPrime[i] == oldI:
                pPrime[i] = cI
    return mPrime, pPrime


def move_p(m, p, pI, cI):
    mPrime = np.copy(m)
    pPrime = np.copy(p)
    oldI = pPrime[pI]
    pPrime[pI] = cI
    if 0 == len(np.where(pPrime == oldI)[0]):
        for i in range(len(mPrime)):
            if mPrime[i] == oldI:
                mPrime[i] = cI
    return mPrime, pPrime


def split(m, p):
    sizeOfClustersM = np.zeros(len(m), int)
    for cluster in m:
        sizeOfClustersM[cluster] += 1
    bigClustersM = {i for i in range(len(sizeOfClustersM)) if sizeOfClustersM[i] > 1}
    sizeOfClustersP = np.zeros(len(p), int)
    for cluster in p:
        sizeOfClustersP[cluster] += 1
    bigClustersP = {i for i in range(len(sizeOfClustersP)) if sizeOfClustersP[i] > 1}
    candidates = bigClustersM.intersection(bigClustersP)
    if candidates:
        mPrime = np.copy(m)
        pPrime = np.copy(p)
        freeCluster = {i for i in range(len(sizeOfClustersM)) if sizeOfClustersM[i] == 0}.intersection(
            {i for i in range(len(sizeOfClustersP)) if sizeOfClustersP[i] == 0})
        newCluster = freeCluster.pop()
        toSplit = random.choice(list(candidates))
        toSplitM = np.array([i for i in range(len(mPrime)) if m[i] == toSplit])
        newElementsM = np.random.choice(toSplitM, size=random.randint(1, len(toSplitM) // 2))
        for i in newElementsM:
            mPrime[i] = newCluster

        toSplitP = np.array([i for i in range(len(pPrime)) if p[i] == toSplit])
        newElementsP = np.random.choice(toSplitP, size=random.randint(1, len(toSplitP) // 2))
        for i in newElementsP:
            pPrime[i] = newCluster
        return mPrime, pPrime
    else:
        return None


def merge(m, p):
    mPrime = np.copy(m)
    pPrime = np.copy(p)
    toMerge = np.random.choice(np.array(list(set(mPrime))), size=2)
    for i in range(len(m)):
        if mPrime[i] == toMerge[0]:
            mPrime[i] = toMerge[1]
    for i in range(len(pPrime)):
        if pPrime[i] == toMerge[0]:
            pPrime[i] = toMerge[1]
    return mPrime, pPrime


def ff(mp, m, p, numberOfOnes):
    nOnesIn = 0
    nZerosIn = 0
    mI = 0
    for machine in mp:
        pI = 0
        for part in machine:
            if m[mI] == p[pI]:
                if part == 1:
                    nOnesIn += 1
                elif part == 0:
                    nZerosIn += 1
            pI += 1
        mI += 1

    # print(nZerosIn)
    # print((numberOfOnes + nZerosIn))
    # print(nOnesIn / (numberOfOnes + nZerosIn))
    return nOnesIn / (numberOfOnes + nZerosIn)


def main(file, seconds):
    with open(file) as f:
        lines = f.readlines()
    firstLine = np.fromstring(lines[0], dtype=int, count=-1, sep=' ')
    if 2 != len(firstLine) or firstLine[0] != len(lines) - 1:
        raise OSError('broken input')
    mp = np.zeros((firstLine[0], firstLine[1]), int)
    linesIter = iter(lines)
    next(linesIter)
    for line in linesIter:
        npLine = np.fromstring(line, dtype=int, count=-1, sep=' ')
        if len(npLine) > firstLine[1] + 1:
            raise OSError('broken input parts')
        machine = npLine[0] - 1
        partIter = iter(npLine)
        next(partIter)
        for part in partIter:
            mp[machine][part - 1] = 1
    numberOfOnes = 0
    for machine in mp:
        for part in machine:
            numberOfOnes += part
    m = np.zeros(len(mp), int)
    p = np.zeros(len(mp[0]), int)

    start = time.perf_counter()
    try:
        while time.perf_counter() - start < seconds:
            k = 0
            while k < 2:
                if 0 == k:
                    mAndP = split(m, p)
                    if (mAndP):
                        mPrime, pPrime = mAndP
                else:
                    mPrime, pPrime = merge(m, p)
                l = 0
                while l < 2:
                    if 0 == l:
                        for mI in range(len(mPrime)):
                            for cI in set(mPrime):
                                mPrimePrime, pPrimePrime = move_m(mPrime, pPrime, mI, cI)
                                if ff(mp, mPrimePrime, pPrimePrime, numberOfOnes) > ff(mp, mPrime, pPrime, numberOfOnes):
                                    mPrime, pPrime = mPrimePrime, pPrimePrime
                                    break
                    if True:
                        for pI in range(len(pPrime)):
                            for cI in set(pPrime):
                                mPrimePrime, pPrimePrime = move_p(mPrime, pPrime, pI, cI)
                                if ff(mp, mPrimePrime, pPrimePrime, numberOfOnes) > ff(mp, mPrime, pPrime, numberOfOnes):
                                    mPrime, pPrime = mPrimePrime, pPrimePrime
                                    break
                    l += 1
                if ff(mp, mPrime, pPrime, numberOfOnes) > ff(mp, m, p, numberOfOnes):
                    m, p = mPrime, pPrime
                    break
                k += 1
        clustered_print(mp, m, p)
        print(ff(mp, m, p, numberOfOnes))
        print(*m)
        print(*p)
    except:
        print(ff(mp, m, p, numberOfOnes))
        print(*m)
        print(*p)

instances = ('20x20.txt', '24x40.txt', '30x50.txt', '30x90.txt', '37x53.txt')
for i in instances:
    print(i)
    main(i, 10 / 5 * 60 * 60)
