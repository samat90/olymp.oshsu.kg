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
    from itertools import permutations
    t=list(map(int,s.split())); n=t[0]; d=[t[1+i*n:1+(i+1)*n] for i in range(n)]
    return min(sum(d[p[i]][p[i+1]] for i in range(n-1)) for p in permutations(range(n)))

if __name__=='__main__':
    print(brute(sys.stdin.read()))
