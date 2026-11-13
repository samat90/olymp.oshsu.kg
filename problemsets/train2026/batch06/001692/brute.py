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
    w=s.split()[0]; n=len(w); al=sorted(set(w))
    st='?'*n; seen={st}; q=deque([(st,0)])
    while q:
        x,d=q.popleft()
        if x==w: return d
        for l in range(n):
            for r_ in range(l,n):
                for c in al:
                    y=x[:l]+c*(r_-l+1)+x[r_+1:]
                    if y not in seen: seen.add(y); q.append((y,d+1))

if __name__=='__main__':
    print(brute(sys.stdin.read()))
