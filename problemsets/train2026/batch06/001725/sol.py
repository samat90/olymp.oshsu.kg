import random,sys
M=10**9+7
def N(r,k,tiny,big):
    if k==0: return r.randint(1,tiny)
    if k==1: return r.randint(1,min(6,big))
    if k==2: return r.randint(1,min(30,big))
    return max(1,big*(k-2)//8)
def L(r,n,lo,hi): return [r.randint(lo,hi) for _ in range(n)]
def S(r,n,al='abc'): return ''.join(r.choice(al) for _ in range(n))
def sol(s):
    a,b=s.split()[:2]; K=int(b); d=list(map(int,a)); n=len(d)
    tight=0; res_free=[0]*K
    for dig in d:
        new=[0]*K
        for r_ in range(K):
            if res_free[r_]:
                for x in range(10): new[(r_+x)%K]+=res_free[r_]
        for x in range(dig): new[(tight+x)%K]+=1
        tight=(tight+dig)%K
        res_free=new
    total=res_free[0]+(1 if tight==0 else 0)
    return total-1  # remove zero

if __name__=='__main__':
    print(sol(sys.stdin.read()))
