from course_builder import add

add(114,'概率DP传播的是概率质量，离开棋盘的质量不能重新归一化。期望则满足首步方程E[i]=1+∑p(i,j)E[j]，有自循环时不能把它当作DAG直接递归。有限小链可以解线性方程；若有正概率进入永不吸收的闭类，吸收时间期望为无穷大。',
'''from fractions import Fraction
from collections import deque

def knight_probability(n,k,row,col):
    if n<=0 or not (0<=row<n and 0<=col<n): return 0.0
    dp=[[0.0]*n for _ in range(n)]; dp[row][col]=1.0
    moves=[(1,2),(1,-2),(-1,2),(-1,-2),(2,1),(2,-1),(-2,1),(-2,-1)]
    for _ in range(k):
        nxt=[[0.0]*n for _ in range(n)]
        for r in range(n):
            for c in range(n):
                for dr,dc in moves:
                    x,y=r+dr,c+dc
                    if 0<=x<n and 0<=y<n: nxt[x][y]+=dp[r][c]/8
        dp=nxt
    return sum(map(sum,dp))

def new21_game(n,k,max_pts):
    if max_pts<=0 or min(n,k)<0: raise ValueError('invalid game parameters')
    if k==0 or n>=k-1+max_pts: return 1.0
    dp=[0.0]*(n+1); dp[0]=1.0; window=1.0; answer=0.0
    for score in range(1,n+1):
        dp[score]=window/max_pts
        if score<k: window+=dp[score]
        else: answer+=dp[score]
        old=score-max_pts
        if 0<=old<k: window-=dp[old]
    return answer

def expected_steps_small_chain(transitions):
    # Row i contains (next_state, probability); [] is absorbing.
    rows=[[(j,p if isinstance(p,Fraction) else Fraction(str(p))) for j,p in row] for row in transitions]
    n=len(rows); reverse=[[] for _ in rows]
    for i,row in enumerate(rows):
        if row and sum(p for j,p in row)!=1: raise ValueError('nonempty rows must sum exactly to one')
        for j,p in row:
            if not 0<=j<n or p<0: raise ValueError('invalid transition')
            if p>0: reverse[j].append(i)
    def ancestors(seeds):
        seen=set(seeds); q=deque(seen)
        while q:
            for u in reverse[q.popleft()]:
                if u not in seen: seen.add(u); q.append(u)
        return seen
    absorbing={i for i,row in enumerate(rows) if not row}
    can_absorb=ancestors(absorbing)
    infinite=ancestors(set(range(n))-can_absorb)
    finite=[i for i in range(n) if i not in absorbing and i not in infinite]; index={v:i for i,v in enumerate(finite)}
    m=len(finite); a=[[Fraction(0) for _ in range(m+1)] for _ in range(m)]
    for r,u in enumerate(finite):
        a[r][r]=1; a[r][-1]=1
        for v,p in rows[u]:
            if v in index: a[r][index[v]]-=p
    for c in range(m):
        pivot=next(r for r in range(c,m) if a[r][c])
        a[c],a[pivot]=a[pivot],a[c]; divisor=a[c][c]; a[c]=[x/divisor for x in a[c]]
        for r in range(m):
            if r!=c:
                factor=a[r][c]; a[r]=[x-factor*y for x,y in zip(a[r],a[c])]
    answer=[float('inf') if i in infinite else 0.0 for i in range(n)]
    for u,r in index.items(): answer[u]=float(a[r][-1])
    return answer
''',
'''show_table(['步数','3×3角落骑士留在棋盘概率'],[(k,knight_probability(3,k,0,0)) for k in range(5)])
chain=[[(0,Fraction(1,2)),(1,Fraction(1,2))],[]]
show_table(['状态','转移','吸收前期望步数'],[(i,row,expected_steps_small_chain(chain)[i]) for i,row in enumerate(chain)])''',
'''from math import isclose,isinf
from functools import cache
assert knight_probability(3,2,0,0)==0.0625
assert knight_probability(3,0,0,0)==1.0
assert expected_steps_small_chain([[(0,Fraction(1,2)),(1,Fraction(1,2))],[]])==[2.0,0.0]
assert expected_steps_small_chain([[(1,1)],[(2,1)],[]])==[2.0,1.0,0.0]
a=expected_steps_small_chain([[(1,0.5),(2,0.5)],[],[(2,1)]])
assert isinf(a[0]) and a[1]==0 and isinf(a[2])
for k in range(7):
    for pts in range(1,6):
        for n in range(12):
            @cache
            def exact(score):
                if score>=k: return Fraction(score<=n)
                return sum((exact(score+x) for x in range(1,pts+1)),Fraction(0))/pts
            got=new21_game(n,k,pts)
            assert -1e-12<=got<=1+1e-12 and isclose(got,float(exact(0)),abs_tol=1e-12)
for k in range(5): assert 0<=knight_probability(4,k,1,1)<=1''',
'全概率公式按上一步状态分解；棋盘外是失败吸收状态，遗漏的质量正是失败概率。New21只把仍需抽牌的分数放进窗口。有限链先排除可到达非吸收闭类的状态，剩余瞬态子矩阵满足(I−Q)可逆，首步方程有唯一有限解；代码用精确有理数消元后转浮点输出。',
'骑士O(kn²)时间O(n²)空间；New21 O(n)时间空间；小链图检查O(V+E)，高斯消元O(V³)有理数操作O(V²)空间，位复杂度另计。[]表示吸收；非空行概率要求精确和为1，可传Fraction。')

add(115,'零和博弈DP要把双方目标放在同一个状态中。保存“当前行动者最多领先对手多少分”，取走一段收益后减去对手能取得的得分差，就自动实现max/min交替。Stone Game II还要保留会改变未来选择范围的M，不能只记录剩余位置。',
'''from functools import cache

def predict_the_winner(nums):
    if not nums: return True
    dp=list(nums)
    for length in range(2,len(nums)+1):
        for l in range(len(nums)-length+1):
            r=l+length-1; dp[l]=max(nums[l]-dp[l+1],nums[r]-dp[l])
    return dp[0]>=0

def stone_game_ii(piles):
    n=len(piles); suffix=[0]*(n+1)
    for i in range(n-1,-1,-1): suffix[i]=suffix[i+1]+piles[i]
    @cache
    def f(i,m):
        if i==n: return 0
        if i+2*m>=n: return suffix[i]
        return max(suffix[i]-f(i+x,max(m,x)) for x in range(1,2*m+1))
    return f(0,1)

def stone_game_iii(stone_value):
    n=len(stone_value); dp=[0]*(n+1)
    for i in range(n-1,-1,-1):
        taken=0; dp[i]=float('-inf')
        for j in range(i,min(n,i+3)):
            taken+=stone_value[j]; dp[i]=max(dp[i],taken-dp[j+1])
    return 'Alice' if dp[0]>0 else 'Bob' if dp[0]<0 else 'Tie'
''',
'''a=[1,2,3,7]; dp=[0]*(len(a)+1); rows=[]
for i in range(len(a)-1,-1,-1):
    options=[sum(a[i:i+k])-dp[i+k] for k in range(1,min(3,len(a)-i)+1)]; dp[i]=max(options); rows.append((i,options,dp[i]))
show_table(['位置','取1..3项得分差','最优差'],rows)''',
'''assert not predict_the_winner([1,5,2]) and predict_the_winner([1,5,233,7])
assert stone_game_ii([2,7,9,4,4])==10
assert stone_game_iii([1,2,3,7])=='Bob' and stone_game_iii([1,2,3,6])=='Tie'
from itertools import product
@cache
def ends(a):
    if not a: return 0
    return max(a[0]-ends(a[1:]),a[-1]-ends(a[:-1]))
@cache
def front(a):
    if not a: return 0
    return max(sum(a[:k])-front(a[k:]) for k in range(1,min(3,len(a))+1))
for a in product((-2,0,3),repeat=6):
    assert predict_the_winner(a)==(ends(a)>=0)
    d=front(a); assert stone_game_iii(a)==('Alice' if d>0 else 'Bob' if d<0 else 'Tie')
@cache
def ii_ref(a,m):
    if not a: return 0
    return max(sum(a[:k])+(sum(a[k:])-ii_ref(a[k:],max(m,k))) for k in range(1,min(len(a),2*m)+1))
for a in product((1,2),repeat=6): assert stone_game_ii(a)==ii_ref(a,1)''',
'每个子问题重置为轮到当前行动者，所以下一状态的优势属于对手，需要减去。边界为空时差为0。Stone Game II用剩余总和减去对手最多所得等价于自身最多所得，且所有石子非负时可全取就最优。',
'两端博弈O(n²)时间O(n)空间；Stone III O(n)时间空间；Stone II保守O(n³)时间O(n²)缓存，递归深度O(n)。II要求非负石堆；III允许负数；平局按接口分别返回True或Tie。')

add(116,'窄网格的指数因素应放在宽度，而非整个面积。把一行选座状态压成mask，预先排除横向相邻；相邻行只检查左上与右上冲突。三色网格用三进制行状态，先排除行内同色相邻，再检查相邻列的逐位不同。',
'''from itertools import product
MOD=10**9+7

def max_students_profile(seats):
    if not seats: return 0
    width=len(seats[0]); dp={0:0}
    for row in seats:
        allowed=sum(1<<i for i,x in enumerate(row) if x=='.')
        states=[mask for mask in range(1<<width) if mask&allowed==mask and not mask&(mask<<1)]
        nxt={}
        for mask in states:
            nxt[mask]=mask.bit_count()+max(v for prev,v in dp.items() if not mask&(prev<<1) and not mask&(prev>>1))
        dp=nxt
    return max(dp.values())

def color_the_grid(m,n):
    if min(m,n)<0: raise ValueError('nonnegative dimensions required')
    if not m or not n: return 1
    states=[p for p in product(range(3),repeat=m) if all(a!=b for a,b in zip(p,p[1:]))]
    compatible=[[j for j,b in enumerate(states) if all(x!=y for x,y in zip(a,b))] for a in states]
    dp=[1]*len(states)
    for _ in range(1,n): dp=[sum(dp[j] for j in neighbors)%MOD for neighbors in compatible]
    return sum(dp)%MOD

def num_of_ways_n3(n):
    if n==0: return 1
    aba=abc=6
    for _ in range(1,n): aba,abc=(3*aba+2*abc)%MOD,(2*aba+2*abc)%MOD
    return (aba+abc)%MOD
''',
'''seats=['.#.','...']; width=3; rows=[]
for r,row in enumerate(seats):
    allowed=sum(1<<i for i,c in enumerate(row) if c=='.')
    for mask in range(1<<width):
        if mask&allowed==mask and not mask&(mask<<1): rows.append((r,format(mask,'03b'),mask.bit_count()))
show_table(['行','合法座位掩码','人数'],rows)
print('全局最多人数',max_students_profile(seats))''',
'''assert color_the_grid(1,1)==3 and num_of_ways_n3(1)==12
assert max_students_profile(['...'])==2
for n in range(1,9): assert num_of_ways_n3(n)==color_the_grid(3,n)
for broken in range(1<<6):
    seats=[''.join('#' if broken>>(r*3+c)&1 else '.' for c in range(3)) for r in range(2)]
    valid=[]
    for mask in range(1<<6):
        if mask&broken: continue
        cells=[(i//3,i%3) for i in range(6) if mask>>i&1]
        if all(not(abs(c-d)==1 and abs(r-s)<=1) for i,(r,c) in enumerate(cells) for s,d in cells[i+1:]): valid.append(mask.bit_count())
    assert max_students_profile(seats)==max(valid)
for m,n in [(1,3),(2,2),(2,3)]:
    count=0
    for colors in product(range(3),repeat=m*n):
        if all(colors[r*n+c]!=colors[(r+1)*n+c] for r in range(m-1) for c in range(n)) and all(colors[r*n+c]!=colors[r*n+c+1] for r in range(m) for c in range(n-1)): count+=1
    assert color_the_grid(m,n)==count''',
'给定上一行状态，未来只受该行边界影响，更早行可被遗忘。合法状态完整枚举了行内选择，兼容关系精确表达跨行约束。宽度3的三色状态按ABA与ABC两类聚合，颜色重命名对称性保证同类转移数相同，得到常数状态递推。',
'选座保守O(R·4^W)时间、O(2^W)状态空间；三色状态数S=3·2^(m−1)，预计算兼容O(mS²)，后续O(nS²)时间和O(S²)空间；宽3聚合版O(n)时间O(1)空间。指数宽度必须小。')

add(117,'DP优化先写明候选集合，再寻找支配关系。窗口最大转移用单调队列丢弃“更旧且值不更大”的状态，因为它们更早过期且收益不占优。约束子序列允许重新开始，跳跃游戏必须从位置0到末尾，转移中不能随意加入0。逆序对计数的转移是连续区间求和，可用滑动和。',
'''from collections import deque
MOD=10**9+7

def constrained_subset_sum(nums,k):
    if not nums or k<1: raise ValueError('nonempty nums and positive k required')
    q=deque(); best=float('-inf')
    for i,x in enumerate(nums):
        while q and q[0][0]<i-k: q.popleft()
        value=x+max(0,q[0][1] if q else 0); best=max(best,value)
        while q and q[-1][1]<=value: q.pop()
        q.append((i,value))
    return best

def max_result(nums,k):
    if not nums or k<1: raise ValueError('nonempty nums and positive k required')
    q=deque([(0,nums[0])]); value=nums[0]
    for i in range(1,len(nums)):
        while q[0][0]<i-k: q.popleft()
        value=nums[i]+q[0][1]
        while q and q[-1][1]<=value: q.pop()
        q.append((i,value))
    return value

def k_inverse_pairs(n,k):
    if min(n,k)<0 or k>n*(n-1)//2: return 0
    dp=[1]+[0]*k
    for length in range(1,n+1):
        nxt=[0]*(k+1); window=0
        for inv in range(k+1):
            window+=dp[inv]
            if inv>=length: window-=dp[inv-length]
            nxt[inv]=window%MOD
        dp=nxt
    return dp[k]
''',
'''nums=[1,-1,-2,4,-7,3]; k=2; q=deque([(0,nums[0])]); rows=[(0,nums[0],list(q))]
for i in range(1,len(nums)):
    while q[0][0]<i-k: q.popleft()
    value=nums[i]+q[0][1]
    while q and q[-1][1]<=value: q.pop()
    q.append((i,value)); rows.append((i,value,list(q)))
show_table(['位置','最优到达分数','单调候选(位置,值)'],rows)''',
'''assert max_result([1,-1,-2,4,-7,3],2)==7
assert constrained_subset_sum([-3,-1,-2],2)==-1
from itertools import product,permutations
for a in product((-2,0,3),repeat=6):
    for k in (1,2,4):
        dp=[a[0]]; sub=[]
        for i,x in enumerate(a):
            if i: dp.append(x+max(dp[max(0,i-k):i]))
            sub.append(x+max([0]+sub[max(0,i-k):i]))
        assert max_result(a,k)==dp[-1]
        assert constrained_subset_sum(a,k)==max(sub)
for n in range(8):
    counts={}
    for p in permutations(range(n)):
        inv=sum(p[i]>p[j] for i in range(n) for j in range(i+1,n)); counts[inv]=counts.get(inv,0)+1
    for k in range(n*(n-1)//2+2): assert k_inverse_pairs(n,k)==counts.get(k,0)''',
'队列按下标递增、值严格递减；过期项从头删除，被新状态支配的项从尾删除，每项至多进出一次。将最大元素n插入n−1个数的排列中，会新增0..n−1个逆序对，因此dp[n][k]是旧行一段连续和，滑动更新保持这个区间不变量。',
'两个窗口DP O(n)时间O(min(n,k))辅助空间；逆序对O(nk)时间O(k)空间。计数模10^9+7。队列优化不自动保留最优路径；恢复路径需要另存前驱O(n)。')
