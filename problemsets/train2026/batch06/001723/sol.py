import random,sys
M=10**9+7
def N(r,k,tiny,big):
    if k==0: return r.randint(1,tiny)
    if k==1: return r.randint(1,min(6,big))
    if k==2: return r.randint(1,min(30,big))
    return max(1,big*(k-2)//8)
def L(r,n,lo,hi): return [r.randint(lo,hi) for _ in range(n)]
def S(r,n,al='abc'): return ''.join(r.choice(al) for _ in range(n))
def sol(s):
    t=list(map(int,s.split())); n,K=t[0],t[1]; p=t[2:2+n]
    buy=[-10**18]*(K+1); sell=[0]*(K+1)
    for x in p:
        for j in range(1,K+1):
            buy[j]=max(buy[j],sell[j-1]-x); sell[j]=max(sell[j],buy[j]+x)
    return sell[K]

if __name__=='__main__':
    print(sol(sys.stdin.read()))
