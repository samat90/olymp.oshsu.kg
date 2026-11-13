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
    w=s.split()[0]; n=len(w)
    a,b=1,(0 if w[0]=='0' else 1)
    for i in range(2,n+1):
        c=0
        if w[i-1]!='0': c+=b
        if 10<=int(w[i-2:i])<=26: c+=a
        a,b=b,c%M
    return b%M

if __name__=='__main__':
    print(sol(sys.stdin.read()))
