from course_builder import add

add(17, '删除元素不必每次移动整个后缀。读指针扫描原数组，写指针只在保留元素时前进；写指针之前恰好是处理完前缀中的有效元素。移动零也是稳定压缩，最后把剩余位置填成零。有效长度之外的内容不属于删除题的答案。',
'''def remove_element(nums,val):
    write=0
    for read in range(len(nums)):
        if nums[read]!=val:
            nums[write]=nums[read]
            write+=1
    return write

def move_zeroes(nums):
    write=0
    for read in range(len(nums)):
        if nums[read]!=0:
            nums[write]=nums[read]
            write+=1
    for i in range(write,len(nums)):
        nums[i]=0
''',
'''a=[0,3,0,2,5]; rows=[]; w=0
for r in range(len(a)):
    value=a[r]
    if value!=0: a[w]=value; w+=1
    rows.append((r,value,w,a[:w]))
show_table(['read','读取值','write','有效前缀'],rows)''',
'''a=[3,2,2,3]; k=remove_element(a,3); assert k==2 and a[:k]==[2,2]
a=[3,3]; assert remove_element(a,3)==0
from itertools import product
for n in range(6):
    for values in product([0,1,2],repeat=n):
        a=list(values); ref=[x for x in a if x]+[0]*a.count(0)
        move_zeroes(a); assert a==ref
assert remove_element([],1)==0''',
'始终有 write≤read，写入不会覆盖未读元素；有效前缀按读取顺序增加，因此稳定且无遗漏。','两个算法 O(n) 时间、O(1) 辅助空间。')

add(18, '螺旋遍历维护尚未访问的矩形边界；处理一条边后必须收缩，并在处理对边前再次检查非空，避免单行或单列被重复访问。方阵顺时针旋转可分解为转置与每行反转：坐标 (i,j) 变为 (j,n−1−i)。',
'''def spiral_order(matrix):
    if not matrix or not matrix[0]: return []
    top,bottom,left,right=0,len(matrix)-1,0,len(matrix[0])-1
    out=[]
    while top<=bottom and left<=right:
        for j in range(left,right+1): out.append(matrix[top][j])
        top+=1
        for i in range(top,bottom+1): out.append(matrix[i][right])
        right-=1
        if top<=bottom:
            for j in range(right,left-1,-1): out.append(matrix[bottom][j])
            bottom-=1
        if left<=right:
            for i in range(bottom,top-1,-1): out.append(matrix[i][left])
            left+=1
    return out

def rotate_square(matrix):
    n=len(matrix)
    if any(len(row)!=n for row in matrix): raise ValueError('requires square matrix')
    for i in range(n):
        for j in range(i+1,n):
            matrix[i][j],matrix[j][i]=matrix[j][i],matrix[i][j]
    for row in matrix: row.reverse()
''',
'''m=[[1,2,3],[4,5,6],[7,8,9]]
order=spiral_order(m)
show_table(['访问序号','元素'], list(enumerate(order,1)))
rotate_square(m)
show_table(['旋转后行号','行'],list(enumerate(m)))''',
'''assert spiral_order([[1,2,3],[4,5,6]])==[1,2,3,6,5,4]
assert spiral_order([[1,2,3]])==[1,2,3]
assert spiral_order([[1],[2],[3]])==[1,2,3]
assert spiral_order([])==[]
for n in range(5):
    m=[[i*n+j for j in range(n)] for i in range(n)]; orig=[r[:] for r in m]
    for _ in range(4): rotate_square(m)
    assert m==orig''',
'未访问元素始终位于当前闭矩形内；每次只取边界并将其删除。转置和反转的坐标复合直接给出旋转映射，且交换是双射。','螺旋 O(rows×cols) 时间与输出空间；旋转 O(n²) 时间、O(1) 辅助空间。')

add(19, '两数和暴力枚举第二个索引；优化时把“已经出现的值→索引”存入字典。对当前 x，只查询 target−x 是否位于过去。先查询再写入，才能允许 [3,3] 匹配两个不同位置，又不会把单个3重复使用。多解输入只要求返回任意合法不同索引对。',
'''def two_sum(nums,target):
    seen={}
    for j,x in enumerate(nums):
        if target-x in seen: return [seen[target-x],j]
        seen[x]=j
    return None

def two_sum_bruteforce(nums,target):
    for i in range(len(nums)):
        for j in range(i+1,len(nums)):
            if nums[i]+nums[j]==target: return [i,j]
    return None
''',
'''a=[2,7,11,15]; seen={}; rows=[]
for j,x in enumerate(a):
    rows.append((j,x,9-x,dict(seen),(9-x) in seen)); seen[x]=j
show_table(['j','x','需寻找','之前字典','是否找到'],rows)''',
'''assert two_sum([2,7,11,15],9)==[0,1]
assert two_sum([3,3],6)==[0,1]
from itertools import product
for n in range(5):
    for a in product([-1,0,1],repeat=n):
        for target in range(-2,3):
            ans=two_sum(a,target); ref=two_sum_bruteforce(a,target)
            assert (ans is None)==(ref is None)
            if ans is not None:
                i,j=ans; assert i<j and a[i]+a[j]==target''',
'考虑任意合法对 i<j：处理 j 时字典中保留了 nums[i] 的某个较早索引，因此一定能找到一个合法对。只查询过去确保索引不同。','哈希版平均 O(n) 时间、O(n) 空间；暴力版 O(n²) 时间、O(1) 空间。')

add(20, '异位词忽略位置但保留每个字符的频次。将单词映射到规范表示，就把比较问题转化为等价类分组。通用字符实现使用排序后的字符元组作键；小写字母固定字母表也可用26维频次数组。分组次序不是问题的本质，测试应规范化组和组内顺序。',
'''from collections import Counter, defaultdict

def is_anagram(s,t):
    return Counter(s)==Counter(t)

def group_anagrams(words):
    groups=defaultdict(list)
    for word in words:
        groups[tuple(sorted(word))].append(word)
    return list(groups.values())
''',
'''words=['eat','tea','tan','ate','nat','bat']
show_table(['单词','规范键'],[(w,''.join(sorted(w))) for w in words])
show_table(['组号','组'],list(enumerate(group_anagrams(words))))''',
'''assert is_anagram('anagram','nagaram')
assert not is_anagram('rat','car')
def normalized(groups): return sorted(sorted(g) for g in groups)
assert normalized(group_anagrams(['eat','tea','eat','bat']))==[['bat'],['eat','eat','tea']]
assert group_anagrams([])==[]
assert is_anagram('','')''',
'两个词的排序字符序列相同，当且仅当所有字符的出现次数相同。这构成等价关系；每次追加原词而非放入集合，保留重复词。','比较平均 O(|s|+|t|)；分组 O(Σ Lᵢ log Lᵢ) 时间，键与输出存储 O(ΣLᵢ)。')

add(21, '连续序列不要求原数组连续。排序能得到 O(n log n) 参照；集合解只从“没有前驱 x−1”的值启动延伸。若从每个值延伸会重复扫描长链，而只从链首启动让每个不同值至多被遍历一次。',
'''def longest_consecutive(nums):
    values=set(nums)
    best=0
    for x in values:
        if x-1 not in values:
            y=x
            while y in values: y+=1
            best=max(best,y-x)
    return best

def unique_intersection(a,b):
    return set(a)&set(b)
''',
'''values=set([100,4,200,1,3,2]); rows=[]
for x in sorted(values):
    if x-1 not in values:
        chain=[]; y=x
        while y in values: chain.append(y); y+=1
        rows.append((x,chain,len(chain)))
show_table(['链首','延伸链','长度'],rows)''',
'''assert longest_consecutive([100,4,200,1,3,2])==4
assert longest_consecutive([1,1,2])==2
assert longest_consecutive([])==0
from itertools import product
for n in range(6):
    for a in product([-1,0,1,3],repeat=n):
        seq=sorted(set(a)); best=run=0; prev=None
        for x in seq:
            run=run+1 if prev is not None and x==prev+1 else 1
            best=max(best,run); prev=x
        assert longest_consecutive(a)==best
assert unique_intersection([1,1,2],[1,3])=={1}''',
'有限整数集合唯一分解为若干最大连续链，每条链有唯一无前驱起点；算法恰好遍历这些链并取最大长度。','平均 O(n) 时间、O(u) 空间；均摊分析需同时计外层起点检查与内部延伸。')

add(22, '同构要求一一对应，不只是同一个字符每次映射一致。`ab→aa`满足单向一致却破坏可逆性，所以必须同时约束正向和反向映射。单词模式只是把“字符”换成“以空格分开的词”。',
'''def bijective_match(left,right):
    if len(left)!=len(right): return False
    forward,backward={},{}
    for x,y in zip(left,right):
        if x in forward and forward[x]!=y: return False
        if y in backward and backward[y]!=x: return False
        forward[x]=y; backward[y]=x
    return True

def is_isomorphic(s,t):
    return bijective_match(s,t)

def word_pattern(pattern,text):
    return bijective_match(pattern,text.split())
''',
'''show_table(['左序列','右序列','是否双射'],[(s,t,is_isomorphic(s,t)) for s,t in [('egg','add'),('foo','bar'),('ab','aa'),('paper','title')]])''',
'''assert is_isomorphic('egg','add')
assert not is_isomorphic('foo','bar')
assert not is_isomorphic('ab','aa')
assert not is_isomorphic('a','ab')
assert word_pattern('abba','dog cat cat dog')
assert not word_pattern('abba','dog cat cat fish')''',
'每步只接受与已有双向映射兼容的字符对，保持局部双射。扫描结束后映射覆盖所有出现的字符，因此给出全局一一对应。','平均 O(n) 时间、O(u) 映射空间；split 还需与文本长度成正比的存储。')

add(23, '解析数字不是“看到数字就累加”。先区分前导空白、可选符号、数字前缀，再处理截断和范围；科学计数法还需要记录小数点、指数以及指数后是否真的出现数字。本章字符范围限定为 ASCII 数字。`my_atoi`允许停止于第一个非法字符；`is_number`要求整个去首尾空白后的串合法。',
'''def my_atoi(s):
    i=0; n=len(s)
    while i<n and s[i]==' ': i+=1
    sign=1
    if i<n and s[i] in '+-':
        sign=-1 if s[i]=='-' else 1; i+=1
    value=0
    while i<n and '0'<=s[i]<='9':
        value=value*10+ord(s[i])-ord('0'); i+=1
    return max(-(1<<31),min((1<<31)-1,sign*value))

def is_number(s):
    s=s.strip()
    if not s: return False
    seen_digit=False; seen_dot=False; seen_exp=False
    for i,c in enumerate(s):
        if '0'<=c<='9': seen_digit=True
        elif c in '+-':
            if i!=0 and s[i-1] not in 'eE': return False
        elif c=='.':
            if seen_dot or seen_exp: return False
            seen_dot=True
        elif c in 'eE':
            if seen_exp or not seen_digit: return False
            seen_exp=True; seen_digit=False
        else: return False
    return seen_digit
''',
'''show_table(['输入','atoi前缀解析','完整数字判定'],[(s,my_atoi(s),is_number(s)) for s in ['  -42','4193 with words','3.5e2','1e','+','.8','9e-3']])''',
'''assert my_atoi('')==0 and my_atoi('  -42')==-42
assert my_atoi('4193 with words')==4193
assert my_atoi('91283472332')==(1<<31)-1
assert my_atoi('-91283472332')==-(1<<31)
for s in ['1e','e3','+','.','1e+','1.2.3','6e-']: assert not is_number(s)
for s in ['2','-0.1','2e10','.8','3.','+6e-1']: assert is_number(s)''',
'指数前必须已有数字，读到指数后重置seen_digit，最终要求指数部分有数字；小数点只能在指数之前出现一次，符号只允许开头或紧跟指数。','O(n) 字符扫描；atoi逐步大整数计算存在位代价，可在超界确定后提前饱和以限制位数。本实现为教学直写。')

add(24, '右旋 k 个位置可转成三次反转：先反转全部，再分别反转前 k 段和其余段。k 要先对 n 取模，空数组必须先处理。字符压缩则读一段相同字符，写字符与十进制计数；返回有效长度，不要把尾部旧数据当答案。',
'''def rotate_array(nums,k):
    n=len(nums)
    if not n: return
    k%=n
    def reverse(left,right):
        while left<right:
            nums[left],nums[right]=nums[right],nums[left]
            left+=1; right-=1
    reverse(0,n-1); reverse(0,k-1); reverse(k,n-1)

def compress(chars):
    read=write=0
    while read<len(chars):
        end=read+1
        while end<len(chars) and chars[end]==chars[read]: end+=1
        chars[write]=chars[read]; write+=1
        if end-read>1:
            for c in str(end-read): chars[write]=c; write+=1
        read=end
    return write
''',
'''a=[1,2,3,4,5]; rows=[]
for k in range(6):
    b=a[:]; rotate_array(b,k); rows.append((k,b))
show_table(['右旋k','数组'],rows)''',
'''a=[1,2,3]; rotate_array(a,4); assert a==[3,1,2]
rotate_array(a,3); assert a==[3,1,2]
a=[]; rotate_array(a,8); assert a==[]
a=list('aab'); k=compress(a); assert k==3 and a[:k]==list('a2b')
a=['a']*12; k=compress(a); assert a[:k]==list('a12')
for n in range(1,7):
    for k in range(12):
        a=list(range(n)); ref=a[-(k%n):]+a[:-(k%n)] if k%n else a[:]
        rotate_array(a,k); assert a==ref''',
'把原数组拆为AB，其中B长度为k；反转全部得到BᴿAᴿ，再分别反转得到BA。压缩每个已读字符段至少能容纳它的压缩表示，因此不会写到未读取区域。','均为 O(n) 时间、O(1) 指针空间；计数字符串长度 O(log n)。')

add(25, '有序两数和的和太小时，固定右端点后所有更靠左的候选也都太小，可以安全丢弃左端点；太大时对称丢弃右端点。这个消元依赖有序性。回文判断则从两端对照，跳过非字母数字字符；规范化大小写后逐对比较。',
'''def two_sum_sorted(numbers,target):
    left,right=0,len(numbers)-1
    while left<right:
        total=numbers[left]+numbers[right]
        if total==target: return [left+1,right+1]
        if total<target: left+=1
        else: right-=1
    return None

def is_palindrome(s):
    left,right=0,len(s)-1
    while left<right:
        while left<right and not s[left].isalnum(): left+=1
        while left<right and not s[right].isalnum(): right-=1
        if s[left].lower()!=s[right].lower(): return False
        left+=1; right-=1
    return True
''',
'''a=[1,2,4,8,10]; l=0; r=len(a)-1; rows=[]
while l<r:
    total=a[l]+a[r]; rows.append((l,r,a[l],a[r],total))
    if total==12: break
    if total<12: l+=1
    else: r-=1
show_table(['left','right','左值','右值','和'],rows)''',
'''assert two_sum_sorted([2,7,11,15],9)==[1,2]
assert is_palindrome('A man, a plan, a canal: Panama')
assert is_palindrome('') and not is_palindrome('race a car')
from itertools import combinations_with_replacement
for n in range(6):
    for a in combinations_with_replacement([-1,0,1,2],n):
        for t in range(-2,5):
            ans=two_sum_sorted(a,t)
            valid=[(i,j) for i in range(n) for j in range(i+1,n) if a[i]+a[j]==t]
            assert (ans is not None)==bool(valid)
            if ans: assert (ans[0]-1,ans[1]-1) in valid''',
'每次移动指针都排除一整行或一整列不可能解；未排除解仍在当前指针范围内。回文每次确认对称一对字符，剩余中段是同一子问题。','两者 O(n) 时间、O(1) 辅助空间。字符分类采用Python语义；平台ASCII范围内与常见题意一致。')

add(26, '有序数组的重复项相邻。最多保留 k 次时，只要写指针不足 k，或当前值不同于有效前缀倒数第 k 个值，就可以写入。比较的是已经写出的前缀，不是原数组固定偏移；这让一个规则同时解决去重与有限次数保留。',
'''def keep_at_most_k(nums,k):
    if k<=0: return 0
    write=0
    for read in range(len(nums)):
        value=nums[read]
        if write<k or value!=nums[write-k]:
            nums[write]=value; write+=1
    return write

def remove_duplicates(nums):
    return keep_at_most_k(nums,1)
''',
'''a=[1,1,1,2,2,3]; rows=[]
for k in [0,1,2,3]:
    b=a[:]; length=keep_at_most_k(b,k); rows.append((k,length,b[:length]))
show_table(['保留上限','有效长度','有效前缀'],rows)''',
'''a=[1,1,2]; k=remove_duplicates(a); assert a[:k]==[1,2]
a=[1,1,1,2,2,3]; k=keep_at_most_k(a,2); assert a[:k]==[1,1,2,2,3]
assert remove_duplicates([])==0
from itertools import combinations_with_replacement
from collections import Counter
for n in range(7):
    for a in combinations_with_replacement([0,1,2],n):
        for limit in range(4):
            b=list(a); k=keep_at_most_k(b,limit)
            ref=[x for x,c in sorted(Counter(a).items()) for _ in range(min(c,limit))]
            assert b[:k]==ref''',
'有序性确保相同值连续。当nums[write−k]等于当前值时，前缀尾部已经保留k个该值；否则再保留一个不会超限。','O(n) 时间、O(1) 辅助空间；仅对有序输入成立。')

add(27, '三数和先固定一个数，将剩余问题转为有序两数和；相同固定值和相同左右值要跳过，避免重复值三元组。盛水容器虽然也用相向指针，理由不同：面积由短板决定，保留短板而缩小宽度不可能改善当前面积，所以应丢弃短板。',
'''def three_sum(nums):
    a=sorted(nums); answer=[]
    for i in range(len(a)-2):
        if i and a[i]==a[i-1]: continue
        if a[i]>0: break
        left,right=i+1,len(a)-1
        while left<right:
            total=a[i]+a[left]+a[right]
            if total<0: left+=1
            elif total>0: right-=1
            else:
                answer.append([a[i],a[left],a[right]])
                left+=1; right-=1
                while left<right and a[left]==a[left-1]: left+=1
                while left<right and a[right]==a[right+1]: right-=1
    return answer

def max_area(height):
    left,right=0,len(height)-1; best=0
    while left<right:
        best=max(best,(right-left)*min(height[left],height[right]))
        if height[left]<=height[right]: left+=1
        else: right-=1
    return best
''',
'''h=[1,8,6,2,5,4,8,3,7]; l=0; r=len(h)-1; rows=[]
while l<r:
    rows.append((l,r,min(h[l],h[r]),(r-l)*min(h[l],h[r])))
    if h[l]<=h[r]: l+=1
    else: r-=1
show_table(['left','right','短板','候选面积'],rows)''',
'''assert sorted(three_sum([-1,0,1,2,-1,-4]))==[[-1,-1,2],[-1,0,1]]
assert three_sum([0,0,0,0])==[[0,0,0]]
from itertools import product,combinations
for n in range(6):
    for a in product([0,1,3],repeat=n):
        ref=max(((j-i)*min(a[i],a[j]) for i in range(n) for j in range(i+1,n)),default=0)
        assert max_area(a)==ref
for a in product([-1,0,1],repeat=5):
    ref={tuple(sorted(t)) for t in combinations(a,3) if sum(t)==0}
    assert set(map(tuple,three_sum(a)))==ref''',
'三数和沿用有序消元并按固定值唯一枚举。容器丢弃的短端点与任何更近端点配对，宽度更小、高度不大于已用短板，因此不优于刚检查的容器。','三数和 O(n²) 时间及 O(n) 排序辅助空间，不计答案；容器 O(n) 时间、O(1) 空间。')

add(28, '固定窗口长度不变时，每次只移除旧左端、加入新右端。区间和由重算 k 项变为更新两项。字符排列窗口则维护频次差：所有字符差都为零才表示两个多重集合相同；本章用Counter直接比较以突出概念，固定字母表下比较成本为常数。',
'''from collections import Counter

def max_average(nums,k):
    if not 1<=k<=len(nums): raise ValueError('requires 1 <= k <= len(nums)')
    total=sum(nums[:k]); best=total
    for right in range(k,len(nums)):
        total+=nums[right]-nums[right-k]
        best=max(best,total)
    return best/k

def check_inclusion(s1,s2):
    k=len(s1)
    if k==0: return True
    if k>len(s2): return False
    need=Counter(s1); have=Counter(s2[:k])
    if need==have: return True
    for right in range(k,len(s2)):
        have[s2[right]]+=1
        old=s2[right-k]; have[old]-=1
        if have[old]==0: del have[old]
        if have==need: return True
    return False
''',
'''a=[1,12,-5,-6,50,3]; k=4
show_table(['左端','窗口','窗口和','平均值'],[(l,a[l:l+k],sum(a[l:l+k]),sum(a[l:l+k])/k) for l in range(len(a)-k+1)])''',
'''import math
assert math.isclose(max_average([1,12,-5,-6,50,3],4),12.75)
assert max_average([3,-1],1)==3
assert max_average([3,-1],2)==1
assert check_inclusion('ab','eidbaooo')
assert not check_inclusion('ab','eidboaoo')
assert check_inclusion('','abc')
from itertools import product
for s in map(''.join,product('ab',repeat=5)):
    for p in ['a','ab','aa','aba']:
        assert check_inclusion(p,s)==any(sorted(s[i:i+len(p)])==sorted(p) for i in range(len(s)-len(p)+1))''',
'窗口由原窗口删除恰好一个离开元素并加入恰好一个新元素，因此聚合量始终对应当前位置。相同长度的字符频次完全相同等价于排列关系。','数值窗口 O(n) 时间、O(1) 空间；字符版 O(nσ) 时间、O(σ) 空间，σ为比较的不同字符数；固定字母表视为 O(n)。')

add(29, '可变窗口不是看到连续子串就能套。需要明确收缩何时恢复合法性。最长无重复子串在出现重复时不断移除左端；最短覆盖在满足目标计数时尽可能收缩并记录答案。两个问题的“何时更新答案”相反。最短覆盖必须计入目标重复字符，而非只计字符种类。',
'''from collections import Counter

def length_of_longest_substring(s):
    counts=Counter(); left=best=0
    for right,c in enumerate(s):
        counts[c]+=1
        while counts[c]>1:
            counts[s[left]]-=1; left+=1
        best=max(best,right-left+1)
    return best

def min_window(s,t):
    if not t: return ''
    need=Counter(t); missing=len(t); left=0; best=None
    for right,c in enumerate(s):
        if need[c]>0: missing-=1
        need[c]-=1
        while missing==0:
            if best is None or right-left+1<best[1]-best[0]: best=(left,right+1)
            old=s[left]; need[old]+=1; left+=1
            if need[old]>0: missing+=1
    return '' if best is None else s[best[0]:best[1]]
''',
'''s='abcaac'; counts=Counter(); left=0; rows=[]
for right,c in enumerate(s):
    counts[c]+=1
    while counts[c]>1:
        counts[s[left]]-=1; left+=1
    rows.append((left,right,s[left:right+1],right-left+1))
show_table(['left','right','合法窗口','长度'],rows)''',
'''assert length_of_longest_substring('abcabcbb')==3
assert length_of_longest_substring('')==0
assert min_window('ADOBECODEBANC','ABC')=='BANC'
assert min_window('a','aa')==''
from itertools import product
for n in range(6):
    for s in map(''.join,product('ab',repeat=n)):
        ref=max((r-l for l in range(n+1) for r in range(l,n+1) if len(set(s[l:r]))==r-l),default=0)
        assert length_of_longest_substring(s)==ref
        for t in ['a','ab','aa','bba']:
            candidates=[s[l:r] for l in range(n) for r in range(l+1,n+1) if not (Counter(t)-Counter(s[l:r]))]
            expected=min(candidates,key=len) if candidates else ''
            ans=min_window(s,t)
            assert len(ans)==len(expected)
            if ans: assert not (Counter(t)-Counter(ans))''',
'每个右端点只向前走，左端点也不回退。无重复窗口收缩后是该右端点的最长合法后缀；覆盖窗口循环检查了该右端点所有可覆盖的左端位置，保留最短者。','平均 O(|s|+|t|) 时间、O(σ) 计数空间；保存最佳索引避免循环内复制答案。')

add(30, '“恰好 k 种”不是便于直接维持的单调约束，但“至多 k 种”对删掉左端是单调的。固定右端点，合法窗口最左位置为 left，则以此右端结束的合法非空子数组有 right−left+1 个。再用两个嵌套集合的计数相减。\n\n$$\n\\#(=k)=\\#(\\leq k)-\\#(\\leq k-1).\n$$',
'''from collections import defaultdict

def at_most_k_distinct(nums,k):
    if k<0: return 0
    counts=defaultdict(int); left=answer=0
    for right,x in enumerate(nums):
        counts[x]+=1
        while len(counts)>k:
            old=nums[left]; counts[old]-=1
            if counts[old]==0: del counts[old]
            left+=1
        answer+=right-left+1
    return answer

def exactly_k_distinct(nums,k):
    if k<=0: return 0
    return at_most_k_distinct(nums,k)-at_most_k_distinct(nums,k-1)
''',
'''a=[1,2,1,2,3]
show_table(['k','至多k','至多k−1','恰好k'],[(k,at_most_k_distinct(a,k),at_most_k_distinct(a,k-1),exactly_k_distinct(a,k)) for k in range(1,5)])''',
'''assert exactly_k_distinct([1,2,1,2,3],2)==7
assert exactly_k_distinct([1,2],0)==0
from itertools import product
for n in range(7):
    for a in product([0,1,2],repeat=n):
        for k in range(4):
            ref=sum(len(set(a[l:r]))==k for l in range(n) for r in range(l+1,n+1))
            assert exactly_k_distinct(a,k)==ref''',
'移除左端不会增加种类数，故最小合法left之后的所有起点都合法；更早起点均被证明非法。每个非空子数组按唯一右端点计数一次。','平均 O(n) 时间、O(k+1) 窗口计数空间；一般可写 O(u)。')

add(31, '区间求和反复查询时，先保存每个位置前的累计值。采用半开区间 [l,r)，让空区间和、整段和和长度 r−l 保持统一。除自身乘积不能在含零时直接除总乘积；用左侧乘积与右侧乘积相乘，不需要除法。\n\n$$\nP[0]=0,\\quad P[i+1]=P[i]+a_i,\\quad S(l,r)=P[r]-P[l].\n$$',
'''class PrefixSum:
    def __init__(self,nums):
        self.prefix=[0]
        for x in nums: self.prefix.append(self.prefix[-1]+x)
    def query(self,left,right):
        if not 0<=left<=right<len(self.prefix): raise IndexError('invalid half-open interval')
        return self.prefix[right]-self.prefix[left]

def product_except_self(nums):
    answer=[1]*len(nums); product=1
    for i,x in enumerate(nums):
        answer[i]=product; product*=x
    product=1
    for i in range(len(nums)-1,-1,-1):
        answer[i]*=product; product*=nums[i]
    return answer
''',
'''a=[1,2,3,4]; p=PrefixSum(a)
show_table(['位置i','P[i]','前缀区间'],[(i,v,f'[0,{i})') for i,v in enumerate(p.prefix)])
show_table(['输入','除自身乘积'],[(a,product_except_self(a)),([0,2,3],product_except_self([0,2,3]))])''',
'''p=PrefixSum([1,2,3]); assert p.query(1,3)==5 and p.query(2,2)==0
assert product_except_self([1,2,3,4])==[24,12,8,6]
assert product_except_self([0,2,3])==[6,0,0]
assert product_except_self([0,2,0])==[0,0,0]
assert product_except_self([])==[]
for l in range(4):
    for r in range(l,4): assert p.query(l,r)==sum([1,2,3][l:r])''',
'两前缀相减取消共同的[0,l)部分。乘积首遍记录严格左侧，逆遍乘严格右侧，两部分互不重叠且恰好覆盖除当前位置之外的全部索引。','前缀构建 O(n)、查询 O(1)、空间 O(n)；乘积 O(n) 时间、O(1) 辅助空间（不计输出）。')

add(32, '区间和为 k 等价于两个前缀的差为 k。扫描当前前缀 P 时，查询以前出现过多少次 P−k；初始前缀零必须放入字典，否则漏掉从数组开头开始的区间。连续子数组和能被 k 整除则比较前缀余数，且要保存最早索引以检查长度至少为2。教学扩展 k=0 表示区间和必须为0。',
'''from collections import defaultdict

def subarray_sum(nums,k):
    counts=defaultdict(int,{0:1}); prefix=answer=0
    for x in nums:
        prefix+=x
        answer+=counts[prefix-k]
        counts[prefix]+=1
    return answer

def check_subarray_sum(nums,k):
    first={0:-1}; prefix=0
    for i,x in enumerate(nums):
        prefix+=x
        key=prefix%abs(k) if k else prefix
        if key in first:
            if i-first[key]>=2: return True
        else: first[key]=i
    return False
''',
'''a=[1,-1,0]; prefix=0; seen={0:1}; rows=[]; total=0
for i,x in enumerate(a):
    prefix+=x; increment=seen.get(prefix,0); total+=increment
    rows.append((i,prefix,increment,total)); seen[prefix]=seen.get(prefix,0)+1
show_table(['i','前缀和','新增零和区间','累计'],rows)''',
'''assert subarray_sum([1,1,1],2)==2
assert subarray_sum([0,0,0],0)==6
assert check_subarray_sum([23,2,4,6,7],6)
assert not check_subarray_sum([6],6)
assert check_subarray_sum([0,0],0)
from itertools import product
for a in product([-1,0,1],repeat=5):
    for k in range(-2,3):
        assert subarray_sum(a,k)==sum(sum(a[l:r])==k for l in range(5) for r in range(l+1,6))
        ref=any((sum(a[l:r])%abs(k)==0 if k else sum(a[l:r])==0) for l in range(5) for r in range(l+2,6))
        assert check_subarray_sum(a,k)==ref''',
'查询时字典只包含严格更早的前缀，因此不会把长度0区间计入。相同余数等价于差是k的倍数；最早前缀给出最大可能间距。','平均 O(n) 时间、O(n) 空间；余数版非零k时不同余数至多 |k| 个。')

add(33, '二维前缀同时复用行方向与列方向的累计和，但左上重叠区被算了两次，必须减去一次。为边界补零行和零列后，所有矩形查询都能统一为四项容斥，避免为贴边区域写特殊分支。所有query参数采用半开区间。',
'''class PrefixSum2D:
    def __init__(self,mat):
        self.rows=len(mat); self.cols=len(mat[0]) if mat else 0
        self.p=[[0]*(self.cols+1) for _ in range(self.rows+1)]
        for i in range(self.rows):
            for j in range(self.cols):
                self.p[i+1][j+1]=mat[i][j]+self.p[i][j+1]+self.p[i+1][j]-self.p[i][j]
    def query(self,r1,c1,r2,c2):
        if not (0<=r1<=r2<=self.rows and 0<=c1<=c2<=self.cols): raise IndexError('invalid rectangle')
        p=self.p
        return p[r2][c2]-p[r1][c2]-p[r2][c1]+p[r1][c1]

def matrix_block_sum(mat,k):
    p=PrefixSum2D(mat)
    return [[p.query(max(0,i-k),max(0,j-k),min(p.rows,i+k+1),min(p.cols,j+k+1))
             for j in range(p.cols)] for i in range(p.rows)]
''',
'''m=[[1,2],[3,4]]; p=PrefixSum2D(m)
show_table(['前缀表行','内容'],list(enumerate(p.p)))
show_table(['半开矩形','查询和'], [((r1,c1,r2,c2),p.query(r1,c1,r2,c2)) for r1,c1,r2,c2 in [(0,0,2,2),(1,1,2,2),(0,1,2,2)]])''',
'''p=PrefixSum2D([[1,2],[3,4]])
assert p.query(0,0,2,2)==10 and p.query(1,1,2,2)==4
assert matrix_block_sum([[1,2],[3,4]],3)==[[10,10],[10,10]]
from random import Random
rng=Random(33)
for rows in range(1,5):
    for cols in range(1,5):
        m=[[rng.randrange(-3,4) for _ in range(cols)] for _ in range(rows)]
        p=PrefixSum2D(m)
        for a in range(rows+1):
            for b in range(a,rows+1):
                for c in range(cols+1):
                    for d in range(c,cols+1):
                        assert p.query(a,c,b,d)==sum(m[i][j] for i in range(a,b) for j in range(c,d))''',
'用集合容斥看四个前缀：目标外的上方与左方各减一次，它们共同左上区域被减两次，再加回一次。','构建 O(RC) 时间与空间；查询 O(1)；整张block sum输出 O(RC)。')

add(34, '一次区间加法对相邻差分只影响两处：在开始处启动增量，在结束后一位取消增量。扫描差分的前缀就重建每个位置的总增量。为避免端点歧义，本章更新接口统一采用零基半开 [l,r)；航班题的一基闭区间 [first,last] 转成 [first−1,last)。',
'''def apply_range_add(n,updates):
    diff=[0]*(n+1)
    for left,right,value in updates:
        if not 0<=left<=right<=n: raise IndexError('invalid range')
        diff[left]+=value; diff[right]-=value
    answer=[]; total=0
    for i in range(n):
        total+=diff[i]; answer.append(total)
    return answer

def car_pooling(trips,capacity):
    events={}
    for passengers,start,end in trips:
        events[start]=events.get(start,0)+passengers
        events[end]=events.get(end,0)-passengers
    load=0
    for position in sorted(events):
        load+=events[position]
        if load>capacity: return False
    return True
''',
'''updates=[(0,2,10),(1,3,20),(1,5,25)]; diff=[0]*6
for l,r,v in updates: diff[l]+=v; diff[r]-=v
out=apply_range_add(5,updates)
show_table(['位置','差分事件','重建值'],[(i,diff[i],out[i] if i<5 else '边界哨兵') for i in range(6)])''',
'''bookings=[[1,2,10],[2,3,20],[2,5,25]]
assert apply_range_add(5,[(a-1,b,v) for a,b,v in bookings])==[10,55,45,25,25]
assert car_pooling([[2,1,5],[3,3,7]],4) is False
assert car_pooling([[2,1,5],[3,5,7]],3) is True
from random import Random
rng=Random(34)
for n in range(1,10):
    updates=[]; ref=[0]*n
    for _ in range(30):
        l=rng.randrange(n+1); r=rng.randrange(l,n+1); v=rng.randrange(-5,6)
        updates.append((l,r,v))
        for i in range(l,r): ref[i]+=v
    assert apply_range_add(n,updates)==ref''',
'每个更新的前缀累积在l前为0、[l,r)为value、r后归零；线性叠加得到全部更新。拼车同站下车与上车可以同时汇总，区间按半开占用处理。','差分 O(n+q) 时间、O(n) 空间；稀疏拼车事件排序 O(q log q)、O(q) 空间。')

add(35, '区间合并先按左端排序。当前段的右端是已合并区间的最远右端；新区间开始于它之后才需要另开一段。闭区间同端点相接也算相交。两个各自有序互不重叠的列表求交时，较早结束的区间以后不可能再与当前另一区间产生新交集，应移动它。',
'''def merge_intervals(intervals):
    merged=[]
    for left,right in sorted(intervals):
        if left>right: raise ValueError('reversed interval')
        if not merged or left>merged[-1][1]: merged.append([left,right])
        else: merged[-1][1]=max(merged[-1][1],right)
    return merged

def insert_interval(intervals,new):
    return merge_intervals([*intervals,list(new)])

def interval_intersection(a,b):
    i=j=0; answer=[]
    while i<len(a) and j<len(b):
        left=max(a[i][0],b[j][0]); right=min(a[i][1],b[j][1])
        if left<=right: answer.append([left,right])
        if a[i][1]<b[j][1]: i+=1
        else: j+=1
    return answer
''',
'''a=[[1,3],[2,6],[8,10],[10,12]]
show_table(['处理前缀','合并后'],[(a[:i],merge_intervals(a[:i])) for i in range(1,len(a)+1)])''',
'''assert merge_intervals([[1,3],[2,6],[8,10]])==[[1,6],[8,10]]
assert merge_intervals([[1,4],[2,3],[4,5]])==[[1,5]]
assert insert_interval([[1,2],[5,7]],[2,6])==[[1,7]]
assert interval_intersection([[1,2]],[[2,3]])==[[2,2]]
from random import Random
rng=Random(35)
for _ in range(100):
    a=[sorted([rng.randrange(6),rng.randrange(6)]) for _ in range(5)]
    m=merge_intervals(a)
    assert all(m[i][1]<m[i+1][0] for i in range(len(m)-1))
    for x in [i/2 for i in range(11)]:
        assert any(l<=x<=r for l,r in a)==any(l<=x<=r for l,r in m)''',
'排序后未来区间的左端不会回退，已经封闭的段不可能被后续桥接。求交时较早结束者与之后所有另一侧区间也不会再相交，移动安全。','合并与本章简洁插入 O(n log n)，已排序输入可把插入进一步做成 O(n)；交集 O(n+m)，输出空间与答案大小一致。')

add(36, '扫描线把区间变成开始与结束事件，活动数的最大值就是最大重叠。闭区间在同一坐标应先加开始、再减结束；半开区间则相反。端点顺序不是实现细节，而是区间语义的一部分。将区间分到互不重叠组时，最大重叠给出必要下界，按时间释放旧组可达到该下界。',
'''def max_overlap(intervals,closed=True):
    events=[]
    for left,right in intervals:
        if left>right: raise ValueError('reversed interval')
        if not closed and left==right: continue
        events.append((left,1)); events.append((right,-1))
    events.sort(key=lambda event:(event[0],-event[1] if closed else event[1]))
    active=best=0
    for _,delta in events:
        active+=delta; best=max(best,active)
    return best

def min_groups(intervals):
    return max_overlap(intervals,closed=True)
''',
'''a=[[1,2],[2,3],[2,2]]
show_table(['区间语义','最大重叠'],[('闭区间',max_overlap(a,True)),('半开区间',max_overlap(a,False))])
events=sorted([(x,d) for l,r in a for x,d in [(l,1),(r,-1)]],key=lambda z:(z[0],-z[1]))
rows=[]; active=0
for x,d in events:
    active+=d; rows.append((x,d,active))
show_table(['坐标','事件增量','活动区间数'],rows)''',
'''assert max_overlap([[1,2],[2,3]],True)==2
assert max_overlap([[1,2],[2,3]],False)==1
assert min_groups([[1,10],[2,9],[3,8]])==3
assert max_overlap([],True)==0
from random import Random
rng=Random(36)
for _ in range(200):
    a=[sorted([rng.randrange(5),rng.randrange(5)]) for _ in range(5)]
    points=[i/2 for i in range(9)]
    assert max_overlap(a,True)==max(sum(l<=x<=r for l,r in a) for x in points)
    assert max_overlap(a,False)==max(sum(l<=x<r for l,r in a) for x in points)''',
'活动数在相邻事件间不变，只需检查事件位置的合法中间状态。达到最大重叠的那一刻所有区间必须分组不同；按开始时间复用最早空出的组不会超过同时活动数。','O(n log n) 排序时间、O(n) 事件空间。')
