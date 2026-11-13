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
    m=r.randint(1,min(20,1+k*2)) if k else r.randint(1,3)
    X=N(r,k,15,10**5)
    hi=8 if k==0 else (10 if k<3 else 10**5)
    c=L(r,m,1,max(1,min(hi,X*2)))
    return "%d %d\n%s\n"%(m,X,' '.join(map(str,c)))

if __name__=='__main__':
    k=int(sys.argv[1]); seed=int(sys.argv[2]) if len(sys.argv)>2 else 1638*100+k
    sys.stdout.write(gen(random.Random(seed),k))
