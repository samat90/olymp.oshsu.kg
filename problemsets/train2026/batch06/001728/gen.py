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
    n=N(r,k,10,10**5); wd=r.choice([1,3,10**9])
    es=[(r.randint(max(1,i-wd),i-1),i) for i in range(2,n+1)]
    return "%d\n%s"%(n,''.join("%d %d\n"%e for e in es))

if __name__=='__main__':
    k=int(sys.argv[1]); seed=int(sys.argv[2]) if len(sys.argv)>2 else 1728*100+k
    sys.stdout.write(gen(random.Random(seed),k))
