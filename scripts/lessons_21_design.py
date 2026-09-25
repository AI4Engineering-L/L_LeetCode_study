from course_builder import add
from lessons_06_trees import TREE

LINKED='''class _CacheNode:
    def __init__(self,key=None,value=None): self.key=key; self.value=value; self.frequency=1; self.prev=self.next=None

class _NodeList:
    def __init__(self):
        self.head=_CacheNode(); self.tail=_CacheNode(); self.head.next=self.tail; self.tail.prev=self.head; self.size=0
    def append(self,node):
        previous=self.tail.prev; previous.next=node; node.prev=previous; node.next=self.tail; self.tail.prev=node; self.size+=1
    def remove(self,node):
        node.prev.next=node.next; node.next.prev=node.prev; node.prev=node.next=None; self.size-=1
    def pop_left(self):
        if not self.size: raise IndexError('empty node list')
        node=self.head.next; self.remove(node); return node
'''
LRU_CODE='''class LRUCache:
    def __init__(self,capacity):
        if capacity<0: raise ValueError('nonnegative capacity required')
        self.capacity=capacity; self.nodes={}; self.order=_NodeList()
    def _touch(self,node): self.order.remove(node); self.order.append(node)
    def get(self,key):
        if key not in self.nodes: return -1
        node=self.nodes[key]; self._touch(node); return node.value
    def put(self,key,value):
        if key in self.nodes:
            node=self.nodes[key]; node.value=value; self._touch(node); return
        if not self.capacity: return
        if len(self.nodes)==self.capacity:
            victim=self.order.pop_left(); del self.nodes[victim.key]
        node=_CacheNode(key,value); self.nodes[key]=node; self.order.append(node)
'''
LFU_CODE='''class LFUCache:
    def __init__(self,capacity):
        if capacity<0: raise ValueError('nonnegative capacity required')
        self.capacity=capacity; self.nodes={}; self.buckets={}; self.minimum=0
    def _touch(self,node):
        old=node.frequency; bucket=self.buckets[old]; bucket.remove(node)
        if not bucket.size:
            del self.buckets[old]
            if self.minimum==old: self.minimum+=1
        node.frequency+=1; self.buckets.setdefault(node.frequency,_NodeList()).append(node)
    def get(self,key):
        if key not in self.nodes: return -1
        node=self.nodes[key]; self._touch(node); return node.value
    def put(self,key,value):
        if key in self.nodes:
            node=self.nodes[key]; node.value=value; self._touch(node); return
        if not self.capacity: return
        if len(self.nodes)==self.capacity:
            bucket=self.buckets[self.minimum]; victim=bucket.pop_left(); del self.nodes[victim.key]
            if not bucket.size: del self.buckets[self.minimum]
        node=_CacheNode(key,value); self.nodes[key]=node; self.buckets.setdefault(1,_NodeList()).append(node); self.minimum=1
'''
add(147,'哈希表负责按key定位，双向链表负责O(1)移动与淘汰，二者不能各保存一份独立状态。LRU维护访问先后；LFU先按频率选桶，再在桶内按LRU打破并列。更新已有key也算一次访问。容量为0时put不保存任何节点。',LINKED+LRU_CODE+LFU_CODE,
'''cache=LRUCache(2); trace=[]
for op in [('put',1,1),('put',2,2),('get',1),('put',3,3),('get',2)]:
    result=getattr(cache,op[0])(*op[1:]); keys=[]; node=cache.order.head.next
    while node is not cache.order.tail: keys.append(node.key); node=node.next
    trace.append((op,result,keys))
show_table(['操作','返回','LRU→MRU顺序'],trace)''',
'''from collections import OrderedDict
from random import Random
rng=Random(147)
def inspect(bucket):
    nodes=[]; previous=bucket.head; node=previous.next
    while node is not bucket.tail:
        assert node.prev is previous and previous.next is node
        assert node not in nodes; nodes.append(node); previous,node=node,node.next
    assert bucket.tail.prev is previous and bucket.size==len(nodes)
    backward=[]; node=bucket.tail.prev
    while node is not bucket.head: backward.append(node); node=node.prev
    assert backward==nodes[::-1]
    return nodes
for capacity in range(5):
    lru=LRUCache(capacity); slow=OrderedDict(); lfu=LFUCache(capacity); reference={}; clock=0
    for _ in range(500):
        key=rng.randrange(8); clock+=1
        if rng.randrange(2):
            value=rng.randrange(100); lru.put(key,value); lfu.put(key,value)
            if capacity:
                if key in slow: del slow[key]
                elif len(slow)==capacity: slow.popitem(last=False)
                slow[key]=value
                if key in reference: old,f,t=reference[key]; reference[key]=(value,f+1,clock)
                else:
                    if len(reference)==capacity: del reference[min(reference,key=lambda k:(reference[k][1],reference[k][2]))]
                    reference[key]=(value,1,clock)
        else:
            expected=slow.get(key,-1)
            if key in slow: slow.move_to_end(key)
            assert lru.get(key)==expected
            expected=reference[key][0] if key in reference else -1
            if key in reference:
                value,f,t=reference[key]; reference[key]=(value,f+1,clock)
            assert lfu.get(key)==expected
        assert [node.key for node in inspect(lru.order)]==list(slow)
        assert set(lru.nodes.values())==set(inspect(lru.order))
        seen=[]
        for frequency,bucket in lfu.buckets.items():
            nodes=inspect(bucket); seen.extend(nodes); assert all(node.frequency==frequency for node in nodes)
            expected=sorted((k for k in reference if reference[k][1]==frequency),key=lambda k:reference[k][2])
            assert [node.key for node in nodes]==expected
        assert set(seen)==set(lfu.nodes.values()) and len(seen)==len(lfu.nodes)==len(reference)
        if reference: assert lfu.minimum==min(v[1] for v in reference.values())''',
'哈希中的每个活节点恰出现于一条链表，移动只重连相邻指针，不创建重复节点。LRU访问移到末端，所以首端始终最久未访问。LFU访问仅从f桶移动到f+1桶；若最小桶因此变空，刚移动的节点保证新的最小频率为f+1。新节点频率1使minimum重置为1。',
'哈希操作平均O(1)，所有链表操作O(1)，所以每次get/put平均O(1)，空间O(capacity)。这是顺序调用接口，未提供并发访问锁；测试同时检查返回值和映射/双向链表结构。')

RANDOM_SET='''from random import Random

class RandomizedSet:
    def __init__(self,rng=None): self.values=[]; self.position={}; self.rng=Random() if rng is None else rng
    def insert(self,value):
        if value in self.position: return False
        self.position[value]=len(self.values); self.values.append(value); return True
    def remove(self,value):
        if value not in self.position: return False
        index=self.position.pop(value); last=self.values.pop()
        if index<len(self.values): self.values[index]=last; self.position[last]=index
        return True
    def getRandom(self):
        if not self.values: raise IndexError('empty randomized set')
        return self.values[self.rng.randrange(len(self.values))]

class RandomizedCollection:
    def __init__(self,rng=None): self.values=[]; self.positions={}; self.rng=Random() if rng is None else rng
    def insert(self,value):
        first=value not in self.positions
        self.positions.setdefault(value,set()).add(len(self.values)); self.values.append(value); return first
    def remove(self,value):
        if value not in self.positions: return False
        index=self.positions[value].pop(); last=self.values[-1]; last_index=len(self.values)-1
        self.values[index]=last; self.positions[last].add(index); self.positions[last].discard(last_index); self.values.pop()
        if not self.positions[value]: del self.positions[value]
        return True
    def getRandom(self):
        if not self.values: raise IndexError('empty randomized collection')
        return self.values[self.rng.randrange(len(self.values))]
'''
add(148,'随机取样要求能O(1)访问随机下标，快速删除要求能O(1)定位元素。用数组加哈希映射，把要删除的槽位用末项填补，再更新末项的位置。允许重复值时，value对应的不是单个下标，而是一组下标；特别要检查被移来的末项与被删值相同的情况。',RANDOM_SET,
'''collection=RandomizedCollection(Random(148)); rows=[]
for op,value in [('insert',1),('insert',1),('insert',2),('remove',1),('remove',2)]:
    result=getattr(collection,op)(value); rows.append((op,value,result,collection.values[:],{k:sorted(v) for k,v in collection.positions.items()}))
show_table(['操作','值','返回','数组','索引集合'],rows)''',
'''from collections import Counter
rng=Random(148); a=RandomizedSet(Random(1)); b=RandomizedCollection(Random(1)); ref=set(); multiset=Counter()
for _ in range(1200):
    x=rng.randrange(10)
    if rng.randrange(2):
        assert a.insert(x)==(x not in ref); ref.add(x)
        assert b.insert(x)==(multiset[x]==0); multiset[x]+=1
    else:
        assert a.remove(x)==(x in ref); ref.discard(x)
        assert b.remove(x)==(multiset[x]>0)
        if multiset[x]: multiset[x]-=1
        if multiset[x]==0: multiset.pop(x,None)
    assert set(a.values)==ref and len(a.values)==len(ref)
    assert a.position=={x:i for i,x in enumerate(a.values)}
    assert Counter(b.values)==multiset
    assert b.positions=={x:{i for i,y in enumerate(b.values) if y==x} for x in multiset}
    if ref: assert a.getRandom() in ref
    if multiset: assert b.getRandom() in multiset
class Tickets:
    def __init__(self): self.next=0
    def randrange(self,n): result=self.next; self.next+=1; return result
b=RandomizedCollection(Tickets())
for x in [1,1,2]: b.insert(x)
assert Counter(b.getRandom() for _ in range(3))==Counter({1:2,2:1})''',
'交换删除只改变一个保留元素的位置，因此仅需常数个映射更新；数组始终紧凑，均匀随机下标等价于均匀随机元素实例。多重集合中某值被选中概率正比于出现次数，而不是对不同值均匀。索引集合增删顺序处理末项同值和删除末槽两种边界。',
'插入、删除与随机取样平均/均摊O(1)，空间O(元素实例数)。getRandom在空结构上抛IndexError；不通过返回任意默认值掩盖非法调用。')

ITERATORS='''class BSTIterator:
    def __init__(self,root): self.stack=[]; self._push_left(root)
    def _push_left(self,node):
        while node: self.stack.append(node); node=node.left
    def hasNext(self): return bool(self.stack)
    def next(self):
        if not self.stack: raise StopIteration
        node=self.stack.pop(); self._push_left(node.right); return node.val
    def __iter__(self): return self
    __next__=next

class PeekingIterator:
    def __init__(self,iterable): self.iterator=iter(iterable); self.empty=object(); self.cached=self.empty
    def _fill(self):
        if self.cached is self.empty:
            try: self.cached=next(self.iterator)
            except StopIteration: return False
        return True
    def hasNext(self): return self._fill()
    def peek(self):
        if not self._fill(): raise StopIteration
        return self.cached
    def next(self):
        value=self.peek(); self.cached=self.empty; return value
    def __iter__(self): return self
    __next__=next

class NestedIterator:
    def __init__(self,nested_list):
        if not isinstance(nested_list,list): raise TypeError('nested Python list required')
        self.stack=[iter(nested_list)]; self.empty=object(); self.cached=self.empty
    def _fill(self):
        if self.cached is not self.empty: return True
        while self.stack:
            try: value=next(self.stack[-1])
            except StopIteration: self.stack.pop(); continue
            if isinstance(value,int): self.cached=value; return True
            if not isinstance(value,list): raise TypeError('only integers and lists are supported')
            self.stack.append(iter(value))
        return False
    def hasNext(self): return self._fill()
    def next(self):
        if not self._fill(): raise StopIteration
        value=self.cached; self.cached=self.empty; return value
    def __iter__(self): return self
    __next__=next
'''
add(149,'迭代器不必预先生成全部输出。BST保留尚未访问的左链；peek只缓存一个已取出但尚未交付的值；嵌套列表用迭代器栈保存当前展开路径。hasNext允许整理内部状态，但重复调用不能跳过下一个值。用唯一哨兵区分“没有缓存”与真正的None值。',TREE+ITERATORS,
'''it=PeekingIterator([1,None,3]); rows=[]
while it.hasNext(): rows.append((it.peek(),it.peek(),it.next()))
show_table(['第一次peek','第二次peek','真正next'],rows)
print('嵌套输出',list(NestedIterator([[],[1,[2,[]]],3])))''',
'''assert list(BSTIterator(tree_from_level([7,3,15,None,None,9,20])))==[3,7,9,15,20]
assert list(BSTIterator(None))==[]
it=PeekingIterator([None,0,False]); assert it.peek() is None and it.peek() is None and it.next() is None
assert list(it)==[0,False] and not it.hasNext()
for data,expected in [([],[]),([[],[[]]],[]),([1,[4,[6]]],[1,4,6]),([[],[1],[],[2,[3]]],[1,2,3])]:
    it=NestedIterator(data); out=[]
    while it.hasNext(): assert it.hasNext(); out.append(it.next())
    assert out==expected
    try: it.next()
    except StopIteration: pass
    else: raise AssertionError('exhaustion must raise StopIteration')
nested=9
for _ in range(1500): nested=[nested]
assert list(NestedIterator(nested))==[9]
root=TreeNode(0); node=root
for value in range(1,1500): node.right=TreeNode(value); node=node.right
assert list(BSTIterator(root))==list(range(1500))''',
'BST栈顶始终是下一中序节点，弹出后只需处理其右子树左链。peek缓存交付前的唯一值，不改变可见输出顺序。嵌套迭代器把递归调用栈显式保存，每个列表元素只取出一次；空列表被跳过但整数不会被hasNext重复消耗。',
'BST构建O(h)，完整遍历O(n)，每次next均摊O(1)，空间O(h)。嵌套结构总耗时按包括空列表在内的结构节点数O(N)，辅助O(深度)。本章NestedIterator使用原生Python嵌套列表；平台NestedInteger需替换取整数/子列表访问器，未声称该签名可原样提交。')

SNAPSHOT='''from bisect import bisect_right

class SnapshotArray:
    def __init__(self,length):
        if length<0: raise ValueError('nonnegative length required')
        self.history=[[(0,0)] for _ in range(length)]; self.current=0
    def _check_index(self,index):
        if not 0<=index<len(self.history): raise IndexError('index outside snapshot array')
    def set(self,index,val):
        self._check_index(index); history=self.history[index]
        if history[-1][0]==self.current: history[-1]=(self.current,val)
        else: history.append((self.current,val))
    def snap(self):
        result=self.current; self.current+=1; return result
    def get(self,index,snap_id):
        self._check_index(index)
        if not 0<=snap_id<self.current: raise ValueError('snapshot must already be committed')
        history=self.history[index]; position=bisect_right(history,snap_id,key=lambda item:item[0])-1
        return history[position][1]
'''
add(150,'每次snap复制整个数组代价很大，且多数位置没有变化。按索引记录稀疏版本历史：一次快照只生成新版本号，查询时找不晚于目标版本的最后一条修改。同一未提交版本内多次set只保留最终值。它支持单点历史查询，不自动提供高效的历史区间和。',SNAPSHOT,
'''snapshots=SnapshotArray(3); snapshots.set(0,5); first=snapshots.snap(); snapshots.set(0,6); snapshots.set(0,7); second=snapshots.snap()
show_table(['索引','稀疏版本记录','快照0值','快照1值'],[(i,h,snapshots.get(i,first),snapshots.get(i,second)) for i,h in enumerate(snapshots.history)])''',
'''array=SnapshotArray(3); assert array.snap()==0 and array.get(1,0)==0
array.set(0,5); array.set(0,6); sid=array.snap(); assert array.get(0,sid)==6 and array.get(0,0)==0
array.set(0,8); assert array.get(0,sid)==6
from random import Random
rng=Random(150); fast=SnapshotArray(7); values=[0]*7; copies=[]
for _ in range(900):
    op=rng.randrange(3)
    if op==0:
        i=rng.randrange(7); value=rng.randrange(-100,101); fast.set(i,value); values[i]=value
    elif op==1:
        assert fast.snap()==len(copies); copies.append(values[:])
    elif copies:
        i=rng.randrange(7); version=rng.randrange(len(copies)); assert fast.get(i,version)==copies[version][i]
for version,values in enumerate(copies):
    for i,x in enumerate(values): assert fast.get(i,version)==x
assert all(all(a[0]<b[0] for a,b in zip(history,history[1:])) for history in fast.history)''',
'一个位置在两次修改之间保持常值，因此历史查询等价于时间前驱查询。版本号单调，二分右界减一得到最后一个version≤snap_id的记录。同版本覆盖只影响尚未提交的状态；已提交版本记录不会被后续set覆盖。',
'set均摊O(1)，snap O(1)，get O(log 该位置修改版本数)，空间O(长度+保留修改数)。持久化线段树可用路径复制支持历史区间查询，但属于拓展；本章只实现稀疏单点历史。Python要求支持bisect的key参数（3.10及以上）。')

TIMELINE='''from bisect import bisect_right
from heapq import heapify,heappop,heappush

class TimeMap:
    def __init__(self): self.history={}
    def set(self,key,value,timestamp):
        history=self.history.setdefault(key,[])
        if history and timestamp<=history[-1][0]: raise ValueError('timestamps per key must strictly increase')
        history.append((timestamp,value))
    def get(self,key,timestamp):
        history=self.history.get(key,[]); index=bisect_right(history,timestamp,key=lambda item:item[0])-1
        return history[index][1] if index>=0 else ''

class Twitter:
    def __init__(self): self.clock=0; self.posts={}; self.following={}
    def postTweet(self,userId,tweetId):
        self.clock+=1; self.posts.setdefault(userId,[]).append((self.clock,tweetId))
    def follow(self,followerId,followeeId):
        if followerId!=followeeId: self.following.setdefault(followerId,set()).add(followeeId)
    def unfollow(self,followerId,followeeId):
        self.following.get(followerId,set()).discard(followeeId)
    def getNewsFeed(self,userId):
        users=self.following.get(userId,set())|{userId}; heap=[]
        for user in users:
            posts=self.posts.get(user,[])
            if posts:
                time,tweet=posts[-1]; heap.append((-time,user,len(posts)-1,tweet))
        heapify(heap); answer=[]
        while heap and len(answer)<10:
            negative,user,index,tweet=heappop(heap); answer.append(tweet)
            if index:
                time,tweet=self.posts[user][index-1]; heappush(heap,(-time,user,index-1,tweet))
        return answer
'''
add(151,'时间键值把每个key的修改日志保持有序，get查询时间前驱。消息流不应每次拼接全部历史并全量排序：每个关注用户的日志已经有序，可以从各自末项做K路归并，只取前10条。关注关系与消息日志分开存储，取消关注不删除历史消息。',TIMELINE,
'''service=Twitter(); service.postTweet(1,101); service.postTweet(2,201); service.follow(1,2); first=service.getNewsFeed(1); service.unfollow(1,2)
show_table(['状态','用户1消息流'],[('关注2时',first),('取消关注2后',service.getNewsFeed(1))])
times=TimeMap(); times.set('x','old',3); times.set('x','new',7)
show_table(['查询时间','返回值'],[(t,times.get('x',t)) for t in [0,3,5,7,20]])''',
'''times=TimeMap(); times.set('foo','bar',1); times.set('foo','bar2',4)
assert times.get('foo',0)=='' and times.get('foo',3)=='bar' and times.get('foo',4)=='bar2' and times.get('missing',9)==''
from random import Random
rng=Random(151); service=Twitter(); posts=[]; following={}; counter=0
for _ in range(600):
    op=rng.randrange(4); user=rng.randrange(7); other=rng.randrange(7)
    if op==0:
        counter+=1; service.postTweet(user,counter); posts.append((counter,user,counter))
    elif op==1:
        service.follow(user,other)
        if user!=other: following.setdefault(user,set()).add(other)
    elif op==2:
        service.unfollow(user,other); following.get(user,set()).discard(other)
    else:
        allowed=following.get(user,set())|{user}; expected=[tweet for time,author,tweet in reversed(posts) if author in allowed][:10]
        assert service.getNewsFeed(user)==expected
for user in range(7):
    service.follow(user,user); service.unfollow(user,user)
    allowed=following.get(user,set())|{user}
    assert service.getNewsFeed(user)==[tweet for time,author,tweet in reversed(posts) if author in allowed][:10]''',
'每个日志严格按时间增加，二分即可查找最后一次不晚于查询的修改。K路堆中保存每个来源尚未取出的最新消息，弹出的就是所有来源中的最新一条，再用该来源前一条补位。全局单调clock消除并列时间，不依赖真实机器时钟精度。',
'TimeMap追加均摊O(1)、查询O(log 每key记录数)；消息流初始化O(F)、输出最多10项O(10 log F)，F含自己及关注人数；日志空间O(消息数+关注边数)。接口按顺序调用，不包含分布式时钟或并发一致性保证。')
