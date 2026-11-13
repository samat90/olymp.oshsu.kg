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
    t=s.split(); w=t[0]; d=int(t[1]); ws=t[2:2+d]
    def go(p):
        if p==len(w): return 1
        return sum(go(p+len(x)) for x in ws if w.startswith(x,p))
    return go(0)%M

if __name__=='__main__':
    print(brute(sys.stdin.read()))
