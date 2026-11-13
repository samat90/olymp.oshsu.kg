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
    n=int(s.split()[0])
    def f(x):
        if x==n: return 1
        if x>n: return 0
        return f(x+1)+f(x+2)
    return f(0)%M

if __name__=='__main__':
    print(brute(sys.stdin.read()))
