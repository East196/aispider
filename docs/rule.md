# 规则说明

```
<root>
    <parse type='re' restr="%s" name='abc' list='True' />
    <parse type='json' jsonpath='jjj' list='False'/>
    <parse type='soup' name='aname' cssselector='div' list='True'>
        <parse type='soup' name='sub' cssselector='a.sub'/>
        <parse type='soup' name='sup' cssselector='a.sup'/>
    </parse>
</root>
```

规则解析自 root起

首先 定义进入的网页url
抓取内容规则如下：
- json表示解析json文档，内容使用jsonpath直接获取

- soup表示解析html文档，内容使用cssselector获取
其中 如果节点并非叶子节点，则取选择到的soup对象进入下一层继续解析
     如果节点是叶子节点，则直接取内容作为最后结果
