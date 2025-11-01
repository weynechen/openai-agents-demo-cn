openai agents 原版使用的openai默认的大模型和一些英文的示例，不利于中文环境使用。这里替换为使用deepseek的中文示例。

# 使用
将代码拷贝下来
```bash
git clone git@github.com:weynechen/openai_agents_example_cn.git
```
使用uv 初始化
```bash
uv sync
```
配置.env
```bash
cp .env.example .env
```
设置 DEEPSEEK_API_KEY

运行
```bash
uv run hello.py
```
# 观察

该项目增加了prompt观察功能。在out文件夹下，会有prompt的记录，便于理解agents背后封装的信息
```txt
=== Prompt Call #1 ===
Timestamp: 20251101_142203_925705
Model: deepseek-chat

=== Formatted Prompt ===

[SYSTEM]
You are a helpful assistant

[USER]
写一个秋天为主题的三行诗


=== Response ===

Content: 枫叶吻别枝头，
风拾起一地私语，
岁月在脉络里静流成秋。

=== Token Usage ===
Prompt Tokens: 16
Completion Tokens: 23
Total Tokens: 39
```

运行 handoffs.py
```txt
=== Prompt Call #1 ===
Timestamp: 20251101_144935_780046
Model: deepseek-chat

=== Formatted Prompt ===

[SYSTEM]
根据用户的问题，分类到历史或地理领域，并转交给相应的 agent。

[USER]
北京在哪个省？

=== AVAILABLE TOOLS ===
{
  "type": "function",
  "function": {
    "name": "transfer_to____agent",
    "description": "Handoff to the 历史 agent agent to handle the request. ",
    "parameters": {
      "additionalProperties": false,
      "type": "object",
      "properties": {},
      "required": []
    }
  }
}
{
  "type": "function",
  "function": {
    "name": "transfer_to____agent",
    "description": "Handoff to the 地理 agent agent to handle the request. ",
    "parameters": {
      "additionalProperties": false,
      "type": "object",
      "properties": {},
      "required": []
    }
  }
}


=== Response ===

Content: 这个问题属于地理领域，我将为您转交给地理专家来处理。
Tool Calls: ["ChatCompletionMessageToolCall(index=0, function=Function(arguments='', name='transfer_to____agent'), id='call_00_CC1Dru5oGElCRTe5k7oZ8mDz', type='function')"]

=== Token Usage ===
Prompt Tokens: 216
Completion Tokens: 22
Total Tokens: 238


=== Prompt Call #2 ===
Timestamp: 20251101_144938_543647
Model: deepseek-chat

=== Formatted Prompt ===

[SYSTEM]
你是一个地理学家，你只会回答关于地理的问题。

[USER]
北京在哪个省？

[ASSISTANT]
这个问题属于地理领域，我将为您转交给地理专家来处理。

[TOOL]
{"assistant": "\u5730\u7406 agent"}


=== Response ===

Content: 北京是中国的首都，位于华北平原的北部，但它并不属于任何一个省。北京是中国的直辖市之一，与省同级，直接由中央政府管辖。因此，北京本身就是一个省级行政区划单位。

=== Token Usage ===
Prompt Tokens: 60
Completion Tokens: 42
Total Tokens: 102

```

