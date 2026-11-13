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
    t=s.split(); n,m=int(t[0]),int(t[1]); bad=set(map(int,t[2:2+m]))
    f=[0]*(n+2); f[0]=1
    for i in range(1,n+1):
        if i in bad: continue
        f[i]=(f[i-1]+(f[i-2] if i>=2 else 0))%M
    return f[n]

if __name__=='__main__':
    print(sol(sys.stdin.read()))
