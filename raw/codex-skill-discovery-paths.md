# Codex Skill 发现路径的官方边界

## 核心观点

- 自定义 Skill 的稳定安装路径，应以官方文档承诺的发现目录为准，而不是依赖当前环境里碰巧可用的内部路径。

## 记录到的信息

- 官方文档列出的可发现位置包括：
  - repo 级 `.agents/skills`
  - 用户级 `$HOME/.agents/skills`
  - admin 级 `/etc/codex/skills`
  - 随 Codex 打包的 system skills
- 文档明确说明 Codex 会扫描这些位置，并支持 symlink。
- 官方页面没有把 `~/.codex/skills` 列为用户可写的官方发现目录。

## 我的判断

- 实践上，团队内共享自定义 Skill 时，最好统一以 `$HOME/.agents/skills` 作为用户级安装路径。
- 如果某些环境里 `~/.codex/skills` 也能工作，更合理的理解是实现细节或内置目录，而不是对用户稳定承诺的接口。
- 分享安装方式时，要明确区分“官方承诺目录”和“当前环境可用路径”，避免未来升级后踩坑。
