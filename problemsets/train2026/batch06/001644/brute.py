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
    n,k=map(int,s.split()); c=0
    for m in range(1<<n):
        b=bin(m)[2:].zfill(n)
        if '1'*k not in b: c+=1
    return c%M

if __name__=='__main__':
    print(brute(sys.stdin.read()))
