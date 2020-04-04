#!/usr/bin/env python
#-*- coding:utf-8 -*-
import re
import json
import xlwt
import argparse

def get_address(data):
    '''
    获取地址名称、地址范围和主机地址
    '''
    address = {}
    key = ""

    for d in data:
        '''
            地址
        '''
        if d.startswith("address "):
            key = re.findall("^address (.+)", d)[0].strip()
            addr = []
        elif d.startswith(" host-address"):
            addr.append(d[14:])
            #host_address = re.findall("^ host-address (.+)", d)[0]
        elif d.startswith(" range-address"):
            ra = re.findall("^ range-address (\d+\.\d+\.\d+\.\d+) (\d+\.\d+\.\d+\.\d+)", d)
            addr.append("{}-{}".format(ra[0][0],ra[0][1]))
        elif d.startswith(" net-address"):
            addr.append(d[len(' net-address'):])
        elif d.startswith('address-group'):
            key = d[len('address-object'):].strip()
            addr = []
        elif d.startswith('   address-object'):
            addr_obj = d[len('   address-object'):].strip()
            addr.append(','.join(address[addr_obj]))
        if key:
            address[key] = addr

        '''
            地址组
        '''

    return address

def get_service(data):
    '''
    获取配置文件中服务端口号、协议和对应的系统
    '''
    service = {}
    key = ""

    for d in data:
        if d.startswith("service "):
            key = re.findall("^service (.+)", d)[0]
            svr = []
        elif d.startswith(" tcp dest"):
            try:
                svr.append('tcp: {}'.format(re.findall(" tcp dest (\d+) source 1 65535", d)[0]))
            except IndexError:
                dest_port = re.findall(" tcp dest (\d+) (\d+) source 1 65535", d)[0]
                svr.append('tcp: {}-{}'.format(dest_port[0], dest_port[1]))
        elif d.startswith(" udp dest"):
            try:
                svr.append('udp: {}'.format(re.findall(" udp dest (\d+) source 1 65535", d)[0]))
            except IndexError:
                dest_port = re.findall(" udp dest (\d+) (\d+) source 1 65535", d)[0]
                svr.append('udp: {}-{}'.format(dest_port[0], dest_port[1]))
        elif d.startswith('service-group'):
            key = re.findall('^service-group (.+)', d)[0].strip()
            svr = []
        elif d.startswith(' service-object'):
            svr_obj = re.findall('^ service-object (.+)', d)[0].strip()
            svr.append(','.join(service[svr_obj]))
        if key:
            service[key] = svr

    return service

    
def get_policy(data):
    key = ""
    policy = {}
    options = {
        'action': '',
        'src-name':'',
        'dst-name':'',
        'src-zone': '',
        'dst-zone': '',
        'src-addr':'',
        'dst-addr': '',
        'service': ''
    }

    count = 0
    address = get_address(data)
    service = get_service(data)

    for d in data:
        if d.startswith("firewall policy "):
            key = re.findall("firewall policy (\d+)", d)[0]
            count += 1
            options = {}
        elif d.startswith(' action '):
            options['action'] = 'permit' if re.findall("^ action (.+)", d)[0] == 'permit' else 'deny'
        elif d.startswith(' src-addr '):
            options['src-name'] = re.findall("^ src-addr (.+)", d)[0]
            try:
                options['src-addr'] = address[re.findall("^ src-addr (.+)", d)[0]]
            except KeyError:
                options['src-addr'] = re.findall("^ src-addr (.+)", d)[0]
        elif d.startswith(' dst-addr '):
            options['dst-name'] = re.findall("^ dst-addr (.+)", d)[0]
            try:
                options['dst-addr'] = address[re.findall("^ dst-addr (.+)", d)[0]]
            except KeyError:
                options['dst-addr'] = re.findall("^ dst-addr (.+)", d)[0]
        elif d.startswith(' service '):
            try:
                options['service'] = service[re.findall("^ service (.+)", d)[0]]
            except KeyError:
                options['service'] = re.findall("^ service (.+)", d)[0]
        elif d.startswith(' src-zone '):
            options['src-zone'] = re.findall("^ src-zone (.+)", d)[0]
        elif d.startswith(' dst-zone '):
            options['dst-zone'] = re.findall("^ dst-zone (.+)", d)[0]
        if key:
            policy[key] = options
    print('[+] 共读取 {} 条策略。'.format(count))
    return policy

def write2Excle(policy):

    row = 1
    wkbook = xlwt.Workbook(encoding = 'utf-8')
    worksheet = wkbook.add_sheet('config')
    #header
    worksheet.write(0, 0, '编号')
    worksheet.write(0, 1, '源名称')
    worksheet.write(0, 2, '源地址')
    worksheet.write(0, 3, '目的名称')
    worksheet.write(0, 4, '目的地址')
    worksheet.write(0, 5, '源接口')
    worksheet.write(0, 6, '目的接口')
    worksheet.write(0, 7, '服务端口')
    worksheet.write(0, 8, '动作')

    for k, v in policy.items():
        worksheet.write(row, 0, k)        
        worksheet.write(row, 1, v['src-name'])        
        worksheet.write(row, 2, v['src-addr'])        
        worksheet.write(row, 3, v['dst-name'])        
        worksheet.write(row, 4, v['dst-addr'])        
        worksheet.write(row, 5, v['src-zone'])        
        worksheet.write(row, 6, v['dst-zone'])        
        worksheet.write(row, 7, v['service'])        
        worksheet.write(row, 8, v['action'])        
        row += 1
    wkbook.save('config.xls')

    print('[+] 共有 {} 条记录写入xls'.format(row - 1))

def cmdParser():
    argparser = argparse.ArgumentParser()
    argparser.add_argument('-f', '--file', dest = 'FILENAME', required = True, help = '指定配置文件')

    return argparser.parse_args()

def main():
    args = cmdParser()
    with open(args.FILENAME,"r") as f:
        data = f.read().splitlines()
    write2Excle(get_policy(data))

if __name__ =="__main__":
    main()
