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
    t=s.split(); n=int(t[0]); ws=sorted(t[1:1+n],key=len); dp={}; best=1
    for w in ws:
        b=1
        for i in range(len(w)):
            x=w[:i]+w[i+1:]
            if x in dp and dp[x]+1>b: b=dp[x]+1
        dp[w]=b; best=max(best,b)
    return best

if __name__=='__main__':
    print(sol(sys.stdin.read()))
