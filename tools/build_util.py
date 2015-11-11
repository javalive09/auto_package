# -*- coding: utf-8 -*-
import os,time,socket,xml.dom.minidom,ConfigParser,subprocess,sys,shutil,distutils,smtplib
from distutils.dir_util import copy_tree
from email.mime.text import MIMEText

mail_host="smtp.126.com"  #设置服务器
mail_user="javalive09"    #用户名
mail_pass="jfzgnrqzrofsdosb"   #口令
mail_postfix="126.com"  #发件箱的后缀

def apks_build(mix, log, branch, type, mails):
	start = time.time()
	src = '/Users/peter/git/xui/BuildTools/src/ant.properties'
	config = ConfigParser.RawConfigParser()
	config.read(src)
	s = config.sections()
	root_dir = config.get(s[0],'root.dir')
	target_apk_dir = config.get(s[0],'target.apk.dir')

	time_name = time.strftime('%Y-%m-%d-%H-%M-%S',time.localtime(time.time()))
	os.chdir(target_apk_dir)
	dir_name = 'time-' + time_name + "_mix-" + mix  + "_log-" + log  + "_urltype-" + type + "_branch-" + branch
	os.system('mkdir ' + dir_name)
	target_apk_dir = target_apk_dir + '/' + dir_name
	
	checkout_branch(branch, root_dir)
	clean_bin(root_dir)

        modify_car_mix(root_dir, mix)
        modify_phone_mix(root_dir, mix)

	#phone_hp 同时打包car_novideo, phone_normal
	build_(root_dir, target_apk_dir, type, log, log, 'false', 'phone_contain_car', 'false')
	#car_video
	build_(root_dir, target_apk_dir, type, log, log, 'false', 'car', 'true')
	
	end = time.time()	
	duration = end - start
	duration = time.strftime('%H:%M:%S', time.gmtime(duration))
	print "打包总耗时>>>>>>>>>>>>>>>>>>>>>"+ duration
	v = "http://192.168.230.119:9191/" + dir_name
	mails_ = mails.split(',')
	print mails_
	if send_mail(mails_,"打包地址",v):
                print "发送邮件成功>>>>>>>>>>>>>>>>>>>>>>"
        else:
                print "发送邮件失败>>>>>>>>>>>>>>>>>>>>>>"
	return v

def build_(root_dir, target_apk_dir, url_type, print_log_phone, print_log_car, ver_scan, apk_type, car_apk_contain_video):
	'''打包脚本'''
	if apk_type == 'phone':
		modify_phone_config_xml(root_dir, url_type, print_log_phone, ver_scan)
		modify_phone_log(root_dir, print_log_phone)
		backup_phone_assert(root_dir)
		clean_phone_assert(root_dir)
		package_phone(root_dir)
		
		update_phone_assert(root_dir)
		
		if ver_scan == 'true':
			copy_phone_apk_to_target_folder(root_dir, target_apk_dir, get_branch_name(), get_phone_ver_name(root_dir), '_noCarApk_scanVer')
			copy_phone_apk_to_target_folder_release(root_dir, target_apk_dir, get_phone_ver_name(root_dir), 'wx_')
		else:
			copy_phone_apk_to_target_folder(root_dir, target_apk_dir, get_branch_name(), get_phone_ver_name(root_dir), '_noCarApk')
			
	elif apk_type == 'car':
		modify_car_config_xml(root_dir, print_log_car)
		modify_car_log(root_dir, print_log_car)
		backup_car_assert(root_dir)
		clean_car_assert(root_dir)
		if car_apk_contain_video == 'true':
			update_car_assert(root_dir)
			package_car(root_dir)
			#copy_car_apk_to_target_folder(root_dir, target_apk_dir, get_branch_name(), get_car_ver_name(root_dir), '_haveVideo')
			copy_car_apk_to_target_folder_release(root_dir, target_apk_dir, get_car_ver_name(root_dir), 'video_')
		else:
			package_car(root_dir)
			#还原car assets
			update_car_assert(root_dir)
			copy_car_apk_to_target_folder(root_dir, target_apk_dir, get_branch_name(), get_car_ver_name(root_dir), '_noVideo')
			copy_car_apk_to_target_folder_release(root_dir, target_apk_dir, get_car_ver_name(root_dir), '')
	elif apk_type == 'phone_contain_car':
		modify_phone_config_xml(root_dir, url_type, print_log_phone, ver_scan)
		modify_phone_log(root_dir, print_log_phone)
		modify_car_config_xml(root_dir, print_log_car)
		modify_car_log(root_dir, print_log_car)
		backup_phone_assert(root_dir)
		clean_phone_assert(root_dir)
		update_phone_assert(root_dir)
		
		
		if car_apk_contain_video == 'true':
			backup_car_assert(root_dir)
			clean_car_assert(root_dir)
			update_car_assert(root_dir)
			
			package_car(root_dir)
			
			#skywindow里面结构有可能会变，这个方法需要更新
			update_tools_car_apk(root_dir)
			
			package_phone(root_dir)
			copy_car_apk_to_target_folder(root_dir, target_apk_dir, get_branch_name(), get_car_ver_name(root_dir), '_haveVideo')
			if ver_scan == 'true':
				copy_phone_apk_to_target_folder(root_dir, target_apk_dir, get_branch_name(), get_phone_ver_name(root_dir),'_haveCarApk_haveVideo_scanVer')
			else:
				copy_phone_apk_to_target_folder(root_dir, target_apk_dir, get_branch_name(), get_phone_ver_name(root_dir),'_haveCarApk_haveVideo')
		else:
			backup_car_assert(root_dir)
			clean_car_assert(root_dir)
			package_car(root_dir)
			update_car_assert(root_dir)
			
			#skywindow里面结构有可能会变，这个方法需要更新
			update_tools_car_apk(root_dir)
			update_phone_assert(root_dir)
			package_phone(root_dir)
			copy_car_apk_to_target_folder_release(root_dir, target_apk_dir, get_car_ver_name(root_dir), '')
			copy_phone_apk_to_target_folder_release(root_dir, target_apk_dir, get_phone_ver_name(root_dir), 'hp_')
			copy_phone_apk_to_target_folder_release(root_dir, target_apk_dir, get_phone_ver_name(root_dir), '')
	return target_apk_dir


def build():
	'''打包脚本'''
	src = '../ant.properties'
	config = ConfigParser.RawConfigParser()
	config.read(src)
	s = config.sections()
	root_dir = config.get(s[0],'root.dir')
	target_apk_dir = config.get(s[0],'target.apk.dir')
	url_type = config.get(s[0],'url.type')
	print_log_phone = config.get(s[0],'print.log.phone')
	print_log_car = config.get(s[0],'print.log.car')
	ver_scan = config.get(s[0],'ver.scan')
	apk_type = config.get(s[0],'apk.type')
	car_apk_contain_video = config.get(s[0],'car.apk.contain.video')
	return build_(root_dir, target_apk_dir, url_type, print_log_phone, print_log_car, ver_scan, apk_type, car_apk_contain_video)


def modify_phone_config_xml(root_dir, url_type, print_log_phone, ver_scan):
	'''修改 phone config_strings.xml'''
	old=open(root_dir + "/PhoneClient/res/values/config_strings.xml")
	try:
		lines=old.readlines()
	finally:
		old.close()
	newlines=[]
	for line in lines:
		print line
		if 'url_type' in line:
			line='''	<string name="url_type">''' + url_type + "</string>" +'\n'
		if 'print_log' in line:
			line='''	<bool name="print_log">''' + print_log_phone + "</bool>" +'\n'
		if 'ver_scan' in line:
			line='''	<bool name="ver_scan">''' + ver_scan + "</bool>" +'\n'
		newlines.append(line)
	print newlines
	new=open(root_dir + "/PhoneClient/res/values/config_strings.xml","w")
	new.writelines(newlines)
	new.close()

#本地ip地址
def Get_local_ip():

    """
    Returns the actual ip of the local machine.
    This code figures out what source address would be used if some traffic
    were to be sent out to some well known address on the Internet. In this
    case, a Google DNS server is used, but the specific address does not
    matter much.  No traffic is actually sent.
    """
    try:
        csock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        csock.connect(('8.8.8.8', 80))
        (addr, port) = csock.getsockname()
        csock.close()
        return addr
    except socket.error:
        return "127.0.0.1"


def start_server(apks_dir):
	os.chdir(apks_dir)
	str = os.popen("ps").read()
	strs = str.split('\n')
	
	# 关闭 simpleHttp 服务
	for line in strs:
		if "SimpleHTTPServer" in line:
			l = line.replace(' ','')
			num = l[0:4]
			print num
			os.system('kill -9 ' + num)
			
	port = 9191
	ip = Get_local_ip()
	#开启 simpleHttp 服务
	try:
		portStr = bytes(port)
		print portStr
		ipStr = "http://" + ip + ':' + portStr
		print ipStr
		os.system("python -m SimpleHTTPServer " + bytes(port))
	except:
		print "重复port"
		port = port + 1
		portStr = bytes(port)
		print portStr
		ipStr = "http://" + ip + ':' + portStr
		print ipStr
		os.system("python -m SimpleHTTPServer " + bytes(port))	
	return ipStr

def modify_car_config_xml(root_dir, print_log_car):
	'''修改 car config_strings.xml'''
	old=open(root_dir + "/CarClient/res/values/config_strings.xml")
	try:
		lines=old.readlines()
	finally:
		old.close()
	newlines=[]
	for line in lines:
		print line
		if 'print_log' in line:
			line='''	<bool name="print_log">''' + print_log_car + "</bool>" +'\n'
		newlines.append(line)
	print newlines
	new=open(root_dir + "/CarClient/res/values/config_strings.xml","w")
	new.writelines(newlines)
	new.close()

def send_mail(to_list,sub,content):
        me="xui打包"+"<"+mail_user+"@"+mail_postfix+">"
        msg = MIMEText(content,_subtype='plain',_charset='utf-8')
        msg['Subject'] = sub
        msg['From'] = me
        msg['To'] = ";".join(to_list)
        try:
                server = smtplib.SMTP()
                server.connect(mail_host)
                server.login(mail_user,mail_pass)
                print to_list
		server.sendmail(me, to_list, msg.as_string())
                server.close()
                return True
        except Exception, e:
                print str(e)
                return False


def modify_phone_log(root_dir, print_log_phone):
	'''修改 phone proguard-project.txt 打开或屏蔽log'''
	old=open(root_dir + "/PhoneClient/proguard-project.txt")
	try:
		lines=old.readlines()
	finally:
		old.close()
	
	if print_log_phone == 'true':
		newlines=[]
		pointLog = 0
		for line in lines:
			if '# Remove Logging' in line:
				pointLog=1
				newlines.append(line)
			else :
				if pointLog == 1:
					if '#' in line:
						line = line
					else:
						line = '#' + line		
				newlines.append(line)	
	elif print_log_phone == 'false':
		newlines=[]
		pointLog = 0
		for line in lines:
			if '# Remove Logging' in line:
				pointLog=1
				newlines.append(line)
			else:	
				if pointLog == 1:
					if '#' in line:
						line = line[1:len(line)]
					else:
						line = line
				newlines.append(line)		
	
	new=open(root_dir + "/PhoneClient/proguard-project.txt","w")
	new.writelines(newlines)
	new.close()


def modify_car_log(root_dir, print_log_car):
	'''修改 car proguard-project.txt 打开或屏蔽log'''
	old=open(root_dir + "/CarClient/proguard-project.txt")
	try:
		lines=old.readlines()
	finally:
		old.close()
	
	if print_log_car == 'true':
		newlines=[]
		pointLog = 0
		for line in lines:
			if '# Remove Logging' in line:
				pointLog=1
				newlines.append(line)
			else :
				if pointLog == 1:
					if '#' in line:
						line = line
					else:
						line = '#' + line		
				newlines.append(line)	
	elif print_log_car == 'false':
		newlines=[]
		pointLog = 0
		for line in lines:
			if '# Remove Logging' in line:
				pointLog=1
				newlines.append(line)
			else:	
				if pointLog == 1:
					if '#' in line:
						line = line[1:len(line)]
					else:
						line = line
				newlines.append(line)			
	
	new=open(root_dir + "/CarClient/proguard-project.txt","w")
	new.writelines(newlines)
	new.close()


def package_car(root_dir):
	'''打包car'''
	os.chdir(root_dir + "/CarClient")
	os.system('ant release -f build.xml')
	print "CarClient >>>>>>>>>>>>>>>>>>>>打包完成"


def package_phone(root_dir):
	'''打包phone'''
	os.chdir(root_dir + "/PhoneClient")
	os.system('ant release -f build.xml')
	print "PhoneClient >>>>>>>>>>>>>>>>>>打包完成"


def get_phone_ver_name(root_dir):
	'''获取 version name'''
	#打开xml文档
	dom = xml.dom.minidom.parse(root_dir + '/PhoneClient/AndroidManifest.xml')
	#得到文档元素对象
	root = dom.documentElement
	v = root.getAttribute("android:versionName")
	return v
	
def get_car_ver_name(root_dir):
	'''获取 version name'''
	#打开xml文档
	dom = xml.dom.minidom.parse(root_dir + '/CarClient/AndroidManifest.xml')
	#得到文档元素对象
	root = dom.documentElement
	v = root.getAttribute("android:versionName")
	return v


def get_branch_name():
	'''获取 branch name'''
	t=os.popen("git branch").read()
	l = t.split('\n')
	branch =''
	for name in l:
		if '* ' in name:
			length = len(name)
			branch = name[2:length]
	print branch
	return branch

def checkout_branch(branch, root_dir):
	os.chdir(root_dir)
	os.system('git pull')
	os.system('git add -A')
	os.system('git reset --hard HEAD')
	os.system('git checkout ' + branch)

def get_remote_branchs_name():
#	os.chdir(root_dir)
	os.chdir("/Users/peter/git/xui")
	os.system('git pull')
	'''获取 branchs name'''
	t=os.popen("git branch -a").read()
	l = t.split('\n')
	branches = [];
	for name in l:
		if 'remotes' in name and (not 'HEAD' in name) and (not 'master' in name) and (('rl_p_v' in name) or 'develop' in name):
			length = len(name)
			name = name[17:length]
			branches.append(name.strip());
	print branches
	return branches

def copy_car_apk_to_target_folder(root_dir, target_apk_dir, branch, version, extend):
	'''拷贝car apk 到 target 目录'''
	src = root_dir + "/CarClient/bin/CarClient-release.apk"
	dst = target_apk_dir + "/CarClient_" + branch + "_v" + version + extend + ".apk";
	shutil.copy(src,dst)
	
def copy_car_apk_to_target_folder_release(root_dir, target_apk_dir, version, extend):
	'''拷贝car apk 到 target 目录'''
	src = root_dir + "/CarClient/bin/CarClient-release.apk"
	dst = target_apk_dir + "/xuic_" + extend + "v" + version + ".apk";
	shutil.copy(src,dst)


def copy_phone_apk_to_target_folder(root_dir, target_apk_dir, branch, version, extend):
	src = root_dir + "/PhoneClient/bin/PhoneClient-release.apk"
	dst = target_apk_dir + "/PhoneClient_" + branch + "_v" + version + extend +".apk"
	shutil.copy(src,dst)
	
	
def copy_phone_apk_to_target_folder_release(root_dir, target_apk_dir, version, extend):
	src = root_dir + "/PhoneClient/bin/PhoneClient-release.apk"
	dst = target_apk_dir + "/xuip_" + extend + "v" + version +".apk"
	shutil.copy(src,dst)


def update_tools_car_apk(root_dir):
	src = root_dir + '/CarClient/bin/CarClient-release.apk'
	dst = root_dir + '/BuildTools/src/asserts_phone/skywindow/apk/CarClient.apk';
	shutil.copy(src, dst)


def backup_phone_assert(root_dir):
	src_dir = root_dir + '/PhoneClient/assets/skywindow'
	dst_dir = root_dir + '/BuildTools/src/asserts_phone/skywindow'
	exist = os.path.exists(src_dir)
	if exist:
		if len(os.listdir(src_dir)) > 0:
			distutils.dir_util._path_created = {}
			copy_tree(src_dir, dst_dir)


def clean_phone_assert(root_dir):
	src = root_dir + '/PhoneClient/assets/skywindow'
	exist = os.path.exists(src)
	if exist:
		#会删除skywindow文件夹
		shutil.rmtree(src)

def clean_bin(root_dir):
	src_car = root_dir + '/CarClient/bin'
	src_phone = root_dir + '/PhoneClient/bin'
	exist = os.path.exists(src_car)
	if exist:
		shutil.rmtree(src_car)
	exist = os.path.exists(src_phone)
	if exist:
		shutil.rmtree(src_phone)

def update_phone_assert(root_dir):
	src_dir = root_dir + '/BuildTools/src/asserts_phone/skywindow'
	dst_dir = root_dir + '/PhoneClient/assets/skywindow'
	exist = os.path.exists(src_dir)
	if exist:
		#是一个bug 反复操作会失败，需要清下缓存再copy
		distutils.dir_util._path_created = {}
		copy_tree(src_dir, dst_dir)


def backup_car_assert(root_dir):
	src_dir = root_dir + '/CarClient/assets/video'
	dst_dir = root_dir + '/BuildTools/src/asserts_car/video'
	exist = os.path.exists(src_dir)
	if exist:
		if len(os.listdir(src_dir)) > 0:
			distutils.dir_util._path_created = {}
			copy_tree(src_dir, dst_dir)


def clean_car_assert(root_dir):
	src = root_dir + '/CarClient/assets/video'
	exist = os.path.exists(src)
	if exist:
		#会删除skywindow文件夹
		shutil.rmtree(src)
#	if exist:
#		os.remove(src)


def update_car_assert(root_dir):
	src_dir = root_dir + '/BuildTools/src/asserts_car/video'
	dst_dir = root_dir + '/CarClient/assets/video'
	exist = os.path.exists(src_dir)
	if exist:
		distutils.dir_util._path_created = {}
		copy_tree(src_dir, dst_dir)
#	shutil.copy(src_dir, dst_dir)

def test_str():
	return "123"

def modify_phone_mix(root_dir, mix):
	'''修改 phone project.properties 打开或屏蔽混淆'''
	old=open(root_dir + "/PhoneClient/project.properties")
	try:
		lines=old.readlines()
	finally:
		old.close()
	
	if mix == 'true':
		newlines=[]
		for line in lines:
			if 'proguard.config=proguard-project.txt' in line:
				if '#' in line:
					line = 'proguard.config=proguard-project.txt\n'
			newlines.append(line)
	elif mix == 'false':
		newlines=[]
		for line in lines:
			if 'proguard.config=proguard-project.txt' in line:
				line = '#proguard.config=proguard-project.txt\n'
			newlines.append(line)
	new=open(root_dir + "/PhoneClient/project.properties","w")
	new.writelines(newlines)
	new.close()

def modify_car_mix(root_dir, mix):
	'''修改 car project.properties 打开或屏蔽混淆'''
	old=open(root_dir + "/CarClient/project.properties")
	try:
		lines=old.readlines()
	finally:
		old.close()
	
	if mix == 'true':
		newlines=[]
		for line in lines:
			if 'proguard.config=proguard-project.txt' in line:
				if '#' in line:
					line = 'proguard.config=proguard-project.txt\n'
			newlines.append(line)
	elif mix == 'false':
		newlines=[]
		for line in lines:
			if 'proguard.config=proguard-project.txt' in line:
				line = '#proguard.config=proguard-project.txt\n'
			newlines.append(line)
	new=open(root_dir + "/CarClient/project.properties","w")
	new.writelines(newlines)
	new.close()

def open_folder(target_apk_dir):
	'''打开目标文件夹'''
	path = target_apk_dir
	if sys.platform == 'darwin':
	    os.system('open ' + path)
	elif sys.platform == 'linux2':
	    print 'not support linux'
	elif sys.platform == 'win32':
	    print 'not support win32'
