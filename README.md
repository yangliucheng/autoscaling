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

# questions remaining
## 多线程问题
* 已通过临时方案解决（限制规则在上一次没有使用完成后继续使用）冷切时间以marathon_name,app_id,scale_type为标识，并没有包括后面的扩容策略，导致多次“被认为是相同的规则”获取了未记录扩容或者指标收集时间之前的记录，因此多条相同的信息会导致结果都满足扩缩容而执行扩缩容，这个问题下一个版本考虑较好的解决方案。

## 日志记录
* 当前已记录扩缩容日志到mysql，代码日志考虑通过统一的日志格式化模块处理
























