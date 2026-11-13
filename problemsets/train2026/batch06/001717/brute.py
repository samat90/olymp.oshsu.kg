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
    t=list(map(int,s.split())); n,m=t[0],t[1]; a=t[2:]
    def go(i,j):
        b=1
        for di,dj in ((1,0),(-1,0),(0,1),(0,-1)):
            x,y=i+di,j+dj
            if 0<=x<n and 0<=y<m and a[x*m+y]>a[i*m+j]: b=max(b,1+go(x,y))
        return b
    return max(go(i,j) for i in range(n) for j in range(m))

if __name__=='__main__':
    print(brute(sys.stdin.read()))
