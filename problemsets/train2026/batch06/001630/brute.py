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
    t=s.split(); n,m=int(t[0]),int(t[1]); bad=set(map(int,t[2:2+m]))
    def g(x):
        if x in bad or x>n: return 0
        if x==n: return 1
        return g(x+1)+g(x+2)
    return g(0)%M

if __name__=='__main__':
    print(brute(sys.stdin.read()))
