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
    n=N(r,k,8,14); kk=r.randint(1,min(n,4))
    a=L(r,n,1,20 if k>3 else 5)
    if r.random()<0.5:
        # build solvable: split into groups
        kk=r.randint(1,min(n,4)); tot=r.randint(kk, 20*(n//kk))
        a=[]
        for g in range(kk):
            rem=tot; cnt=0; parts=[]
            while rem>0 and len(a)+len(parts)<n-(kk-g-1):
                x=r.randint(1,min(20,rem)); parts.append(x); rem-=x
            a+=parts
            if rem>0: break
        a=a[:14]; n=len(a)
        if n<kk: kk=1
    return "%d %d\n%s\n"%(len(a),kk,' '.join(map(str,a)))

if __name__=='__main__':
    k=int(sys.argv[1]); seed=int(sys.argv[2]) if len(sys.argv)>2 else 1699*100+k
    sys.stdout.write(gen(random.Random(seed),k))
