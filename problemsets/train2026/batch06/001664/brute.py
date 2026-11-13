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
    p,t=s.split()[:2]
    def f(i,j):
        if i==len(p): return j==len(t)
        if p[i]=='*': return any(f(i+1,x) for x in range(j,len(t)+1))
        return j<len(t) and (p[i]=='?' or p[i]==t[j]) and f(i+1,j+1)
    return "YES" if f(0,0) else "NO"

if __name__=='__main__':
    print(brute(sys.stdin.read()))
