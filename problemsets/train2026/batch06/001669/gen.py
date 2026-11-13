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
    n=N(r,k,10,100); W=N(r,k,25,10**4)
    hi=max(3,W//3)
    return "%d %d\n%s\n"%(n,W,'\n'.join("%d %d"%(r.randint(1,hi),r.randint(1,1000)) for _ in range(n)))

if __name__=='__main__':
    k=int(sys.argv[1]); seed=int(sys.argv[2]) if len(sys.argv)>2 else 1669*100+k
    sys.stdout.write(gen(random.Random(seed),k))
