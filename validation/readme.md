Validation 的核心不是「给每个模块加路由」,
而是提供一套统一的验证能力。HTTP 路由只是其中一种入口。
更准确的说法是:它是一个开发验证层(Validation Layer),
可以用来验证 Ingress、Document、
未来的 Processor、Retriever 等模块,对吧?


http://localhost:8000/static/validation/validation.html