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
    t=list(map(int,s.split())); n,m=t[0],t[1]; a=t[2:]; cur=a[:m]; INF=10**18
    for i in range(1,n):
        new=[]
        for j in range(m):
            b=cur[j]
            if j>0 and cur[j-1]<b: b=cur[j-1]
            if j+1<m and cur[j+1]<b: b=cur[j+1]
            new.append(b+a[i*m+j])
        cur=new
    return min(cur)

if __name__=='__main__':
    print(sol(sys.stdin.read()))
