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
    w=s.split()[0]
    from collections import deque
    seen={w}; q=deque([(w,0)])
    al=sorted(set(w))
    while q:
        x,d=q.popleft()
        if x==x[::-1]: return d
        for i in range(len(x)+1):
            for c in al:
                y=x[:i]+c+x[i:]
                if y not in seen: seen.add(y); q.append((y,d+1))

if __name__=='__main__':
    print(brute(sys.stdin.read()))
