---
name: davinci-resolve-develop
version: 1.1.0
description: DaVinci Resolve 开发与操作技能。当用户需要操作达芬奇、控制 Resolve、开发达芬奇脚本、编写 Resolve 自动化脚本、管理项目/时间线/媒体池、创建 Fusion 合成/模板、编写 DCTL 色彩效果、开发 OpenFX 插件、制作 LUT、开发 Workflow Integration 插件、编写 Fuse 节点时使用。关键词：DaVinci Resolve、达芬奇、Resolve 脚本、Fusion、DCTL、OpenFX、LUT、Fuse、调色、剪辑自动化、渲染、时间线、媒体池、项目管理。
---

# DaVinci Resolve 开发技能

基于本机 DaVinci Resolve 安装目录中的官方文档进行开发，确保 API 与当前安装版本完全一致。

## 本机文档根目录

按操作系统确定 Resolve 支持目录（以下简称 `$RESOLVE`）和开发者文档目录（`$DEV`）：

| 系统 | `$RESOLVE` | `$DEV` |
|------|-----------|--------|
| **macOS** | `/Library/Application Support/Blackmagic Design/DaVinci Resolve` | `$RESOLVE/Developer` |
| **Windows** | `%PROGRAMDATA%\Blackmagic Design\DaVinci Resolve\Support` | `$RESOLVE\Developer` |
| **Linux** | `/opt/resolve` | `$RESOLVE/Developer` |

如果不确定路径是否存在，先用 Bash `ls` 确认。

## 执行工作流

当用户要求操作 DaVinci Resolve 时，通过 `resolve_run.py` 直接执行 Python 代码：

```bash
python3 %当前SKILL文件父目录%/scripts/resolve_run.py "
# 你的业务代码，以下变量已自动就绪：
# resolve   - Resolve 实例
# pm        - ProjectManager
# project   - 当前项目
# timeline  - 当前时间线（可能为 None）
# mediapool - 媒体池（可能为 None）
print(project.GetName())
"
```

也支持执行脚本文件：`python3 %当前SKILL文件父目录%/scripts/resolve_run.py -f script.py`

**流程**：

1. 用户描述需求
2. 阅读本机 `$DEV` 中对应领域的参考文档确认 API
3. 编写业务代码，通过 Bash 调用 `resolve_run.py` 执行
4. 根据输出向用户反馈结果

## 开发领域与参考文档

编写代码前**必须先阅读对应的参考文档**，所有路径相对于 `$DEV`：

| 领域 | 语言/格式 | 参考文档（相对 $DEV） | 适用场景 |
|------|-----------|----------------------|----------|
| **Scripting API** | Python / Lua | `Scripting/README.txt` | 项目管理、时间线操作、媒体池、渲染自动化 |
| **DCTL** | C-like (DCTL) | `DaVinciCTL/README.txt` | 色彩变换、GPU 像素着色器、自定义调色效果 |
| **OpenFX 插件** | C++ / CUDA / OpenCL / Metal | `OpenFX/README.txt` | GPU 加速视觉效果插件 |
| **LUT** | .cube 格式 | `LUT/README.txt` | 1D/3D 查找表、色彩映射 |
| **Fusion Fuse** | Lua (Fuse SDK) | `Fusion Fuse/Fuse Read Me.txt` | 自定义 Fusion 工具节点 |
| **Fusion Templates** | Macro (.setting) | `Fusion Templates/README.txt` | 转场、生成器、标题、特效模板 |
| **Codec Plugin** | C/C++ | `CodecPlugin/README.txt` | 自定义编解码器和容器格式 |
| **Workflow Integration** | JS (Electron) / Python | `Workflow Integrations/README.txt` | 工作流集成插件、UIManager 界面 |

示例代码位于各领域的 `Examples/` 子目录。

## Scripting API 开发指南

使用 `resolve_run.py` 执行代码，连接和变量注入已自动处理。DaVinci Resolve 必须正在运行。

### 核心对象层级

```
Resolve
├── GetProjectManager() → ProjectManager
│   ├── GetCurrentProject() → Project
│   │   ├── GetMediaPool() → MediaPool
│   │   │   ├── GetRootFolder() → Folder
│   │   │   ├── ImportMedia([filePaths]) → [MediaPoolItem]
│   │   │   └── AppendToTimeline([{clipInfo}]) → [TimelineItem]
│   │   ├── GetCurrentTimeline() → Timeline
│   │   │   ├── GetItemListInTrack(trackType, index) → [TimelineItem]
│   │   │   ├── AddMarker(frameId, color, name, note, duration) → Bool
│   │   │   └── Export(filePath, exportType, exportSubtype) → Bool
│   │   ├── AddRenderJob() → string
│   │   ├── StartRendering([jobIds]) → Bool
│   │   └── SetRenderSettings({settings}) → Bool
│   └── CreateProject(name) → Project
├── OpenPage(pageName) → Bool
└── GetCurrentPage() → string
```

> **完整 API 列表**：阅读 `$DEV/Scripting/README.txt`
> **示例脚本**：`$DEV/Scripting/Examples/`

### 注意事项

- DaVinci Resolve 必须处于运行状态才能执行脚本
- `SetLUT()` 和 `SetCDL()` 的 nodeIndex 从 1 开始（v16.2.0+）
- 脚本执行权限可在 Resolve Preferences 中配置

## DCTL 开发指南

### 基本结构

```c
// 可选：自定义 UI 控件
DEFINE_UI_PARAMS(gain, Gain, DCTLUI_SLIDER_FLOAT, 1.0, 0.0, 10.0, 0.1)

// Transform 入口函数（必须）
__DEVICE__ float3 transform(int p_Width, int p_Height, int p_X, int p_Y, float p_R, float p_G, float p_B)
{
    return make_float3(p_R * gain, p_G * gain, p_B * gain);
}
```

### 关键点

- **Transform DCTL**：处理单张图像的色彩变换
- **Transition DCTL**：两个片段之间的过渡效果，使用 `TRANSITION_PROGRESS`
- **UI 控件类型**：`DCTLUI_SLIDER_FLOAT`、`DCTLUI_SLIDER_INT`、`DCTLUI_VALUE_BOX`、`DCTLUI_CHECK_BOX`、`DCTLUI_COMBO_BOX`、`DCTLUI_COLOR_PICKER`
- **数学函数**：使用下划线前缀，如 `_powf()`, `_sinf()`, `_clampf()`, `_saturatef()`
- **float 值必须有 'f' 后缀**：如 `1.0f`

> **完整语法参考**：`$DEV/DaVinciCTL/README.txt`

## OpenFX 插件开发指南

### 基本架构

- 继承 `OFX::ImageProcessor`，重写 `processImagesCUDA/OpenCL/Metal/multiThreadProcessImages`
- 继承 `OFX::ImageEffect`，重写 `render()`、`isIdentity()`、`changedParam()`
- 实现 `PluginFactory`：`describe()`、`describeInContext()`、`createInstance()`

### 安装路径

- **macOS**：`/Library/OFX/Plugins/`
- **Linux**：`/usr/OFX/Plugins/`
- **Windows**：`C:\Program Files\Common Files\OFX\Plugins\`

> **完整参考**：`$DEV/OpenFX/README.txt`
> **示例插件**：`$DEV/OpenFX/GainPlugin/`

## Fusion 开发指南

### Fuse 开发

- 使用 Lua 编写，无需编译器
- 实时编译执行，一键重载
- 支持 UI 控件、图像处理、形状绘制、文本渲染、Metadata、DCTL GPU 加速

**安装路径**：

- macOS：`~/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Fuses`
- Windows：`C:\ProgramData\Blackmagic Design\DaVinci Resolve\Support\Fusion\Fuses`
- Linux：`~/.local/share/DaVinciResolve/Fusion/Fuses`

> **参考**：`$DEV/Fusion Fuse/Fuse Read Me.txt`

### Fusion Templates（转场/生成器/标题/特效）

- 使用 Macro 创建，保存为 `.setting` 文件
- **Anim Curves** 修改器实现自适应时长动画
- 支持打包为 `.drfx` 分发包

**模板路径**：

- macOS：`~/Library/Application Support/Blackmagic Design/DaVinci Resolve/Fusion/Templates/Edit/{Transitions,Titles,Generators,Effects}/`
- Windows：`C:\ProgramData\Blackmagic Design\DaVinci Resolve\Fusion\Templates\Edit\{...}\`

> **参考**：`$DEV/Fusion Templates/README.txt`

## LUT 开发指南

`.cube` 格式，支持：

- **1D LUT**：`LUT_1D_SIZE N` + `LUT_1D_INPUT_RANGE MIN MAX`
- **3D LUT**：`LUT_3D_SIZE N` + `LUT_3D_INPUT_RANGE MIN MAX`（N³ 个条目）
- **Shaper LUT**：1D LUT 作为预处理步骤

> **参考**：`$DEV/LUT/README.txt`

## Workflow Integration 开发指南

### 两种方式

1. **Electron 插件**：使用 `WorkflowIntegration.node` 模块调用 Resolve JS API
2. **Python/Lua 脚本**：使用 UIManager 构建 Qt 界面

### 插件目录结构

```
com.<company>.<plugin_name>/
├── package.js
├── main.js
├── index.html
├── manifest.xml
└── node_modules/
```

**安装路径**：

- macOS：`/Library/Application Support/Blackmagic Design/DaVinci Resolve/Workflow Integration Plugins/`
- Windows：`%PROGRAMDATA%\Blackmagic Design\DaVinci Resolve\Support\Workflow Integration Plugins\`

> **完整参考**：`$DEV/Workflow Integrations/README.txt`

## 技术文档

- **远程面板控制**：`$RESOLVE/Technical Documentation/DaVinci Remote Panel.txt`
- **用户配置目录**：`$RESOLVE/Technical Documentation/User Configuration folders and customization.txt`

## 开发原则

1. **文档驱动**：所有代码必须基于本机 `$DEV` 目录中的参考文档，禁止编造函数
2. **先读后写**：编写任何代码前必须先阅读对应领域的参考文档
3. **平台适配**：注意 macOS/Windows/Linux 的路径差异
4. **版本一致**：使用本机文档确保 API 与安装版本匹配
5. **示例参考**：优先参考 `Examples/` 目录中的官方示例代码
