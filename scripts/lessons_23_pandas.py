"""Real DataFrame operations; explicit schemas and SQL cross-checks."""
from course_builder import add

PANDAS_BASE = '''import pandas as pd
from pandas.testing import assert_frame_equal

'''

P157 = PANDAS_BASE + '''def create_dataframe(student_data):
    """Rows are (student_id, age); an empty input keeps both integer columns."""
    return pd.DataFrame(student_data, columns=['student_id', 'age']).astype(
        {'student_id': 'int64', 'age': 'int64'})

def drop_duplicate_emails(customers):
    # First occurrence wins, including the first missing email.
    return customers.drop_duplicates(subset=['email'], keep='first').reset_index(drop=True)

def drop_missing_names(students):
    # An empty string is present, not a missing value.
    return students.dropna(subset=['name']).reset_index(drop=True)

def change_grade_type(students):
    """Teaching contract: nullable integer Int64 preserves missing grades."""
    result = students.copy()
    result['grade'] = result['grade'].astype('Int64')
    return result
'''
add(157,
'''表格操作首先是**数据契约**：列名是什么，缺失表示什么，重复保留哪一行，结果索引是否有意义？不能只检查屏幕上看起来相同。

从学生记录列表创建表；删除重复邮件时选定“保留首次出现”；删除缺失姓名时仅检查 `name`，不顺便删掉其他列有缺失的学生。`None`、`NaN` 由 `isna`/`dropna` 处理，空字符串则是另一种业务状态。

这里把成绩转为 Pandas 的可空整数 `Int64`，与 NumPy 非可空 `int64` 区别大小写。它能保留缺失值，却拒绝把非整数分数无声截断。每个函数返回新表，不修改输入。''',
P157,
'''raw = pd.DataFrame({'student_id':[1,2,3,4], 'name':['Li',None,'','Zhou'], 'grade':[90.0,81.0,None,75.0]})
clean = change_grade_type(drop_missing_names(raw))
show_table(['stage','rows','index','dtype'], [
    ['before', len(raw), raw.index.tolist(), str(raw.dtypes.to_dict())],
    ['after', len(clean), clean.index.tolist(), str(clean.dtypes.to_dict())]])
display(clean)
''',
'''assert_frame_equal(create_dataframe([]), pd.DataFrame({
    'student_id': pd.Series(dtype='int64'), 'age': pd.Series(dtype='int64')}))
assert_frame_equal(create_dataframe([[1,20],[2,21]]), pd.DataFrame({'student_id':[1,2],'age':[20,21]}))
customers = pd.DataFrame({'id':[3,1,2,4], 'email':['a@x','a@x',None,None]})
original = customers.copy(deep=True)
assert_frame_equal(drop_duplicate_emails(customers), customers.iloc[[0,2]].reset_index(drop=True))
assert_frame_equal(customers, original)
students = pd.DataFrame({'name':['a',None,''], 'grade':[90.0,75.0,float('nan')]})
before = students.copy(deep=True)
assert_frame_equal(drop_missing_names(students), students.iloc[[0,2]].reset_index(drop=True))
expected = pd.DataFrame({'name':['a',None,''], 'grade':pd.Series([90,75,None],dtype='Int64')})
assert_frame_equal(change_grade_type(students), expected)
assert_frame_equal(students,before)
try:
    change_grade_type(pd.DataFrame({'grade':[90.5]}))
except (TypeError, ValueError):
    pass
else:
    raise AssertionError('A fractional grade must not be silently truncated')
assert_frame_equal(drop_missing_names(students.iloc[:0]), students.iloc[:0].reset_index(drop=True))
''',
'''筛选只改变行集合；去重的输出是每个邮件等价类第一次出现的位置。显式 `reset_index` 声明旧索引不是业务主键。整数转换只改变 `grade`，转换失败是契约错误而不是填 0 的理由。''',
'''建表、筛选、类型转换对行数 n 线性；哈希去重通常期望 O(n)。结果需要 O(n) 空间；具体内部实现常数不构成算法复杂度证明。''')

P158 = PANDAS_BASE + '''def concatenate_tables(df1, df2):
    if list(df1.columns) != list(df2.columns):
        raise ValueError('Both tables must have the same ordered schema')
    return pd.concat([df1, df2], ignore_index=True)

def pivot_weather(weather):
    """One measurement per (city, month); duplicates are errors, not averages."""
    if weather.duplicated(['city', 'month']).any():
        raise ValueError('Duplicate (city, month) measurement')
    return weather.pivot(index='month', columns='city', values='temperature').sort_index().sort_index(axis=1)

def melt_sales(report):
    quarters = ['quarter_1','quarter_2','quarter_3','quarter_4']
    return report.melt(id_vars=['product'], value_vars=quarters,
                       var_name='quarter', value_name='sales').reset_index(drop=True)

def customers_without_orders(customers, orders):
    # NULL customerId does not match a real customer, just as with SQL NOT EXISTS.
    ordered_ids = orders['customerId'].dropna()
    return customers.loc[~customers['id'].isin(ordered_ids), ['name']].rename(
        columns={'name':'Customers'}).reset_index(drop=True)
'''
add(158,
'''连接不一定保持行数：一对多键连接会复制左表行，多对多甚至会产生笛卡尔式膨胀。因此先明确键的唯一性，再判断应使用 `concat`、`merge`、`pivot` 还是集合式反连接。

纵向拼表要求相同列序；宽表到长表把“季度列”变成“季度值”，四季度的 n 行变成 4n 行。`pivot` 不是聚合，重复 `(city, month)` 没有唯一温度，应报错而非擅自平均。

未下单客户用成员关系取反。右表同一客户重复下单不应复制结果，缺失的订单客户键也不能导致全部结果消失。''',
P158,
'''sales = pd.DataFrame({'product':['A','B'], 'quarter_1':[1,5], 'quarter_2':[2,6], 'quarter_3':[3,7], 'quarter_4':[4,8]})
long = melt_sales(sales)
show_table(['representation','rows','columns'], [['wide',len(sales),list(sales.columns)],['long',len(long),list(long.columns)]])
display(long)
weather = pd.DataFrame({'city':['Seoul','Paris','Seoul','Paris'], 'month':['Jan','Jan','Feb','Feb'], 'temperature':[0,5,2,7]})
display(pivot_weather(weather))
''',
'''a = pd.DataFrame({'x':[1,2], 'y':['a','b']})
b = pd.DataFrame({'x':[3], 'y':['c']})
assert_frame_equal(concatenate_tables(a,b),pd.DataFrame({'x':[1,2,3],'y':['a','b','c']}))
assert_frame_equal(concatenate_tables(a.iloc[:0],a),a)
try:
    concatenate_tables(a,b[['y','x']])
except ValueError:
    pass
else:
    raise AssertionError('Schema mismatch was accepted')
r = pd.DataFrame({'product':['A','B'], 'quarter_1':[1,5], 'quarter_2':[2,6], 'quarter_3':[3,7], 'quarter_4':[4,8]})
expected = pd.DataFrame({'product':['A','B']*4,
 'quarter':[q for q in ['quarter_1','quarter_2','quarter_3','quarter_4'] for _ in range(2)],
 'sales':[1,5,2,6,3,7,4,8]})
assert_frame_equal(melt_sales(r),expected)
assert len(melt_sales(r)) == 4*len(r)
w = pd.DataFrame({'city':['A','B','A','B'], 'month':[1,1,2,2], 'temperature':[10,20,11,21]})
expected = pd.DataFrame({'A':[10,11], 'B':[20,21]},index=pd.Index([1,2],name='month'))
expected.columns.name = 'city'
assert_frame_equal(pivot_weather(w),expected)
try:
    pivot_weather(pd.concat([w,w.iloc[:1]]))
except ValueError:
    pass
else:
    raise AssertionError('Ambiguous pivot was accepted')
customers = pd.DataFrame({'id':[1,2,3], 'name':['a','b','c']})
orders = pd.DataFrame({'customerId':[1,1,None]})
assert_frame_equal(customers_without_orders(customers,orders),pd.DataFrame({'Customers':['b','c']}))
import sqlite3
with sqlite3.connect(':memory:') as conn:
    customers.to_sql('Customers',conn,index=False)
    orders.to_sql('Orders',conn,index=False)
    sql = pd.read_sql_query('SELECT name AS Customers FROM Customers c WHERE NOT EXISTS (SELECT 1 FROM Orders o WHERE o.customerId=c.id) ORDER BY c.id',conn)
assert_frame_equal(customers_without_orders(customers,orders),sql)
''',
'''反连接结果恰是不存在匹配右表键的左表行；重复右表键不改变存在性。宽长变换用 `(product, quarter)` 标识每个原单元格；唯一键前提成立时可以逆变换。''',
'''拼接、melt、哈希成员关系通常为 O(n+m)；四季度只是固定因子。pivot 的组织与排序可达 O(n log n)，存储量取决于展开后的行列组合，稀疏输入也可能产生较大的宽表。''')

P159 = PANDAS_BASE + '''from decimal import Decimal, ROUND_HALF_UP

def _round2(value):
    return float(Decimal(str(value)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))

def department_top_three_salaries(employees, departments):
    ranked = employees.copy()
    ranked['_rank'] = ranked.groupby('departmentId')['salary'].rank(method='dense', ascending=False)
    kept = ranked.loc[ranked['_rank'] <= 3].merge(
        departments.rename(columns={'id':'departmentId','name':'Department'}),
        on='departmentId',how='inner',validate='many_to_one')
    return kept.rename(columns={'name':'Employee','salary':'Salary'})[
        ['Department','Employee','Salary']].sort_values(
        ['Department','Salary','Employee'],ascending=[True,False,True]).reset_index(drop=True)

def next_day_retention(activity):
    if activity.empty:
        return 0.0
    days = activity[['player_id','event_date']].copy()
    days['event_date'] = pd.to_datetime(days['event_date']).dt.normalize()
    days = days.drop_duplicates()
    first = days.groupby('player_id',as_index=False)['event_date'].min()
    first['event_date'] += pd.Timedelta(days=1)
    hits = first.merge(days,on=['player_id','event_date'],validate='one_to_one')
    return _round2(Decimal(len(hits)) / Decimal(len(first)))

def normalize_names(users):
    """ASCII alphabetic names; retain schema and sort by user_id."""
    result = users.copy()
    result['name'] = result['name'].str.capitalize()
    return result.sort_values('user_id').reset_index(drop=True)

def daily_rolling_sales(df):
    """Seven natural days, missing days contribute zero; output observed days only."""
    data = df[['visited_on','amount']].copy()
    data['visited_on'] = pd.to_datetime(data['visited_on']).dt.normalize()
    daily = data.groupby('visited_on')['amount'].sum().sort_index()
    if daily.empty:
        return pd.DataFrame({'visited_on':pd.Series(dtype='datetime64[ns]'),
                             'amount':pd.Series(dtype='int64'),
                             'average_amount':pd.Series(dtype='float64')})
    total = daily.rolling('7D',closed='right').sum()
    total = total.loc[total.index >= daily.index.min()+pd.Timedelta(days=6)]
    # The teaching inputs are bounded integer amounts, exactly representable as float64.
    result = total.astype('int64').rename('amount').reset_index()
    result['average_amount'] = [_round2(Decimal(int(x))/Decimal(7)) for x in result['amount']]
    return result
'''
add(159,
'''“前三名”先问并列算几个名次。本章用部门内薪资 `dense` 排名，第三个不同薪资的所有员工都保留，而不是只截取三行。

次日留存的分母是玩家数，不是日志行数；先对玩家—日期去重，取各自首次日期，再判断次日是否存在。自然日跨月仍是加一天，不能把日期字符串最后一位加一。

七日营业额窗口为 `(当日−7天, 当日]`。先按日聚合，再做时间窗口。缺失日视为零，但输出只保留原表出现、且已经历七个自然日的日期。按行数 `rolling(7)` 在日期缺口存在时是另一道题。金额限定为可精确表示的有界整数；这不是通用财务精度库。''',
P159,
'''sales = pd.DataFrame({'visited_on':['2024-01-01','2024-01-01','2024-01-03','2024-01-07','2024-01-08'], 'amount':[10,20,30,70,80]})
display(sales)
display(daily_rolling_sales(sales))
activity = pd.DataFrame({'player_id':[1,1,1,2,3], 'event_date':['2024-01-31','2024-02-01','2024-02-01','2024-01-01','2024-01-02']})
show_table(['quantity','value'],[['raw rows',len(activity)],['players',activity.player_id.nunique()],['next-day fraction',next_day_retention(activity)]])
''',
'''employees = pd.DataFrame({'id':[1,2,3,4,5,6], 'name':['a','b','c','d','e','f'], 'salary':[100,90,90,80,70,10], 'departmentId':[1,1,1,1,1,2]})
departments = pd.DataFrame({'id':[1,2], 'name':['IT','HR']})
expected = pd.DataFrame({'Department':['HR','IT','IT','IT','IT'], 'Employee':['f','a','b','c','d'], 'Salary':[10,100,90,90,80]})
assert_frame_equal(department_top_three_salaries(employees,departments),expected)
a = pd.DataFrame({'player_id':[1,1,1,2,3], 'event_date':['2024-01-31','2024-02-01','2024-02-01','2024-01-01','2024-01-02']})
assert next_day_retention(a) == 0.33
assert next_day_retention(a.iloc[:0]) == 0.0
one_eighth = pd.DataFrame({'player_id':list(range(8))+[0], 'event_date':['2024-02-28']*8+['2024-02-29']})
assert next_day_retention(one_eighth) == 0.13
users = pd.DataFrame({'user_id':[2,1], 'name':['aLICE','bOB']})
assert_frame_equal(normalize_names(users),pd.DataFrame({'user_id':[1,2], 'name':['Bob','Alice']}))
sales = pd.DataFrame({'visited_on':['2024-01-01','2024-01-01','2024-01-03','2024-01-07','2024-01-08'], 'amount':[10,20,30,70,80]})
expected = pd.DataFrame({'visited_on':pd.to_datetime(['2024-01-07','2024-01-08']), 'amount':[130,180], 'average_amount':[18.57,25.71]})
assert_frame_equal(daily_rolling_sales(sales),expected)
assert daily_rolling_sales(sales.iloc[:0]).empty
import sqlite3
query = """WITH daily AS (
 SELECT visited_on,SUM(amount) AS value FROM Sales GROUP BY visited_on
), totals AS (
 SELECT visited_on,SUM(value) OVER (ORDER BY JULIANDAY(visited_on)
 RANGE BETWEEN 6 PRECEDING AND CURRENT ROW) AS amount FROM daily
) SELECT visited_on,amount,ROUND(amount/7.0,2) AS average_amount FROM totals
 WHERE JULIANDAY(visited_on)-(SELECT JULIANDAY(MIN(visited_on)) FROM daily)>=6
 ORDER BY visited_on"""
with sqlite3.connect(':memory:') as conn:
    sales.to_sql('Sales',conn,index=False)
    actual_sql = pd.read_sql_query(query,conn,parse_dates=['visited_on'])
assert_frame_equal(daily_rolling_sales(sales),actual_sql)
''',
'''先聚合和去重决定统计单位，再做排名或日期对齐；顺序不可任意交换。时间窗口查询的是日历范围，跨月与缺口不改变定义。留存通过与唯一玩家—次日键一对一匹配，保证每个玩家最多贡献一次。''',
'''分组通常期望线性；排序和排名通常 O(n log n)。时间滑窗在已排序序列上处理，避免每一行重新扫描全表；存储 O(n)。''')
