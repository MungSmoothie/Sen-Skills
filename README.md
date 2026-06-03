# Sen-Skills

个人使用的 OpenClaw Skills 集合

## Skills

| Skill | 描述 |
|-------|------|
| [ai-daily-news](./ai-daily-news/) | 固定中文报刊模板的 AI / 科技日报生成技能，强调真实新闻、稳定版式与高信息密度 |
| [federation-evolution](./federation-evolution/) | 联邦协同进化技能，用于在 bot 联邦内同步技能、经验、模式和教训 |
| [imagetoolbox-cli](./imagetoolbox-cli/) | 便携版图片处理 CLI，可用于素材切分、去背景、黑白双底抠图、透明素材规范化和指定框裁切 |
| [openclaw-federation](./openclaw-federation/) | 多 bot 联邦协作系统，通过 Redis + Telegram 实现任务路由与协调 |
| [sen-frontend-design](./sen-frontend-design/) | 前端设计技能，基于 Element Plus、shadcn/ui、MUI、Untitled UI |

## 使用方式

将 skill 目录复制到 `~/.openclaw/workspace/skills/` 即可使用。

### ImageToolBox CLI

`imagetoolbox-cli` 内置便携运行时，不需要额外携带 ImageToolBox 项目代码。首次使用前安装依赖：

```bash
python3 ~/.openclaw/workspace/skills/imagetoolbox-cli/scripts/run_imagetoolbox.py --install-deps
```

复制到 Codex skills 目录时也可以使用：

```bash
python3 ~/.codex/skills/imagetoolbox-cli/scripts/run_imagetoolbox.py --install-deps
```
