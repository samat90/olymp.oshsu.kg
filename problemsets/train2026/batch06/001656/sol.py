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
    t=s.split(); p,q,rr=map(int,t[:3]); a,b=t[3],t[4]
    prev=[j*p for j in range(len(b)+1)]
    for i,x in enumerate(a,1):
        cur=[i*q]
        for j,y in enumerate(b,1):
            cur.append(min(prev[j]+q,cur[j-1]+p,prev[j-1]+(0 if x==y else rr)))
        prev=cur
    return prev[-1]

if __name__=='__main__':
    print(sol(sys.stdin.read()))
