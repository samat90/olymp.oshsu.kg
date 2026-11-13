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
    t=list(map(int,s.split())); n,A,B=t[:3]
    dp=[[0]*(B+1) for _ in range(A+1)]
    for i in range(n):
        a,b,c=t[3+3*i:6+3*i]
        for x in range(A,a-1,-1):
            row=dp[x]; src=dp[x-a]
            for y in range(B,b-1,-1):
                if src[y-b]+c>row[y]: row[y]=src[y-b]+c
    return dp[A][B]

if __name__=='__main__':
    print(sol(sys.stdin.read()))
