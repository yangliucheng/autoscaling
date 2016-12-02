# autoscaling：the auto scaling module

# build program
* bash build/build.sh {package_name} <br/>
* 打包后tar包放在bin目录
* 复制{package_name}-v1.1.tgz（目前版本是1.1）到目标机器

# deploy program
* 获取上一步的{package_name}-v1.1.tgz后，解压到任意目录
* 配置文件主目录文件stardigi_policy.json<br/>
![image](https://github.com/yangliucheng/autoscaling/blob/develop/golang/doc/1.jpg)
* bash deploy/deploy.sh
* ps -ef | grep Stardigi-Policy查看程序的运行状态

# RUN OR STOP
* bash scli.sh start
* bash scli.sh stop

# questions remaining

## 日志记录
* 当前已记录扩缩容日志到mysql，代码日志考虑通过统一的日志格式化模块处理
























