# -*- coding: utf-8 -*-
 
from __future__ import unicode_literals
from django.http import HttpResponse
import json,os
from django.shortcuts import render
from build_util import *

def home(request):
    mix =['正常打包','快速打包']
    type = ['测试包','正式包']
    log = ['打印日志','不打印日志']
    branch = get_remote_branchs_name()
    return render(request,'index.html',{'mix':json.dumps(mix),'type':json.dumps(type),'log':json.dumps(log),'branch':json.dumps(branch)})

def package(request):
    mix = request.GET['mix']
    type = request.GET['type']
    log = request.GET['log']
    branch = request.GET['branch']
    mails = request.GET['mail']
    mails = mails[0:len(mails)-1]
    v = 'result'
    if "快速" in mix:
        mix = 'false'
    else:
        mix = 'true'
    if "不打印日志" in log:
        log = 'false'
    else:
        log = 'true'
   
    if "测试包" in type:
        type = 'public_test'
    else:
        type = 'public_online'

    print mix + "," + log + "," + branch + "," + type + "," + mails
    v = apks_build(mix, log, branch, type, mails)
 
    return HttpResponse(v)
