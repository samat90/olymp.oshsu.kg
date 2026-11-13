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
    from bisect import bisect_left
    t=list(map(int,s.split())); n=t[0]
    p=sorted((t[1+2*i],-t[2+2*i]) for i in range(n)); d=[]
    for w,h in p:
        h=-h; i=bisect_left(d,h)
        if i==len(d): d.append(h)
        else: d[i]=h
    return len(d)

if __name__=='__main__':
    print(sol(sys.stdin.read()))
