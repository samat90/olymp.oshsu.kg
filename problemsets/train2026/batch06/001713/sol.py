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
    t=s.split(); n,m=int(t[0]),int(t[1]); g=t[2:2+n]; prev=[0]*(m+1); tot=0
    for i in range(n):
        cur=[0]*(m+1)
        for j in range(m):
            if g[i][j]=='1':
                cur[j+1]=min(prev[j],prev[j+1],cur[j])+1; tot+=cur[j+1]
        prev=cur
    return tot

if __name__=='__main__':
    print(sol(sys.stdin.read()))
