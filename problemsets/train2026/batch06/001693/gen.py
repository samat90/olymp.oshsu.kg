import random,sys
M=10**9+7
def N(r,k,tiny,big):
    if k==0: return r.randint(1,tiny)
    if k==1: return r.randint(1,min(6,big))
    if k==2: return r.randint(1,min(30,big))
    return max(1,big*(k-2)//8)
def L(r,n,lo,hi): return [r.randint(lo,hi) for _ in range(n)]
def S(r,n,al='abc'): return ''.join(r.choice(al) for _ in range(n))
def gen(r,k):
    m=N(r,k,6,100); Lg=r.randint(m+1,max(m+2,10 if k==0 else (200 if k<5 else 10**6)))
    m=min(m,Lg-1)
    p=r.sample(range(1,Lg),m)
    return "%d %d\n%s\n"%(Lg,m,' '.join(map(str,p)))

if __name__=='__main__':
    k=int(sys.argv[1]); seed=int(sys.argv[2]) if len(sys.argv)>2 else 1693*100+k
    sys.stdout.write(gen(random.Random(seed),k))
