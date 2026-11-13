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
    t=list(map(int,s.split())); n=t[0]; p=1; rows=[]
    for i in range(1,n+1): rows.append(t[p:p+i]); p+=i
    cur=rows[-1][:]
    for i in range(n-2,-1,-1):
        cur=[rows[i][j]+min(cur[j],cur[j+1]) for j in range(i+1)]
    return cur[0]

if __name__=='__main__':
    print(sol(sys.stdin.read()))
