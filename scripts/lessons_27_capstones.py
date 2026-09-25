"""Combinations, adversarial boundaries, iterative state search and held-out exercises."""
from course_builder import add

SCHEDULING = '''from collections import Counter, deque
import heapq

def least_interval(tasks,n):
    if n<0:raise ValueError('Cooldown must be nonnegative')
    counts=Counter(tasks)
    if not counts:return 0
    maximum=max(counts.values())
    tied=sum(value==maximum for value in counts.values())
    return max(len(tasks),(maximum-1)*(n+1)+tied)

def cooldown_schedule(tasks,n):
    """Small-case trace with None for idle slots; labels must be comparable."""
    if n<0:raise ValueError('Cooldown must be nonnegative')
    ready=[(-count,label) for label,count in Counter(tasks).items()]
    heapq.heapify(ready)
    cooling=deque();trace=[];time=0
    while ready or cooling:
        while cooling and cooling[0][0]<=time:
            _,count,label=cooling.popleft();heapq.heappush(ready,(count,label))
        if ready:
            count,label=heapq.heappop(ready);trace.append(label)
            if count+1<0:cooling.append((time+n+1,count+1,label))
        else:trace.append(None)
        time+=1
    return trace

def reorganize_string(s):
    counts=Counter(s)
    if max(counts.values(),default=0)>(len(s)+1)//2:return ''
    heap=[(-count,char) for char,count in counts.items()];heapq.heapify(heap)
    held=(0,'');out=[]
    while heap:
        count,char=heapq.heappop(heap);out.append(char)
        if held[0]<0:heapq.heappush(heap,held)
        held=(count+1,char)
    return ''.join(out) if held[0]==0 else ''

def video_stitching(clips,time):
    if time<0:raise ValueError('Nonnegative target time required')
    clips=sorted(clips);i=answer=0;covered=0
    while covered<time:
        farthest=covered
        while i<len(clips) and clips[i][0]<=covered:
            farthest=max(farthest,clips[i][1]);i+=1
        if farthest==covered:return -1
        covered=farthest;answer+=1
    return answer
'''
add(172,
'''三个问题共享“局部选择＋结构约束”，但不应共用一个未经证明的贪心模板。

任务冷却的下界一是总任务数，二是把最高频任务的前 f−1 次隔开形成长度 n+1 的框架，再放并列最高频的末次任务，得到 `(f−1)(n+1)+c`。两者最大值可由排列填空达到；演示另构造真实冷却时间线核验。

字符重排禁止相邻重复，暂时扣住刚输出字符，再从剩余最大频字符中选择。视频覆盖则在当前可接上的所有片段中选择结束最远的，更新覆盖前沿；片段的输入顺序无关。''',
SCHEDULING,
'''trace=cooldown_schedule('AAABBB',2)
show_table(['time','task'],list(enumerate(trace)))
show_table(['problem','input','result'],[
 ['reorganization','aaabbc',reorganize_string('aaabbc')],
 ['coverage',[[0,2],[1,5],[4,8]],video_stitching([[0,2],[1,5],[4,8]],8)]])
''',
'''from itertools import product,combinations
from random import Random
assert least_interval('AAABBB',2)==8
assert reorganize_string('aaab')==''
assert video_stitching([[0,1],[2,3]],3)==-1
assert video_stitching([],0)==0
def brute_cooldown(counts,n):
    start=(tuple(counts),(0,)*len(counts));queue=deque([(start,0)]);seen={start}
    while queue:
        (remaining,wait),time=queue.popleft()
        if not any(remaining):return time
        choices=[i for i in range(len(counts)) if remaining[i] and wait[i]==0]+[None]
        for choice in choices:
            new_counts=list(remaining);new_wait=[max(0,x-1) for x in wait]
            if choice is not None:new_counts[choice]-=1;new_wait[choice]=n
            state=(tuple(new_counts),tuple(new_wait))
            if state not in seen:seen.add(state);queue.append((state,time+1))
for counts in product(range(3),repeat=3):
    tasks=''.join(chr(65+i)*count for i,count in enumerate(counts))
    for n in range(3):
        expected=brute_cooldown(counts,n)
        assert least_interval(tasks,n)==expected
        trace=cooldown_schedule(tasks,n)
        assert len(trace)==expected and Counter(x for x in trace if x is not None)==Counter(tasks)
        last={}
        for time,label in enumerate(trace):
            if label is not None:
                assert label not in last or time-last[label]>n
                last[label]=time
    out=reorganize_string(tasks)
    possible=max(counts,default=0)<=(len(tasks)+1)//2
    if possible:assert Counter(out)==Counter(tasks) and all(a!=b for a,b in zip(out,out[1:]))
    else:assert out==''
def brute_cover(clips,target):
    for count in range(len(clips)+1):
        for subset in combinations(clips,count):
            end=0
            for left,right in sorted(subset):
                if left>end:break
                end=max(end,right)
            if end>=target:return count
    return -1
rng=Random(172)
for _ in range(250):
    clips=[]
    for i in range(rng.randrange(8)):
        left=rng.randrange(7);clips.append((left,left+rng.randrange(1,5)))
    target=rng.randrange(10)
    assert video_stitching(clips,target)==brute_cover(clips,target)
''',
'''冷却框架给出必要下界：最后一轮之前，每个最高频任务之间都要留足间隔；其他任务可填入空位，若超出空位则无须空闲。重排中最大频率不超过其余字符间隙数是可行必要条件，优先消耗最多者避免把稀缺间隙留到最后。区间贪心用交换论证：用结束更远、同样可接上的片段替换任一首段，不增加段数且不缩短后续可达范围。''',
'''冷却最短长度计算 O(m)，不同标签空间 O(u)；演示时间线可能包含大量空闲，仅用于小输入。重排 O(m log u)，覆盖排序 O(k log k)、扫描 O(k)。''')

HARD_SEQUENCES = '''from collections import Counter,deque

def min_window_audited(s,t):
    if not t:return ''
    required=Counter(t);missing=len(t);left=0;best=None
    for right,char in enumerate(s):
        if required[char]>0:missing-=1
        required[char]-=1
        while missing==0:
            if best is None or right-left+1<best[1]-best[0]:best=(left,right+1)
            old=s[left];required[old]+=1;left+=1
            if required[old]>0:missing+=1
    return '' if best is None else s[best[0]:best[1]]

def shortest_subarray_audited(nums,k):
    if k<=0:raise ValueError('Positive threshold required')
    prefixes=[0]
    for value in nums:prefixes.append(prefixes[-1]+value)
    queue=deque();best=len(nums)+1
    for j,value in enumerate(prefixes):
        while queue and value-prefixes[queue[0]]>=k:best=min(best,j-queue.popleft())
        while queue and prefixes[queue[-1]]>=value:queue.pop()
        queue.append(j)
    return -1 if best>len(nums) else best

def merge_stones_audited(stones,k):
    if k<2:raise ValueError('At least two adjacent piles per merge')
    if any(value<0 for value in stones):raise ValueError('Nonnegative pile weights required')
    n=len(stones)
    if n<=1:return 0
    if (n-1)%(k-1):return -1
    prefix=[0]
    for value in stones:prefix.append(prefix[-1]+value)
    dp=[[0]*n for _ in range(n)]
    for length in range(2,n+1):
        for left in range(n-length+1):
            right=left+length-1
            dp[left][right]=min(dp[left][middle]+dp[middle+1][right]
                for middle in range(left,right,k-1))
            if (length-1)%(k-1)==0:dp[left][right]+=prefix[right+1]-prefix[left]
    return dp[0][-1]
'''
add(173,
'''Hard 题的难点常是多个小前提同时成立，而非更长代码。最小覆盖窗口记录**缺少的字符实例数**，不是缺少的字符种类；目标 `AABC` 中两个 A 都必须被覆盖。

带负数最短子数组不能照搬普通窗口，改用前缀支配队列。合并石头则先检查可达性：每次把 k 堆变一堆，总堆数减少 k−1，因此 `(n−1)` 必须被 k−1 整除。

区间 DP 保存每段能压缩到的最少合法堆数的最小成本；分割点步长 k−1，只有区间能最终压成一堆时才加总重量。输出值正确之外，还必须解释每次“加区间和”的物理含义。''',
HARD_SEQUENCES,
'''s='ADOBECODEBANC';t='ABC'
show_table(['mechanism','input','result'],[
 ['multiplicity window',(s,t),min_window_audited(s,t)],
 ['prefix dominance',([2,-1,2],3),shortest_subarray_audited([2,-1,2],3)],
 ['interval merge',([3,2,4,1],2),merge_stones_audited([3,2,4,1],2)],
 ['unreachable remainder',([3,2,4,1],3),merge_stones_audited([3,2,4,1],3)]])
''',
'''from functools import cache
from itertools import product
from random import Random
def brute_window(s,t):
    if not t:return ''
    need=Counter(t);best=''
    for i in range(len(s)):
        for j in range(i+1,len(s)+1):
            found=Counter(s[i:j])
            if all(found[x]>=count for x,count in need.items()):
                if not best or j-i<len(best):best=s[i:j]
                break
    return best
for n in range(7):
    for chars in product('AB',repeat=n):
        s=''.join(chars)
        for t in ['','A','AA','AB','AAB']:
            assert min_window_audited(s,t)==brute_window(s,t)
assert min_window_audited('ADOBECODEBANC','ABC')=='BANC'
assert shortest_subarray_audited([-2,-1],1)==-1
rng=Random(173)
for _ in range(250):
    nums=[rng.randrange(-5,8) for _ in range(rng.randrange(9))];k=rng.randrange(1,15)
    expected=min((j-i for i in range(len(nums)) for j in range(i+1,len(nums)+1) if sum(nums[i:j])>=k),default=-1)
    assert shortest_subarray_audited(nums,k)==expected
@cache
def brute_merge(state,k):
    if len(state)<=1:return 0
    answer=float('inf')
    for i in range(len(state)-k+1):
        merged=sum(state[i:i+k]);cost=brute_merge(state[:i]+(merged,)+state[i+k:],k)
        answer=min(answer,merged+cost)
    return answer
for n in range(8):
    for k in [2,3,4]:
        for _ in range(8):
            stones=tuple(rng.randrange(1,6) for _ in range(n))
            expected=brute_merge(stones,k)
            expected=-1 if expected==float('inf') else expected
            assert merge_stones_audited(stones,k)==expected
assert merge_stones_audited([3,2,4,1],2)==20
assert merge_stones_audited([3,2,4,1],3)==-1
# Scale smoke cases never call the exponential or cubic-string references.
assert min_window_audited('x'*20000+'AAB','AAB')=='AAB'
assert shortest_subarray_audited([1]*20000,100)==100
assert merge_stones_audited([1]*30,2)>0
''',
'''窗口缺额为零等价于每个目标字符重数都满足。单调队列删除的是被较新、更小前缀支配的旧状态。石头区间长度 L 可压缩到 `(L−1) mod (k−1)+1` 堆；分割令左段可压一堆，穷举其最后分界覆盖所有合法结构。只有余数为零时还能把 k 堆合成一堆，成本恰是区间总和。''',
'''前两个算法时间 O(n+|t|)、O(n)，空间分别 O(字符种类)、O(n)。合并石头 O(n³/(k−1)) 时间（上界 O(n³)）、O(n²) 空间。独立穷举与规模冒烟分开。''')

GRAPH_CAPSTONE = '''from collections import deque

def max_genetic_difference(parents,queries,trace=None):
    n=len(parents)
    if n==0:
        if queries:raise ValueError('Queries require a nonempty tree')
        return []
    roots=[i for i,p in enumerate(parents) if p==-1]
    if len(roots)!=1:raise ValueError('Exactly one root required')
    children=[[] for _ in range(n)]
    for node,p in enumerate(parents):
        if p!=-1:
            if not 0<=p<n or p==node:raise ValueError('Invalid parent')
            children[p].append(node)
    by_node=[[] for _ in range(n)]
    maximum=n-1
    for i,(node,value) in enumerate(queries):
        if not 0<=node<n or value<0:raise ValueError('Invalid query')
        by_node[node].append((i,value));maximum=max(maximum,value)
    width=max(1,maximum.bit_length())
    links=[[-1,-1]];counts=[0]
    def change(value,delta):
        current=0;counts[current]+=delta
        assert counts[current]>=0
        for bit in range(width-1,-1,-1):
            digit=(value>>bit)&1
            if links[current][digit]==-1:
                assert delta==1
                links[current][digit]=len(links);links.append([-1,-1]);counts.append(0)
            current=links[current][digit];counts[current]+=delta
            assert counts[current]>=0
    def query(value):
        current=0;answer=0
        assert counts[0]>0
        for bit in range(width-1,-1,-1):
            digit=(value>>bit)&1;preferred=links[current][digit^1]
            if preferred!=-1 and counts[preferred]>0:
                answer|=1<<bit;current=preferred
            else:
                current=links[current][digit]
                assert current!=-1 and counts[current]>0
        return answer
    answer=[0]*len(queries);path=[];visited=0
    stack=[(roots[0],False)]
    while stack:
        node,exiting=stack.pop()
        if exiting:
            change(node,-1);assert path.pop()==node
            continue
        visited+=1;change(node,1);path.append(node)
        for index,value in by_node[node]:answer[index]=query(value)
        if trace is not None:trace.append((node,path[:],[(v,answer[i]) for i,v in by_node[node]]))
        stack.append((node,True))
        stack.extend((child,False) for child in reversed(children[node]))
    if visited!=n:raise ValueError('Disconnected cycle in parent relation')
    assert counts[0]==0 and not path
    return answer

def shortest_path_visiting_all(graph):
    n=len(graph)
    if n<=1:return 0
    full=(1<<n)-1
    queue=deque((i,1<<i,0) for i in range(n))
    seen={(i,1<<i) for i in range(n)}
    while queue:
        node,mask,distance=queue.popleft()
        if mask==full:return distance
        for other in graph[node]:
            state=(other,mask|(1<<other))
            if state not in seen:
                seen.add(state);queue.append((*state,distance+1))
    return -1
'''
add(174,
'''祖先最大异或查询需要的是**当前 DFS 路径**，不是整棵树。进入节点时把编号加入计数 Trie，回答该节点的全部查询，退出时删除。只建 Trie 不删除，会让兄弟分支的节点泄漏到答案中。

Trie 从高位优先选择相反位，因为任何更高位的 1 都优于所有低位之和。删除后保留的空节点不能继续参与查询，因此分支可用性取决于计数而不只是节点存在。

访问全部图节点的最短路，状态是 `(当前位置, 已访问掩码)`。同一位置在不同掩码下不是同一状态；多源 BFS 允许任选起点。树与图算法均采用迭代结构，深链不靠提高递归上限。''',
GRAPH_CAPSTONE,
'''trace=[]
answer=max_genetic_difference([-1,0,1,1],[[0,2],[3,2],[2,5]],trace)
show_table(['DFS node','current ancestor path','query value / xor result'],trace)
show_table(['graph','minimum walk length'],[([[1,2,3],[0],[0],[0]],shortest_path_visiting_all([[1,2,3],[0],[0],[0]]))])
''',
'''from random import Random
from itertools import permutations
assert max_genetic_difference([-1,0,1,1],[[0,2],[3,2],[2,5]])==[2,3,7]
rng=Random(174)
for n in range(1,35):
    parents=[-1]+[rng.randrange(i) for i in range(1,n)]
    queries=[(rng.randrange(n),rng.randrange(128)) for _ in range(30)]
    expected=[]
    for node,value in queries:
        candidates=[]
        while node!=-1:candidates.append(node^value);node=parents[node]
        expected.append(max(candidates))
    assert max_genetic_difference(parents,queries)==expected
assert max_genetic_difference([2,2,-1],[(0,1),(1,1)])==[3,3]
parents=[-1]+list(range(1999))
assert max_genetic_difference(parents,[(1999,2048)])[0]==max(i^2048 for i in range(2000))
def metric_reference(graph):
    n=len(graph)
    if n<=1:return 0
    dist=[[0 if i==j else float('inf') for j in range(n)] for i in range(n)]
    for i,neighbors in enumerate(graph):
        for j in neighbors:dist[i][j]=1
    for k in range(n):
        for i in range(n):
            for j in range(n):dist[i][j]=min(dist[i][j],dist[i][k]+dist[k][j])
    value=min(sum(dist[a][b] for a,b in zip(order,order[1:])) for order in permutations(range(n)))
    return -1 if value==float('inf') else value
for n in range(1,6):
    for _ in range(45):
        graph=[[] for _ in range(n)]
        for i in range(n):
            for j in range(i+1,n):
                if rng.randrange(3)==0:graph[i].append(j);graph[j].append(i)
        assert shortest_path_visiting_all(graph)==metric_reference(graph)
assert shortest_path_visiting_all([[],[]])==-1
''',
'''DFS 进入/退出配对保证 Trie 的正计数元素集合恰是根到当前节点路径，查询因此只看合法祖先。位贪心由二进制位权支配成立。BFS 中每条状态边成本为 1，第一次到达完整掩码就是最短；按图节点去重会错误合并不同已访问信息。参照用 Floyd 距离加所有访问排列，与状态 BFS 的实现路径独立。''',
'''祖先查询 O((n+q)B) 时间，Trie 分配空间上界 O(nB)，B 是编号与查询值的最大位长；可选完整路径轨迹另计。全访问 BFS 至多 n·2ⁿ 个状态，时间 O((n+m)2ⁿ)，空间 O(n2ⁿ)。''')

FINAL_CODE = '''from bisect import bisect_right
from itertools import combinations
import heapq

def job_scheduling(start,end,profit):
    if not len(start)==len(end)==len(profit):raise ValueError('Length mismatch')
    jobs=sorted(zip(end,start,profit))
    if any(left>=right for right,left,value in jobs):raise ValueError('Positive job duration required')
    ends=[right for right,left,value in jobs]
    dp=[0]*(len(jobs)+1)
    for i,(right,left,value) in enumerate(jobs,1):
        previous=bisect_right(ends,left,hi=i-1)
        dp[i]=max(dp[i-1],dp[previous]+value)
    return dp[-1]

def kth_smallest_row_sum(mat,k):
    if not mat or any(not row for row in mat):raise ValueError('Nonempty rows required')
    if k<1:raise ValueError('Positive rank required')
    combinations_count=1
    for row in mat:
        if any(a>b for a,b in zip(row,row[1:])):raise ValueError('Each row must be sorted')
        combinations_count*=len(row)
    if k>combinations_count:raise ValueError('Rank exceeds the number of choices')
    sums=[0]
    for row in mat:
        heap=[(value+row[0],i,0) for i,value in enumerate(sums)]
        heapq.heapify(heap);merged=[]
        while heap and len(merged)<k:
            value,i,j=heapq.heappop(heap);merged.append(value)
            if j+1<len(row):heapq.heappush(heap,(sums[i]+row[j+1],i,j+1))
        sums=merged
    return sums[k-1]

def _variant_jobs(instance):
    jobs=sorted(instance['jobs'],key=lambda job:(job[1],job[0],job[2]))
    limit=instance['max_jobs'];cooldown=instance['cooldown']
    if limit<0 or cooldown<0 or any(start>=end for start,end,value in jobs):
        raise ValueError('Invalid job limit, cooldown or interval')
    return jobs,min(limit,len(jobs)),cooldown

def solve_unseen_variant(instance):
    """Choose at most K nonoverlapping jobs, with a fixed gap after each selected job."""
    jobs,limit,cooldown=_variant_jobs(instance)
    ends=[end for start,end,value in jobs]
    predecessors=[bisect_right(ends,start-cooldown,hi=i) for i,(start,end,value) in enumerate(jobs)]
    previous=[0]*(len(jobs)+1)
    for _ in range(limit):
        current=[0]*(len(jobs)+1)
        for i,(start,end,value) in enumerate(jobs,1):
            current[i]=max(current[i-1],previous[predecessors[i-1]]+value)
        previous=current
    return previous[-1]

def reference_unseen_variant(instance):
    jobs,limit,cooldown=_variant_jobs(instance)
    best=0
    for count in range(limit+1):
        for subset in combinations(jobs,count):
            ordered=sorted(subset,key=lambda job:job[0])
            if all(a[1]+cooldown<=b[0] for a,b in zip(ordered,ordered[1:])):
                best=max(best,sum(job[2] for job in ordered))
    return best
'''
add(175,
'''结业不是再做一遍已展示的例题，而是迁移已有结构。先复习两条主线：带权区间调度用“选/不选当前工作＋二分前驱”；有序矩阵行和用“逐行合并有序和列表＋Top-k 截断”。重复和值不能去重，因为不同选择组合各占一个排名。

**迁移练习契约：** 输入 `instance={jobs:[(start,end,profit),...], max_jobs:K, cooldown:g}`；选择至多 K 份工作，前一份的 end+g 不大于后一份 start，允许一份不选，返回最大收益。相邻相接在 g=0 时合法；收益可负，因此最优值至少为零。

状态新增“还能选多少份”，而不是另造一个庞大框架。前驱条件从 end≤start 改成 end≤start−g。课程演示数据与测试随机源分离；这里的“陌生”指未展示给学习者的组合变体，不声称它是研究界全新问题或模型训练中从未出现过。

**结业提交：** 先写自己的推导与实现，再打开参考实现。评分分别记录接口正确、证明完整、边界处理、复杂度及约束改变后的迁移解释；不以已刷题数代替能力。''',
FINAL_CODE,
'''example={'jobs':[(1,3,20),(3,5,25),(4,6,30),(7,8,15)],'max_jobs':2,'cooldown':1}
show_table(['candidate','value','purpose'],[
 ['subset enumeration',reference_unseen_variant(example),'small independent reference'],
 ['predecessor + K-layer DP',solve_unseen_variant(example),'optimized transfer'],
 ['row-sum heap',kth_smallest_row_sum([[1,3,11],[2,4,6]],5),'duplicates count separately']])
''',
'''from itertools import product
from random import Random
assert job_scheduling([1,2,3,3],[3,4,5,6],[50,10,40,70])==120
assert job_scheduling([],[],[])==0
assert job_scheduling([1,2],[2,3],[-1,-2])==0
assert kth_smallest_row_sum([[1,3,11],[2,4,6]],5)==7
assert kth_smallest_row_sum([[1,1],[2,2]],4)==3
rng=Random(17501)
for _ in range(160):
    mat=[sorted(rng.randrange(-3,8) for _ in range(rng.randrange(1,5))) for _ in range(rng.randrange(1,5))]
    expected=sorted(sum(choice) for choice in product(*mat))
    for k in sorted({1,len(expected),rng.randrange(1,len(expected)+1)}):
        assert kth_smallest_row_sum(mat,k)==expected[k-1]
# Different seed and fresh cases from the displayed teaching example.
heldout=Random(17599)
for _ in range(300):
    jobs=[]
    for i in range(heldout.randrange(10)):
        start=heldout.randrange(12);end=start+heldout.randrange(1,5)
        jobs.append((start,end,heldout.randrange(-4,21)))
    instance={'jobs':jobs,'max_jobs':heldout.randrange(6),'cooldown':heldout.randrange(4)}
    assert solve_unseen_variant(instance)==reference_unseen_variant(instance)
    ordinary={'jobs':jobs,'max_jobs':len(jobs),'cooldown':0}
    assert job_scheduling([x[0] for x in jobs],[x[1] for x in jobs],[x[2] for x in jobs])==reference_unseen_variant(ordinary)
large={'jobs':[(3*i,3*i+1,1) for i in range(5000)],'max_jobs':12,'cooldown':1}
assert solve_unseen_variant(large)==12
# No exponential reference on the large case.
assert kth_smallest_row_sum([[i for i in range(50)] for _ in range(10)],20)>=0
try:kth_smallest_row_sum([[1],[2]],2)
except ValueError:pass
else:raise AssertionError('Invalid rank was accepted')
''',
'''带权调度按结束时间排序后，包含最后一份工作的解，其余工作全部属于已兼容前缀；选/不选覆盖全部解。新增计数层保持同一分解。行和合并中，已有和排在第 k 名之后的前缀不可能进入下一轮前 k：至少已有 k 个不大的前缀能配相同最小后缀；重数保留使此论证对相等值成立。''',
'''带权调度 O(n log n) 时间、O(n) 空间。迁移版 O(n log n+nK)，滚动两层 O(n) 空间。r 行的 Top-k 合并至多 O(rk log k)，工作空间 O(k)，另有读取与排序性验证成本。参考子集枚举指数级，仅限小数据。''')
