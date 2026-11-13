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
    N_=int(s.split()[0])
    return sum(1 for x in range(1,N_+1) if all(a!=b for a,b in zip(str(x),str(x)[1:])))

if __name__=='__main__':
    print(brute(sys.stdin.read()))
