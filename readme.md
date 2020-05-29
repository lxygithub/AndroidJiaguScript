### 基于python 3的360一键加固、签名和生成多渠道包脚本
#### 1.配置
```python
options = {
    "jiagu": "jiagu.jar",  # jar路径
    "username": "xxxx",# 360加固用户名
    "password": "xxxx",#360加固密码
    "output_dir": "E:/xxxxx/",#渠道包输出目录 不存在会自动创建
    #用于手动签名方法，不需要时可以不配置
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
```
#### 2.使用
确保 *source_dir*中配置的目录下有名字包含release的apk安装包，
在该目录下打开命令行窗口，执行：

> python build.py aaa
 
命令即可，（其中aaa或bbb为*source_dir*中配置的目录名称）任务开始后，脚本会按照时间排序找到最新的一个release包，
从而自动完成剩余的操作。