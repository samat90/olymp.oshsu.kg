import re,sys,glob,random,time,json,os
PRE='''import random,sys
M=10**9+7
def N(r,k,tiny,big):
    if k==0: return r.randint(1,tiny)
    if k==1: return r.randint(1,min(6,big))
    if k==2: return r.randint(1,min(30,big))
    return max(1,big*(k-2)//8)
def L(r,n,lo,hi): return [r.randint(lo,hi) for _ in range(n)]
def S(r,n,al='abc'): return ''.join(r.choice(al) for _ in range(n))
'''
def parse(path):
    txt=open(path,encoding='utf8').read()
    parts=re.split(r'^#### ',txt,flags=re.M)[1:]
    res=[]
    for p in parts:
        head,rest=p.split('\n',1)
        title,_,tl=head.partition('|')
        d={'title':title.strip(),'tl':float(tl.strip() or 1)}
        secs=re.split(r'^#([SEGAB])\n',rest,flags=re.M)
        for i in range(1,len(secs),2): d[secs[i]]=secs[i+1].strip('\n')
        res.append(d)
    return res
def load(d):
    ns={}
    exec(PRE+d['G']+'\n'+d['A']+'\n'+d['B'],ns)
    return ns
def main():
    probs=[]
    for f in sorted(glob.glob('src/*.txt')): probs+=parse(f)
    only=sys.argv[1] if len(sys.argv)>1 else None
    bad=0
    for i,d in enumerate(probs):
        code=1629+i; d['code']=code
        if only and only!='all' and str(code)!=only and not only.startswith('f'): continue
        ns=load(d)
        gen,sol,brute=ns['gen'],ns['sol'],ns['brute']
        for sd in range(300):
            s=gen(random.Random(sd),0)
            a,b=sol(s),brute(s)
            if str(a).strip()!=str(b).strip():
                print('MISMATCH',code,d['title'],repr(s[:200]),a,b); bad+=1; break
        tm=0
        for k in range(1,11):
            t=time.time(); s=gen(random.Random(code*100+k),k); sol(s); tm=max(tm,time.time()-t)
        print(code,d['title'],'ok' if not bad else '', 'maxtime %.2f'%tm, 'size',len(s),flush=True)
    print('total',len(probs),'bad',bad)
    json.dump([ (d['code'],d['title']) for d in probs],open('index.json','w'),ensure_ascii=False)
if __name__=="__main__" and sys.argv[1:2]!=["emit"]: main()

def emit(root):
    import shutil
    probs=[]
    for f in sorted(glob.glob('src/*.txt')): probs+=parse(f)
    titles=[d['title'] for d in probs]; assert len(set(titles))==len(titles)
    shutil.rmtree(root,ignore_errors=True)
    for i,d in enumerate(probs):
        code=1629+i; name='%06d'%code; ns=load(d)
        out=ns['sol'](d['E']+'\n')
        dd=os.path.join(root,name); os.makedirs(dd)
        st="# %s\n\n%s\n\n**Пример**\n\nВвод:\n```\n%s\n```\nВывод:\n```\n%s\n```\n"%(d['title'],d['S'],d['E'],str(out).strip())
        open(dd+'/statement.md','w',encoding='utf8').write(st)
        g=d['G'].split('\n')
        open(dd+'/gen.py','w',encoding='utf8').write(PRE+d['G']+"\n\nif __name__=='__main__':\n    k=int(sys.argv[1]); seed=int(sys.argv[2]) if len(sys.argv)>2 else %d*100+k\n    sys.stdout.write(gen(random.Random(seed),k))\n"%code)
        open(dd+'/sol.py','w',encoding='utf8').write(PRE+d['A']+"\n\nif __name__=='__main__':\n    print(sol(sys.stdin.read()))\n")
        open(dd+'/brute.py','w',encoding='utf8').write(PRE+d['B']+"\n\nif __name__=='__main__':\n    print(brute(sys.stdin.read()))\n")
        json.dump({'code':name,'title':d['title'],'topic':'Динамическое программирование','topic_key':'DP','time_limit':d['tl'],'memory_mb':256,'points':100,'tests':10,'seed_rule':'seed = code*100 + k, k = 1..10 (python gen.py k)','languages_same_tl':True},open(dd+'/meta.json','w',encoding='utf8'),ensure_ascii=False,indent=1)
    print('emitted',len(probs))
if len(sys.argv)>2 and sys.argv[1]=='emit': emit(sys.argv[2])
