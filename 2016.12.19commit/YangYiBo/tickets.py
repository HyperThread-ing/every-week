# coding: utf-8

#程序开头申明中文注释

"""命令行火车票查看器       

#用法
Usage:
    tickets [-gdtkz] <from> <to> <date>

#选项
Options:
    -h,--help  显示帮助菜单
    -g    高铁
    -d    动车
    -t    特快
    -k    快速
    -z    直达

#示例
Eixample:
      tickets 北京 上海 2016-10-10
      tickets -dg 成都 南京 2016-10-10
"""

#从模板中导入模块

#获取URL的数据
import requests
#按预设置格式解析参数
from docopt import docopt
#导入表格方式输入内容模块
from prettytable import PrettyTable
#命令行着色工具
from colorama import init, Fore
#从stations字典中获取字母代码
from stations import stations


init()

#封装类解析数据
class TrainsCollection:
#加上头信息伪装成浏览器访问，防止有些网站禁止爬虫，并用字符串切片函数split进行切片分隔
    header = '车次 车站 时间 历时 一等 二等 软卧 硬卧 硬座 无座'.split()#切片效果例如['车次','车站',]

#初始化函数
    def __init__(self, available_trains, options):#给自己对象赋初值
        """查询到的火车班次集合
        
        :param available_trains: 一个列表, 包含可获得的火车班次, 每个火车
                                班次是一个字典
        :param options: 查询的选项, 如高铁, 动车, etc...
         """
        self.available_trains = available_trains
        self.options = options

#函数得到火车历时
    def _get_duration(self, raw_train):
        duration = raw_train.get('lishi').replace(':', '小时') + '分'#把旧字符串':'替换成 '小时'并在后面追加分 eg:23:30 ->23小时30分
        if duration.startswith('00'):#如果以00开头，则截取第四位开始以后部分
            return duration[4:]     #eg:00小时23分->23分，下面也如此
        if duration.startswith('0'):
            return duration[1:]
        return duration

#装饰器 负责把一个方法变成类属性调用
    @property
    def trains(self):
        for raw_train in self.available_trains:#available_trains是一个列表, 包含可获得的火车班次, 每个火车班次是一个字典
            train_no = raw_train['station_train_code']#获得班次字典的班次
            initial = train_no[0].lower()   #.lower()方法转换字符串中所有大写字符为小写
            #获得查询的选项并转换为小写，选项有-gdtkz
            if not self.options or initial in self.options:
                train = [
                    train_no,
                    '\n'.join([Fore.GREEN + raw_train['from_station_name'] + Fore.RESET,    #Fore.颜色 + 内容可以改变输出字体颜色
                            Fore.RED + raw_train['to_station_name'] + Fore.RESET]),
                    '\n'.join([Fore.GREEN + raw_train['start_time'] + Fore.RESET,
                            Fore.RED + raw_train['arrive_time'] + Fore.RESET]),     #.join()方法将序列中元素以制定字符连接上成一个新的字符串
                    self._get_duration(raw_train),
                    raw_train['zy_num'],
                    raw_train['ze_num'],
                    raw_train['rw_num'],#软卧
                    raw_train['yw_num'],#硬卧
                    raw_train['yz_num'],#有座
                    raw_train['wz_num'],#无座
                ]
                yield train     #yield可以把一个函数变成一个generator（生成器）每次运行到yield时暂停然后返回一个迭代值，下次迭代时从yield的下一条语句继续执行
    
    def pretty_print(self):
        pt = PrettyTable()      #PrettyTable模块将输出内容表格化
        pt._set_field_names(self.header)
        for train in self.trains:#把上面trains函数当作类属性使用
            pt.add_row(train)
        print(pt)
            

#为自定义的函数创建 __doc__ 的方法示例：
#>>> def func():
#   """Here's a doc string"""
#    pass
#>>> func.__doc__
#"Here's a doc string"

#主执行函数
def cli():
    """command-line interface"""
    arguments = docopt(__doc__)     #从最上面的三引号usage获取文档字符串,示例在上面
    from_station = stations.get(arguments['<from>'])
    to_station = stations.get(arguments['<to>'])
    date = arguments['<date>']
    # 构建URL
    url = 'https://kyfw.12306.cn/otn/lcxxcx/query?purpose_codes=ADULT&queryDate={}&from_station={}&to_station={}'.format(
                date, from_station, to_station#从URL反馈的信息里提取出Date，from_station和to_station
            )               #.format是格式化字符串函数
    
            # 获取参数
    options = ''.join([
            key for key, value in arguments.items() if value is True #items()函数以列表返回可遍历的(键, 值) 元组数组。
            ])#如果值是True就把key（键）从列表参数里返回给key
    # 添加verify=False参数不验证证书
    
    r = requests.get(url, verify=False);
    available_trains = r.json()['data']['datas']#json方式对字典进行编码，['data']是键，['datas']是值
    TrainsCollection(available_trains, options).pretty_print()#传参实例对象并调用输出函数

    
if __name__ == '__main__':
    cli()


#__name__是指示当前py文件调用方式的方法。如果它等于"__main__"就表示是直接执行，如果不是，则用来被别的文件调用，
#这个时候if就为False，那么它就不会执行最外层的代码了。
#比如你有个Python文件里面
#def XXXX():
#pass
#print "asdf"
#这样的话，就算是别的地方导入这个文件，要调用这个XXXX函数，也会执行print "asdf"，因为他是最外层代码，或者叫做全局代码。
#但是往往我们希望只有我在执行这个文件的时候才运行一些代码，不是的话（也就是被调用的话）那就不执行这些代码，所以一般改为
#def XXXX():
#pass
#print "asdf"