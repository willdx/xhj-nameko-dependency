# 薪行家代付nameko dependency


## install

```shell
pip install xhj-nameko-dependency
```

## config

通过yaml文件方式配置nameko环境变量

```
xhj:
  MCHNT_NUM: ${XHJ_MCHNT_NUM}
  API_BASE_URL: ${XHJ_API_BASE_URL}
  DES_KEY: ${XHJ_DES_KEY}
  PUBLIC_KEY: ${XHJ_PUBLIC_KEY}
  PRIVATE_KEY: ${XHJ_PRIVATE_KEY}
```

## How to use?

```python
from xhj import XHJ

class TestService(Base):
    xhj = XHJ()

    @rpc
    def create_package(self, data):
        return self.xhj.call("remit/createpackage", data)
```


