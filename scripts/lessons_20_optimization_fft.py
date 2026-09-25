from course_builder import add

OPT='''def _cost_size(cost):
    n=len(cost)-1
    if n<0 or any(len(row)!=n+1 for row in cost): raise ValueError('cost must be an (n+1)x(n+1) matrix')
    return n

def partition_dp_quadratic(cost,k):
    n=_cost_size(cost)
    if k<0: raise ValueError('nonnegative segment count required')
    if k>n: return float('inf')
    prev=[0]+[float('inf')]*n
    for groups in range(1,k+1):
        dp=[float('inf')]*(n+1)
        for r in range(groups,n+1): dp[r]=min(prev[l]+cost[l][r] for l in range(groups-1,r))
        prev=dp
    return prev[n]

def _check_monge(cost):
    n=_cost_size(cost)
    for l in range(n):
        for r in range(l+1,n+1):
            x=cost[l][r]
            if x!=x or x in (float('inf'),float('-inf')): raise ValueError('finite segment costs required for this check')
    for l in range(n-1):
        for r in range(l+2,n):
            if cost[l][r]+cost[l+1][r+1]>cost[l][r+1]+cost[l+1][r]: raise ValueError('Monge inequality failed; use the quadratic reference')

def divide_conquer_dp(cost,k,*,check=True):
    n=_cost_size(cost)
    if k<0: raise ValueError('nonnegative segment count required')
    if k>n: return float('inf')
    if check: _check_monge(cost)
    prev=[0]+[float('inf')]*n
    for groups in range(1,k+1):
        dp=[float('inf')]*(n+1)
        def compute(left,right,opt_left,opt_right):
            if left>right: return
            mid=(left+right)//2; best=float('inf'); split=opt_left
            for l in range(opt_left,min(mid-1,opt_right)+1):
                value=prev[l]+cost[l][mid]
                if value<best: best=value; split=l
            dp[mid]=best
            compute(left,mid-1,opt_left,split); compute(mid+1,right,split,opt_right)
        compute(groups,n,groups-1,n-1); prev=dp
    return prev[n]

class _LineNode:
    def __init__(self,line): self.line=line; self.left=self.right=None

def _evaluate(line,x): return line[0]*x+line[1]

class LiChaoMin:
    def __init__(self,left,right):
        if left>right: raise ValueError('nonempty inclusive integer domain required')
        self.left=left; self.right=right; self.root=None
    def add_line(self,slope,intercept):
        def insert(node,l,r,line):
            if node is None: return _LineNode(line)
            mid=(l+r)//2
            if _evaluate(line,mid)<_evaluate(node.line,mid): line,node.line=node.line,line
            if l==r: return node
            if _evaluate(line,l)<_evaluate(node.line,l): node.left=insert(node.left,l,mid,line)
            elif _evaluate(line,r)<_evaluate(node.line,r): node.right=insert(node.right,mid+1,r,line)
            return node
        self.root=insert(self.root,self.left,self.right,(slope,intercept))
    def query(self,x):
        if not self.left<=x<=self.right: raise ValueError('query outside fixed integer domain')
        node=self.root; l,r=self.left,self.right; answer=float('inf')
        while node:
            answer=min(answer,_evaluate(node.line,x)); mid=(l+r)//2
            if l==r: break
            if x<=mid: node=node.left; r=mid
            else: node=node.right; l=mid+1
        return answer

def cht_dp_reference(a,b):
    if len(a)!=len(b): raise ValueError('equal lengths required')
    if not a: return []
    dp=[0]
    for i in range(1,len(a)): dp.append(min(dp[j]+b[j]*a[i] for j in range(i)))
    return dp

def cht_dp_li_chao(a,b):
    if len(a)!=len(b): raise ValueError('equal lengths required')
    if not a: return []
    tree=LiChaoMin(min(a),max(a)); tree.add_line(b[0],0); dp=[0]
    for i in range(1,len(a)): dp.append(tree.query(a[i])); tree.add_line(b[i],dp[-1])
    return dp
'''
add(145,'高级优化首先是一个有条件的定理，而不是能替换所有双重循环的模板。分段DP为dp[g][r]=min_l(dp[g−1][l]+cost[l][r])。若代价满足Monge不等式，最左最优切点随r不减，才可递归缩小搜索范围。另一类转移dp[i]=min_j(dp[j]+b[j]a[i])可看成查询一组直线的下包络；Li Chao不要求斜率或查询点单调。',OPT,
'''a=[1,2,3,4,2]; prefix=[0]
for x in a: prefix.append(prefix[-1]+x)
cost=[[0]*(len(a)+1) for _ in range(len(a)+1)]
for l in range(len(a)):
    for r in range(l+1,len(a)+1): cost[l][r]=(prefix[r]-prefix[l])**2
show_table(['段数','平方版','分治版'],[(k,partition_dp_quadratic(cost,k),divide_conquer_dp(cost,k)) for k in range(1,len(a)+1)])
lines=[(2,3),(-1,8),(2,1)]; tree=LiChaoMin(-4,6)
for line in lines: tree.add_line(*line)
show_table(['x','各直线值','最小值'],[(x,[_evaluate(line,x) for line in lines],tree.query(x)) for x in range(-4,7)])''',
'''from random import Random
from itertools import combinations
rng=Random(145)
def squared_cost(a):
    prefix=[0]
    for x in a: prefix.append(prefix[-1]+x)
    return [[(prefix[r]-prefix[l])**2 if r>=l else 0 for r in range(len(a)+1)] for l in range(len(a)+1)]
for n in range(1,16):
    for _ in range(8):
        a=[rng.randrange(6) for _ in range(n)]; cost=squared_cost(a)
        for k in range(1,n+1): assert divide_conquer_dp(cost,k)==partition_dp_quadratic(cost,k)
for n in range(1,8):
    a=list(range(1,n+1)); cost=squared_cost(a)
    for k in range(1,n+1):
        expected=min(sum(cost[l][r] for l,r in zip((0,)+cuts,cuts+(n,))) for cuts in combinations(range(1,n),k-1))
        assert partition_dp_quadratic(cost,k)==expected
try: divide_conquer_dp(squared_cost([1,1,-2]),2)
except ValueError: pass
else: raise AssertionError('failed Monge condition must be reported')
lines=[]; tree=LiChaoMin(-30,30)
for _ in range(70):
    line=(rng.randrange(-20,21),rng.randrange(-100,101)); lines.append(line); tree.add_line(*line)
    for x in range(-30,31): assert tree.query(x)==min(_evaluate(line,x) for line in lines)
for _ in range(70):
    a=[rng.randrange(-20,21) for _ in range(14)]; b=[rng.randrange(-6,7) for _ in a]
    assert cht_dp_li_chao(a,b)==cht_dp_reference(a,b)
assert cht_dp_li_chao([10**30,-10**30,10**30+1],[10**30,10**30,-2])==cht_dp_reference([10**30,-10**30,10**30+1],[10**30,10**30,-2])''',
'Monge条件C(a,c)+C(b,d)≤C(a,d)+C(b,c)在加上每行dp[g−1][l]后仍成立，最左最小值位置因此随列单调。这里对有效三角域检查相邻四边形，它们可望远镜相加得到更大矩形不等式。非负数组的区间和平方差为−2·左外段和·右外段和≤0。Li Chao在中点保留更优直线，另一条线只可能在一侧重新变优；沿查询路径取最小值即可。Knuth还需不同的区间递推和夹逼条件，不能由本章Monge检查自动推出。',
'平方参照O(kn²)；已满足单调条件的分治部分O(kn log n)，但默认Monge校验和输入矩阵本身仍为O(n²)，必须计入总成本。Li Chao在整数域宽度C上每次插入/查询O(log C)，不计算浮点交点；精确整数乘法位复杂度另计。check=False仅可用于已独立证明的代价，不能用来绕过失败测试。')

FFT='''from cmath import exp,pi
from functools import cache
from math import isqrt

def convolve_naive(a,b):
    if not a or not b: return []
    out=[0]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b): out[i+j]+=x*y
    return out

def fft(values,invert=False):
    a=list(map(complex,values)); n=len(a)
    if not n: return []
    if n&(n-1): raise ValueError('power-of-two transform length required')
    j=0
    for i in range(1,n):
        bit=n>>1
        while j&bit: j^=bit; bit>>=1
        j^=bit
        if i<j: a[i],a[j]=a[j],a[i]
    length=2
    while length<=n:
        root=exp((2j if invert else -2j)*pi/length)
        for start in range(0,n,length):
            w=1
            for offset in range(length//2):
                u=a[start+offset]; v=a[start+offset+length//2]*w
                a[start+offset]=u+v; a[start+offset+length//2]=u-v; w*=root
        length*=2
    return [x/n for x in a] if invert else a

def convolve_fft(a,b):
    # Returns floating approximations, not an exact arbitrary-integer convolution.
    if not a or not b: return []
    size=1; result_length=len(a)+len(b)-1
    while size<result_length: size*=2
    left=fft(list(a)+[0]*(size-len(a))); right=fft(list(b)+[0]*(size-len(b)))
    return [x.real for x in fft([x*y for x,y in zip(left,right)],True)[:result_length]]

@cache
def _is_prime(mod):
    if mod<2: return False
    if mod%2==0: return mod==2
    return all(mod%d for d in range(3,isqrt(mod)+1,2))

def ntt(values,invert,mod,primitive_root):
    a=[x%mod for x in values]; n=len(a)
    if not n: return []
    if n&(n-1) or not _is_prime(mod) or (mod-1)%n: raise ValueError('prime modulus and power-of-two length dividing mod-1 required')
    root_n=pow(primitive_root,(mod-1)//n,mod)
    if pow(root_n,n,mod)!=1 or n>1 and pow(root_n,n//2,mod)==1: raise ValueError('root does not provide required order')
    j=0
    for i in range(1,n):
        bit=n>>1
        while j&bit: j^=bit; bit>>=1
        j^=bit
        if i<j: a[i],a[j]=a[j],a[i]
    length=2
    while length<=n:
        root=pow(primitive_root,(mod-1)//length,mod)
        if invert: root=pow(root,mod-2,mod)
        for start in range(0,n,length):
            w=1
            for offset in range(length//2):
                u=a[start+offset]; v=a[start+offset+length//2]*w%mod
                a[start+offset]=(u+v)%mod; a[start+offset+length//2]=(u-v)%mod; w=w*root%mod
        length*=2
    if invert:
        inv=pow(n,mod-2,mod); a=[x*inv%mod for x in a]
    return a

def convolve_ntt(a,b,mod=998244353,primitive_root=3):
    if not a or not b: return []
    size=1; length=len(a)+len(b)-1
    while size<length: size*=2
    left=ntt(list(a)+[0]*(size-len(a)),False,mod,primitive_root)
    right=ntt(list(b)+[0]*(size-len(b)),False,mod,primitive_root)
    return ntt([x*y%mod for x,y in zip(left,right)],True,mod,primitive_root)[:length]
'''
add(146,'卷积系数c[k]=∑a[i]b[k−i]是多项式乘法。DFT把卷积变成逐点乘法；按偶数、奇数下标拆分可递归复用较短DFT，得到蝶形网络。必须补零到至少len(a)+len(b)−1，否则得到循环卷积而发生折叠。FFT用复数浮点，NTT在满足单位根条件的有限域中计算，两者的精确性范围不同。',FFT,
'''a,b=[1,2],[3,4]; exact=convolve_naive(a,b); approximate=convolve_fft(a,b); modular=convolve_ntt(a,b)
show_table(['系数下标','直接整数卷积','浮点FFT近似','NTT模结果'],[(i,exact[i],approximate[i],modular[i]) for i in range(len(exact))])
values=[1,2,3,4]; spectrum=fft(values)
show_table(['频率','DFT实部','DFT虚部'],[(k,x.real,x.imag) for k,x in enumerate(spectrum)])''',
'''from random import Random
from math import isclose
rng=Random(146)
assert convolve_naive([1,2],[3,4])==[3,10,8]
assert convolve_ntt([1,2],[3,4])==[3,10,8]
for n in [1,2,4,8,16,32]:
    values=[rng.randrange(-100,101) for _ in range(n)]
    restored=fft(fft(values),True)
    assert all(abs(a-b)<1e-9 for a,b in zip(values,restored))
    assert ntt(ntt(values,False,998244353,3),True,998244353,3)==[x%998244353 for x in values]
for _ in range(140):
    a=[rng.randrange(-100,101) for _ in range(rng.randrange(1,30))]; b=[rng.randrange(-100,101) for _ in range(rng.randrange(1,30))]
    expected=convolve_naive(a,b); approximate=convolve_fft(a,b)
    assert all(isclose(x,y,rel_tol=1e-10,abs_tol=1e-7) for x,y in zip(expected,approximate))
    assert convolve_ntt(a,b)==[x%998244353 for x in expected]
assert ntt([1,2,3,4],False,17,3)
try: ntt([1,2,3,4],False,21,2)
except ValueError: pass
else: raise AssertionError('composite modulus must be rejected')
assert convolve_fft([],[])==convolve_ntt([],[])==[]''',
'DFT在单位根上求值，多项式乘法在每个点变成乘法，逆变换恢复系数。蝶形利用ω_N^(2k)=ω_(N/2)^k和ω_N^(k+N/2)=−ω_N^k。NTT要求模数为素数、变换长度整除p−1且所用根确有该阶，才能使用逆长度与逆单位根。当前代码明确返回FFT近似值，不把舍入接近整数当成任意大整数正确性的证明。',
'直接卷积O(nm)；补零长度N的FFT/NTT O(N log N)算术操作O(N)空间。NTT参数初次试除验证素性另有O(√p)代价并缓存。FFT测试仅覆盖长度<30、系数绝对值≤100且明确容差；更大范围需误差分析。NTT只保证模p结果，恢复更大有符号整数需额外模数与系数界。')
