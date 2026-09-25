from course_builder import add

add(93,'区间调度的局部选择不是“最短区间”，而是“最早结束”。更早结束为后续保留不少于其他选择的空间。注意接口边界不同：不重叠区间允许端点接触；数对链要求前一终点严格小于后一开头。',
'''def erase_overlap_intervals(intervals):
    end=float('-inf'); kept=0
    for a,b in sorted(intervals,key=lambda x:x[1]):
        if a>=end: kept+=1; end=b
    return len(intervals)-kept

def find_longest_chain(pairs):
    end=float('-inf'); length=0
    for a,b in sorted(pairs,key=lambda x:x[1]):
        if a>end: length+=1; end=b
    return length
''',
'''intervals=[[1,2],[2,3],[3,4],[1,3]]; end=float('-inf'); trace=[]
for a,b in sorted(intervals,key=lambda x:x[1]):
    take=a>=end
    if take: end=b
    trace.append((a,b,take,end))
show_table(['起点','终点','保留','已选终点'],trace)''',
'''assert erase_overlap_intervals([[1,2],[2,3],[3,4],[1,3]])==1
assert find_longest_chain([[1,2],[2,3],[3,4]])==2
from itertools import combinations
from random import Random
rng=Random(93)
for _ in range(120):
    a=[sorted(rng.sample(range(8),2)) for _ in range(rng.randrange(8))]
    def opt(strict):
        best=0
        for k in range(len(a)+1):
            for group in combinations(a,k):
                seq=sorted(group)
                if all((seq[i][1]<seq[i+1][0] if strict else seq[i][1]<=seq[i+1][0]) for i in range(k-1)): best=max(best,k)
        return best
    assert erase_overlap_intervals(a)==len(a)-opt(False)
    assert find_longest_chain(a)==opt(True)''',
'令最优方案首区间为O，最早结束区间为G。用G替换O不会与后续区间冲突，因为G结束不晚于O。因此存在以G开始的最优方案，对剩余区间归纳即可。严格与非严格比较必须和题意一致。',
'O(n log n)时间、O(n)排序副本空间。输入每段满足start<end；不修改输入。')

add(94,'把位置视为图顶点，跳跃视为边，朴素BFS会枚举许多相同范围。每层可达位置形成前缀区间，只需保存当前层右边界和下一层能到达的最远位置。边界不再增长时，后面的位置永远不可达。',
'''def can_jump(nums):
    if not nums: return False
    far=0
    for i,x in enumerate(nums):
        if i>far: return False
        far=max(far,i+x)
        if far>=len(nums)-1: return True
    return False

def min_jumps(nums):
    if not nums: return -1
    end=far=jumps=0
    for i in range(len(nums)-1):
        if i>far: return -1
        far=max(far,i+nums[i])
        if i==end:
            if far==end: return -1
            jumps+=1; end=far
            if end>=len(nums)-1: return jumps
    return jumps
''',
'''a=[2,3,1,1,4]; far=0; rows=[]
for i,x in enumerate(a):
    old=far; far=max(far,i+x); rows.append((i,x,old,far))
show_table(['位置','跳长上界','旧前沿','新前沿'],rows)''',
'''assert can_jump([2,3,1,1,4]) and min_jumps([2,3,1,1,4])==2
assert not can_jump([3,2,1,0,4]) and min_jumps([3,2,1,0,4])==-1
assert min_jumps([0])==0
from itertools import product
from collections import deque
for n in range(1,7):
    for a in product(range(3),repeat=n):
        dist=[-1]*n; dist[0]=0; q=deque([0])
        while q:
            i=q.popleft()
            for j in range(i+1,min(n,i+a[i]+1)):
                if dist[j]==-1: dist[j]=dist[i]+1; q.append(j)
        assert min_jumps(a)==dist[-1]
        assert can_jump(a)==(dist[-1]!=-1)''',
'层内所有顶点的出边并集决定下一层边界。扫描到当前层末端后才增加跳数，完全对应BFS层数，因此是最少跳数，而不是贪心地立即跳到最远位置。',
'O(n)时间、O(1)辅助空间。跳长必须为非负整数。不可达扩展契约：min_jumps返回−1；空输入can_jump返回False。')

add(95,'加油站问题考察连续收支：从候选起点到i累计为负，则这段中任何后续位置都不能作为起点挽救这段失败。糖果问题则有来自左右的两组不等式；分别求满足一侧约束的最小量，再逐点取最大，不能只单向扫描。',
'''def can_complete_circuit(gas,cost):
    if len(gas)!=len(cost) or not gas: return -1
    total=tank=start=0
    for i,(g,c) in enumerate(zip(gas,cost)):
        total+=g-c; tank+=g-c
        if tank<0: start=i+1; tank=0
    return start if total>=0 else -1

def candy(ratings):
    n=len(ratings); left=[1]*n; right=1; total=0
    for i in range(1,n):
        if ratings[i]>ratings[i-1]: left[i]=left[i-1]+1
    for i in range(n-1,-1,-1):
        right=right+1 if i<n-1 and ratings[i]>ratings[i+1] else 1
        total+=max(left[i],right)
    return total
''',
'''ratings=[1,3,4,5,2]; left=[1]*len(ratings); right=[1]*len(ratings)
for i in range(1,len(ratings)):
    if ratings[i]>ratings[i-1]: left[i]=left[i-1]+1
for i in range(len(ratings)-2,-1,-1):
    if ratings[i]>ratings[i+1]: right[i]=right[i+1]+1
show_table(['评分','左约束','右约束','分配'],[(r,a,b,max(a,b)) for r,a,b in zip(ratings,left,right)])''',
'''assert can_complete_circuit([1,2,3,4,5],[3,4,5,1,2])==3
assert can_complete_circuit([1],[2])==-1
assert candy([1,0,2])==5
from itertools import product
for ratings in product(range(3),repeat=4):
    feasible=[]
    for values in product(range(1,5),repeat=4):
        if all(ratings[i]==ratings[i+1] or (values[i]>values[i+1] if ratings[i]>ratings[i+1] else values[i]<values[i+1]) for i in range(3)): feasible.append(sum(values))
    assert candy(ratings)==min(feasible)
for differences in product(range(-2,3),repeat=4):
    gas=[max(x,0) for x in differences]; cost=[max(-x,0) for x in differences]
    starts=[s for s in range(4) if all(sum(differences[(s+j)%4] for j in range(k+1))>=0 for k in range(4))]
    got=can_complete_circuit(gas,cost)
    assert (got in starts) if starts else got==-1''',
'加油站扫描不变量：当前候选以前的起点已被一个负和区间排除；总和非负时，最后剩余候选可完成一圈。糖果左右数组分别是必要下界，其逐点最大同时满足两侧不等式，故不仅可行，而且逐点最小。',
'均O(n)时间；加油站O(1)辅助，糖果O(n)辅助。相邻同分不要求相同糖果；空评分总量0。')

add(96,'堆贪心的作用是允许撤销先前决定。按截止时间处理课程，超时就删除已选课程中最长的一门：数量相同而总时长更小，留给以后更多空间。IPO则不同：已满足资本门槛的项目中选利润最大者，但这里利润是净增加，不扣除门槛资本。',
'''from heapq import heappush,heappop

def schedule_course(courses):
    total=0; chosen=[]
    for duration,deadline in sorted(courses,key=lambda c:c[1]):
        heappush(chosen,-duration); total+=duration
        if total>deadline: total+=heappop(chosen)
    return len(chosen)

def find_maximized_capital(k,w,profits,capital):
    projects=sorted(zip(capital,profits)); i=0; available=[]
    for _ in range(k):
        while i<len(projects) and projects[i][0]<=w:
            heappush(available,-projects[i][1]); i+=1
        if not available or available[0]>=0: break
        w-=heappop(available)
    return w
''',
'''courses=[[100,200],[200,1300],[1000,1250],[2000,3200]]; heap=[]; total=0; rows=[]
for duration,deadline in sorted(courses,key=lambda x:x[1]):
    heappush(heap,-duration); total+=duration; removed=None
    if total>deadline: removed=-heappop(heap); total-=removed
    rows.append((duration,deadline,removed,total,len(heap)))
show_table(['时长','截止','撤销','累计时长','课程数'],rows)''',
'''assert schedule_course([[100,200],[200,1300],[1000,1250],[2000,3200]])==3
assert schedule_course([[5,4]])==0
assert find_maximized_capital(2,0,[1,2,3],[0,1,1])==4
assert find_maximized_capital(3,0,[5],[1])==0
from itertools import combinations
from random import Random
rng=Random(96)
for _ in range(100):
    a=[(rng.randrange(1,7),rng.randrange(1,15)) for _ in range(rng.randrange(8))]; best=0
    for k in range(len(a)+1):
        for group in combinations(a,k):
            total=0; valid=True
            for t,d in sorted(group,key=lambda x:x[1]):
                total+=t
                if total>d: valid=False
            if valid: best=max(best,k)
    assert schedule_course(a)==best

def brute(k,w,p,c,used=0):
    if not k: return w
    return max([w]+[brute(k-1,w+p[i],p,c,used|1<<i) for i in range(len(p)) if not used>>i&1 and c[i]<=w])
for _ in range(60):
    p=[rng.randrange(6) for _ in range(5)]; c=[rng.randrange(8) for _ in range(5)]
    assert find_maximized_capital(3,1,p,c)==brute(3,1,p,c)''',
'课程按截止期交换排序不损害可行性。加入新课程若超时，必须至少放弃一门，删除最长者在保持最多数量的候选中使占用时间最小。IPO利润非负时，先选更大利润不会减少后续可选项目集合，可将最优顺序首项替换为当前最大收益项目。',
'O(n log n+k log n)时间上界，O(n)辅助空间。IPO假定最多选k项、每项只能一次、capital是启动门槛；负收益并非本章标准题域，实现会提前停在非正最大收益处。')

add(97,'字典序目标依赖最早出现差异的位置。删除k位时，当前更小字符可以替换左侧较大字符，但必须仍有删除预算。去重字母还要保证被弹出的字母以后再次出现。重排字符串不是字典序最小问题：用最大频次堆并暂存上次字符，禁止立即重复。',
'''from collections import Counter
from heapq import heapify,heappush,heappop

def remove_k_digits(num,k):
    stack=[]
    for c in num:
        while k and stack and stack[-1]>c: stack.pop(); k-=1
        stack.append(c)
    if k: del stack[-k:]
    return ''.join(stack).lstrip('0') or '0'

def remove_duplicate_letters(s):
    last={c:i for i,c in enumerate(s)}; used=set(); stack=[]
    for i,c in enumerate(s):
        if c in used: continue
        while stack and stack[-1]>c and last[stack[-1]]>i: used.remove(stack.pop())
        stack.append(c); used.add(c)
    return ''.join(stack)

def reorganize_string(s):
    counts=Counter(s)
    if max(counts.values(),default=0)>(len(s)+1)//2: return ''
    heap=[(-n,c) for c,n in counts.items()]; heapify(heap); pending=(0,''); out=[]
    while heap:
        neg,c=heappop(heap); out.append(c)
        if pending[0]<0: heappush(heap,pending)
        pending=(neg+1,c)
    return ''.join(out) if pending[0]==0 else ''
''',
'''s='cbacdcbc'; last={c:i for i,c in enumerate(s)}; stack=[]; used=set(); rows=[]
for i,c in enumerate(s):
    if c not in used:
        while stack and stack[-1]>c and last[stack[-1]]>i: used.remove(stack.pop())
        stack.append(c); used.add(c)
    rows.append((i,c,''.join(stack)))
show_table(['位置','读入','栈'],rows)''',
'''assert remove_k_digits('1432219',3)=='1219'
assert remove_k_digits('10200',1)=='200'
assert remove_duplicate_letters('cbacdcbc')=='acdb'
from itertools import product,combinations
for n in range(1,7):
    for chars in product('ab',repeat=n):
        s=''.join(chars); answer=reorganize_string(s)
        feasible=max(Counter(s).values())<=(n+1)//2
        assert bool(answer)==feasible
        if feasible: assert Counter(answer)==Counter(s) and all(a!=b for a,b in zip(answer,answer[1:]))
for chars in product('abc',repeat=5):
    s=''.join(chars); k=len(set(s)); options=[''.join(s[i] for i in ids) for ids in combinations(range(5),k) if len({s[i] for i in ids})==k]
    assert remove_duplicate_letters(s)==min(options)
for chars in product('012',repeat=4):
    s=''.join(chars)
    for k in range(5):
        choices=[int(''.join(s[i] for i in ids) or '0') for ids in combinations(range(4),4-k)]
        assert int(remove_k_digits(s,k))==min(choices)''',
'单调栈删除发生在能改善最早差异的位置，未用完预算时应删末尾。去重栈的弹出必须有未来副本，才能维持覆盖所有字母的可行性。重排的必要条件是最大频数不超过其余字符数加1；优先安排最多的可选字符并隔离上一字符，可维持该可行性条件。',
'删除数字与去重字母O(n)时间、O(n)空间；重排O(n log σ)时间、O(σ+n)空间，σ为不同字符数。无可行重排返回空串；空输入也返回空串。')
