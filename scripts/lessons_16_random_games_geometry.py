from course_builder import add

add(131,'“看起来随机”不等于每个结果等概率。Fisher–Yates每次从尚未固定的位置中均匀选一个；蓄水池在第i项出现时以k/i概率保留它；加权抽样把整数权重变成等长基本抽签区间。rand10通过拒绝不能均分为10份的尾部样本消除偏差。',
'''from bisect import bisect_right
from random import Random

def fisher_yates(a,rng):
    for i in range(len(a)-1,0,-1):
        j=rng.randrange(i+1); a[i],a[j]=a[j],a[i]
    return a

def reservoir_sample(stream,k,rng):
    if k<0: raise ValueError('nonnegative reservoir size required')
    reservoir=[]
    for i,x in enumerate(stream):
        if i<k: reservoir.append(x)
        elif k:
            j=rng.randrange(i+1)
            if j<k: reservoir[j]=x
    return reservoir

class WeightedSampler:
    def __init__(self,weights,rng=None):
        if any(not isinstance(w,int) or w<0 for w in weights) or sum(weights)<=0: raise ValueError('nonnegative integer weights with positive total required')
        self.prefix=[]; total=0
        for w in weights: total+=w; self.prefix.append(total)
        self.total=total; self.rng=Random() if rng is None else rng
    def pick_index(self):
        ticket=self.rng.randrange(self.total)
        return bisect_right(self.prefix,ticket)

def rand10(rand7):
    while True:
        a,b=rand7(),rand7()
        if not 1<=a<=7 or not 1<=b<=7: raise ValueError('rand7 must return 1..7')
        ticket=(a-1)*7+(b-1)
        if ticket<40: return ticket%10+1
''',
'''from itertools import product
from collections import Counter
class FixedRng:
    def __init__(self,values): self.values=iter(values)
    def randrange(self,stop):
        value=next(self.values); assert 0<=value<stop; return value
counts=Counter(tuple(fisher_yates([0,1,2],FixedRng([a,b]))) for a,b in product(range(3),range(2)))
show_table(['排列','六条等概率抽签轨迹中的次数'],sorted(counts.items()))''',
'''from itertools import product
from collections import Counter
class FixedRng:
    def __init__(self,values): self.values=iter(values)
    def randrange(self,stop):
        value=next(self.values); assert 0<=value<stop; return value
counts=Counter(tuple(fisher_yates([0,1,2],FixedRng([a,b]))) for a,b in product(range(3),range(2)))
assert len(counts)==6 and set(counts.values())=={1}
subsets=Counter(tuple(sorted(reservoir_sample(range(4),2,FixedRng([a,b])))) for a,b in product(range(3),range(4)))
assert len(subsets)==6 and set(subsets.values())=={2}
assert [WeightedSampler([0,2,0,3],FixedRng([i])).pick_index() for i in range(5)]==[1,1,3,3,3]
assert reservoir_sample(range(10),3,Random(131))==reservoir_sample(range(10),3,Random(131))
assert reservoir_sample(iter([1,2]),5,Random(1))==[1,2]
assert reservoir_sample(range(5),0,Random(1))==[]
accepted=Counter()
for a,b in product(range(1,8),repeat=2):
    if (a-1)*7+b-1<40:
        values=iter([a,b]); accepted[rand10(lambda:next(values))]+=1
assert accepted==Counter({i:4 for i in range(1,11)})
values=iter([7,7,1,1]); assert rand10(lambda:next(values))==1''',
'洗牌每个最终排列对应唯一抽签路径，概率为1/n!。蓄水池中旧元素在第i步后存活概率(k/(i−1))·(1−1/i)=k/i，新元素被保留概率也是k/i；完整均匀k子集性质可继续按子集归纳。加权区间包含恰好w[i]张票；拒绝抽样接受的40张票对10个结果各贡献4张。',
'洗牌O(n)时间O(1)辅助；蓄水池O(n)时间O(k)空间且仅遍历一次；加权初始化O(n)、每次O(log n)；rand10期望调用rand7次数2·49/40，无确定有限最坏次数。统计频率仅辅助诊断，测试主要使用精确轨迹枚举。')

add(132,'无偏组合博弈中，双方可用动作只依赖当前状态，正常规则下无步可走者输。SG值是后继SG集合的最小缺失非负数mex；多个独立子游戏的SG值按异或合并。注意力扣can_win_nim接口是每次取1–3根的减法游戏，不能把其n%4规则误套到所有Nim变体。',
'''from math import isqrt

def can_win_nim(n):
    if n<0: raise ValueError('nonnegative pile required')
    return n%4!=0

def winner_square_game(n):
    if n<0: raise ValueError('nonnegative pile required')
    dp=[False]*(n+1)
    for x in range(1,n+1): dp[x]=any(not dp[x-s*s] for s in range(1,isqrt(x)+1))
    return dp[n]

def grundy(state,moves):
    memo={}; active=set()
    def solve(s):
        if s in memo: return memo[s]
        if s in active: raise ValueError('finite acyclic game graph required')
        active.add(s); reachable={solve(t) for t in moves(s)}; active.remove(s)
        value=0
        while value in reachable: value+=1
        memo[s]=value; return value
    return solve(state)
''',
'''moves=lambda n:[n-k for k in (1,2) if k<=n]
show_table(['石子数','取1或2的SG','取1..3是否必胜','取平方数是否必胜'],[(n,grundy(n,moves),can_win_nim(n),winner_square_game(n)) for n in range(11)])''',
'''assert not can_win_nim(4) and can_win_nim(5)
assert not winner_square_game(2)
assert grundy(0,lambda s:[])==0
from functools import cache
moves=lambda n:[n-k for k in (1,2) if k<=n]
@cache
def win_pair(a,b):
    return any(not win_pair(a-k,b) for k in (1,2) if a>=k) or any(not win_pair(a,b-k) for k in (1,2) if b>=k)
for a in range(9):
    for b in range(9): assert bool(grundy(a,moves)^grundy(b,moves))==win_pair(a,b)
@cache
def square_ref(n): return any(not square_ref(n-k*k) for k in range(1,isqrt(n)+1))
for n in range(80): assert winner_square_game(n)==square_ref(n)
try: grundy(0,lambda s:[s])
except ValueError: pass
else: raise AssertionError('cycle should not be silently treated as a losing state')''',
'SG为0时，所有后继SG都非零；SG非零时，mex定义保证存在SG为0的后继，因此输赢与SG是否为0一致。独立游戏和的异或为0时任一单游戏变化使异或非零；异或非零时可选最高不同位对应的分量转移到较小的指定SG，使总异或变0。该结论依赖正常玩法、无偏与有限终止。',
'取1..3 O(1)算术；平方取石O(n√n)时间O(n)空间；一般SG按可达DAG求值，O(V+E)级集合操作和O(V+E)空间上界。递归版仅用于小有限状态；有环游戏、失手规则和双方动作不同的游戏不能直接套此模板。')

add(133,'计算几何先把图形关系写成代数谓词。叉积符号判断左转、右转或共线；线段相交还需处理共线端点的包围盒。凸包通过不断删除不构成左转的中间点得到外边界。整数坐标用精确整数运算，避免不必要浮点斜率；共线计数用约分后的方向对。',
'''from math import gcd
from collections import Counter

def cross(o,a,b): return (a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0])

def _on_segment(a,b,p):
    return cross(a,b,p)==0 and min(a[0],b[0])<=p[0]<=max(a[0],b[0]) and min(a[1],b[1])<=p[1]<=max(a[1],b[1])

def segments_intersect(a,b,c,d):
    x,y,z,w=cross(a,b,c),cross(a,b,d),cross(c,d,a),cross(c,d,b)
    if (x>0 and y<0 or x<0 and y>0) and (z>0 and w<0 or z<0 and w>0): return True
    return _on_segment(a,b,c) or _on_segment(a,b,d) or _on_segment(c,d,a) or _on_segment(c,d,b)

def rectangles_overlap(a,b):
    return max(a[0],b[0])<min(a[2],b[2]) and max(a[1],b[1])<min(a[3],b[3])

def convex_hull(points,include_collinear=False):
    points=sorted(set(map(tuple,points)))
    if len(points)<=2: return points
    if all(cross(points[0],points[-1],p)==0 for p in points): return points if include_collinear else [points[0],points[-1]]
    def half(sequence):
        stack=[]
        for p in sequence:
            while len(stack)>=2 and (cross(stack[-2],stack[-1],p)<0 if include_collinear else cross(stack[-2],stack[-1],p)<=0): stack.pop()
            stack.append(p)
        return stack
    return half(points)[:-1]+half(reversed(points))[:-1]

def max_points(points):
    best=0
    for i,(x,y) in enumerate(points):
        slopes=Counter(); duplicates=0
        for u,v in points[i+1:]:
            dx,dy=u-x,v-y
            if dx==dy==0: duplicates+=1; continue
            divisor=gcd(dx,dy); dx//=divisor; dy//=divisor
            if dx<0 or dx==0 and dy<0: dx,dy=-dx,-dy
            slopes[(dx,dy)]+=1
        best=max(best,1+duplicates+max(slopes.values(),default=0))
    return best
''',
'''points=[(0,0),(1,0),(2,0),(2,2),(0,2),(1,1)]; hull=convex_hull(points)
show_table(['输入点','极点凸包成员','包含共线边界时成员'],[(p,p in hull,p in convex_hull(points,True)) for p in points])
show_table(['凸包有向边','内部测试点(1,1)叉积'],[((a,b),cross(a,b,(1,1))) for a,b in zip(hull,hull[1:]+hull[:1])])''',
'''assert segments_intersect((0,0),(2,2),(0,2),(2,0))
assert segments_intersect((0,0),(1,0),(1,0),(2,0))
assert not segments_intersect((0,0),(1,0),(2,0),(3,0))
assert not rectangles_overlap([0,0,1,1],[1,0,2,1])
assert max_points([(1,1),(1,1),(2,2)])==3
assert convex_hull([(0,0),(1,1),(2,2)])==[(0,0),(2,2)]
assert len(convex_hull([(0,0),(1,1),(2,2)],True))==3
from random import Random
rng=Random(133)
for _ in range(250):
    points=[(rng.randrange(-3,4),rng.randrange(-3,4)) for _ in range(rng.randrange(1,10))]; hull=convex_hull(points)
    if len(hull)>=3:
        assert all(cross(a,b,p)>=0 for a,b in zip(hull,hull[1:]+hull[:1]) for p in points)
        assert all(cross(hull[i-2],hull[i-1],hull[i])>0 for i in range(len(hull)))
    elif len(hull)==2: assert all(_on_segment(hull[0],hull[1],p) for p in points)
    else: assert len(set(points))==1
    want=max(Counter(points).values())
    for i,a in enumerate(points):
        for b in points[i+1:]:
            if a!=b: want=max(want,sum(cross(a,b,p)==0 for p in points))
    assert max_points(points)==want''',
'叉积等于有向平行四边形面积。凸包栈删除非左转点时，该点位于相邻两点与当前点包围的内侧，不能成为该半边的极点；上下两条单调链合成逆时针凸包。方向对用GCD约分并统一符号，竖直线和重复点均不需要浮点特例斜率。',
'凸包O(n log n)时间O(n)空间；最多共线点O(n²)次方向处理、O(n)辅助。默认凸包只保留极点，include_collinear=True返回所有边界输入点（适配围栏类题）。线段接触算相交；矩形只有正面积交叠才返回True。')
