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
    e=s.split()[0]; v=e[0::2]; op=e[1::2]
    def go(i,j):
        if i==j: return [v[i]=='T']
        res=[]
        for m in range(i,j):
            for x in go(i,m):
                for y in go(m+1,j):
                    o=op[m]
                    res.append(x and y if o=='&' else (x or y if o=='|' else x!=y))
        return res
    return sum(go(0,len(v)-1))%M

if __name__=='__main__':
    print(brute(sys.stdin.read()))
