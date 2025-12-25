核心任务	执行指令	交付物
苏格拉底提问引擎	实现socraticHint函数：输入用户步骤（字符串），返回提示问题（最多3层）。使用if-else规则，避免复杂逻辑	实时提问系统
学习跟踪与报告	用Zustand记录步骤耗时、错误类型、提示触发次数；用react-pdf生成单页PDF报告（含前3个错误点+1道推荐题）	学习总结PDF生成器
AI集成与通信	WebSocket服务，连接GPT-4 Turbo。当用户提交步骤时，调用socraticHint并返回响应	全栈联调Demo
