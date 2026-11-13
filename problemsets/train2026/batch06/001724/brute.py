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
    from collections import deque
    t=list(map(int,s.split())); n=t[0]; a=t[1:1+n]
    d={0:0}; q=deque([0])
    while q:
        x=q.popleft()
        for y in range(x+1,min(n-1,x+a[x])+1):
            if y not in d: d[y]=d[x]+1; q.append(y)
    return d.get(n-1,-1)

if __name__=='__main__':
    print(brute(sys.stdin.read()))
