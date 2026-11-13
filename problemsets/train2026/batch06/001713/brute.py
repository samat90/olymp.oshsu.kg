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
    t=s.split(); n,m=int(t[0]),int(t[1]); g=t[2:2+n]; c=0
    for i in range(n):
        for j in range(m):
            for d in range(1,min(n-i,m-j)+1):
                if all(g[x][y]=='1' for x in range(i,i+d) for y in range(j,j+d)): c+=1
    return c

if __name__=='__main__':
    print(brute(sys.stdin.read()))
