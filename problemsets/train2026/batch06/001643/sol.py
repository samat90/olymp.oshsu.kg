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
    n=int(s.split()[0]); u=[1]; i2=i3=i5=0
    while len(u)<n:
        x=min(u[i2]*2,u[i3]*3,u[i5]*5); u.append(x)
        if x==u[i2]*2: i2+=1
        if x==u[i3]*3: i3+=1
        if x==u[i5]*5: i5+=1
    return u[n-1]

if __name__=='__main__':
    print(sol(sys.stdin.read()))
