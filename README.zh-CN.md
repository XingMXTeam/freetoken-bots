# FreeToken Bots（免费模型机器人）

**给 AI agent 用的免费大模型名单：每天重新核查，并真实调用验证还能用。**

[English](README.md)

「免费模型清单」最大的问题是过期：模型改名、免费层缩水、目录里
写着免费、实际调用却返回 429 甚至 404。这个仓库把免费层当成一个
每天变化的目标来盯：

- **每日名单**：脚本重新读取 OpenRouter 公开目录，只保留定价字段
  全为 0、支持工具调用、输出文本的模型。今天全目录 468 个模型里
  合格的只有 16 个。→ [`data/free-models.json`](data/free-models.json)
- **实测体检**：对头部模型发真实的极小调用，把结果（可用 / 限流 /
  无端点）和时间戳一起记录。→ [`data/status.json`](data/status.json)
- **集成配方**：把这些模型接进 agent 产品的现成配置，每份都真实
  跑通过才发布。→ [`recipes/`](recipes/)

## 当前名单（2026-10-23 刷新）

排名前五：`poolside/laguna-s-2.1:free`、`poolside/laguna-xs-2.1:free`、
`cohere/north-mini-code:free`、`thinkingmachines/inkling-small:free`、
`thinkingmachines/inkling:free`。完整 16 个见
[`data/free-models.md`](data/free-models.md)，另加兜底路由
`openrouter/free`（服务端自动挑选可用的免费模型）。

## 最近一次实测（2026-10-22，人工探测）

- `cohere/north-mini-code:free`：可用，且随后在 Pi agent 里完成了
  真实的写文件、执行命令任务，产出经人工核对无误
- `openrouter/free`：可用，约 1.3 秒返回
- `google/gemma-4-31b-it:free`：成功一次后 429（上游共享池限流）
- `poolside/laguna-s-2.1:free`：直连 429，但经路由调用时可用
- `nvidia/nemotron-3-super-120b-a12b:free`：目录在册，调用 404

一句话教训：**免费模型必须配故障转移**，把单个免费模型写死进
agent 是用不了几天的。

## 快速开始

1. 在 [openrouter.ai](https://openrouter.ai) 免费注册并创建 API key
   （不用绑卡，不用充值）。
2. 选一份配方，比如 [Pi 编程 agent](recipes/pi/)：两个配置文件
   丢进 `~/.pi/agent/` 即可开跑。
3. 任何兼容 OpenAI 接口的客户端：base URL 用
   `https://openrouter.ai/api/v1`，模型填 `openrouter/free` 或名单
   里任意 `:free` 模型。

## 防收费护栏

- 只白名单 `:free` 结尾的模型 ID。同名不带 `:free` 的版本通常是
  **收费版**，这是最常见的坑。
- 在 OpenRouter 后台给 key 设一个很小的消费上限，作为第二道锁。
- 只用自己的 key。共享、拼车 key 给公众用违反各家免费条款，
  额度也撑不住。
- 体检要省着用：每次探测都消耗你自己 agent 的同一份每日额度
  （本仓库每天约 6 次极小调用）。

## 路线图

- [x] OpenRouter 名单 + 体检（GitHub Actions 每日自动）
- [x] Pi agent 配方
- [ ] 更多来源：Gemini 免费层、Groq、NVIDIA NIM、Cloudflare
      Workers AI，以及国内免费端点（智谱 GLM Flash、魔搭、硅基流动）
- [ ] 更多配方：Claude Code、Cursor、OpenCode

## 出处与声明

名单逻辑源自 [@MinLiBuilds](https://grokbot.dev/marketplace/freetoken/)
的 FreeToken 模板，本仓库在此基础上加了实测体检、防收费护栏和
集成配方。维护者 [@maoxunxing](https://x.com/maoxunxing)：这些模型
是他每天真实在用的，体检数据由此而来。

与 OpenRouter 及任何模型厂商无隶属关系。免费政策、额度和可用性
随时变化，请以 `data/` 里的时间戳判断每条信息的新鲜程度。
