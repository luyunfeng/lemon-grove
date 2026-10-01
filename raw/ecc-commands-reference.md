# ECC 命令参考：Claude Code 生产力工具集

# ECC 命令参考

> **说明**：ECC（Everything Claude Code）提供了一套丰富的斜杠命令（Slash Commands），用于在 Claude Code 中快速触发特定工作流。以下命令基于实际使用经验和公开资料整理。

---

## 命令分类总览

| 分类 | 命令数量 | 说明 |
|------|---------|------|
| **PR & 代码审查** | 5+ | PR 创建、代码审查、提交管理 |
| **项目管理** | 5+ | 项目初始化、工作流操作、任务跟踪 |
| **产品开发** | 10+ | 产品分析、能力规划、设计验证 |
| **工程实现** | 15+ | 代码实现、测试、构建修复 |
| **安全 & 合规** | 5+ | 安全审计、风险审查 |
| **数据 & 研究** | 5+ | 数据分析、市场研究 |
| **运维 & 部署** | 5+ | 生产审计、调度、发布 |
| **Prompt 优化** | 3+ | Prompt 分析、优化 |

---

## 一、PR & 代码审查

### `/ecc:pr`
**作用**：从当前分支创建 GitHub PR，自动发现模板、分析变更。

**使用场景**：
- 完成功能开发后快速创建 PR
- 自动填充 PR 描述（基于 commit message 和代码变更）
- 自动关联相关 issue

**示例**：
```bash
/ecc:pr
# 或指定目标分支
/ecc:pr --target main
```

---

### `/ecc:prp-pr`
**作用**：PR 创建和管理的增强版（PRP = PR Process）。

**与 `/ecc:pr` 的区别**：
- 更严格的验证流程
- 自动运行预设的检查清单
- 支持更复杂的 PR 模板

---

### `/ecc:prp-commit`
**作用**：用自然语言描述快速提交（Quick commit with natural language file targeting）。

**示例**：
```bash
/ecc:prp-commit "修复登录页面的样式问题"
# Agent 会自动识别相关文件并生成 commit
```

---

### `/ecc:review` / `/ecc:code-review`
**作用**：代码审查 —— 针对本地未提交变更或 GitHub PR。

**使用方式**：
```bash
# 审查本地未提交变更
/ecc:review

# 审查指定 PR
/ecc:review 123

# 审查指定文件
/ecc:review ./src/auth/login.ts
```

**输出**：结构化审查报告，包含：
- 代码质量问题
- 安全漏洞
- 性能问题
- 建议改进

---

## 二、项目管理

### `/ecc:project-init`
**作用**：检测项目技术栈，生成 ECC 接入的 dry-run 计划。

**流程**：
1. 分析项目结构（package.json、Cargo.toml、go.mod 等）
2. 识别使用的框架和工具
3. 生成推荐的 ECC 配置
4. 输出 dry-run 报告（不实际修改文件）

**示例**：
```bash
/ecc:project-init
# 输出示例：
# Detected: React + TypeScript + Vite
# Recommended skills: react-patterns, typescript-strict, vite-config
# Recommended rules: component-naming, hook-rules
```

---

### `/ecc:projects`
**作用**：列出已知项目及其 instinct（本能/经验）统计。

**输出**：
- 项目名称
- 已学习的技能数量
- 应用的经验模式
- 使用频率

---

### `/ecc:promote`
**作用**：将项目级 instinct 提升为全局级。

**说明**：
- **项目级 instinct**：仅对当前项目生效
- **全局级 instinct**：对所有项目生效
- 用于沉淀跨项目通用的最佳实践

---

### `/ecc:project-flow-ops`
**作用**：跨 GitHub 和 Linear 执行工作流操作。

**功能**：
- 分类 issue 和 PR
- 关联活跃工作项
- 自动更新状态

---

## 三、产品开发

### `/ecc:product-capability`
**作用**：将 PRD 意图、路线图需求或产品讨论转化为可实施的能力计划。

**输入**：
- PRD 文档
- 产品讨论记录
- 路线图项

**输出**：
- 技术实现方案
- 依赖分析
- 风险评估
- 工作量估算

---

### `/ecc:product-lens`
**作用**：在构建前验证"为什么"，运行产品诊断，压力测试产品假设。

**使用场景**：
- 新功能开发前的合理性检查
- 产品方案评审
- 竞品分析

**检查维度**：
- 用户需求匹配度
- 技术可行性
- 商业价值
- 与现有产品的协同

---

## 四、工程实现

### `/ecc:prp-plan`
**作用**：创建全面的功能实现计划，包含代码库分析和模式提取。

**输出**：
1. 代码库结构分析
2. 相关文件识别
3. 实现步骤规划
4. 测试策略
5. 风险点

---

### `/ecc:prp-implement`
**作用**：执行实现计划，带严格验证循环。

**流程**：
1. 读取 `/ecc:prp-plan` 生成的计划
2. 按步骤实现
3. 每步验证（测试、类型检查）
4. 遇到问题自动回滚或调整

---

### `/ecc:build-fix`
**作用**：检测项目构建系统，增量修复构建/类型错误。

**支持**：
- TypeScript
- Go
- Python
- Rust
- Java

**策略**：
- 最小安全变更
- 优先修复阻塞性问题
- 保持代码语义不变

---

### `/ecc:production-audit`
**作用**：本地证据生产就绪审计。

**适用场景**：
- 已发布应用的审计
- 发布前审查
- 合并后检查

**检查项**：
- 性能指标
- 安全合规
- 日志完整性
- 监控覆盖

---

### `/ecc:production-scheduling`
**作用**：生产调度、作业排序、流水线平衡、换线优化。

**适用领域**：
- 制造业生产计划
- CI/CD 流水线优化
- 批处理作业调度

---

## 五、安全 & 合规

### `/ecc:prediction-market-risk-review`
**作用**：审查预测市场、篮子、预言机和交易代理工作流的合规性、安全性、数据质量。

**检查维度**：
- 合规性（法规遵循）
- 安全性（漏洞、风险）
- 数据质量（准确性、完整性）

---

## 六、数据 & 研究

### `/ecc:prediction-market-oracle-research`
**作用**：研究预测市场作为数据源或预言机信号，用于产品、代理、仪表板和策略。

**输出**：
- 数据源评估
- 信号质量分析
- 集成方案
- 风险提示

---

## 七、Prompt 优化

### `/ecc:prompt-optimizer`
**作用**：分析原始 prompt，识别意图和缺口，匹配 ECC 组件（skills/commands/agents/hooks）。

**使用场景**：
- 优化自定义 prompt
- 将自然语言需求转化为结构化 ECC 配置
- 发现缺失的技能或规则

---

## 八、其他实用命令

### `/ecc:prisma-patterns`
**作用**：Prisma ORM 模式 —— 架构设计、查询优化、事务、分页。

**适用**：TypeScript 后端项目使用 Prisma 时。

---

### `/ecc:checkpoint`
**作用**：创建、验证或列出工作流检查点。

**使用场景**：
- 长任务中间保存
- 关键节点备份
- 状态恢复

---

### `/ecc:auto-update`
**作用**：拉取最新 ECC 仓库变更并重新安装当前管理目标。

**建议**：定期运行以保持 ECC 最新。

---

## 命令使用模式

### 典型工作流 1：新功能开发
```bash
# 1. 分析需求并制定计划
/ecc:prp-plan "实现用户登录功能"

# 2. 按 plan 执行实现
/ecc:prp-implement

# 3. 代码自审
/ecc:review

# 4. 提交并创建 PR
/ecc:prp-commit "实现用户登录功能"
/ecc:pr
```

### 典型工作流 2：项目接入 ECC
```bash
# 1. 分析项目结构
/ecc:project-init

# 2. 查看推荐配置
/ecc:projects

# 3. 将项目经验提升为全局
/ecc:promote
```

### 典型工作流 3：生产发布
```bash
# 1. 生产就绪审计
/ecc:production-audit

# 2. 安全审查
/ecc:prediction-market-risk-review  # 或相关安全命令

# 3. 创建发布 PR
/ecc:pr --target production
```

---

## 注意事项

1. **命令前缀**：ECC 命令以 `/ecc:` 开头，与 Claude Code 内置命令（如 `/plan`、`/clear`）区分
2. **上下文感知**：大多数命令会自动读取当前项目上下文
3. **Dry-run 模式**：部分命令（如 `project-init`）默认 dry-run，不会实际修改文件
4. **技能激活**：执行命令时会自动激活相关 Skill
5. **跨 Harness**：ECC 命令设计为可在 Claude Code、Cursor、Codex 等工具间迁移

---

## 相关资源

- [Everything Claude Code GitHub](https://github.com/affaan-m/everything-claude-code)
- [ECC 官网](https://ecc.tools)
- [AgentShield 安全扫描](https://www.npmjs.com/package/ecc-agentshield)
- [ECC 通用包](https://www.npmjs.com/package/ecc-universal)
