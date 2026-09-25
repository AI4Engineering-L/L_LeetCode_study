from course_builder import add

add(124,'位运算在二进制表示上操作。n&(n−1)删除最低位的1，因此循环次数等于置位数。Python整数没有固定32位溢出，位反转题必须显式截取低32位；负整数的无限符号扩展不能直接套“不断清除1直到零”的循环。二进制加法逐位维护carry。',
'''def popcount(n):
    if n<0: raise ValueError('popcount requires nonnegative integer')
    count=0
    while n: n&=n-1; count+=1
    return count

def reverse_bits32(n):
    n&=(1<<32)-1; out=0
    for _ in range(32): out=(out<<1)|(n&1); n>>=1
    return out

def add_binary(a,b):
    if any(c not in '01' for c in a+b): raise ValueError('binary strings required')
    i,j=len(a)-1,len(b)-1; carry=0; out=[]
    while i>=0 or j>=0 or carry:
        if i>=0: carry+=ord(a[i])-48; i-=1
        if j>=0: carry+=ord(b[j])-48; j-=1
        out.append(str(carry&1)); carry>>=1
    return ''.join(reversed(out)).lstrip('0') or '0'
''',
'''n=44; rows=[]
while n:
    nxt=n&(n-1); rows.append((n,format(n,'08b'),format(nxt,'08b'))); n=nxt
show_table(['十进制','二进制','清除最低1'],rows)''',
'''assert popcount(0)==0 and popcount(7)==3
assert add_binary('11','1')=='100' and add_binary('000','0')=='0'
for n in range(1000):
    assert popcount(n)==n.bit_count()
    assert reverse_bits32(reverse_bits32(n))==n
assert reverse_bits32(-1)==(1<<32)-1
for a in range(64):
    for b in range(64): assert add_binary(format(a,'b'),format(b,'b'))==format(a+b,'b')
try: popcount(-1)
except ValueError: pass
else: raise AssertionError('negative domain must be rejected')''',
'n−1把最低1变为0，并把其右侧零变成1；与原数相与正好只删除那一位。反转循环每步把原数最低位接到输出末尾，32步后各位位置映射i→31−i。加法carry记录来自较低位的进位，保持部分和一致。',
'popcount执行O(置位数)次整数位操作；任意精度整数的每次位操作成本随位宽增长。32位反转固定O(1)；字符串加法O(max(m,n))时间和输出空间。')

add(125,'子掩码枚举中的(s−1)&mask先减一，再清除不属于原集合的位，可按降序遍历所有子集。异或能抵消出现偶数次的数。最大异或Trie按高位优先寻找相反位：高位增加的收益大于所有低位之和，因此可以逐位贪心。',
'''def enumerate_submasks(mask):
    if mask<0: raise ValueError('nonnegative mask required')
    out=[]; sub=mask
    while True:
        out.append(sub)
        if sub==0: return out
        sub=(sub-1)&mask

def single_number(nums):
    answer=0
    for x in nums: answer^=x
    return answer

class BinaryTrie:
    def __init__(self,bits=32):
        if bits<1: raise ValueError('positive bit width required')
        self.bits=bits; self.children=[[-1,-1]]; self.size=0
    def _check(self,x):
        if not 0<=x<1<<self.bits: raise ValueError('value outside bit width')
    def insert(self,x):
        self._check(x); node=0
        for shift in range(self.bits-1,-1,-1):
            bit=x>>shift&1
            if self.children[node][bit]==-1: self.children[node][bit]=len(self.children); self.children.append([-1,-1])
            node=self.children[node][bit]
        self.size+=1
    def max_xor(self,x):
        self._check(x)
        if not self.size: raise ValueError('empty trie')
        node=answer=0
        for shift in range(self.bits-1,-1,-1):
            bit=x>>shift&1; opposite=bit^1
            if self.children[node][opposite]!=-1: answer|=1<<shift; node=self.children[node][opposite]
            else: node=self.children[node][bit]
        return answer

def find_maximum_xor(nums):
    if not nums: return 0
    trie=BinaryTrie(max(1,max(nums).bit_length()))
    for x in nums: trie.insert(x)
    return max(trie.max_xor(x) for x in nums)
''',
'''mask=0b10110
show_table(['子掩码','二进制','元素数'],[(s,format(s,'05b'),s.bit_count()) for s in enumerate_submasks(mask)])
print('最大异或',find_maximum_xor([3,10,5,25,2,8]))''',
'''assert single_number([2,2,1])==1
assert find_maximum_xor([3,10,5,25,2,8])==28
for mask in range(64):
    subs=enumerate_submasks(mask)
    assert subs==sorted((s for s in range(mask+1) if s&mask==s),reverse=True)
    assert len(subs)==len(set(subs))==1<<mask.bit_count()
from random import Random
rng=Random(125)
for _ in range(150):
    a=[rng.randrange(1024) for _ in range(rng.randrange(1,16))]
    assert find_maximum_xor(a)==max(x^y for x in a for y in a)
trie=BinaryTrie(4); trie.insert(3); trie.insert(3)
assert trie.max_xor(12)==15''',
'子掩码更新给出当前集合编码以下的最大合法编码，因此无重无漏，0必须显式处理否则会回到mask。Trie每一层选可行的最大异或位；若高位可取1，任何高位取0的方案都不可能被低位补偿。',
'含k个1的掩码有2^k个子集，输出本身就是指数规模。Trie插入/查询O(B)，总O(nB)时间空间上界。最大异或输入为非负整数；单独异或抵消要求除目标外其他元素出现偶数次。')

add(126,'欧几里得算法保留公约数集合：a与b的公约数也整除a%b，反之亦然。扩展算法同时跟踪每个余数如何写成原输入的线性组合，最终得到Bézout系数。字符串“公因子”不是字符集合交集，而是共同的重复基本块。',
'''def gcd_euclid(a,b):
    a,b=abs(a),abs(b)
    while b: a,b=b,a%b
    return a

def extended_gcd(a,b):
    old_r,r=abs(a),abs(b); old_x,x=1,0; old_y,y=0,1
    while r:
        q=old_r//r
        old_r,r=r,old_r-q*r; old_x,x=x,old_x-q*x; old_y,y=y,old_y-q*y
    return old_r,old_x*(1 if a>=0 else -1),old_y*(1 if b>=0 else -1)

def lcm(a,b): return abs((a//gcd_euclid(a,b))*b) if a and b else 0

def gcd_of_strings(a,b):
    if not a or not b or a+b!=b+a: return ''
    return a[:gcd_euclid(len(a),len(b))]
''',
'''a,b=252,105; rows=[]
while b: rows.append((a,b,a//b,a%b)); a,b=b,a%b
show_table(['a','b','商','余数'],rows)
g,x,y=extended_gcd(252,105); print(f'252×{x}+105×{y}={g}')''',
'''import math
assert gcd_euclid(54,24)==6 and gcd_euclid(0,0)==0
assert gcd_of_strings('ABCABC','ABC')=='ABC'
assert gcd_of_strings('ABABAB','ABAB')=='AB' and gcd_of_strings('LEET','CODE')==''
for a in range(-40,41):
    for b in range(-40,41):
        g,x,y=extended_gcd(a,b)
        assert g==gcd_euclid(a,b)==math.gcd(a,b)
        assert a*x+b*y==g
        assert lcm(a,b)==math.lcm(a,b)''',
'余数变换是可逆的整数线性组合，因此公约数不变。扩展算法每轮保留r=a·x+b·y的不变量。非空字符串若ab=ba，则都由同一原始串重复组成，公共重复块最大长度为两长度的最大公约数。',
'整数GCD执行O(log min(|a|,|b|))级别除法次数，实际大整数除法位复杂度另计；字符串拼接比较O(|a|+|b|)时间空间。约定gcd(0,0)=0，含0的lcm=0；空字符串扩展返回空串。')

add(127,'逐数试除重复做很多整除检查。筛法从已知质数p开始标记其倍数；小于p²的倍数已有更小质因子处理，因此可从p²起步。最小质因子表不仅判断素性，还把多次分解查询变成不断除去最小因子的过程。',
'''from math import isqrt

def sieve(n):
    if n<=2: return []
    prime=[True]*n; prime[0]=prime[1]=False
    for p in range(2,isqrt(n-1)+1):
        if prime[p]:
            for x in range(p*p,n,p): prime[x]=False
    return [x for x in range(2,n) if prime[x]]

def smallest_prime_factors(n):
    if n<0: raise ValueError('nonnegative bound required')
    spf=list(range(n+1))
    for p in range(2,isqrt(n)+1):
        if spf[p]==p:
            for x in range(p*p,n+1,p):
                if spf[x]==x: spf[x]=p
    return spf

def factorize(x,spf):
    if not 1<=x<len(spf): raise ValueError('x must be positive and covered by the SPF table')
    factors={}
    while x>1:
        p=spf[x]; factors[p]=factors.get(p,0)+1; x//=p
    return factors
''',
'''spf=smallest_prime_factors(30)
show_table(['整数','最小质因子','质因数分解'],[(x,spf[x],factorize(x,spf)) for x in range(2,21)])''',
'''assert sieve(10)==[2,3,5,7] and sieve(2)==[] and sieve(0)==[]
spf=smallest_prime_factors(500)
def trial_prime(x): return x>=2 and all(x%d for d in range(2,isqrt(x)+1))
for x in range(1,501):
    factors=factorize(x,spf); product=1
    for p,e in factors.items(): assert trial_prime(p); product*=p**e
    assert product==x
    if x>=2: assert spf[x]==next(d for d in range(2,x+1) if x%d==0)
assert sieve(501)==[x for x in range(501) if trial_prime(x)]''',
'每个合数都有不超过平方根的质因子，所以最终都会被标记；质数不会被更小质数整除。SPF只在尚未被标记时赋值，按p从小到大处理保证记录最小质因子。分解每轮严格减小x并保持“已取因子乘积×剩余x=原值”。',
'埃拉托斯特尼筛O(n log log n)算术工作量、O(n)空间；SPF同级预处理，分解最多O(log x)次整除。sieve返回严格小于n的质数，SPF表包含上界n，两个边界不混用。')

add(128,'模运算中加减乘可直接化简，除法不行：只有与模数互素的元素才有逆元。快速幂按指数二进制分解，每次平方底数、处理最低指数位。超长十进制指数不必转换为一个巨大整数，读入新位d后把原结果提升十次方再乘a^d。',
'''def mod_pow(a,n,mod):
    if n<0 or mod<=0: raise ValueError('nonnegative exponent and positive modulus required')
    result=1%mod; a%=mod
    while n:
        if n&1: result=result*a%mod
        a=a*a%mod; n>>=1
    return result

def mod_inverse(a,mod):
    if mod<2: raise ValueError('inverse modulus must be at least 2')
    old_r,r=a%mod,mod; old_x,x=1,0
    while r:
        q=old_r//r; old_r,r=r,old_r-q*r; old_x,x=x,old_x-q*x
    if old_r!=1: raise ValueError('inverse does not exist: gcd != 1')
    return old_x%mod

def super_pow(a,digits):
    answer=1
    for digit in digits:
        if not isinstance(digit,int) or not 0<=digit<=9: raise ValueError('decimal exponent digits required')
        answer=mod_pow(answer,10,1337)*mod_pow(a,digit,1337)%1337
    return answer
''',
'''a,n,mod=3,13,17; result=1; rows=[]
while n:
    rows.append((n,a,result,n&1))
    if n&1: result=result*a%mod
    a=a*a%mod; n>>=1
show_table(['剩余指数','当前底数','累计结果','是否相乘'],rows)
print('最终结果',result)''',
'''import math
assert mod_inverse(3,11)==4 and mod_pow(4,0,1)==0
for a in range(-12,13):
    for n in range(20):
        for mod in range(1,15): assert mod_pow(a,n,mod)==pow(a,n,mod)
    for mod in range(2,20):
        if math.gcd(a,mod)==1: assert a*mod_inverse(a,mod)%mod==1
        else:
            try: mod_inverse(a,mod)
            except ValueError: pass
            else: raise AssertionError('noninvertible value accepted')
    for n in range(80): assert super_pow(a,list(map(int,str(n))))==pow(a,n,1337)
assert super_pow(2,[])==1''',
'快速幂保持result·a^n与原目标同余，处理奇偶后不变量不变。扩展GCD给出ax+my=g，只有g=1时x才是逆元。指数逐位更新利用a^(10e+d)=(a^e)^10a^d，对任意正模数成立，不依赖模数为素数。',
'快速幂O(log n)次模乘；逆元O(log mod)级别除法；D位十进制指数O(D)次固定小指数模幂。均需计入大整数乘除位复杂度；不盲用费马小定理处理复合模数。')

add(129,'组合数计数“从n个不同元素中选k个”，不是排列。逐项乘除可保持精确整数而避免浮点。Catalan可由合法括号路径的反射法得到：全部路径减去越过边界的非法路径。满射计数使用容斥，把遗漏指定目标元素的函数交替加减。',
'''def binomial(n,k):
    if n<0: raise ValueError('nonnegative n required')
    if k<0 or k>n: return 0
    k=min(k,n-k); answer=1
    for i in range(1,k+1): answer=answer*(n-k+i)//i
    return answer

def catalan(n):
    if n<0: raise ValueError('nonnegative n required')
    return binomial(2*n,n)//(n+1)

def count_onto_small(n,k):
    if min(n,k)<0: raise ValueError('nonnegative sizes required')
    if k>n: return 0
    return sum((-1)**i*binomial(k,i)*(k-i)**n for i in range(k+1))
''',
'''n,k=4,3
show_table(['遗漏目标数i','选遗漏集合','剩余函数数','带符号贡献'],[(i,binomial(k,i),(k-i)**n,(-1)**i*binomial(k,i)*(k-i)**n) for i in range(k+1)])
print('满射数',count_onto_small(n,k))''',
'''import math
from itertools import product
assert binomial(5,2)==10 and binomial(3,5)==0 and catalan(3)==5
for n in range(25):
    for k in range(n+1): assert binomial(n,k)==math.comb(n,k)
for n in range(6):
    valid=0
    for seq in product((1,-1),repeat=2*n):
        total=0; good=True
        for x in seq:
            total+=x
            if total<0: good=False
        valid+=good and total==0
    assert catalan(n)==valid
    for k in range(5): assert count_onto_small(n,k)==sum(set(values)==set(range(k)) for values in product(range(k),repeat=n))''',
'容斥中，一个恰好遗漏r个目标的函数被计数∑(-1)^i C(r,i)=(1−1)^r，因此只保留r=0的满射。Catalan=C(2n,n)−C(2n,n+1)=C(2n,n)/(n+1)。这些等式在整数域计算，不引入模逆元存在性的额外前提。',
'组合数O(min(k,n−k))次大整数乘除；Catalan同阶；小满射实现O(k²)级组合数算术上界，可预计算一行降为O(k)项。输出整数位数不可忽略；空集到空集的函数数为1。')

add(130,'若状态满足线性递推x[t+1]=A·x[t]，那么多步转移就是A的幂。二进制快速幂适用于矩阵，因为矩阵乘法满足结合律；一般矩阵不交换，所以不能随意改变乘法次序。状态维度必须固定且小，否则矩阵乘法本身可能比线性DP更贵。',
'''def matmul_mod(a,b,mod):
    if mod is not None and mod<=0: raise ValueError('positive modulus required')
    if not a or not b: return []
    rows,inner,cols=len(a),len(a[0]),len(b[0])
    if any(len(row)!=inner for row in a) or len(b)!=inner or any(len(row)!=cols for row in b): raise ValueError('incompatible rectangular matrices')
    out=[[0]*cols for _ in range(rows)]
    for i in range(rows):
        for k in range(inner):
            for j in range(cols):
                out[i][j]+=a[i][k]*b[k][j]
                if mod is not None: out[i][j]%=mod
    return out

def matpow_mod(a,n,mod):
    size=len(a)
    if n<0 or any(len(row)!=size for row in a): raise ValueError('square matrix and nonnegative exponent required')
    result=[[int(i==j) if mod is None else int(i==j)%mod for j in range(size)] for i in range(size)]; base=[row[:] for row in a]
    while n:
        if n&1: result=matmul_mod(result,base,mod)
        base=matmul_mod(base,base,mod); n>>=1
    return result

def fib_matrix(n):
    if n<0: raise ValueError('nonnegative index required')
    return matpow_mod([[1,1],[1,0]],n,None)[0][1]

def count_vowel_permutation(n):
    if n<0: raise ValueError('nonnegative length required')
    if n==0: return 1
    edges={0:[1],1:[0,2],2:[0,1,3,4],3:[2,4],4:[0]}; matrix=[[0]*5 for _ in range(5)]
    for old,nexts in edges.items():
        for new in nexts: matrix[new][old]=1
    power=matpow_mod(matrix,n-1,10**9+7)
    return sum(map(sum,power))%(10**9+7)
''',
'''matrix=[[1,1],[1,0]]
show_table(['指数','矩阵幂','F(n)'],[(n,matpow_mod(matrix,n,None),fib_matrix(n)) for n in range(6)])''',
'''assert matpow_mod([[2,3],[4,5]],0,17)==[[1,0],[0,1]]
assert fib_matrix(0)==0 and fib_matrix(10)==55
assert count_vowel_permutation(1)==5 and count_vowel_permutation(2)==10 and count_vowel_permutation(5)==68
x,y=0,1
for n in range(120): assert fib_matrix(n)==x; x,y=y,x+y
edges={0:[1],1:[0,2],2:[0,1,3,4],3:[2,4],4:[0]}; dp=[1]*5
for n in range(1,40):
    assert count_vowel_permutation(n)==sum(dp)%(10**9+7)
    nxt=[0]*5
    for old,targets in edges.items():
        for new in targets: nxt[new]+=dp[old]
    dp=nxt
assert matmul_mod([[1,2,3]],[[4],[5],[6]],97)==[[32]]''',
'转移矩阵的列代表旧状态、行代表新状态。乘法展开正好累加所有一步来源，矩阵幂相乘拼接独立转移步。快速幂保持已累积结果与尚未处理的幂因子乘积不变；零次幂必须为单位阵而非零阵。',
'd维稠密矩阵幂O(d³ log n)次算术操作、O(d²)空间。fib_matrix用mod=None得到精确整数，结果位数为Θ(n)，因此不能称总位复杂度O(log n)。元音计数采用模10^9+7。')
