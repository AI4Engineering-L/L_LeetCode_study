from course_builder import add

add(104,'二维前缀状态dp[i][j]描述两个序列的前i、j个元素。LCS选择是否对齐最后一项；编辑距离枚举最后一次操作；子序列计数则对“用或不用当前字符”求和。它们共享网格形状，却有不同代数：max、min、sum不能混用。',
'''def lcs(a,b):
    dp=[0]*(len(b)+1)
    for x in a:
        old=dp; dp=[0]*(len(b)+1)
        for j,y in enumerate(b,1): dp[j]=old[j-1]+1 if x==y else max(old[j],dp[j-1])
    return dp[-1]

def edit_distance(a,b):
    dp=list(range(len(b)+1))
    for i,x in enumerate(a,1):
        old=dp; dp=[i]+[0]*len(b)
        for j,y in enumerate(b,1): dp[j]=old[j-1] if x==y else 1+min(old[j],dp[j-1],old[j-1])
    return dp[-1]

def num_distinct(s,t):
    dp=[1]+[0]*len(t)
    for x in s:
        for j in range(len(t),0,-1):
            if x==t[j-1]: dp[j]+=dp[j-1]
    return dp[-1]
''',
'''a,b='abcde','ace'; dp=[[0]*(len(b)+1) for _ in range(len(a)+1)]
for i,x in enumerate(a,1):
    for j,y in enumerate(b,1): dp[i][j]=dp[i-1][j-1]+1 if x==y else max(dp[i-1][j],dp[i][j-1])
show_table(['a的前缀','b前缀的LCS长度'],[(a[:i],row) for i,row in enumerate(dp)])''',
'''assert lcs('abcde','ace')==3 and edit_distance('horse','ros')==3
assert num_distinct('rabbbit','rabbit')==3 and num_distinct('abc','')==1
from itertools import product,combinations
from functools import cache
words=[''.join(p) for n in range(5) for p in product('ab',repeat=n)]
def subs(s): return {''.join(s[i] for i in ids) for k in range(len(s)+1) for ids in combinations(range(len(s)),k)}
@cache
def edit_ref(a,b):
    if not a or not b: return len(a)+len(b)
    return min(edit_ref(a[1:],b)+1,edit_ref(a,b[1:])+1,edit_ref(a[1:],b[1:])+(a[0]!=b[0]))
for a in words:
    for b in words:
        assert lcs(a,b)==max(map(len,subs(a)&subs(b)))
        assert edit_distance(a,b)==edit_ref(a,b)
        assert num_distinct(a,b)==sum(''.join(a[i] for i in ids)==b for ids in combinations(range(len(a)),len(b)))''',
'前缀边界明确处理空序列。LCS相同末字符可以在某个最优解中对齐，不同末字符至少丢弃一端；编辑距离按最后操作分解；计数的逆序更新保证一个来源字符至多匹配目标中的一个位置。',
'各算法O(mn)算术操作、O(n)辅助空间。编辑距离使用单位插入/删除/替换成本；计数保留任意精度整数，输出位数影响实际代价。')

add(105,'分词是前缀可达性，解码是前缀路径计数，通配符与正则是模式状态自动机。两种星号语义不同：通配符*匹配任意字符串；简化正则x*重复前一个元素。匹配必须覆盖整个字符串，不能把搜索某个子串当成完整匹配。',
'''def word_break(s,words):
    words=set(words); words.discard(''); dp=[True]+[False]*len(s)
    lengths={len(w) for w in words}
    for i in range(1,len(s)+1): dp[i]=any(i>=k and dp[i-k] and s[i-k:i] in words for k in lengths)
    return dp[-1]

def num_decodings(s):
    if not s: return 0
    dp=[0]*(len(s)+1); dp[0]=1
    for i in range(1,len(s)+1):
        if s[i-1]!='0': dp[i]+=dp[i-1]
        if i>=2 and '10'<=s[i-2:i]<='26': dp[i]+=dp[i-2]
    return dp[-1]

def wildcard_match(s,p):
    dp=[False]*(len(p)+1); dp[0]=True
    for j,c in enumerate(p,1): dp[j]=dp[j-1] and c=='*'
    for x in s:
        old=dp; dp=[False]*(len(p)+1)
        for j,c in enumerate(p,1): dp[j]=(dp[j-1] or old[j]) if c=='*' else old[j-1] and (c=='?' or c==x)
    return dp[-1]

def regex_match(s,p):
    if p.startswith('*') or '**' in p: raise ValueError('star requires a preceding atom')
    dp=[[False]*(len(p)+1) for _ in range(len(s)+1)]; dp[0][0]=True
    for i in range(len(s)+1):
        for j in range(1,len(p)+1):
            if p[j-1]=='*':
                dp[i][j]=dp[i][j-2] or (i>0 and (p[j-2]=='.' or p[j-2]==s[i-1]) and dp[i-1][j])
            elif i>0: dp[i][j]=(p[j-1]=='.' or p[j-1]==s[i-1]) and dp[i-1][j-1]
    return dp[-1][-1]
''',
'''s='226'; rows=[]; dp=[1]
for i in range(1,len(s)+1):
    one=dp[i-1] if s[i-1]!='0' else 0; two=dp[i-2] if i>=2 and '10'<=s[i-2:i]<='26' else 0
    dp.append(one+two); rows.append((s[:i],one,two,dp[i]))
show_table(['前缀','一位末码','两位末码','总数'],rows)''',
'''assert word_break('leetcode',['leet','code']) and not word_break('catsandog',['cats','dog','sand','and','cat'])
assert num_decodings('06')==0 and num_decodings('226')==3
assert regex_match('aab','c*a*b') and not regex_match('mississippi','mis*is*p*.')
assert regex_match('','a*') and wildcard_match('','**')
from itertools import product
from functools import cache
import re
@cache
def wildcard_ref(s,p):
    if not p: return not s
    if p[0]=='*': return wildcard_ref(s,p[1:]) or bool(s) and wildcard_ref(s[1:],p)
    return bool(s) and p[0] in ('?',s[0]) and wildcard_ref(s[1:],p[1:])
for n in range(4):
    for a in product('ab',repeat=n):
        s=''.join(a)
        for p in product('ab?*',repeat=3):
            p=''.join(p); assert wildcard_match(s,p)==wildcard_ref(s,p)
        for atoms in product(('a','b','.','a*','b*','.*'),repeat=2):
            p=''.join(atoms); assert regex_match(s,p)==bool(re.fullmatch(p,s))''',
'分词最后一段必须属于字典；解码最后一码长度只可能1或2，且0不可独立解码。通配符星号分为匹配空串或消耗一个字符；正则星号分为零次前一元素或再消耗一次，二者下标移动不同。',
'匹配DP O(|s||p|)时间；通配符O(|p|)辅助，正则此处O(|s||p|)辅助。分词含Python子串复制与哈希，保守O(n∑候选长度)字符工作量。解码输入为十进制数字串；简化正则只含普通字符、点和星号。')

add(106,'股票DP是带约束的状态机。状态必须说清持仓、已用交易次数与是否处于冷冻期；当天转移应读前一天的状态，避免无意中在同一天多次操作。费用只扣一次。所有接口允许不交易，最终只能返回未持仓收益。',
'''def max_profit_once(prices):
    low=float('inf'); best=0
    for p in prices: low=min(low,p); best=max(best,p-low)
    return best

def max_profit_k(prices,k):
    if k<=0: return 0
    if k>=len(prices)//2: return sum(max(0,b-a) for a,b in zip(prices,prices[1:]))
    buy=[float('-inf')]*(k+1); sell=[0]*(k+1)
    for p in prices:
        old_buy,old_sell=buy,sell; buy=old_buy[:]; sell=old_sell[:]
        for t in range(1,k+1):
            buy[t]=max(old_buy[t],old_sell[t-1]-p)
            sell[t]=max(old_sell[t],old_buy[t]+p)
    return sell[k]

def max_profit_cooldown(prices):
    hold=sold=float('-inf'); rest=0
    for p in prices: hold,sold,rest=max(hold,rest-p),hold+p,max(rest,sold)
    return max(0,sold,rest)

def max_profit_fee(prices,fee):
    hold=float('-inf'); cash=0
    for p in prices: hold,cash=max(hold,cash-p),max(cash,hold+p-fee)
    return cash
''',
'''prices=[1,2,3,0,2]; hold=sold=float('-inf'); rest=0; rows=[]
for day,p in enumerate(prices):
    hold,sold,rest=max(hold,rest-p),hold+p,max(rest,sold); rows.append((day,p,hold,sold,rest))
show_table(['天','价格','持仓','刚售出','可买入'],rows)''',
'''assert max_profit_once([7,1,5,3,6,4])==5
assert max_profit_cooldown([1,2,3,0,2])==3
assert max_profit_fee([1,3,2,8,4,9],2)==8
from itertools import product
from functools import cache

def brute(prices,k=99,fee=0,cooldown=False):
    @cache
    def f(i,holding,remaining,blocked):
        if i==len(prices): return float('-inf') if holding else 0
        best=f(i+1,holding,remaining,False)
        if holding and remaining: best=max(best,prices[i]-fee+f(i+1,False,remaining-1,cooldown))
        if not holding and not blocked and remaining: best=max(best,-prices[i]+f(i+1,True,remaining,False))
        return best
    return f(0,False,k,False)
for prices in product(range(3),repeat=5):
    assert max_profit_once(prices)==brute(prices,1)
    assert max_profit_k(prices,2)==brute(prices,2)
    assert max_profit_fee(prices,1)==brute(prices,fee=1)
    assert max_profit_cooldown(prices)==brute(prices,cooldown=True)''',
'每个合法交易过程映射到状态机的一条路径。枚举休息、买入、卖出三种动作完整覆盖合法路径，非法转移被状态限制排除。冷冻状态只能在卖出后经过一天休息再买；元组赋值右侧都读取旧值。',
'单次、冷冻和费用版O(n)时间O(1)辅助；k次版O(nk)时间O(k)辅助，k足够大时退化为无限交易O(n)。价格非负，手续费非负，交易必须先买后卖。')

add(107,'区间DP常通过“最后一步”恢复子问题独立性。戳气球若先选第一个戳的气球，邻接关系会变化；选最后戳的气球，两侧边界固定。合并石头还要记录要剩几堆，并检查每次合并减少k−1堆的整除条件。三角剖分选与边(l,r)相邻的最后三角形。',
'''from functools import cache
from itertools import accumulate

def burst_balloons(nums):
    a=[1]+list(nums)+[1]; n=len(a); dp=[[0]*n for _ in range(n)]
    for gap in range(2,n):
        for l in range(n-gap):
            r=l+gap; dp[l][r]=max(dp[l][k]+dp[k][r]+a[l]*a[k]*a[r] for k in range(l+1,r))
    return dp[0][-1]

def merge_stones(stones,k):
    if k<2: raise ValueError('k must be at least 2')
    n=len(stones)
    if not n: return 0
    if (n-1)%(k-1): return -1
    prefix=[0]+list(accumulate(stones))
    @cache
    def f(l,r,piles):
        length=r-l
        if length<piles or (length-piles)%(k-1): return float('inf')
        if length==1: return 0 if piles==1 else float('inf')
        if piles==1: return f(l,r,k)+prefix[r]-prefix[l]
        return min((f(l,m,1)+f(m,r,piles-1) for m in range(l+1,r,k-1)),default=float('inf'))
    return f(0,n,1)

def min_score_triangulation(values):
    n=len(values)
    if n<3: return 0
    dp=[[0]*n for _ in range(n)]
    for gap in range(2,n):
        for l in range(n-gap):
            r=l+gap; dp[l][r]=min(dp[l][k]+dp[k][r]+values[l]*values[k]*values[r] for k in range(l+1,r))
    return dp[0][-1]
''',
'''a=[3,1,5,8]; rows=[]
for k,x in enumerate(a):
    rows.append((k,x))
show_table(['候选最后戳下标','值'],rows)
print('完整区间最优',burst_balloons(a))
# 可直接检查一、二气球区间的独立答案。
show_table(['小输入','最优得分'],[(s,burst_balloons(s)) for s in [[],[3],[3,1],[1,5],[5,8]]])''',
'''assert burst_balloons([3,1,5,8])==167
assert merge_stones([3,2,4,1],2)==20 and merge_stones([3,2,4,1],3)==-1
assert min_score_triangulation([1,3,1,4,1,5])==13
@cache
def pop_ref(a):
    return max((a[i]*(a[i-1] if i else 1)*(a[i+1] if i+1<len(a) else 1)+pop_ref(a[:i]+a[i+1:]) for i in range(len(a))),default=0)
@cache
def merge_ref(a,k):
    if len(a)==1: return 0
    return min((sum(a[i:i+k])+merge_ref(a[:i]+(sum(a[i:i+k]),)+a[i+k:],k) for i in range(len(a)-k+1)),default=float('inf'))
from itertools import product
for a in product(range(1,4),repeat=5):
    assert burst_balloons(a)==pop_ref(a)
    for k in (2,3): assert merge_stones(a,k)==merge_ref(a,k)''',
'固定最后一步后，两侧操作互不改变边界，因此可以组合各自最优解。石头区间压成p堆必须满足长度与p模k−1同余；从k堆合成1堆才加整个区间和，不能在每次分割时重复加。三角形将凸多边形分成两个独立子多边形。',
'气球和三角剖分O(n³)时间O(n²)空间。石头记忆化使用(l,r,p)状态，保守O(n³k)时间O(n²k)空间上界；递归深度O(n)，仅用于题目小规模区间。')

add(108,'划分DP枚举最后一段起点。先规定段数是否固定、段长是否有上限，再决定状态维度。最大分块和是前缀最优；回文划分先预计算每段改成回文所需替换次数；工作日安排必须每天非空，不能用零成本空段凑天数。',
'''def max_sum_after_partitioning(arr,k):
    if k<=0: raise ValueError('positive segment limit required')
    dp=[0]+[float('-inf')]*len(arr)
    for i in range(1,len(arr)+1):
        maximum=float('-inf')
        for length in range(1,min(k,i)+1):
            maximum=max(maximum,arr[i-length]); dp[i]=max(dp[i],dp[i-length]+maximum*length)
    return dp[-1]

def palindrome_partition_k(s,k):
    n=len(s)
    if k==0: return 0 if not n else -1
    if k<0 or k>n: return -1
    cost=[[0]*n for _ in range(n)]
    for gap in range(1,n):
        for l in range(n-gap):
            r=l+gap; cost[l][r]=(cost[l+1][r-1] if gap>1 else 0)+(s[l]!=s[r])
    prev=[0]+[float('inf')]*n
    for groups in range(1,k+1):
        dp=[float('inf')]*(n+1)
        for i in range(groups,n+1): dp[i]=min(prev[j]+cost[j][i-1] for j in range(groups-1,i))
        prev=dp
    return prev[n]

def min_difficulty(jobs,d):
    n=len(jobs)
    if d==0: return 0 if not n else -1
    if n<d or d<0: return -1
    prev=[0]+[float('inf')]*n
    for day in range(1,d+1):
        dp=[float('inf')]*(n+1)
        for i in range(day,n+1):
            maximum=float('-inf')
            for j in range(i-1,day-2,-1): maximum=max(maximum,jobs[j]); dp[i]=min(dp[i],prev[j]+maximum)
        prev=dp
    return prev[n]
''',
'''a=[1,15,7,9,2,5,10]; show_table(['前缀长度','最大分块和，k=3'],[(i,max_sum_after_partitioning(a[:i],3)) for i in range(len(a)+1)])''',
'''assert max_sum_after_partitioning([1,15,7,9,2,5,10],3)==84
assert min_difficulty([6,5,4,3,2,1],2)==7 and min_difficulty([1,2],3)==-1
assert palindrome_partition_k('abc',2)==1 and palindrome_partition_k('abc',3)==0
from itertools import combinations,product

def partitions(a,k):
    for cuts in combinations(range(1,len(a)),k-1):
        ends=(0,)+cuts+(len(a),)
        yield [a[ends[i]:ends[i+1]] for i in range(k)]
for a in product(range(3),repeat=5):
    s=''.join(map(str,a))
    for k in range(1,6):
        ps=list(partitions(a,k)); sp=list(partitions(s,k))
        assert min_difficulty(a,k)==min(sum(max(x) for x in p) for p in ps)
        assert palindrome_partition_k(s,k)==min(sum(sum(x[i]!=x[-1-i] for i in range(len(x)//2)) for x in p) for p in sp)
    for limit in (1,2,3):
        want=max(sum(max(x)*len(x) for x in p) for k in range(1,6) for p in partitions(a,k) if all(len(x)<=limit for x in p))
        assert max_sum_after_partitioning(a,limit)==want''',
'每个合法划分都有唯一最后切点j；前缀最优加最后段代价枚举了全部划分。段数g的前缀至少长g，限制j≥g−1保证每段非空。回文修复成本等于相对位置不相等的对数，各对独立。',
'最大分块和O(nk)时间O(n)空间；回文划分O(n²+kn²)时间O(n²)空间；工作安排O(dn²)时间O(n)辅助。固定段数不合法时返回−1。')
