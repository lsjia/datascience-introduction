import pandas as pd
import json

samples = {}
col_sum = {}
col_avg = {}

columns = [
    'YEAR_DATE', 'UNIQUE_CARRIER', 'ORIGIN', 'ORIGIN_STATE_ABR', 'DEST',
    'DEST_STATE_ABR', 'DEP_DELAY', 'TAXI_OUT', 'TAXI_IN', 'ARR_DELAY',
    'AIR_TIME', 'DISTANCE'
]

num_cols = [
    'YEAR_DATE', 'DEP_DELAY', 'TAXI_OUT', 'TAXI_IN', 'ARR_DELAY', 'AIR_TIME',
    'DISTANCE'
]
cate_cols = [
    'UNIQUE_CARRIER', 'ORIGIN', 'ORIGIN_STATE_ABR', 'DEST', 'DEST_STATE_ABR'
]

total_num = 1000000  # 总数据量
sample_num = 1000  # 样本量


def aqp_online(data: pd.DataFrame, Q: list) -> list:
    global columns, samples, col_sum, col_avg, num_cols, cate_cols
    queries = []  # 把Q的每一条json格式字符串，解析成一个dict
    for i in Q:
        queries.append(json.loads(i))

    results = []  # 存放每条query的aqp结果
    for q in queries:
        result_col = q['result_col']
        if result_col[-1][0] == 'count':
            results.append(do_count(q))
        elif result_col[-1][0] == 'avg':
            results.append(do_avg(q))
        elif result_col[-1][0] == 'sum':
            results.append(do_sum(q))
        # print(results[-1])
        results[-1] = json.dumps(results[-1], ensure_ascii=False)

    return results


def aqp_offline(data: pd.DataFrame, Q: list) -> None:
    '''无需返回任何值
    必须编写的aqp_offline函数，用data和Offline-workload，构建采样、索引、机器学习相关的结构或模型
    data是一个DataFrame，Q是一个包含多个json格式字符串的list
    如果你的算法无需构建结构或模型，该函数可以为空
    '''
    global columns, samples, col_sum, col_avg, num_cols, cate_cols

    # 采样
    for col in columns:
        samples[col] = sampling(data, col)
    # 求每个数值型列的sum和avg
    for col in num_cols:
        col_sum[col] = data[col].sum()
        col_avg[col] = data[col].mean()


def sampling(data, col_name):
    global columns, samples, num_cols, cate_cols, total_num, sample_num

    sample_list = []
    if col_name in num_cols:  # 是数值型列，等间隔采样
        col_list = list(data[col_name])
        col_list.sort()  # 排序
        step = int(total_num / sample_num)
        for i in range(0, total_num, step):
            sample_list.append(col_list[i])
        sample_list.append(col_list[-1])
        return sample_list
    else:  # 非数值型列，统计频次
        dic = {}
        types = list(set(data[col_name]))
        for type in types:
            dic[type] = list(data[col_name]).count(type)
        return dic


def do_count(q):
    res = []
    pred = q['predicate']
    percent = 1.0

    # 计算百分比
    for p in pred:
        if p['col'] in cate_cols:
            num = samples[p['col']][p['lb']]
            percent *= num / total_num

        else:
            lst = samples[p['col']]
            # interval = float((lst[-1] - lst[0])) / sample_num
            lower = 0.0
            upper = 0.0
            if p['lb'] != "_None_":
                lower = max(lst[0], p['lb'])
            else:
                lower = lst[0]

            if p['ub'] != "_None_":
                upper = min(lst[-1], p['ub'])
            else:
                upper = lst[-1]

            num = 0
            for i in lst:
                if i >= lower and i <= upper:
                    num += 1

            num *= total_num / sample_num
            percent *= num / total_num
    if len(pred) != 1:
        percent = percent**0.855  # 微调
    if q['groupby'] == '_None_':
        res.append([total_num * percent])

    else:
        type_name = q['result_col'][0][0]
        for i in pred:
            if i['col'] == type_name:  # 约束条件是类别列
                res.append([i['lb'], total_num * percent])
                return res

        dic = samples[q['result_col'][0][0]]
        for key in dic.keys():
            res.append([key, dic[key] * percent])

    return res


def do_sum(q):
    res = []
    pred = q['predicate']
    percent = 1.0

    # 计算百分比
    for p in pred:
        if p['col'] in cate_cols:
            num = samples[p['col']][p['lb']]
            percent *= num / total_num

        else:
            lst = samples[p['col']]
            # interval = (lst[-1] - lst[0]) / sample_num

            lower = 0.0
            upper = 0.0
            if p['lb'] != "_None_":
                lower = max(lst[0], p['lb'])
            else:
                lower = lst[0]

            if p['ub'] != "_None_":
                upper = min(lst[-1], p['ub'])
            else:
                upper = lst[-1]

            num = 0
            for i in lst:
                if i >= lower and i <= upper:
                    num += 1

            num *= total_num / sample_num
            # num = (upper - lower) * step / interval
            percent *= num / total_num
    if len(pred) != 1:
        percent = percent**0.855  # 微调
    certain_sum = col_sum[q['result_col'][-1][1]]
    if q['groupby'] == '_None_':
        res.append([certain_sum * percent])

    else:
        type_name = q['result_col'][0][0]
        for i in pred:
            if i['col'] == type_name:  # 约束条件是类别列
                res.append([i['lb'], col_sum[q['result_col'][1][1]] * percent])
                return res
        dic = samples[q['result_col'][0][0]]
        for key in dic.keys():
            res.append([key, certain_sum * percent * (dic[key] / total_num)])

    return res


def do_avg(q):
    res = []
    avg = col_avg[q['result_col'][-1][1]]
    if q['groupby'] == '_None_':
        res.append([avg])
    else:
        dct = samples[q['result_col'][0][0]]
        for key in dct.keys():
            res.append([key, avg])

    return res
