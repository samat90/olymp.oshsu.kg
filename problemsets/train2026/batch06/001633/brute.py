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
    t=list(map(int,s.split())); n,k=t[0],t[1]; h=t[2:2+n]
    def f(i):
        if i==n-1: return 0
        return min(abs(h[i]-h[j])+f(j) for j in range(i+1,min(n,i+k+1)))
    return f(0)

if __name__=='__main__':
    print(brute(sys.stdin.read()))
