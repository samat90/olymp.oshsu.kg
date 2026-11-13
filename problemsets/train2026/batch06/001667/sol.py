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
    t=list(map(int,s.split())); a=t[1:1+t[0]]; n=len(a); best=min(n,2)
    d=[{} for _ in range(n)]
    for i in range(n):
        for j in range(i):
            df=a[i]-a[j]; v=d[j].get(df,1)+1
            if v>d[i].get(df,0): d[i][df]=v
            if v>best: best=v
    return best

if __name__=='__main__':
    print(sol(sys.stdin.read()))
