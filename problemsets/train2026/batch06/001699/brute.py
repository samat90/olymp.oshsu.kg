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
    t=list(map(int,s.split())); n,k=t[0],t[1]; a=t[2:2+n]; tot=sum(a)
    if tot%k: return "NO"
    T=tot//k; sums=[0]*k
    def go(i):
        if i==n: return all(x==T for x in sums)
        for g in range(k):
            if sums[g]+a[i]<=T:
                sums[g]+=a[i]
                if go(i+1): sums[g]-=a[i]; return True
                sums[g]-=a[i]
        return False
    return "YES" if go(0) else "NO"

if __name__=='__main__':
    print(brute(sys.stdin.read()))
