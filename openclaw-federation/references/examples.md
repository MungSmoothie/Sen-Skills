# 行为示例

## 示例 1：自动路由到 ops
Telegram 群里的用户消息：
- “今晚 Plex 很卡，帮我看看哪里有问题。”

期望联邦行为：
1. coordinator bot 在群里先确认接单
2. coordinator 读取 presence，发现 ops bot 在线且不忙
3. coordinator 向 `claw:tasks` 发出一条任务
4. ops bot claim 任务、排查问题，并把结果写入 `claw:results`
5. coordinator 在 Telegram 中做汇总，不暴露原始 payload

## 示例 2：自动路由到 lab
Telegram 群里的用户消息：
- “谁能帮我抓一下这个商品链接的标题和价格？”

期望联邦行为：
1. 当前 coordinator 判断这需要浏览器或抓取能力
2. 系统优先选择 lab bot，而不是 ops bot
3. lab bot 返回结构化结果
4. coordinator 在群里发一条简短回答，并可附带下一步建议

## 示例 3：超时与回退
Telegram 群里的用户消息：
- “为什么我的媒体索引器一直卡住？”

期望联邦行为：
1. coordinator 先把任务委派给 ops
2. ops 超时或离线
3. coordinator 在 Telegram 群里发出简短超时说明
4. coordinator 重试一次，或者改为执行一次更小范围的本地检查
5. coordinator 避免让同一个任务无限来回弹跳
