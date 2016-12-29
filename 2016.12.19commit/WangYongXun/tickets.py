#coding: utf-8

"""命令行火车票查看器

Usage:
    tickets [-gdtkz] <from> <to> <date>

Options:
    -h,--help   显示帮助菜单
    -g          高铁
    -d          动车
    -t          特快
    -k          快速
    -z          直达

Example:
    tickets 北京 上海 2016-10-10
    tickets -dg 成都 南京 2016-10-10
"""
import requests
from docopt import docopt
from prettytable import PrettyTable
from colorama import init,Fore
from stations import stations

init()

class TrainsCollection:

    header = '车次 车站 时间 历时 一等 二等 软卧 硬卧 硬座 无座'.split()

    def __init__(self,available_trains,options):
        """查询到的火车班次集合
        :param available_trains: 一个列表, 包含可获得的火车班次, 每个
        火车班次是一个字典
        :param options: 查询的选项, 如高铁, 动车, etc...
        """
        self.available_trains = available_trains
        self.options = options

    def _get_duration(self, raw_train):#将符合条件的车次字典中的'lishi'即 历时 封装规范
        #把时间里的冒号':'换为'小时' 并在后面追加一个'分'  EX  20:13 -> 20小时13分　
        duration = raw_train.get('lishi').replace(':', '小时') + '分'
        if duration.startswith('00'): #若封装后的开头为 00  则从第四个元素开始截取到最后  EX 00小时42分 -> 42分
                 return duration[4:]
        if duration.startswith('0'): #若封装后的开头为 0  则从第一个元素开始截取到最后  EX 01小时42分 -> 1小时42分
                 return duration[1:]
        return duration

    @property
    def trains(self):
        for raw_train in self.available_trains: #raw_train为字典类型 available_trains为传入的由一个个符合要求的车次字典组成的列表
            train_no = raw_train['station_train_code']#train_no为车次类型编号 如 G D T K Z 
            initial = train_no[0].lower()#将代表车次类型的字母转化为小写
            #将符合条件的车次封装为train列表 包含 车次 起点 终点 时间 历时 一等 二等 软卧 硬卧 硬座 无座
            if not self.options or initial in self.options:
                train = [
                    train_no,#车次编号 下面的起点终点等 用到了colorama的着色
                    '\n'.join([Fore.GREEN + raw_train['from_station_name'] + Fore.RESET,#起点
                            Fore.RED + raw_train['to_station_name'] + Fore.RESET]),#终点
                    '\n'.join([Fore.GREEN + raw_train['start_time'] + Fore.RESET,#出站时间
                            Fore.RED + raw_train['arrive_time'] + Fore.RESET]),#到站时间
                    self._get_duration(raw_train),#历时 参考_get_duration函数
                    raw_train['zy_num'],
                    raw_train['ze_num'],
                    raw_train['rw_num'],   #这些为车座类型 一等 二等 软卧 等
                    raw_train['yw_num'],
                    raw_train['yz_num'],
                    raw_train['wz_num'],
                ]
                yield train #返回一个车次的字典 yield表明这个函数是一个生成器 则每次执行返回一个符合条件的车次

    def pretty_print(self):
        pt = PrettyTable()#导入的prettytable类型
        pt._set_field_names(self.header)#设置表头
        for train in self.trains:#这里执行def trains(self)函数 这个函数为一个生成器 每次执行返回一个符合条件的车次
            pt.add_row(train)# 参考网址 http://www.liaoxuefeng.com/wiki/0014316089557264a6b348958f449949df42a6d3a2e542c000/0014317799226173f45ce40636141b6abc8424e12b5fb27000
        print(pt)#最终结果

def cli():
    """command-line interface"""
    arguments = docopt(__doc__ ) #按照说明中Usage的格式创建一个字典赋值给arguments
    #输入的值被封装为一个字典 对应三个键 <from> <to> <date>
    #这个链接用于解答关于docopt的使用  http://www.tuicool.com/articles/36zyQnu
    #下面导入station.py里的station字典 用于将输入的汉字按照stations字典转化为编号
    from_station = stations.get(arguments['<from>'])#起点为汉字需要转换url中
    to_station = stations.get(arguments['<to>'])#终点为汉字需要转换加入到url中
    date = arguments['<date>']#日期可以直接赋值加入到url中
    #构建 URL 由基本的链接加上日期 起点和终点 构造可获得车次信息的链接
    url= 'https://kyfw.12306.cn/otn/lcxxcx/query?purpose_codes=ADULT&queryDate={}&from_station={}&to_station={}'.format(
            date,from_station,to_station
             )
    #遍历arguments.items()
    #arguments.items()返回的是一个列表（list） 列表的每一项为字典里的键和其对应的值组成的一个元祖
    #示例： 定义一词典为 d = {'Michael': 95, 'Bob': 75, 'Tracy': 85}
    #则d.items() 为 [('Michael', 95), ('Bob', 75), ('Tracy', 85)]
    #print的结果
    #dict_items([('Michael', 95), ('Bob', 75), ('Tracy', 85)])

    options = ''.join([
        key for key,value in arguments.items() if value is True
        ])
    #这里for后面的 key,value 为一省略括号的元祖 
    #规范些是这样的 for (key,value) in arguments.items() if value is True
    #即 从arguments.items()返回的元组列表( in arguments.items() )中找到值为True( if value is True )的键
    #作用为 可以定义查找车次类型


    #添加verify=False参数不验证证书
    #获取url返回的结果
    r = requests.get(url, verify=False)
    #用['data']['datas']的格式解析json得到一个列表 列表里是各个车次的字典
    available_trains = r.json()['data']['datas']
    #通过解析得到符合条件类型的车次 即available_trains 实例化解析车次的TrainsCollection类
    TrainsCollection(available_trains,options).pretty_print()

if __name__ == '__main__':
    cli()
