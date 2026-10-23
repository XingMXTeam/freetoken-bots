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

**在线状态页：** [maoxunxing.com/ai/free-llm-models](https://maoxunxing.com/ai/free-llm-models/)
把本仓库的数据渲染成网页（名单、体检结果、三步上手），每小时从
`data/` 刷新一次。

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

## 全部平台

深度接入的是 OpenRouter（实时名单 + 体检）。其他免费来源已全部
登记进 `scripts/providers.py`，各家名单在
`data/models-<平台>.json`，总索引在 `data/providers.json`。
标为**种子**的名单是策展起始清单（这些平台的目录要 key 才能读）：
把对应 key 加为仓库 Secret 后，每日任务会自动升级为 API 实时
名单并开始探活。额度细节见 `data/providers.json`。

| 平台 | 类型 | 免费额度（简） | 名单状态 |
|------|------|----------------|----------|
| OpenRouter | 免费层 | 免费模型 50 次/天 | **实时** + 体检 |
| Google Gemini（AI Studio） | 免费层 | Flash 最高约 1500 次/天（社区实测） | 种子 → 加 `GEMINI_API_KEY` 转实时 |
| Groq | 免费层 | 约 1000 次/天，另有约 20 万 token/天总帽 | 种子 → 加 key 转实时 |
| NVIDIA NIM | 免费层 | 约 40 RPM、单模型最高 1 万次/天（社区） | 种子 → 加 key 转实时 |
| Cloudflare Workers AI | 免费层 | 每天 1 万 Neurons（约 400 万输入 token） | 种子 → 加 token 转实时 |
| 智谱 GLM Flash | 免费层 | Flash 端点免费，约 1 并发 | 种子 → 加 key 转实时 |
| 魔搭 ModelScope | 免费层 | 约 2000 次/天（社区） | 种子 → 加 key 转实时 |
| 硅基流动 | 免费层 | 部分模型免费 | 种子 → 加 key 转实时 |
| Mistral | 试用额度 | 每月约 $10 额度，非免费层 | 种子 → 加 key 转实时 |
| Cerebras | 试用额度 | $5、30 天、要绑卡 | 种子 → 加 key 转实时 |
| Ollama（本地） | 本地 | 无限（看自己硬件） | 种子 → 设 `OLLAMA_HOST` 读本机实装 |
| OpenCode Zen | 锁应用内 | DeepSeek 免费版仅应用内可用 | 仅登记说明，API 无法探活 |

## 路线图

- [x] OpenRouter 名单 + 体检（GitHub Actions 每日自动）
- [x] Pi agent 配方
- [x] 平台注册表：Gemini、Groq、NVIDIA NIM、Cloudflare Workers
      AI、智谱、魔搭、硅基流动、Mistral、Cerebras、Ollama、
      OpenCode Zen（种子名单，加 key 后转实时）
- [ ] 上述平台的实时体检（需维护者把各家 key 加为仓库 Secret）
- [ ] 更多配方：Claude Code、Cursor、OpenCode

## 出处与声明

名单逻辑源自 [@MinLiBuilds](https://grokbot.dev/marketplace/freetoken/)
的 FreeToken 模板，本仓库在此基础上加了实测体检、防收费护栏和
集成配方。维护者 [@maoxunxing](https://x.com/maoxunxing)：这些模型
是他每天真实在用的，体检数据由此而来。

与 OpenRouter 及任何模型厂商无隶属关系。免费政策、额度和可用性
随时变化，请以 `data/` 里的时间戳判断每条信息的新鲜程度。
