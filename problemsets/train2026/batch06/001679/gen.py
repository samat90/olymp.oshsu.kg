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
    g=N(r,k,5,50); W=N(r,k,15,5000); hi=max(3,min(5000,W//3)) if k else 7
    lines=[]
    for _ in range(g):
        s0=r.randint(1,3 if k==0 else 5)
        lines.append(' '.join([str(s0)]+["%d %d"%(r.randint(1,hi),r.randint(1,1000)) for _ in range(s0)]))
    return "%d %d\n%s\n"%(g,W,'\n'.join(lines))

if __name__=='__main__':
    k=int(sys.argv[1]); seed=int(sys.argv[2]) if len(sys.argv)>2 else 1679*100+k
    sys.stdout.write(gen(random.Random(seed),k))
