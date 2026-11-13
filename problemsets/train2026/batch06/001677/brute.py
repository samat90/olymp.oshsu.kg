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
    t=list(map(int,s.split())); n,A,B=t[:3]; it=[t[3+3*i:6+3*i] for i in range(n)]; best=0
    for m in range(1<<n):
        a=sum(it[i][0] for i in range(n) if m>>i&1); b=sum(it[i][1] for i in range(n) if m>>i&1)
        if a<=A and b<=B: best=max(best,sum(it[i][2] for i in range(n) if m>>i&1))
    return best

if __name__=='__main__':
    print(brute(sys.stdin.read()))
