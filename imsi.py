#!/usr/bin/env python 
# -*-coding:utf-8-*-
import xlrd
import re
import urllib.request
import json
import ssl

class imsi2area :
    
    def __init__(self, file) :
        #定义映射字典
        self.dicts = {
            's130'  : "^46001(\\d{3})(\\d)[0,1]\\d+",
            's131'  : "^46001(\\d{3})(\\d)9\\d+",
            's132'  : "^46001(\\d{3})(\\d)2\\d+",
            's134'  : "^460020(\\d)(\\d{3})\\d+",
            's13x0' : "^46000(\\d{3})([5,6,7,8,9])\\d+",
            's13x'  : "^46000(\\d{3})([0,1,2,3,4])(\\d)\\d+",
            's150'  : "^460023(\\d)(\\d{3})\\d+",
            's151'  : "^460021(\\d)(\\d{3})\\d+",
            's152'  : "^460022(\\d)(\\d{3})\\d+",
            's155'  : "^46001(\\d{3})(\\d)4\\d+",
            's156'  : "^46001(\\d{3})(\\d)3\\d+",
            's157'  : "^460077(\\d)(\\d{3})\\d+",
            's158'  : "^460028(\\d)(\\d{3})\\d+",
            's159'  : "^460029(\\d)(\\d{3})\\d+",
            's147'  : "^460079(\\d)(\\d{3})\\d+",
            's185'  : "^46001(\\d{3})(\\d)5\\d+",
            's186'  : "^46001(\\d{3})(\\d)6\\d+",
            's187'  : "^460027(\\d)(\\d{3})\\d+",
            's188'  : "^460078(\\d)(\\d{3})\\d+",
            's1705' : "^460070(\\d)(\\d{3})\\d+",
            's170x' : "^46001(\\d{3})(\\d)8\\d+", 
            's178'  : "^460075(\\d)(\\d{3})\\d+",
            's145'  : "^46001(\\d{3})(\\d)7\\d+",
            's182'  : "^460026(\\d)(\\d{3})\\d+",
            's183'  : "^460025(\\d)(\\d{3})\\d+",
            's184'  : "^460024(\\d)(\\d{3})\\d+",
            #电信的，下面的还没有找到规则
            's180'  : "^46003(\\d)(\\d{3})7\\d+",
            's153'  : "^46003(\\d)(\\d{3})8\\d+",
            's189'  : "^46003(\\d)(\\d{3})9\\d+",
        }
        self.excel = xlrd.open_workbook(file)
        self.sheet = self.excel.sheet_by_index(0) #第一个表
    
    '''
    获取xls文件中的imsi数据
    '''
    def getData(self):
        for i in range(1, self.sheet.nrows):
            imsi = self.sheet.cell(i,0).value
            if imsi == '#' or imsi == 0:
                continue
            for dic in self.dicts:
                prefix = self.match(self.dicts[dic], dic, imsi)
                if prefix is None :
                    continue
                sstr = self.getArea(prefix, imsi)
                print(sstr)
    


    '''
    正则匹配imsi，转换为手机号段前缀
    '''
    def match(self, preg, tag, imsi):
        prefix = None
        pattern = re.compile(preg)
        res = pattern.findall(imsi)
        if res == [] :
            return prefix
    
        result = {
            's130'  : lambda prefix : tag + res[0][1] + res[0][0],
            's131'  : lambda prefix : tag + res[0][1] + res[0][0],
            's132'  : lambda prefix : tag + res[0][1] + res[0][0],
            's134'  : lambda prefix : tag + res[0][0] + res[0][1],
            's13x0' : lambda prefix : 's13' + res[0][1] + '0' + res[0][0],
            's13x'  : lambda prefix : 's13' + str(int(res[0][1]) + 5) + res[0][2] + res[0][0],
            's150'  : lambda prefix : tag + res[0][1] + res[0][0],
            's151'  : lambda prefix : tag + res[0][0] + res[0][1],
            's152'  : lambda prefix : tag + res[0][0] + res[0][1],
            's155'  : lambda prefix : tag + res[0][1] + res[0][0],
            's156'  : lambda prefix : tag + res[0][1] + res[0][0],
            's157'  : lambda prefix : tag + res[0][0] + res[0][1],
            's158'  : lambda prefix : tag + res[0][0] + res[0][1],
            's159'  : lambda prefix : tag + res[0][0] + res[0][1],
            's147'  : lambda prefix : tag + res[0][0] + res[0][1],
            's185'  : lambda prefix : tag + res[0][1] + res[0][0],
            's186'  : lambda prefix : tag + res[0][1] + res[0][0],
            's187'  : lambda prefix : tag + res[0][0] + res[0][1],
            's188'  : lambda prefix : tag + res[0][0] + res[0][1],
            's1705' : lambda prefix : 's170' + res[0][0] + res[0][1],
            's170x' : lambda prefix : 's170' + res[0][1] + res[0][0],
            's178'  : lambda prefix : tag + res[0][0] + res[0][1],
            's145'  : lambda prefix : tag + res[0][1] + res[0][0],
            's182'  : lambda prefix : tag + res[0][0] + res[0][1],
            's183'  : lambda prefix : tag + res[0][0] + res[0][1],
            's184'  : lambda prefix : tag + res[0][0] + res[0][1],
            's180'  : lambda prefix : tag + res[0][0] + res[0][1],
            's153'  : lambda prefix : tag + res[0][0] + res[0][1],
            's189'  : lambda prefix : tag + res[0][0] + res[0][1]
        }[tag](prefix)
        return result.replace('s', '')
    
    '''
    通过手机号段前缀获取地理位置信息
    '''
    def getArea(self, prefix, imsi):
        url = "https://sp0.baidu.com/8aQDcjqpAAV3otqbppnN2DJv/api.php?query=" + prefix  + "+%E6%89%8B%E6%9C%BA%E5%8F%B7%E6%AE%B5&resource_id=6004&ie=utf8&oe=utf8";
    
        req = urllib.request.Request(url)
        gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
        data = json.loads(urllib.request.urlopen(req, context = gcontext).read().decode('utf8'))
        sstr  = ''
        if data['data'] and data['data'][0] is not None :
            sstr = "imsi：" + imsi + ",手机号码前缀：" + prefix + ",地区：" + data['data'][0]['type'] + data['data'][0]['prov'] + data['data'][0]['city']
        return sstr


if __name__ == '__main__' :
    file = "imsi.xls"
    #文件格式内容为
    '''
    4600012xxxxxxxxx
    4600252xxxxxxxxx
    '''
    imsi2area(file).getData()
  
