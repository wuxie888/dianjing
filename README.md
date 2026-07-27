# 点睛

<p align="center">
  <a href="https://wuxie888.github.io/dianjing/">
    <picture>
      <source media="(prefers-reduced-motion: reduce)" srcset="./assets/dianjing-hero.svg">
      <img src="./assets/dianjing-hero.gif" alt="点睛：为代码库完成视觉风格设计与装修" width="100%">
    </picture>
  </a>
</p>

> **把一个已经完成或接近发布的代码仓库，变成别人一眼看懂、能安装、愿意相信和分享的 GitHub 产品页。**

<p align="center">
  <a href="https://github.com/wuxie888/dianjing/actions/workflows/validate.yml"><img alt="Checks" src="https://github.com/wuxie888/dianjing/actions/workflows/validate.yml/badge.svg?branch=main"></a>
  <a href="./LICENSE"><img alt="License MIT" src="https://img.shields.io/badge/license-MIT-b38a42?style=flat-square"></a>
  <a href="./skills/dianjing/SKILL.md"><img alt="Agent Skill" src="https://img.shields.io/badge/Agent-Skill-c24f32?style=flat-square"></a>
  <a href="./skills/dianjing/SKILL.md"><img alt="Runtime Codex" src="https://img.shields.io/badge/runtime-Codex-6f42c1?style=flat-square"></a>
  <a href="https://wuxie888.github.io/dianjing/"><img alt="Showcase Live" src="https://img.shields.io/badge/showcase-live-1f883d?style=flat-square"></a>
</p>

点睛是一个可安装的 Agent Skill。你给它一个真实代码仓库，它会先核验产品和发布状态，再整理产品定位、README、真实截图与动效、安装说明和公开验收；Logo、Hero、操作 GIF、展示网站、Social Preview 和 Release 媒体只在确有必要时采用。

它不替产品补造功能，也不拿漂亮图片掩盖尚未完成的产品。

- **你提供**：一个真实、已经完成或接近发布的仓库
- **点睛会做**：核验事实，重组说明，组织真实素材，补齐安装与验收
- **你得到**：一个美观、可信、易懂、可安装、可传播的公开仓库

**[安装点睛](#安装与第一次运行)** · **[阅读 Skill](./skills/dianjing/SKILL.md)** · **[查看动态展示](https://wuxie888.github.io/dianjing/)**

## 它适合谁

- 已经做完产品，却还没有把 GitHub 仓库整理成公开产品页的独立开发者
- 正在发布 Agent Skill、CLI、SDK、App 或开源工具的项目维护者
- 已有真实产品和素材，需要补 README、安装路径、视觉证据与发布验收的团队

点睛不适合用来包装尚未实现的产品构想，也不会替缺少真实界面的项目伪造产品截图。

## 它会交付什么

### 所有仓库都要完成

- **产品说明**：一句话说清产品是什么、给谁用、解决什么
- **README 结构**：按“看懂 → 相信 → 会用 → 验收”的顺序重组
- **真实证据**：使用真实界面、真实输出、真实运行状态和真实发布信息
- **第一次成功**：给出可复制的安装、调用方式和成功标准
- **公开边界**：写清许可证、版本、发布状态、未完成项和需要授权的动作
- **最终验收**：检查桌面端、移动端、链接、媒体、命令和公开页面

### 只有确实需要时才采用

| 条件模块 | 采用条件 |
| --- | --- |
| Logo、Hero 与动态图 | 能更快说明产品、建立识别或证明真实操作 |
| 展示网站 | README 无法承载关键交互或在线体验，而且产品没有可复用官网 |
| Social Preview 与 Release 媒体 | 产品已经进入外部分享或版本发布阶段 |
| 深度文档 | 安装、配置、API 或维护复杂到 README 已经不够用 |

展示网站不是默认交付，动效也不是装修完成度的证明。

## 点睛怎样工作

1. **核验产品** — 确认真正的 Git 仓库、源码入口、运行状态、许可证、发布渠道和已有素材，先区分事实与宣传。

2. **建立产品合同** — 写清用户交给产品什么、产品完成什么、用户最终得到什么，以及最适合谁、不适合谁。

3. **完成仓库门面** — 修改 README 和必要文档，组织真实截图与媒体，补齐安装、第一次成功、排错、升级和发布状态。

4. **分别验收** — 把本地完成、远端源码、Tag、Release、Pages、Social Preview 和用户首次成功分开验证，不把其中一项冒充全部完成。

## 安装与第一次运行

### 1. 安装

```bash
git clone https://github.com/wuxie888/dianjing.git
mkdir -p ~/.codex/skills
cp -R dianjing/skills/dianjing ~/.codex/skills/dianjing
```

重新开启任务后，进入准备装修的仓库。

### 2. 调用

```text
使用 $dianjing 装修这个代码库。
先核验真实产品和仓库状态，再给出采用模块与修改计划。
```

### 3. 第一次运行成功

点睛应该先返回：

- 当前 Git 仓库边界与工作区状态
- 产品的真实入口、能力、许可证与发布状态
- 可以复用的真实素材
- 必做底座、条件模块和明确的不采用项
- 准备修改的文件与需要用户授权的远端动作

事实没有确认之前，点睛不会直接编写漂亮但失真的 README。

## 什么叫真正完成

| 状态 | 可验证结果 |
| --- | --- |
| 安装成功 | 新任务可以加载并调用 `$dianjing` |
| 首次运行成功 | 返回事实审计、采用模块和修改计划 |
| 装修交付成功 | README、真实素材、安装、文档和本地验收已经完成 |
| 公开发布成功 | 远端源码及采用的 Pages、Tag、Release、Social Preview 分别通过验证 |

这四个状态必须分开报告。审计完成不等于装修完成，本地完成也不等于已经公开发布。

## 当前证据与边界

- 本仓库展示了点睛如何装修自己，但自举不能单独证明它适合所有项目
- 当前从 `main` 分支安装，尚未发布版本化 Tag 或 GitHub Release
- 动态展示页是点睛的条件性展示面，不代表所有仓库都需要建设网站
- 外部仓库案例完成并公开验收之前，不把跨项目复用写成已经得到充分证明

## 只运行只读审计

如果暂时不希望修改仓库，可以只运行审计脚本：

```bash
python3 skills/dianjing/scripts/audit_repository.py /path/to/repository
```

它会检查 Git 边界、发布与文档表面、视觉媒体、可能的本机路径、占位文案和敏感文件名，并区分公开跟踪资产与本地文件。

## 文档与验证

- [阅读完整 Skill](./skills/dianjing/SKILL.md)
- [README 与文档准则](./skills/dianjing/references/readme-and-documentation.md)
- [视觉与动效准则](./skills/dianjing/references/visual-and-motion.md)
- [发布与公开验收](./skills/dianjing/references/release-and-acceptance.md)
- [验证工作流](https://github.com/wuxie888/dianjing/actions/workflows/validate.yml)
- [MIT License](./LICENSE)
