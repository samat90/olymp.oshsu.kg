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
    n=N(r,k,12,100); a=L(r,n,0,100 if k>3 else 4)
    T=r.randint(-sum(a),sum(a)) if r.random()<0.8 else r.randint(-10**4,10**4)
    T=max(-10**4,min(10**4,T))
    return "%d %d\n%s\n"%(n,T,' '.join(map(str,a)))

if __name__=='__main__':
    k=int(sys.argv[1]); seed=int(sys.argv[2]) if len(sys.argv)>2 else 1674*100+k
    sys.stdout.write(gen(random.Random(seed),k))
