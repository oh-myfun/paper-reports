---
name: paper-report
description: Convert academic papers into structured Chinese reading reports with original figures. Supports arXiv HTML and local PDF inputs. For arXiv links, HTML mode is preferred for textual accuracy. Use when the user asks to summarize, read, analyze, or create a reading report for an academic paper (PDF file or arXiv link).
---

# Paper Reader

将学术论文转化为结构化的中文阅读报告，支持 HTML 和 PDF 两种输入形式。输出格式默认为 HTML，用户可选 Markdown。

**Python 路径约定**：本文档中 `{PYTHON}` 代表系统 Python3 解释器路径。
- macOS（有 CommandLineTools）：`/Library/Developer/CommandLineTools/usr/bin/python3`
- 其他环境：`python3`

---

## Step 1: 路由决策

在开始处理之前，确定两个维度的决策：**输入处理模式**和**输出格式**。

### 1.1 确定输出格式

根据用户要求确定输出格式：

- **用户明确指定了格式**（如"生成 HTML 报告"或"给我 Markdown"）→ 按用户要求。
- **用户未指定** → **默认使用 HTML**。

输出格式决定后续的图片处理方式：
- **Markdown 模式**：图片保存为独立文件，Markdown 中用相对路径引用。
- **HTML 模式**：图片保存为独立文件（`{简短标题}/` 目录），HTML 中用相对路径引用；CSS/JS 引用 `../static/report.css` 和 `../static/report.js`。

> 后续步骤中，标注 `[MD]` 的仅 Markdown 模式执行，`[HTML]` 的仅 HTML 模式执行，无标注的两种都执行。

### 1.2 选择输入处理模式

两种模式完全独立，**不得混用**。根据输入类型按以下规则决定：

**规则 1：用户提供本地 PDF 文件路径**
→ 直接使用 **PDF 模式**，跳转至 [path-pdf.md](path-pdf.md) 执行 P1–P5。

**规则 2：用户提供 arXiv 链接（不论是 `/pdf/` 还是 `/html/` 形式）**
→ 优先尝试 HTML 模式。构造 HTML URL：将 `/pdf/` 替换为 `/html/`，并去掉末尾的 `.pdf` 后缀。
例：`https://arxiv.org/pdf/2605.12036` → `https://arxiv.org/html/2605.12036`

用 curl 检查 HTML 页面是否存在：
```bash
curl -sI "https://arxiv.org/html/{ARXIV_ID}" | head -1
```
- 返回 `HTTP/... 200` → 使用 **HTML 模式**，跳转至 [path-html.md](path-html.md) 执行 H1–H3。
- 返回非 200（如 404）→ 回退到 **PDF 模式**，跳转至 [path-pdf.md](path-pdf.md) 执行 P1–P5。

**规则 3：用户提供其他 HTML 页面链接**
→ 直接使用 **HTML 模式**，跳转至 [path-html.md](path-html.md) 执行 H1–H3。

> 完成对应模式的步骤后，回到本文档继续执行 **Step 2**。

---

## Step 2: 生成中文阅读报告

两种模式完成各自步骤后，`{workspace}/figures/` 目录中已有所有需要的图表图片。

**报告结构（参考框架，可根据论文内容灵活调整）**：

```
1. 论文基本信息（标题、作者、机构、发表信息）
2. 研究背景与动机
3. 核心方法 / 技术方案（配架构图）
4. 实验设计
5. 实验结果与分析（配结果图表）
6. 主要贡献与创新点
7. 局限性与未来方向
8. 个人点评与总结
```

**灵活性说明**：以上为参考框架，不是死板模板。根据论文内容可以：
- 增加章节（如 Case Study、数据集详解等）
- 合并章节（如实验设计与结果合为一章）
- 在方法章节内自由组织子结构

**附录内容集成指引**：
- 附录中"方法实现细节/超参数/训练配置"类内容 → **融入对应的主方法章节**，让读者在一处看到完整技术描述
- 附录中"补充实验/额外消融"类内容 → 融入实验结果章节或设独立小节
- 附录中"独立子课题/独立证明"类内容 → 可设独立附录章节
- 附录中"详细架构图/训练优化公式/算法伪代码"类内容 → 如果篇幅过长影响主报告阅读流畅性，应创建**附录扩展页面**（`{简短标题}-appendix.html`），在主报告中头部和适当位置添加链接引用

### 模板参考

- **[MD] Markdown 模式**：详见 [report-template.md](report-template.md)
- **[HTML] HTML 模式**：详见 [report-template.html](report-template.html)

### 图片处理

**[MD] Markdown 模式**：将图片复制到 `{workspace}/outputs/{论文简短标题}-images/`，Markdown 中用相对路径引用：
```
![图 1 说明](./{论文简短标题}-images/fig1.png)
```

**[HTML] HTML 模式**：将图片保存为独立文件，HTML 中用相对路径引用：

图片文件放在 `{简短标题}/` 目录下（与 HTML 文件同级），命名为 `img01.png`、`img02.png` 等（附录图片命名为 `appendix-img01.png` 等）。HTML 中使用：
```html
<img src="{简短标题}/img01.png" alt="Figure 1: ...">
```

目录结构示例：
```
reports/
  minimind-o.html
  minimind-o/
    img01.png
    img02.png
    ...
  supertonic-tts.html
  supertonic-tts-appendix.html
  supertonic-tts/
    img01.png
    ...
    appendix-img01.png
    ...
```

### 图表选取原则

根据报告内容需要选取图表，**不设数量硬上限**。原则：
- 架构图/流程图：必选（帮助读者建立全局理解）
- 主实验结果表/图：必选
- 关键消融/对比图：如报告中有讨论则选入
- Case Study 截图：如有且有说明价值则选入

### 关键写作要求

- 全文使用中文撰写，术语首次出现时附英文原文，如"注意力机制（Attention Mechanism）"
- 图表引用格式："如图 1 所示，..." 或 "表 1 汇总了..."
- 保持学术严谨性，严格基于原文，不添加原文未涉及的推测或数据
- 每个章节应有实质内容，避免泛泛而谈
- 不包含任何"报告生成日期"或"AI 生成"相关的描述文字
- **[HTML] 数学公式处理**：使用 LaTeX 语法书写公式，行内用 `$...$`，独立公式用 `$$...$$`。模板已内置 MathJax 3，无需额外引入。生成 HTML 时注意：在 Python 中构建含公式的字符串时，使用**原始字符串（raw string）或单反斜杠**确保输出文件中 LaTeX 命令前是单个 `\`（如 `\mathcal`），而非双反斜杠 `\\mathcal`。
- **[MD] 数学公式处理**：使用标准 LaTeX 语法 `$...$` 和 `$$...$$`，与主流 Markdown 渲染器兼容。

### 输出文件

**文件命名**：从论文标题中提取核心关键词作为简短标题（去除特殊字符，空格替换为短横线或下划线）。HTML 文件的 `<title>` 和 `<h1>` 标签中**不得包含"阅读报告"字样**，应仅包含论文标题或其简短形式。

**[MD] Markdown 模式输出**（保存到 `{workspace}/outputs/`）：
1. `{简短标题}.md` — Markdown 报告
2. `{简短标题}-images/` — 图片文件夹

**[HTML] HTML 模式输出**（保存到 `{workspace}/reports/`）：
1. `{简短标题}.html` — HTML 报告（图片以相对路径引用同级目录中的文件）
2. `{简短标题}/` — 图片文件夹（与 HTML 同级）
3. `{简短标题}-appendix.html` — 附录扩展页面（可选，当附录内容过长影响主报告阅读时创建。附录图片同样放在 `{简短标题}/` 目录下，以 `appendix-` 前缀命名）

### 报告头部链接要求

报告头部区域必须包含以下链接（如信息可获取）：
- **论文链接**：arXiv 论文提供 `https://arxiv.org/abs/{ARXIV_ID}` 链接；其他来源提供对应的论文 URL
- **代码仓链接**：如论文中提及了开源代码仓库（GitHub 等），在头部一并附上链接

链接样式应使用与报告整体一致的强调色（如 `<a href="..." style="color:var(--text-link)">`）。

---

## Step 3: 校验

使用 Read 工具查看生成的报告文件，逐项检查：

### 通用检查

- 各章节标题完整、层级清晰
- 每个章节有实质内容，不存在空段落或占位符文本（如 `{{...}}`）
- 不包含"报告生成日期"或"AI 辅助生成"相关文字

### [MD] Markdown 专项检查

- 图片引用为有效相对路径，指向 `{简短标题}-images/` 目录下的实际文件
- **必须用 `ls` 命令显式验证图片文件存在，不可跳过**：
  ```bash
  ls {workspace}/outputs/{简短标题}-images/
  ```
- 逐个确认 Markdown 中每个 `![...](./{简短标题}-images/xxx.png)` 引用的文件确实在目录中
- 公式使用 LaTeX 内联格式（`$...$` 或 `` `...` ``），确认无乱码

### [HTML] HTML 专项检查

- HTML 基本结构完整（`<!DOCTYPE html>`、`<html>`、`<head>`、`<body>`、`</html>` 齐全）
- **MathJax 已引入**：`<head>` 中包含 MathJax 配置和 `tex-svg.js` 脚本引用
- **CSS/JS 引用外部文件**：`<head>` 中引用 `../static/report.css`，`<body>` 末尾引用 `../static/report.js`，不得内嵌样式或交互脚本
- **交互功能 HTML 元素必须存在**（CSS/JS 由外部文件提供，但 HTML 元素必须写在页面中）：
  - `<div class="progress-indicator" id="progressIndicator">` + SVG + progress-text（进度指示器）
  - `<div class="lightbox-overlay" id="lightbox">` + `<img id="lightboxImg" />`（图片灯箱）
  - 参考 `report-template.html` 中的完整结构
- 所有 `<img>` 的 `src` 为有效相对路径引用（指向同级 `{简短标题}/` 目录下的图片文件）
- 不存在 base64 data URI 或外部图片链接
- **必须用 `ls` 命令显式验证图片文件存在**：
  ```bash
  ls {workspace}/reports/{简短标题}/
  ```
- 每张图片有描述性 `alt` 属性和 `<figcaption>`
- **公式反斜杠检查**：确认 LaTeX 命令前是单个 `\`（如 `\mathbf`），而非 `\\mathbf`。可用 `grep -c '\\\\\\\\math' file.html` 检查（结果应为 0）

**如果发现问题**：直接修复对应文件，修复后重新保存到同一路径。

---

## 特殊情况处理

**超长论文（>20 页 / >50,000 字符文本）**：分批处理，先通读整体结构，再聚焦核心章节（方法、实验、结论）。

**双栏排版论文（PDF 模式）**：单栏图宽约 30–280 或 300–565 pt，跨栏图宽约 30–565 pt，注意调整裁剪坐标。

**扫描版 PDF**：文字模糊时依然可通过图片阅读，但在报告中注明来源质量受限。

**论文含附录**：参照 Step 2 中"附录内容集成指引"处理。
