# Matt Pocock：AI 时代最该练的，是说清你在乎什么，并让代码库配得上 Agent

来自 @nateherk 对 @mattpocockuk 44 分钟的访谈，Pocock 认为：最值钱的肯定不是追最新模型，是两件事：把你在乎什么说清楚，以及把测试、代码质量和流程做到 agent 能靠得住；他自己试了几个月 Spec 驱动开发，代码反而越来越差。

Youtube 视频：
https://www.youtube.com/watch?v=Z8lf5oWKfj0

Pocock 什么时候开始改主意
自学约十年、职业约八年，对 coding agent 一直偏怀疑。大约 2025 年 12 月 Opus 4.5 出来后，他觉得门槛过了：自己不再手写一行代码。他本来就爱改善同事的工作环境和教学；agent 够用以后，同样的本事转向「怎么让 agent 工作得更好」。

核心：告诉 agent 你在乎什么
人和 agent 之间有一道常被低估的沟通鸿沟。它不知道你到底要什么，也不知道你在乎什么，所以要反复说清楚。代码库没人维护、全是随便拼出来的，agent 也只能交出垃圾，还是 garbage in, garbage out。正确做法像给最差的人类同事兜底：测试、检查、挡住一类错误。经典软件工程因此又有用了。Agent 也能教你，但要保持怀疑，优先读一手材料。他的 /teach 会找可信来源并标注出处，用 AI 当导读，再读原文。

机会在哪
变化大，机会也多：教人、做嵌 AI 的产品、帮公司改系统。咨询或内部晋升都一样，押可带走的能力。模型再强，仍要学：怎么信任、怎么组织多个 agent、给它什么信息、怎么把公司流程翻成 agent 能跑的工作流。代码和数学容易验；真实知识工作更难，把这类流程打包给组织，是一块大机会。

未知的未知与 Grill Me
「Pragmatic Programmer」说：没人一开始就知道自己要什么。他的高频 skill grill me 让 agent 不停追问，挖出你真正在乎的上下文；Grill with Docs 再帮你建领域用语（DDD 里的 ubiquitous language：代码、库表、界面、客户、用户说同一套词）。关键能力是意识到「还有自己不知道的空白」，设计在落成代码之前都不算完成。

怎么显得靠谱
「周末堆作品集」很难建立信任。客户要的是懂他们在乎什么的人。用 agent 快速做出能证明你懂业务的原型就够。真正跑得好的人，往往是最会沟通的人，想清楚了，PR、产品和给 agent 的指令都会清楚。

Spec 驱动为什么踩坑（26:03）
受 AI Engineer 上 OpenAI 一侧「specs are the new code」启发，他在个人类 Descript 的视频编辑仓库里试了几个月：规格越写越细，再让 agent 生成代码。结果代码质量一路下滑，agent 也越做越差。他后来认定：代码本身就是 agent 的工作环境；能安全改动的可维护代码，比一直活在规格里更管用。模型不会读心，skills 和流程会长期需要；大家也低估了 harness（Claude Code、Codex 这类），别只看模型牌子。

模型、Harness、Effort
他现在常用 Claude Code + Opus 5.5。一个鲜明看法是：多数人把 effort 开太高。他自己用 medium，还考虑再降，换更快回复和更省 token，因为测试已经把底线抬起来了。让 agent 能开浏览器、看截图，往往比换更新的模型更赚；环境好的旧 Opus 4.5，可以压过环境差的新模型。Harness 选 Claude Code、Codex 或 Copilot 都行，别纠结太久。

怎么开始
先装一个主流 harness，要不要用他的 skills 随意。他提到 Lauren Tan（Twitter 上的 Potato，做 Grok Bot）说的 trust ladder：先学会刹车，再踩油门。空文件夹、一个真想法，盯着看；再扩到多 agent、自定义 skill、接 Slack 和邮件。别一上来就丢最难的活，先给琐碎、无聊、能衡量、改错成本低的事（比如回信草稿），再谈野心。

他接下来兴奋什么
自认是老师，不是评论家。他在想 software factories：怎么稳定地把想法变成工作和长期改库；多 agent 怎么组织，现在还没答案。也期待开源模型接近 Opus 5.5，以及更省 token、说话更直白、能干活的模型。
