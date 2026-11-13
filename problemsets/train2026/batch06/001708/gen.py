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
    n=N(r,k,5,500); m=N(r,k,5,500); p=r.choice([0.05,0.15,0.3])
    g=[''.join('#' if r.random()<p else '.' for _ in range(m)) for _ in range(n)]
    if r.random()<0.8:
        g[0]='.'+g[0][1:]; g[-1]=g[-1][:-1]+'.'
    return "%d %d\n%s\n"%(n,m,'\n'.join(g))

if __name__=='__main__':
    k=int(sys.argv[1]); seed=int(sys.argv[2]) if len(sys.argv)>2 else 1708*100+k
    sys.stdout.write(gen(random.Random(seed),k))
