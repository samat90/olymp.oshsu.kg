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
    n=N(r,k,8,1000); al='ab' if k<6 else 'abc'
    t=S(r,n,al); p=[]
    i=0
    while i<n:
        x=r.random(); ch=t[i]
        if x<0.3:
            p.append(ch+'*'); i+=1
            while i<n and t[i]==ch and r.random()<0.8: i+=1
        elif x<0.4: p.append('.'); i+=1
        elif x<0.5: p.append(r.choice(al)+'*')
        else: p.append(ch if r.random()<0.92 else r.choice(al)); i+=1
    p=''.join(p)
    return p+"\n"+t+"\n"

if __name__=='__main__':
    k=int(sys.argv[1]); seed=int(sys.argv[2]) if len(sys.argv)>2 else 1665*100+k
    sys.stdout.write(gen(random.Random(seed),k))
