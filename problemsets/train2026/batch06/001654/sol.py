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
    a,b=s.split()[:2]; n,m=len(a),len(b)
    F=[[0]*(m+2) for _ in range(n+2)]
    for i in range(n-1,-1,-1):
        for j in range(m-1,-1,-1):
            F[i][j]=F[i+1][j+1]+1 if a[i]==b[j] else max(F[i+1][j],F[i][j+1])
    al=sorted(set(a)&set(b))
    nxa=[{} for _ in range(n+1)]; nxb=[{} for _ in range(m+1)]
    cur={}
    for i in range(n-1,-1,-1):
        cur=dict(cur); cur[a[i]]=i; nxa[i]=cur
    cur={}
    for j in range(m-1,-1,-1):
        cur=dict(cur); cur[b[j]]=j; nxb[j]=cur
    i=j=0; out=[]; need=F[0][0]
    while need>0:
        for c in al:
            if c in nxa[i] and c in nxb[j]:
                p=nxa[i][c]; q=nxb[j][c]
                if F[p+1][q+1]==need-1:
                    out.append(c); i=p+1; j=q+1; need-=1; break
    return "%d\n%s"%(len(out),''.join(out))

if __name__=='__main__':
    print(sol(sys.stdin.read()))
