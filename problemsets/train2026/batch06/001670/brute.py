import random,sys
M=10**9+7
def N(r,k,tiny,big):
    if k==0: return r.randint(1,tiny)
    if k==1: return r.randint(1,min(6,big))
    if k==2: return r.randint(1,min(30,big))
    return max(1,big*(k-2)//8)
def L(r,n,lo,hi): return [r.randint(lo,hi) for _ in range(n)]
def S(r,n,al='abc'): return ''.join(r.choice(al) for _ in range(n))
def brute(s):
    t=list(map(int,s.split())); n,W=t[0],t[1]; it=[(t[2+2*i],t[3+2*i]) for i in range(n)]
    def go(i,rem):
        if i==n: return 0
        w,v=it[i]
        return max(q*v+go(i+1,rem-q*w) for q in range(rem//w+1))
    return go(0,W)

if __name__=='__main__':
    print(brute(sys.stdin.read()))
