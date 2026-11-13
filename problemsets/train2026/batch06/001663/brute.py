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
    a,b,c=s.split()[:3]
    def f(i,j):
        if i+j==len(c): return i==len(a) and j==len(b)
        ch=c[i+j]
        return (i<len(a) and a[i]==ch and f(i+1,j)) or (j<len(b) and b[j]==ch and f(i,j+1))
    return "YES" if f(0,0) else "NO"

if __name__=='__main__':
    print(brute(sys.stdin.read()))
