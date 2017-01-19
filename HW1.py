#!/usr/bin/python

#########################################
## CS 3430: S2017: HW01: Euclid Numbers
## Russ Barnes
## A01645845
#########################################

import math

def is_prime(n):
    '''is_prime(n) ---> True if n is prime; False otherwise.'''
    bool = false
    if n == 1:
        return true
    if n == 3:
        return true
    if n/2.0 > 1:
        bool = is_prime(n/2.0)
    if bool == ture:
        return true
    if n 

    pass

def next_prime_after(p):
    '''computes next prime after prime p; if p is not prime, returns None.'''
    if not is_prime(p): return None
    ## your code here
    pass

def euclid_number(i):
    '''euclid_number(i) --> i-th Euclid number.'''
    if i < 0: return None
   ## your code here
    pass

def compute_first_n_eucs(n):
    '''returns a list of the first n euclid numbers.'''
    eucs = []
    ## your code here
    return eucs

def prime_factors_of(n):
    '''returns a list of prime factors of n if n > 1 and [] otherwise.'''
    if n < 2: return []
    factors = []
    ## your code here
    return factors

def tabulate_euc_factors(n):
    '''returns a list of 3-tuples (i, euc, factors).'''
    euc_factors = []
    ## your code here
    return euc_factors