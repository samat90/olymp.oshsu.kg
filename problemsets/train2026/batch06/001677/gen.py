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
    n=N(r,k,10,100); A=N(r,k,20,100); B=N(r,k,20,100)
    hi=max(2,min(100,max(A,B)//3))
    return "%d %d %d\n%s\n"%(n,A,B,'\n'.join("%d %d %d"%(r.randint(1,hi),r.randint(1,hi),r.randint(1,1000)) for _ in range(n)))

if __name__=='__main__':
    k=int(sys.argv[1]); seed=int(sys.argv[2]) if len(sys.argv)>2 else 1677*100+k
    sys.stdout.write(gen(random.Random(seed),k))
