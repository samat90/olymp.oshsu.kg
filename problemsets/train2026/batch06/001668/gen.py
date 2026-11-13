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
    n=N(r,k,8,1000); al='ab' if k<3 else 'abcd'
    ws=set()
    tries=0
    while len(ws)<n and tries<50*n:
        tries+=1
        if ws and r.random()<0.7:
            w=r.choice(sorted(ws)) if k==0 else r.choice(list(ws))
            if len(w)<16:
                i=r.randint(0,len(w)); ws.add(w[:i]+r.choice(al)+w[i:])
        else: ws.add(S(r,r.randint(1,(4 if k<4 else 8)),al))
    ws=sorted(ws); r.shuffle(ws)
    return "%d\n%s\n"%(len(ws),'\n'.join(ws))

if __name__=='__main__':
    k=int(sys.argv[1]); seed=int(sys.argv[2]) if len(sys.argv)>2 else 1668*100+k
    sys.stdout.write(gen(random.Random(seed),k))
