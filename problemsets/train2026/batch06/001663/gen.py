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
    n=N(r,k,5,1000); m=N(r,k,5,1000); al='ab' if k<6 else 'abc'
    a=S(r,n,al); b=S(r,m,al)
    if r.random()<0.6:
        i=j=0; c=[]
        while i<n or j<m:
            if j>=m or (i<n and r.random()<0.5): c.append(a[i]); i+=1
            else: c.append(b[j]); j+=1
        c=''.join(c)
        if r.random()<0.3 and len(c)>1:
            c=list(c); x=r.randrange(len(c)); c[x]=r.choice(al); c=''.join(c)
    else: c=S(r,n+m,al)
    return a+"\n"+b+"\n"+c+"\n"

if __name__=='__main__':
    k=int(sys.argv[1]); seed=int(sys.argv[2]) if len(sys.argv)>2 else 1663*100+k
    sys.stdout.write(gen(random.Random(seed),k))
