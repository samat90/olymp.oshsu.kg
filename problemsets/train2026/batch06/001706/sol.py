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
    t=s.split(); n=int(t[0]); ws=t[1:1+n]; reach={0}
    for w in ws:
        if len(set(w))<len(w): continue
        mk=0
        for ch in w: mk|=1<<(ord(ch)-97)
        reach|={x|mk for x in reach if not x&mk}
    return max(bin(x).count('1') for x in reach)

if __name__=='__main__':
    print(sol(sys.stdin.read()))
