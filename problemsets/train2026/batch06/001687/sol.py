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
    pal=[[False]*n for _ in range(n)]
    cut=[0]*n
    for j in range(n):
        cut[j]=j
        for i in range(j+1):
            if w[i]==w[j] and (j-i<2 or pal[i+1][j-1]):
                pal[i][j]=True
                cut[j]=0 if i==0 else min(cut[j],cut[i-1]+1)
    return cut[n-1]

if __name__=='__main__':
    print(sol(sys.stdin.read()))
