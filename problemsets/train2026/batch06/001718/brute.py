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
    t=list(map(int,s.split())); n,m=t[0],t[1]; a=[t[2+i*m:2+(i+1)*m] for i in range(n)]
    return max(sum(a[x][y] for x in range(i,i2+1) for y in range(j,j2+1)) for i in range(n) for i2 in range(i,n) for j in range(m) for j2 in range(j,m))

if __name__=='__main__':
    print(brute(sys.stdin.read()))
