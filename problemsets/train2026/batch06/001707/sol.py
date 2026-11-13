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
    t=list(map(int,s.split())); n=t[0]; a=t[1:1+n]
    pr=[2,3,5,7,11,13,17,19,23,29]
    cnt=[0]*31
    for x in a: cnt[x]+=1
    dp=[0]*1024; dp[0]=1
    for v in range(2,31):
        if not cnt[v]: continue
        mk=0; ok=True; y=v
        for i,p in enumerate(pr):
            if y%p==0:
                y//=p
                if y%p==0: ok=False
                mk|=1<<i
        if not ok: continue
        nd=dp[:]
        for x in range(1024):
            if dp[x] and not x&mk: nd[x|mk]=(nd[x|mk]+dp[x]*cnt[v])%M
        dp=nd
    return (sum(dp)*pow(2,cnt[1],M)-1)%M

if __name__=='__main__':
    print(sol(sys.stdin.read()))
