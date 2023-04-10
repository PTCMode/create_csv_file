# create_csv_file

```python
# 生成列的数量
colCount = 14

# 生成行的数量
rowCount = 100

# 自定义文字列数组
customStrList1 = [
    "\"北京\"",
    "\"天津\"",
    "\"上海\"",
    "\"重庆\"",
    "\"河北\"",
]

customStrList2 = [
    "\"山西\"",
    "\"内蒙古\"",
    "\"辽宁\"",
    "\"吉林\"",
    "\"黑龙江\"",
]

# 各列初始化参数
colInfoList = [
    # 不添加特殊处理, 默认顺序递增 (CUSTOM 会在用户定义list中循环递增)
    # [ 数据类型, 设定值, (步长), ([ 特殊处理 ]...) ]
    [
        # 该列数据类型为 INT, 最小数据值为 5, 数据变更步长为 2
        'INT', 5, 2,

        # 设置数据最大值附加值，最终最大值 = 最小数据值 + 最大值附加值 - 1
        # [ 'LIMIT', 最大值附加值 ]
        ['LIMIT', 6]

        # 最终结果为 5, 7, 9, 5, 7...
    ],
    [
        # 该列数据类型为 CHAR 或 VARCHAR, 使用用户定义list中的字符串
        'CUSTOM', customStrList1,

        # 设置数据的Key值, 若未设置百分比, 则默认为剩余Key值在剩余百分比中的平均值
        # 注: 不适合Key值很高的场景, 执行效率较低
        # [ 'KEY', Key值数量, (对应Key值所占百分比...) ]
        ['KEY', 5, 0.25, 0.25, 0.20]

        # 最终结果为 "北京"(25%), "天津"(25%), "上海"(20%), "重庆"(15%), "河北"(15%)
    ],
    [
        # 该列数据类型为 CHAR, 最小数据值为 "100"
        'CHAR', 100,

        # 生成 "最小数据值 ~ (最小数据值 + 设定值(当前为100) - 1)" 闭区间内的随机数
        # [ 'RANDOM', 随机数最大Key值数量 ]
        ['RANDOM', 100],

        # 在结果前补空格, 处理后字符串总长度为 设定值(当前为10)
        # 注: 目前只有 CHAR、VARCHAR、CUSTOM 会进行此处理
        # [ 随机长度, 随机字符, "", 长度 ]
        ['EXLEN', [ True, True, " ABCDEFGHIGKLMNOPQRSTUVWXYZabcdefghigklmnopqrstuvwxyz", 10 ] ]
    ],
    [
        'CUSTOM', customStrList2,

        # CUSTOM 也可以设置 RANDOM 特殊处理
        # [ 'RANDOM', 随机数最大Key值数量 ]
        ['RANDOM', 5]
    ],

    # 目前支持的列类型
    ['INT', 0],
    ['LONG', 0],
    ['DOUBLE', 0],
    ['NUMBER', 0],
    ['CHAR', 0],
    ['VARCHAR', 0],
    ['DATE', 0],
    ['YMINTERVAL', 0],
    ['DSINTERVAL', 0],
    ['TIMESTAMP', 0],
]
```