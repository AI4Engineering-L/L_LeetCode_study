from course_builder import add

add(98,'递归首先定义答案：走到第n阶的最后一步来自n−1或n−2。直接递归重复计算同一个n；记忆化按状态去重；表格按依赖顺序计算。三者不是不同数学模型，只是同一个依赖图的不同求值策略。约定0阶有一种空走法。',
'''from functools import cache

def climb_stairs_recursive(n):
    if n<0: return 0
    if n<=1: return 1
    return climb_stairs_recursive(n-1)+climb_stairs_recursive(n-2)

def climb_stairs_memo(n):
    @cache
    def f(k):
        if k<0: return 0
        if k<=1: return 1
        return f(k-1)+f(k-2)
    return f(n)

def climb_stairs_table(n):
    if n<0: return 0
    dp=[1]*(n+1)
    for i in range(2,n+1): dp[i]=dp[i-1]+dp[i-2]
    return dp[n]
''',
'''dp=[1,1]
for i in range(2,8): dp.append(dp[-1]+dp[-2])
show_table(['阶数','空路径/两种末步求和'],list(enumerate(dp)))''',
'''assert [climb_stairs_table(n) for n in [1,2,5]]==[1,2,8]
for n in range(18): assert climb_stairs_recursive(n)==climb_stairs_memo(n)==climb_stairs_table(n)
assert climb_stairs_table(0)==1
assert climb_stairs_memo(12)==233 and climb_stairs_memo(3)==3''',
'按最后一步分成两个互斥且完备的集合，相加不重不漏。以n归纳，两种更小状态正确即推出当前状态正确。缓存位于函数内部，每次输入独立，不污染其他问题。',
'直接递归O(2^n)上界、O(n)栈；记忆化与表格O(n)算术操作、O(n)空间。答案整数位数随n增长；极深输入用表格而非提高递归上限。')

add(99,'打家劫舍的状态可压缩为两个前缀最优值：不选末屋沿用前一项，选末屋则只能接前两项。环形问题把首尾冲突拆成“不含首屋”与“不含末屋”。最大子数组不同：必须保留“以当前位置结尾”的非空状态，不能将全负输入错误地返回0。',
'''def rob(nums):
    before=prev=0
    for x in nums: before,prev=prev,max(prev,before+x)
    return prev

def rob_circular(nums):
    if len(nums)<=1: return max([0]+list(nums))
    return max(rob(nums[:-1]),rob(nums[1:]))

def max_subarray(nums):
    if not nums: raise ValueError('nonempty array required')
    ending=best=nums[0]
    for x in nums[1:]: ending=max(x,ending+x); best=max(best,ending)
    return best
''',
'''a=[-2,1,-3,4,-1,2,1,-5,4]; ending=best=a[0]; rows=[(0,a[0],ending,best)]
for i,x in enumerate(a[1:],1): ending=max(x,ending+x); best=max(best,ending); rows.append((i,x,ending,best))
show_table(['位置','值','以此结尾','全局最优'],rows)''',
'''assert rob([2,7,9,3,1])==12 and rob_circular([2,3,2])==3
assert max_subarray([-3,-1,-2])==-1
from itertools import product
for n in range(1,7):
    for a in product((-2,0,3),repeat=n):
        linear=[]; circular=[]
        for mask in range(1<<n):
            if mask&(mask<<1): continue
            value=sum(a[i] for i in range(n) if mask>>i&1); linear.append(value)
            if n==1 or not (mask&1 and mask>>(n-1)&1): circular.append(value)
        assert rob(a)==max(linear) and rob_circular(a)==max(circular)
        assert max_subarray(a)==max(sum(a[l:r]) for l in range(n) for r in range(l+1,n+1))''',
'所有合法独立集按是否选择末项划分，取两者最大。环上合法集必不同时包含首尾，两个线性子问题覆盖全部可能。非空连续区间若以i结尾，要么从i开始，要么接在以i−1结尾的最优区间后。',
'O(n)时间、线性rob与最大子数组O(1)辅助；环形实现切片O(n)辅助，可改索引范围消除。rob允许不选任何项；max_subarray必须非空。')

add(100,'网格DP的重点是依赖方向。向右向下走使网格成为DAG，路径数相加、最小成本取min。地牢需要反向思考：dp[r][c]不是累计血量，而是进入该格前保证生存所需的最小血量；离开所需减去本格收益后，至少还要1。',
'''def unique_paths(m,n):
    if m<=0 or n<=0: return 0
    dp=[1]*n
    for _ in range(1,m):
        for c in range(1,n): dp[c]+=dp[c-1]
    return dp[-1]

def unique_paths_with_obstacles(grid):
    if not grid or not grid[0]: return 0
    dp=[0]*len(grid[0]); dp[0]=1
    for row in grid:
        for c,x in enumerate(row):
            if x: dp[c]=0
            elif c: dp[c]+=dp[c-1]
    return dp[-1]

def min_path_sum(grid):
    if not grid or not grid[0]: return 0
    dp=[float('inf')]*len(grid[0]); dp[0]=0
    for row in grid:
        for c,x in enumerate(row): dp[c]=min(dp[c],dp[c-1] if c else float('inf'))+x
    return dp[-1]

def calculate_minimum_hp(dungeon):
    if not dungeon or not dungeon[0]: return 1
    m,n=len(dungeon),len(dungeon[0]); dp=[float('inf')]*(n+1); dp[n-1]=1
    for r in range(m-1,-1,-1):
        for c in range(n-1,-1,-1): dp[c]=max(1,min(dp[c],dp[c+1])-dungeon[r][c])
    return dp[0]
''',
'''grid=[[-2,-3,3],[-5,-10,1],[10,30,-5]]; dp=[[0]*3 for _ in range(3)]
for r in range(2,-1,-1):
    for c in range(2,-1,-1):
        after=1 if (r,c)==(2,2) else min([dp[nr][nc] for nr,nc in [(r+1,c),(r,c+1)] if nr<3 and nc<3])
        dp[r][c]=max(1,after-grid[r][c])
show_table(['行','进入各格最少血量'],list(enumerate(dp)))''',
'''assert unique_paths(3,7)==28
assert unique_paths_with_obstacles([[1]])==0
assert unique_paths_with_obstacles([[0,0],[0,1]])==0
assert calculate_minimum_hp([[-5]])==6
assert calculate_minimum_hp([[-2,-3,3],[-5,-10,1],[10,30,-5]])==7
from itertools import product

def paths(g,r=0,c=0):
    if r==len(g)-1 and c==len(g[0])-1: return [[g[r][c]]]
    return [[g[r][c]]+tail for nr,nc in [(r+1,c),(r,c+1)] if nr<len(g) and nc<len(g[0]) for tail in paths(g,nr,nc)]
for a in product((-2,1,3),repeat=6):
    g=[a[:3],a[3:]]; p=paths(g)
    assert min_path_sum(g)==min(map(sum,p))
    need=min(max(1,1-min(sum(x[:k]) for k in range(1,len(x)+1))) for x in p)
    assert calculate_minimum_hp(g)==need''',
'每条路径的最后或下一步只有两个互斥方向，DAG顺序确保依赖已计算。地牢从终点向前归纳：进入血量h满足h≥1且h+格值≥下一格所需，故h=max(1,next−格值)。',
'O(mn)算术操作、O(n)辅助空间。矩形输入；教学扩展的空网格结果已显式定义。路径计数是任意精度整数，不隐式取模。')

add(101,'0/1背包的第i层只允许前i件物品。压成一维时必须逆序容量：读取dp[c−w]时它仍来自上一层，因此同一物品不会重复使用。符号和计数还必须区分“最优值”与“方案数”；值为0的元素依然有正负两种选择。',
'''from collections import Counter

def knapsack_01(weights,values,capacity):
    if len(weights)!=len(values) or capacity<0 or any(w<0 for w in weights): raise ValueError('invalid knapsack')
    dp=[0]*(capacity+1)
    for w,v in zip(weights,values):
        for c in range(capacity,w-1,-1): dp[c]=max(dp[c],dp[c-w]+v)
    return dp[-1]

def can_partition(nums):
    total=sum(nums)
    if any(x<0 for x in nums): raise ValueError('nonnegative values required')
    if total%2: return False
    reachable=1
    for x in nums: reachable|=reachable<<x
    return bool(reachable>>(total//2)&1)

def find_target_sum_ways(nums,target):
    states=Counter({0:1})
    for x in nums:
        nxt=Counter()
        for value,count in states.items(): nxt[value+x]+=count; nxt[value-x]+=count
        states=nxt
    return states[target]
''',
'''weights=[2,3,4]; values=[4,5,7]; cap=6; dp=[0]*(cap+1); rows=[('无物品',dp[:])]
for w,v in zip(weights,values):
    for c in range(cap,w-1,-1): dp[c]=max(dp[c],dp[c-w]+v)
    rows.append((f'w={w},v={v}',dp[:]))
show_table(['已处理物品','各容量最优值'],rows)''',
'''assert can_partition([1,5,11,5])
assert knapsack_01([2],[3],4)==3
assert find_target_sum_ways([0,0],0)==4
from itertools import product
from random import Random
rng=Random(101)
for _ in range(140):
    n=rng.randrange(7); w=[rng.randrange(5) for _ in range(n)]; v=[rng.randrange(-2,9) for _ in range(n)]; cap=rng.randrange(9)
    want=max(sum(v[i] for i in range(n) if mask>>i&1) for mask in range(1<<n) if sum(w[i] for i in range(n) if mask>>i&1)<=cap)
    assert knapsack_01(w,v,cap)==want
    assert can_partition(w)==any(2*sum(w[i] for i in range(n) if mask>>i&1)==sum(w) for mask in range(1<<n))
for a in product(range(3),repeat=5):
    for target in range(-2,3):
        assert find_target_sum_ways(a,target)==sum(sum(s*x for s,x in zip(signs,a))==target for signs in product((-1,1),repeat=5))''',
'背包按“取第i件”与“不取”划分；逆序保证转移读取旧层。位集的第s位代表和s可达，左移x对应加入物品x；或操作合并两种可能。计数Counter每一步创建新层，零值对应两条不同决策边，所以自然翻倍。',
'背包O(nC)时间O(C)空间；位集在总和S位上做n次移位/或，位复杂度O(nS)上界、O(S)位空间；符号计数至多O(nS)状态处理，S=各数绝对值之和。这些是伪多项式代价，不是对输入比特长度的多项式。')

add(102,'完全背包允许重复选一件，所以同一层容量要正序。计数时循环顺序决定语义：先枚举物品再金额得到无序组合；先金额再末项得到有序序列。有限次数背包可以把数量拆为1、2、4…和余数的小包，再当0/1物品处理。分组背包必须读取上一组，不能在本组内部重复选。',
'''def _positive_unique(values):
    if any(x<=0 for x in values): raise ValueError('strictly positive values required')
    return sorted(set(values))

def coin_change(coins,amount):
    coins=_positive_unique(coins); dp=[0]+[float('inf')]*amount
    for a in range(1,amount+1):
        for c in coins:
            if c<=a: dp[a]=min(dp[a],dp[a-c]+1)
    return -1 if dp[amount]==float('inf') else dp[amount]

def coin_change_combinations(coins,amount):
    dp=[1]+[0]*amount
    for c in _positive_unique(coins):
        for a in range(c,amount+1): dp[a]+=dp[a-c]
    return dp[amount]

def ordered_sum_count(nums,target):
    nums=_positive_unique(nums); dp=[1]+[0]*target
    for a in range(1,target+1):
        dp[a]=sum(dp[a-x] for x in nums if x<=a)
    return dp[target]

def bounded_knapsack(items,capacity):
    # items: (positive weight, value, nonnegative count)
    dp=[0]*(capacity+1)
    for weight,value,count in items:
        if weight<=0 or count<0: raise ValueError('invalid bounded item')
        bundle=1
        while count:
            take=min(bundle,count); w=weight*take; v=value*take
            for c in range(capacity,w-1,-1): dp[c]=max(dp[c],dp[c-w]+v)
            count-=take; bundle*=2
    return dp[-1]

def group_knapsack(groups,capacity):
    dp=[0]*(capacity+1)
    for group in groups:
        prev=dp; dp=prev[:]
        for w,v in group:
            for c in range(w,capacity+1): dp[c]=max(dp[c],prev[c-w]+v)
    return dp[-1]
''',
'''show_table(['目标','[1,2]组合数','[1,2]有序序列数'],[(a,coin_change_combinations([1,2],a),ordered_sum_count([1,2],a)) for a in range(7)])''',
'''assert coin_change_combinations([1,2,5],5)==4
assert ordered_sum_count([1,2],3)==3 and coin_change_combinations([1,2],3)==2
assert coin_change([2],3)==-1 and coin_change([],0)==0
assert group_knapsack([[(1,5),(1,6)]],2)==6
from itertools import product
from random import Random
rng=Random(102)
for _ in range(150):
    items=[(rng.randrange(1,5),rng.randrange(1,8),rng.randrange(5)) for _ in range(3)]; cap=rng.randrange(12)
    feasible=[sum(t*v for t,(w,v,q) in zip(counts,items)) for counts in product(*(range(q+1) for w,v,q in items)) if sum(t*w for t,(w,v,q) in zip(counts,items))<=cap]
    assert bounded_knapsack(items,cap)==max(feasible)
for a in range(12):
    assert coin_change_combinations([1,2,5],a)==sum(x+2*y+5*z==a for x in range(a+1) for y in range(a+1) for z in range(a+1))''',
'无序组合按最后一种可使用的币值分组，不会把同一组硬币的排列重复计数；有序序列按最后一个数划分。二进制数量包的子集能表达0..原数量的每个取用量；有重复表达也不影响取最大值，但不能直接用于方案数计数。',
'完全背包O(nA)时间O(A)空间；有限次数O(C∑log(q+1))时间O(C)空间；分组O(C∑组内物品数)。amount/target/capacity非负，正值条件防止无限方案与循环依赖。')

add(103,'LIS平方DP保存“以i结尾”的最长长度。耐心排序保存另一种信息：每个长度可达到的最小末值。更小末值不会削弱未来延伸能力，所以可二分更新。tails数组本身不一定是原数组子序列；要恢复答案，必须保存前驱与每个长度的末项位置。信封宽度相等时高度降序，避免被错误同时选中。',
'''from bisect import bisect_left

def lis_quadratic(nums):
    dp=[1]*len(nums)
    for i,x in enumerate(nums):
        dp[i]=1+max((dp[j] for j in range(i) if nums[j]<x),default=0)
    return max(dp,default=0)

def lis_length(nums):
    tails=[]
    for x in nums:
        p=bisect_left(tails,x)
        if p==len(tails): tails.append(x)
        else: tails[p]=x
    return len(tails)

def reconstruct_lis(nums):
    tails=[]; indices=[]; parent=[-1]*len(nums)
    for i,x in enumerate(nums):
        p=bisect_left(tails,x)
        if p: parent[i]=indices[p-1]
        if p==len(tails): tails.append(x); indices.append(i)
        else: tails[p]=x; indices[p]=i
    out=[]; i=indices[-1] if indices else -1
    while i!=-1: out.append(nums[i]); i=parent[i]
    return out[::-1]

def max_envelopes(envelopes):
    return lis_length([h for w,h in sorted(envelopes,key=lambda x:(x[0],-x[1]))])
''',
'''a=[10,9,2,5,3,7,101,18]; tails=[]; rows=[]
for x in a:
    p=bisect_left(tails,x)
    if p==len(tails): tails.append(x)
    else: tails[p]=x
    rows.append((x,p,tails[:]))
show_table(['读入','替换长度下标','最小末值表'],rows)
print('真实恢复序列',reconstruct_lis(a))''',
'''assert lis_length([10,9,2,5,3,7,101,18])==4
assert lis_length([2,2,2])==1
assert max_envelopes([[5,4],[6,4],[6,7],[2,3]])==3
assert max_envelopes([[1,1],[1,2],[1,3]])==1
from itertools import product
for n in range(7):
    for a in product(range(3),repeat=n):
        b=reconstruct_lis(a)
        assert len(b)==lis_length(a)==lis_quadratic(a)
        assert all(x<y for x,y in zip(b,b[1:]))
        it=iter(a); assert all(any(x==y for y in it) for x in b)''',
'长度相同的递增序列，末值较小者支配较大者。lower_bound找到第一个不小于x的位置，保持严格递增含义；前驱在处理i前记录，保证索引和数值同时递增。相同宽度高度降序后，严格高度LIS不可能选择同宽的两项。',
'平方版O(n²)时间O(n)空间；二分版O(n log n)时间O(n)空间；恢复额外O(n)前驱。严格递增与非递减的区别是lower_bound/upper_bound，不能随意互换。')
