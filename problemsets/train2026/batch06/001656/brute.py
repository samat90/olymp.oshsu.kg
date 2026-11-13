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
    t=s.split(); p,q,rr=map(int,t[:3]); a,b=t[3],t[4]
    def f(i,j):
        if i==len(a): return (len(b)-j)*p
        if j==len(b): return (len(a)-i)*q
        return min(f(i+1,j)+q,f(i,j+1)+p,f(i+1,j+1)+(0 if a[i]==b[j] else rr))
    return f(0,0)

if __name__=='__main__':
    print(brute(sys.stdin.read()))
