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
    n=N(r,k,7,12)
    sq=[x*x for x in range(2,15)]
    a=[r.randint(1,30)]
    while len(a)<n:
        c=r.choice(sq)-a[-1]
        if r.random()<0.8 and 1<=c<=100: a.append(c)
        else: a.append(r.randint(1,100 if k>5 else 20))
    r.shuffle(a)
    return "%d\n%s\n"%(n,' '.join(map(str,a)))

if __name__=='__main__':
    k=int(sys.argv[1]); seed=int(sys.argv[2]) if len(sys.argv)>2 else 1701*100+k
    sys.stdout.write(gen(random.Random(seed),k))
