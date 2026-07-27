# 视觉与动效

## 目录

- README、Social Preview、Release 与 Pages
- 动效机会矩阵与类型能力库
- 选择流程与 motion-anything
- 克制、无障碍、GIF/视频与视觉验收

## 平台表面

### README

适合：

- PNG、JPG、WebP、GIF 等视觉媒体
- 静态 SVG
- 动态 Hero GIF
- 真实操作 GIF
- 视频附件或带封面的外部视频入口

README 不是任意前端运行环境。GitHub 官方说明 SVG 不支持内联脚本或动画；不要把依赖 JavaScript、CSS、Lottie 或动画 SVG 的效果承诺为 README 内可运行。

官方参考：

- [GitHub Markdown 图片](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax#images)
- [GitHub 非代码文件与 SVG 限制](https://docs.github.com/en/repositories/working-with-files/using-files/working-with-non-code-files)
- [GitHub 支持的附件格式](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/attaching-files)

### Social Preview

它服务仓库链接在外部平台的展开卡片。GitHub 当前接受小于 1 MB 的 PNG、JPG 或 GIF，并建议至少 640 × 320，最佳 1280 × 640。

不同外部平台可能只展示 GIF 首帧，因此首帧必须是一张完整封面。透明背景需要同时检查深浅底色。

官方参考：

- [自定义仓库 Social Preview](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/customizing-your-repositorys-social-media-preview)

### Release 媒体

适合：

- 发布亮点 GIF
- MP4、MOV、WebM 演示
- 带字幕的短视频
- 新旧版本对比

不要让 Release 视频成为唯一说明；同时提供文字摘要和静态封面。

### GitHub Pages

GitHub Pages 可以从仓库发布 HTML、CSS 和 JavaScript，是高级交互与动效的可选表面，不是仓库装修的默认交付。

只有至少满足一项时才建设展示网站：

- README 无法承载产品的关键交互或视觉体验
- 产品需要在线 Demo、实时配置器、可交互样例或非开发者转化入口
- 产品没有可复用的正式官网

Agent Skill、CLI、SDK、小型库和后端工具通常不需要额外展示站。产品已经有正式官网时，优先复用并连接现有官网，避免制造第二份会漂移的产品叙事。

官方参考：

- [GitHub Pages 是什么](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages)

## 动效机会矩阵

每次装修都评估，按产品价值选择。`Pages / 官网` 一列只在展示网站通过条件门或正式官网已经存在时使用：

| 叙事任务 | README | Pages / 官网 | 发布媒体 |
| --- | --- | --- | --- |
| 品牌识别 | 动态 Hero GIF | Logo/标题入场 | 动态封面 |
| 解释工作流 | 流程 GIF | 连线、滚动、步骤过渡 | 解说短片 |
| 证明产品存在 | 真实操作 GIF | 交互 Demo、界面滚动 | 完整演示视频 |
| 强调关键差异 | 前后对比 GIF | 滑块、视差、数据过渡 | Before/After |
| 引导下一步 | 静态链接或徽章 | CTA 微交互 | Release 链接 |
| 营造气质 | 克制循环 | 环境背景、光影、粒子 | 品牌片头 |

## 动效类型能力库

Skill 应能选择但不应同时堆叠所有类型：

- 标题逐字/逐词入场
- 淡入、上浮、缩放和交错入场
- 滚动揭示
- 视差和景深
- 卡片高光、聚光、倾斜与悬停反馈
- CTA 高光或磁吸反馈
- 流程连线与节点状态
- 数据计数、图表和状态过渡
- 产品界面轮播与镜头移动
- 背景网格、渐变、光晕、噪点、粒子和轨道
- 成功反馈和发布庆祝
- 动态 Logo、动态图标和品牌循环
- 真实操作录屏、GIF 与发布视频

## 选择流程

1. 先写明每项动效承担的叙事任务。
2. 优先搜索已经存在且可安装的真实实现。
3. 阅读 `avoid_when`、`restraint`、减少动态、依赖和许可证。
4. 一项效果只用于少量关键对象。
5. 先验证静态状态，再启用动画。
6. 在真实浏览器中检查响应式和减少动态。

使用 motion-anything 时，优先选择 `implementation_status: ready`。例如：

- `kinetic-headline`：一个 Hero 标题
- `scroll-reveal`：长页面少量章节，首屏内容立即可见
- `glare-hover`：Hero 卡片或少数图片，触屏和减少动态下关闭
- `shimmer-button`：唯一主 CTA

这些只是选择示例，不是所有产品的固定组合。每次应重新搜索与读取实现。

## 克制与无障碍

- 每屏最多一个环境背景效果
- 每屏最多一个主要文字动效
- 每屏最多一个庆祝或高光效果
- 不给正文逐字动画
- 不隐藏首屏关键信息等待入场
- 优先使用 `transform` 和 `opacity`
- `prefers-reduced-motion` 下立即显示最终状态
- 键盘、触屏和无悬停设备保持完整功能
- 动画不制造闪烁、眩晕或持续干扰

## GIF 与视频验收

检查：

- 首帧独立成立
- 循环接缝自然
- 光标、账号、通知和私密内容已清理
- 演示使用真实产品和真实结果
- 文字在窄屏仍可读
- 时长只覆盖一个核心任务
- 有字幕或文字替代
- 文件大小适合仓库加载
- 原始高质量版本与压缩发布版分开保存

不要用评论数量、检测到的媒体数量或导出成功冒充逐帧目视验收。

## 视觉验收

- Logo 与产品名称一致
- Hero 在深浅背景都可读
- 截图裁切不隐藏关键上下文
- 图片顺序服务产品叙事
- 图标风格和线宽一致
- 不复制参考品牌的身份、商标或产品文案
- 上游动效和图标许可证已记录
- 动效关闭后页面仍然完整、美观、可用
