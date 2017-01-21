#!/usr/bin/python

#########################################
## CS 3430: S2017: HW01: Euclid Numbers
## Russ Barnes
## A01645845
#########################################

import math
iNext = 0
iUsed = set()
iAt = 0
def is_prime(n):
    '''is_prime(n) ---> True if n is prime; False otherwise.'''
    if len(iUsed) < 2:
        iUsed.add(2)
        iUsed.add(3)
    if n == 2:
        return True
    if n == 1:
        return False
    if n == 3:
        return True
    i=2
    while(i <= n):
        j=2
        while(j <= (i/j)):
            if not(i%j): break
            j = j + 1
            if (j > i/j):
                iUsed.add(i)
                if i == n:
                    return True
        i = i + 1
    return False

def next_prime_after(p):
    '''computes next prime after prime p; if p is not prime, returns None.'''
    if not is_prime(p): return None
    ## your code here
    if n == 2:
        return 3
    if n == 1:
        return 2
    if n == 3:
        return True
    i=2
    while():
        j=2
        while(j <= (i/j)):
            if not(i%j): break
            j = j + 1
            if (j > i/j): 
                if i > p:
                    iUsed.add(i)
                    return i
        i = i + 1
    pass

def euclid_number(i):
    '''euclid_number(i) --> i-th Euclid number.'''
    if i < 0: return None
    ## your code here
    iBy = 50
    iTotal = 1
    if i > 20:
        iBy = iBy * i
    if len(iUsed) < i:
        next_prime_after(iBy)
    lPrimes = sorted(iUsed)
    for iCount in xrange(i+1):
        iTotal = iTotal * lPrimes[iCount]
    iTotal = iTotal + 1
    return iTotal

def compute_first_n_eucs(n):
    '''returns a list of the first n euclid numbers.'''
    eucs = []
    ## your code here
    for i in xrange(n + 1):
        eucs.append(euclid_number(i))
    return eucs

def prime_factors_of(n):
    '''returns a list of prime factors of n if n > 1 and [] otherwise.'''
    if n < 2: return []
    factors = []
    ## your code here
    if is_prime(n):
        factors.append(n)
    else:
        lPrime = sorted(iUsed)
        iFactored = n
        iAt = 0
        while (lPrime[iAt] < n):
            if iFactored%lPrime[iAt] == 0:
                iFactored = iFactored/lPrime[iAt]
                factors.append(iAt)
            else:
                iAt+=iAt
    return factors

def tabulate_euc_factors(n):
    '''returns a list of 3-tuples (i, euc, factors).'''
    euc_factors = []
    ## your code here
    return euc_factors