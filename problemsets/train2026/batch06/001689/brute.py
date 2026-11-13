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
    t=list(map(int,s.split())); a=t[1:1+t[0]]
    def go(l):
        n=len(l)
        if n==1: return 0
        best=10**18
        for i in range(n):
            j=(i+1)%n
            if n==2 and i==1: continue
            nl=[l[x] for x in range(n) if x!=i and x!=j]
            c=l[i]+l[j]
            # place merged pile at position of the earlier-in-circle one
            if j==0:
                nl=nl+[c]
            else:
                nl=nl[:i]+[c]+nl[i:]
            best=min(best,c+go(nl))
        return best
    return go(a)

if __name__=='__main__':
    print(brute(sys.stdin.read()))
