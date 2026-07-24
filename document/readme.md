你这个 document 目录其实已经进入了知识库的核心业务层了,这四个目录我建议职责划分清楚。dispatcher 就是文档调度中心,也就是你之前一直说的 Document Dispatch Center,负责决定一份文档应该走哪条处理链路,比如 PDF 要不要走 OCR、Markdown 是否直接解析,本身不直接处理文档。parser 才是真正做文档解析的,负责把原始文档转成统一的数据结构。module 这个名字我反而建议你认真考虑一下,因为比较泛,通常可能放领域对象、插件实现或公共组件,不如直接叫 models 或 domain 更清晰。如果放的是插件实现,也可以叫 plugins。如果是处理流程,就叫 processors。这样一看名字就知道里面放什么,比抽象的 module 更好维护。


service
   |
   v
dispatcher
   |
   v
parser
   |
   v
model