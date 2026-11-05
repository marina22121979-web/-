---
name: vfx-video
description: >-
  制作特效视频与网页展示动画。涵盖文字/形状的动画与特效视频、把一张图片做成带特效和动画的视频
  (Ken Burns/光扫/粒子/调色/视差)、以及物理与数学模拟动画 (先用 Python/scipy 算出轨迹再渲染，
  如双摆、N 体引力、Lorenz、抛体、振动弦)。基于 AE 实现原理 (图层/关键帧/缓动/合成/特效栈/运动模糊)，
  自带纯 Python 合成引擎 vfxkit (numpy+scipy+Pillow+ffmpeg，无需 Manim)，也支持导出 MP4 或自包含
  HTML Canvas 网页动画。当用户想做特效视频、动画特效、文字动画、形状动画、图片转视频、运动图形、
  motion graphics、物理/数学动画演示、双摆、粒子、辉光、漏光、kinetic typography，或提到 AE/After
  Effects 风格效果时使用。
---

# vfx-video — 特效视频 & 网页动画生成

把需求变成**特效视频(MP4)**或**网页展示动画(HTML)**。核心理念：**先用 Python 算，再做动画**；一切按 **AE 实现原理**（图层 Layer / 关键帧 Keyframe / 缓动 Easing / 合成 Composite / 特效栈 / 运动模糊）组织。

自带纯 Python 合成引擎 **vfxkit**（`numpy+scipy+Pillow+ffmpeg`，**不依赖 Manim**）。物理/数学模拟用 `scipy` 解微分方程得到轨迹，再逐帧采样绘制。参考实现：[ManimCommunity/manim](https://github.com/ManimCommunity/manim)（Manim 在本 skill 中是可选项，仅用于 LaTeX 矢量公式）。

> 本文中 `<skill>` = 本 skill 目录（项目内为 `vfx-video/`，即 `特效视频/vfx-video`）。
> 给执行者：**严格按阶段走，能渲一张静帧用眼睛看的地方一定先看再继续。** 不确定 API 就读 `references/vfxkit-guide.md`，别凭记忆瞎写。

---

## 0. 核心心法（必读）

0. **配方优先（最重要）。** 产出"高级感"最可靠的方式是用高层配方 `vfxkit.recipes` + 命名调色板 `vfxkit.palettes`，**不要从零拼基础图元**。配方已内置打磨好的关键帧/缓动/辉光/调色/可读性。先查 `references/recipes.md`，几行就能成片。**但配方是地板不是天花板**——配方没有的效果，掉到底层图元自定义即可：`ShapeLayer(draw_fn)` 任意逐帧绘制、任意 `img→img` numpy 像素特效、`scipy` 自写物理、任意缓动函数。完整自定义指南见 `references/extend.md`（能力上限 = "你能算出每一帧像素"）。
1. **先设计，后编码。** 没有分镜（storyboard）不写代码。见阶段 B。
2. **一屏只讲一件事。** 进下一个点前，把上一屏不需要的元素淡出。**永远不让元素重叠或飘出画面。**
3. **先算后画。** 物理/数学：先用 `vk.physics.*` 解出轨迹 `Interp`，渲染只做"采样 + 绘制"，不在每帧现场积分。
4. **自动自检 + 小步验证（关键反馈闭环）。** 渲染前先跑 `check_comp.py`（自动查出画/空帧/低对比/重叠，无需看图），按提示改；再 `render.py --still T` 出一张 PNG 亲眼看布局；最后才渲视频。
5. **确定性。** 随机（粒子/grain）一律传固定 `seed`；时间只从入参 `t` 取。
6. **交付前自检。** 视频确认 MP4 存在能播；网页确认浏览器能打开、交互有效。

---

## 1. 阶段总览（先复制这个清单跟踪）

```
进度：
- [ ] A. 明确需求（类型/形式/画幅时长/风格/数据来源）
- [ ] B. 写分镜 storyboard.md + 选引擎与产物形式
- [ ] C. 准备环境（setup.sh + check_env.py）
- [ ] D. 制作
        视频：选调色板+配方组装 build() → check_comp.py 自检 → 静帧自检 → 完整渲染 → 验证 MP4
        网页：套 HTML 模板 → 填内容/交互 → 浏览器验证
- [ ] E. 交付（文件路径 + 如何查看 + 默认值 + 可调项）
```

---

## 2. 阶段 A — 明确需求

确认下面几项。**用户没说清的，用合理默认值并在交付时说明，不要反复追问。**

| 维度 | 要点 | 默认 |
|---|---|---|
| 类型 | 文字/形状动画 · 图片→特效视频 · 物理/数学模拟 · 综合 | 看用户描述 |
| 形式 | 视频(MP4) / 网页(HTML) / 两者 | 见下决策 |
| 画幅·帧率·时长 | 1920×1080 / 30fps / 短片 | 6–15s 钩子；30s 完整 |
| 风格 | 配色/字体/节奏（电影感/科技/极简/数据…） | 深色 + 高对比 |
| 数据来源 | 物理模拟用什么方程/参数 | 见 `physics-cookbook.md` |
| 语言 | 中英（文字层 `cjk=True` 显示中文） | 跟随用户（中文） |

**形式决策：** 要固定时长成片/发平台/重特效 → **视频**；要拖参数即时看/嵌网页/交互 → **网页**；都要 → 先视频讲主线，再网页给探索。

---

## 3. 阶段 B — 写分镜 + 选引擎（最重要）

复制 `templates/storyboard.md` 填写。合格分镜含：**一句话目标** + **镜头清单**（每镜：画面/动画关键帧/切换方式）+ **收尾**。

**选引擎：**

| 需求 | 引擎 | 入口 |
|---|---|---|
| 文字/形状动画、特效视频 | **vfxkit** | `templates/comp_project.py` |
| 一张图 → 特效动画视频 | **vfxkit** | `templates/image_effect.py` |
| 物理/数学模拟（双摆等） | **vfxkit** + `vk.physics` | `references/physics-cookbook.md` |
| 网页展示/交互动画 | **HTML Canvas** | `templates/web_animation.html` |
| 必须 LaTeX 矢量公式排版 | Manim（可选） | `references/manim-optional.md` |

不进入阶段 D 之前必须有分镜。

---

## 4. 阶段 C — 准备环境（做视频才需要；纯网页可跳过）

按顺序执行，**每步看输出**：

```bash
bash <skill>/scripts/setup.sh        # 装 numpy/scipy/Pillow，检查 ffmpeg（幂等，轻量）
python3 <skill>/scripts/check_env.py # 必须 PASS 才继续
python3 <skill>/scripts/selftest.py  # 可选：端到端跑一遍引擎
```
`manim` 与 `LaTeX` 显示为 optional，**没有它们也能做全部特效**。只有要 LaTeX 公式时才 `setup.sh --with-manim`。

---

## 5. 阶段 D — 视频（vfxkit）

**先读 `references/recipes.md`（场景→配方 速查，最常用）**；需要手写图元或排错再读 `references/vfxkit-guide.md`；图片/物理读 `references/image-effects.md`、`references/physics-cookbook.md`。

**逐步执行：**

1. **建项目**：在工作区建 `<英文短名>/video.py`（或复制 `templates/comp_project.py`）。文件须定义 `build() -> vk.Composition`。
2. **配方优先组装 `build()`**：选 `palettes.get(...)` 调色板 → 从 `recipes.md` 抄对应场景的配方（`rich_background` / `kinetic_text` / `text_shine` / `ken_burns` / `trail` / `tagline` / `transition` / `flip_in` / `equalizer` / `particle_burst` …）→ 最后 `rx.cinematic_grade(comp)`。配方不够时才手写图层+关键帧（见 `extend.md`）。
3. **自动自检（必做）**：
```bash
python3 <skill>/scripts/check_comp.py video.py    # 查出画/空帧/低对比/重叠，按提示改
```
4. **静帧自检**：
```bash
python3 <skill>/scripts/render.py video.py --still 2.0 --out /tmp/p.png   # 能看图就亲眼确认布局
```
5. **草稿/定稿渲染**：
```bash
python3 <skill>/scripts/render.py video.py draft.mp4 --fps 24 --preset ultrafast --crf 24   # 草稿
python3 <skill>/scripts/render.py video.py out.mp4   --preset slow --crf 18 --mb 8           # 定稿
```
6. **验证 MP4**：确认文件存在、大小>0，可 `ffmpeg -ss T -i out.mp4 -frames:v 1 f.png` 抽帧确认。

**物理模拟要点**：`traj, meta = vk.physics.XXX(...)` 先算轨迹；`rx.trail(comp, sample_fn)` 画拖尾，`ShapeLayer(draw)` 里 `state=traj(t)` 采样画杆/球；`solve_fps` 远高于视频 fps 保证稳定。完整可跑代码见 `references/physics-cookbook.md`。

**视频质量底线**：无重叠/出画、对比足够、停留够读完字幕、（物理）轨迹正确、结尾有定格或干净淡出。

---

## 6. 阶段 D — 网页（HTML Canvas）

读 `references/web-animation.md`，复制 `templates/web_animation.html` 改。

1. 复制为 `index.html`。内置：深色主题、DPR 自适应 canvas、`requestAnimationFrame` 循环、CSS kinetic 标题、（示例）RK4 双摆。
2. **填内容**：物理实时积分或预计算轨迹回放；文字用 CSS keyframes/渐变；形状用 Canvas2D（`shadowBlur` 做辉光）。
3. **加交互**（若需要）：`<input type=range>` 绑参数 → 重绘；点击/键盘控制。
4. **验证**：浏览器打开（mac `open index.html`），确认动画流畅、resize 不变形、交互生效、移动端可用。

**网页质量底线**：单文件可直接打开；至少 1 个真正影响画面的交互（若定位交互）；自适应不溢出。

---

## 7. 阶段 E — 交付

给一份简短交付说明：
- 产物路径（MP4 / HTML / storyboard / 项目 .py）。
- 如何查看（视频用播放器；网页双击或 `open`）。
- 用了哪些默认值（画幅/时长/风格/引擎）。
- 可继续打磨点（改配色、延长镜头、加运动模糊、加交互参数、换真实图片/深度图视差、加配音/BGM）。

---

## 8. 常见错误速查

| 现象 | 原因 | 处理 |
|---|---|---|
| `ffmpeg not found` | 没装 ffmpeg | `brew install ffmpeg` |
| 斜线/曲线有锯齿 | `ShapeLayer` 抗锯齿不足 | 用 `ss=3`（默认）或 `ss=4`；分辨率默认 1080p |
| 中文/箭头/符号成方框 | 没开 cjk | `TextLayer(..., cjk=True)` / `cv.text(..., cjk=True)` |
| 文字不在期望位置 | 图层默认自动居中 | 显式 `position.const([x,y])` |
| 图层没出现 | opacity=0 / 时间窗外 / 出画 | `--still` 该时刻确认；查关键帧与 `start/end` |
| 物理动画发疯/不稳 | 步长太大 | 调高 `solve_fps`；渲染加 `--mb 8` |
| 渲染很慢 | 全帧特效 + 高分辨率 | 草稿降配（低分辨率/ultrafast/关重特效）；定稿再上 |
| `latex failed`（仅 Manim） | 用了 MathTex 但无 LaTeX | 装 LaTeX 或改 `Text`；或干脆用 vfxkit |

完整排错见 `references/vfxkit-guide.md`。

---

## 资源索引

- **`references/recipes.md` — 场景→配方 速查（最常用，先看这个）**
- **`references/extend.md` — 超越配方：自定义绘制/特效/物理/缓动（配方不够用时看，含能力边界与绕过办法）**
- `references/ae-principles.md` — AE 概念 → vfxkit 对照（图层/关键帧/缓动/特效/混合/运动模糊/表达式）
- `references/vfxkit-guide.md` — 引擎 API、缓动表、特效表、绘制 API、纪律、错误速查
- `references/image-effects.md` — 图片→特效视频（Ken Burns/光扫/粒子/调色/2.5D 视差）
- `references/physics-cookbook.md` — 物理/数学模拟配方（双摆/N 体/Lorenz/抛体/振动弦/傅里叶）
- `references/web-animation.md` — 自包含 HTML Canvas 动画与交互
- `references/manim-optional.md` — 何时及如何用 Manim（仅 LaTeX 矢量公式）
- `templates/comp_project.py` · `image_effect.py` · `web_animation.html` · `storyboard.md`
- `examples/gorden_title/render.py` — 绚丽逐字文字动画范例（**仅 8 行配方**：背景+逐字+爆发+扫光+标语+调色），含成片 `out.mp4` 与 GIF 预览。物理/数据/转场等更多场景见 `references/recipes.md`、`references/physics-cookbook.md`、`references/extend.md`
- `scripts/setup.sh` · `check_env.py` · `render.py`（运行器）· `check_comp.py`（自动检查）· `selftest.py`
- `vfxkit/` — 引擎源码：`recipes`（高层配方）· `palettes`（调色板）· easing / keyframe / layer / effects / comp / shapes / physics
