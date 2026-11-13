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
    t=list(map(int,s.split())); n=t[0]; p=1; rows=[]
    for i in range(1,n+1): rows.append(t[p:p+i]); p+=i
    def go(i,j):
        if i==n-1: return rows[i][j]
        return rows[i][j]+min(go(i+1,j),go(i+1,j+1))
    return go(0,0)

if __name__=='__main__':
    print(brute(sys.stdin.read()))
