## 天青汉马防火墙配置解析工具 ##
---

本脚本主要用于天青汉马防火墙配置解析，是对地址对象、服务对象和访问控制策略解析，并将策略写到电子表格，可用于日常备份。
由于调试用的配置文件是实际运行的文件，所以在这里未提供示例。

### 依赖 ###

1. python3
2. xlwt     电子表格库 -> pip install xlwt

### USAGE ###

```bash
usage: config_parse.py [-h] -f FILENAME

optional arguments:
  -h, --help            show this help message and exit
  -f FILENAME, --file FILENAME
                        指定配置文件
```

### Demo ###

...


