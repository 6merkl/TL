from operator import mul
from functools import reduce
from TL.tl import *
from TL.jones_wenzl import JW

def nu(m,p):
    if isinstance(m,int):
        if m % p != 0:
            return 0
        return 1 + nu(m//p,p)
    if isinstance(m, Fraction):
        return nu(m.numerator,p) - nu(m.denominator,p)
    if isinstance(m,TL):
        return min(nu(d._coefficient,p) for d in m._diagrams)

def numberToBase(n, b):
    if n == 0:
        return [0]
    digits = []
    while n:
        digits.append(int(n % b))
        n //= b
    return digits[::-1]

def baseToNumber(vp, p):
    return sum(x * p**i for i,x in enumerate(reversed(vp)))

def mother(v,p):
    vp = numberToBase(v,p)
    lastnonzeroindex = max (i for i,x in enumerate(vp) if x != 0)
    vp[lastnonzeroindex] = 0
    
    return baseToNumber(vp,p)

def ancestors(v,p): 
    m = mother(v,p)
    if m != 0:
        return [m] + ancestors(m,p)
    else:
        return []

def powerset(S):
    if len(S) == 0:
        yield []
    else:
        s = S[0]
        for m in powerset(S[1:]):
            yield m
            yield [s] + m
    return

def flatten(l):
    return [x for y in l for x in y]

def buildStreches(S):
    result = []
    temp = []
    for s in S:
        if len(temp) == 0 or s == temp[-1] - 1:
            temp.append(s)
        else:
            result.append(temp)
            temp = [s]
    result.append(temp)
    return result

def isDownAdmissible(v,S,p):
    if len(S) == 0:
        return True
    S = sorted(S, reverse = True)
    vp = numberToBase(v,p)
    stretches = buildStreches(S)
    
    is_down_admissible = True
    for stretch in stretches:
        is_down_admissible &= vp[-stretch[-1]-1] != 0

    for s in S:
        is_down_admissible &= (vp[-s-2] != 0 or (s+1 in S))
    return is_down_admissible

def isUpAdmissible(v,S,p):
    S = sorted(S, reverse = True)
    vp = numberToBase(v,p)
    stretches = buildStreches(S)
    
    is_up_admissible = True
    for stretch in stretches:
        is_up_admissible &= vp[stretch[-1]-1] != 0

    for s in S:
        is_up_admissible &= (vp[-s-2] != p-1 or (s+1 in S))
    return is_up_admissible

def minimalDownAdmissibleStretches(v,p):
    vp = numberToBase(v,p)
    result = []
    temp = []
    for i,a in enumerate(reversed(vp)):
        if len(temp) == 0 and a != 0:
            temp.append(i)
        elif len(temp) != 0:
            if a == 0:
                temp.append(i)
            else:
                result.append(list(reversed(temp)))
                temp = [i]
    return list(reversed(result))

def allDownAdmissibleSets(v,p):
    for S in powerset(minimalDownAdmissibleStretches(v,p)):
        yield flatten(S)

def vbracket(v,S,p):
    vp = numberToBase(v,p)
    vbracketp = [vp[-i-1] if i not in S else -vp[-i-1] for i in reversed(range(len(vp)))]

    return sum(x * p**i for i,x in enumerate(reversed(vbracketp)))

def vparenthese(v,S,p):
    vp = numberToBase(v,p)
    S = sorted(S)
    rev_vparanp = []
    
    for k in range(max(S)+2):
        a = vp[-k-1] if k < len(vp) else 0
        if k in S:
            aprime = -a
        if k not in S and k - 1 in S:
            aprime = a + 2
        if k not in S and k - 1 not in S:
            aprime = a
        rev_vparanp.append(aprime)
    return sum(x * p**i for i,x in enumerate((rev_vparanp)))

def a(v,s,p):
    if s == -1:
        return v
    vp = numberToBase(v,p)
    ap = vp[:-s-1] + (s+1)*[0]
    return baseToNumber(ap,p)

def lambdavS(v,S,p):
    vp = numberToBase(v,p)
    return reduce(mul, ((-1)**(vp[-s-1]*p**s)*Fraction(vbracket(a(v,s-1,p),S,p),vbracket(a(v,s,p),S,p)) for s in S),1)

# v is passed, but v - 1 strands are generated
def d(v,i,p):
    vp = numberToBase(v,p)
    assert i >= 0 and i < len(vp)
    
    xp = vp[-i:] if i > 0 else [0]
    x = baseToNumber(xp,p)
    aipi = vp[-i-1]*p**i
    w = v - x - 1 - 2*aipi
    d = TL.id(x) & TL.nestedCaps(aipi) & TL.id(w)
    return d

def dtilde(v,i,p):
    vp = numberToBase(v,p)
    assert i >= 0 and i < len(vp) - 1
    
    xp = vp[-i:] if i > 0 else [0]
    x = baseToNumber(xp,p)
    aipi = vp[-i-1]*p**i
    w = v - x - 1 - 2*aipi

    return (d(v,i,p))*(TL.id(x+aipi) & JW.get(w+aipi))
    
# Ltilde^S_{v-1}
def Ltilde(v,S,p):
    if len(S) == 0:
        return JW.get(v-1)
    
    S = sorted(S, reverse = True)
    dfactors = [dtilde(v,S[0],p)]
    for s in S[1:]:
        thisv = dfactors[-1]._diagrams[0].n + 1
        dfactors.append(dtilde(thisv,s,p))
    dpart = reduce(mul,reversed(dfactors),1)
    
    return dpart.flip() * JW.get(vbracket(v,S,p)-1) * dpart

def rationalpJW(v,p):
    return sum( lambdavS(v,S,p)*Ltilde(v,S,p) for S in allDownAdmissibleSets(v,p))

def L(v,S,p):
    if len(S) == 0:
        return TL.id(v-1)
    
    S = sorted(S, reverse = True)
    dfactors = [d(v,S[0],p)]
    for s in S[1:]:
        thisv = dfactors[-1]._diagrams[0].n + 1
        dfactors.append(d(thisv,s,p))
    dpart = reduce(mul,reversed(dfactors),1)
    pjw = rationalpJW(v,p)
    return pjw*dpart.flip()*dpart*pjw