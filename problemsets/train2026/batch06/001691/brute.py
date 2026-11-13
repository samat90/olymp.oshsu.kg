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
    t=list(map(int,s.split())); a=t[1:1+t[0]]
    def play(i,j,turn,diff):
        if i>j: return diff
        sgn=1 if turn==0 else -1
        r1=play(i+1,j,1-turn,diff+sgn*a[i]); r2=play(i,j-1,1-turn,diff+sgn*a[j])
        return max(r1,r2) if turn==0 else min(r1,r2)
    return play(0,len(a)-1,0,0)

if __name__=='__main__':
    print(brute(sys.stdin.read()))
