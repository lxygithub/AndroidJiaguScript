# -*- coding: utf-8 -*-
import ctypes
import os
import subprocess
import sys

options = {
    "jiagu": "jiagu.jar",  # jar路径
    "username": "xxxx",# 360加固用户名
    "password": "xxxx",#360加固密码
    "output_dir": "E:/xxxxx/",#渠道包输出目录 不存在会自动创建
    "apksigner": "C:/Users/Administrator/AppData/Local/Android/Sdk/build-tools/29.0.3/apksigner.bat",  # apksigner 路径
    "channels_path": "Channel.txt",  # 渠道信息文件路径
}

# 签名密钥
key_store = {
    "keystore_path": "xxxx.jks",# 签名路径
    "key_pass": "xxx",
    "ks_key_alias": "xxx",
    "ks_pass": "xxx",
}
# release包目录 可配置多个
source_dir = {
    "aaa": "E:/xxxx/",
    "bbb": "E:/xxxxx/",
}

release_apk = None

# 字体颜色定义 text colors
FOREGROUND_BLUE = 0x09  # blue.
FOREGROUND_GREEN = 0x0a  # green.
FOREGROUND_RED = 0x0c  # red.
FOREGROUND_YELLOW = 0x0e  # yellow.

# get handle
std_out_handle = ctypes.windll.kernel32.GetStdHandle(subprocess.STD_OUTPUT_HANDLE)


def set_cmd_text_color(color, handle=std_out_handle):
    Bool = ctypes.windll.kernel32.SetConsoleTextAttribute(handle, color)
    return Bool


# reset white
def resetColor():
    set_cmd_text_color(FOREGROUND_RED | FOREGROUND_GREEN | FOREGROUND_BLUE)


# red
def printRed(mess):
    set_cmd_text_color(FOREGROUND_RED)
    sys.stdout.write(mess + '\n')
    resetColor()


# 获取最新的apk包
def find_apk(name):
    dir_path = source_dir[name]
    if not os.path.exists(dir_path):
        printRed("you specified release dir is not exist，please check your input")
        return
    file_list = os.listdir(dir_path)
    # 过滤掉非release包
    file_list = list(filter(lambda x: "release" in x, file_list))
    # 按时间排序
    file_list.sort(key=lambda fn: os.path.getmtime(dir_path + fn) if not os.path.isdir(dir_path + fn) else 0)

    if file_list:
        # 获取最新的一个
        newest = dir_path + file_list[-1]
        return newest
    else:
        printRed("not found release apk，please confirmed your apk building process is finished！")
        return


# 获取版本号
def get_apk_version(apk_name):
    # source_dir["baby"]
    return apk_name.split("-")[-1].replace(".apk", "") + "_release"


# 360加固登录
def _360_login_success():
    command_login = "java -jar -Dfile.encoding=UTF-8 {jiagu_360_jar} -login {username} {password}".format(
        jiagu_360_jar=options["jiagu"], username=options["username"], password=options["password"]
    )
    login_result = subprocess.Popen(command_login, shell=True, stderr=subprocess.PIPE)
    login_result.wait()
    return login_result.returncode == 0


# 360加固导入签名信息
def _360_load_sign():
    command_import_sign_info = "java -jar -Dfile.encoding=UTF-8 {jiagu_360_jar} -importsign {keystore_path} {keystore_password} {alias} {alias_password}".format(
        jiagu_360_jar=options["jiagu"],
        keystore_path=key_store["keystore_path"],
        keystore_password=key_store["key_pass"],
        alias=key_store["ks_key_alias"],
        alias_password=key_store["ks_pass"],
    )
    print(command_import_sign_info)
    import_result = subprocess.Popen(command_import_sign_info, shell=True, stderr=subprocess.PIPE)
    import_result.wait()
    return import_result.returncode == 0


# 360加固导入渠道信息
def _360_load_channels():
    command_import_channels = "java -jar -Dfile.encoding=UTF-8 {jiagu_360_jar} -importmulpkg {channels_path}".format(
        jiagu_360_jar=options["jiagu"],
        channels_path=options["channels_path"],
    )
    import_result = subprocess.Popen(command_import_channels, shell=True, stderr=subprocess.PIPE)
    import_result.wait()
    return import_result.returncode == 0


# 创建目标文件夹
def _create_dest_dir(name):
    if release_apk:
        # dest dir
        (apk_path, file_name) = os.path.split(release_apk)
        dest_dir = options["output_dir"] + name + "_" + get_apk_version(file_name)
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)

        # subprocess.call("chmod -R 775 {jiagu_tmp}".format(jiagu_tmp=dest_dir), shell=True)
        return dest_dir
    else:
        printRed("------------------------------create dest_dir failed!!------------------------------")


# 加固
def _jiagu(release_apk, dest_dir):
    # jiagu
    command_jiagu = 'java -jar -Dfile.encoding=UTF-8 {jiagu_360_jar} -jiagu {apk_file} {output_dir} -autosign -automulpkg'.format(
        jiagu_360_jar=options["jiagu"],
        apk_file=release_apk,
        output_dir=dest_dir, )
    jiagu_result = subprocess.Popen(command_jiagu, shell=True, stderr=subprocess.PIPE)
    jiagu_result.wait()
    _delete_cache()
    return jiagu_result.returncode == 0


def apk_build(name):
    if _360_login_success():
        if _360_load_sign():
            if _360_load_channels():
                dest_dir = _create_dest_dir(name)
                _jiagu(release_apk, dest_dir)
            else:
                printRed("------------------------------import channels failed!!------------------------------")
        else:
            printRed("------------------------------import sign info failed!!------------------------------")
    else:
        printRed("------------------------------login failed!!------------------------------")


# 手动签名
def sign_apk(keystore_path, dest_apk, unsigned_apk):
    command_sign = "{apksigner} sign --ks {keystore_path} --ks-pass pass:{keystore_pass} --out {dest_apk} {unsigned_apk}".format(
        apksigner=options["apksigner"],
        keystore_path=keystore_path,
        keystore_pass=key_store["key_pass"],
        dest_apk=dest_apk,
        unsigned_apk=unsigned_apk,
    )

    sign_result = subprocess.Popen(command_sign, shell=True, stderr=subprocess.PIPE)
    sign_result.wait()
    if sign_result.returncode == 0:
        print("------------------------------signed success!!------------------------------")


def _delete_cache():
    if os.path.exists("jiagu.db"):
        os.remove("jiagu.db")


if __name__ == '__main__':
    # python build.py baby
    _delete_cache()
    argv_name = sys.argv[1]
    release_apk = find_apk(argv_name)
    if release_apk:
        apk_build(argv_name)
