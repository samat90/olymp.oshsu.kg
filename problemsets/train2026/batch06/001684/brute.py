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
    t=list(map(int,s.split())); n=t[0]; d=t[1:2+n]
    def go(i,j):
        if i==j: return 0
        return min(go(i,m)+go(m+1,j)+d[i]*d[m+1]*d[j+1] for m in range(i,j))
    return go(0,n-1)

if __name__=='__main__':
    print(brute(sys.stdin.read()))
