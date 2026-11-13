import random,sys
M=10**9+7
def N(r,k,tiny,big):
    if k==0: return r.randint(1,tiny)
    if k==1: return r.randint(1,min(6,big))
    if k==2: return r.randint(1,min(30,big))
    return max(1,big*(k-2)//8)
def L(r,n,lo,hi): return [r.randint(lo,hi) for _ in range(n)]
def S(r,n,al='abc'): return ''.join(r.choice(al) for _ in range(n))
def brute(s):
    t=list(map(int,s.split())); a=t[1:1+t[0]]
    def go(l):
        if len(l)==1: return 0
        return min(l[i]+l[i+1]+go(l[:i]+[l[i]+l[i+1]]+l[i+2:]) for i in range(len(l)-1))
    return go(a)

if __name__=='__main__':
    print(brute(sys.stdin.read()))
