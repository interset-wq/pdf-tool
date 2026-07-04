# PDF Tool

一个基于 CustomTkinter 的现代 PDF 工具，提供查看、合并、拆分、转换、加密等全面功能。

## 功能特性

### 查看与导航
- PDF 查看器，支持滚动和翻页模式
- 缩略图侧边栏，快速跳转
- 演示模式（F5 全屏）
- 缩放控制（滚轮 / Ctrl +/-）

### 编辑操作
- **合并** - 多个 PDF 合并为一个
- **拆分** - 按页拆分 PDF
- **旋转** - 旋转页面（90°/180°/270°）
- **重排** - 自定义页面顺序

### 转换
- PDF 转 PNG 图片
- 图片转 PDF
- 提取 PDF 文本

### 安全与优化
- 密码加密
- 添加文字水印
- 压缩优化

### 界面
- 深色/浅色主题切换
- 可折叠侧边栏（Ctrl+B）
- 自适应宽度（根据 PDF 比例自动调整）
- 键盘快捷键

## 安装

### 从源码运行

```bash
# 克隆仓库
git clone https://github.com/interset-wq/pdf-tool.git
cd pdf-tool

# 安装依赖
uv sync

# 运行
uv run python main.py
```

### 下载预编译版本

前往 [Releases](https://github.com/interset-wq/pdf-tool/releases) 下载最新版本。

## 快捷键

| 快捷键 | 功能 |
|--------|------|
| `Ctrl+O` | 打开文件 |
| `Ctrl+S` | 保存 |
| `Ctrl+B` | 切换侧边栏 |
| `F5` | 演示模式 |
| `←/→` | 翻页 |
| `Ctrl+/-` | 缩放 |
| `Home/End` | 首页/末页 |

## 技术栈

- **UI**: CustomTkinter 6.x
- **PDF 渲染**: PyMuPDF
- **PDF 操作**: pikepdf
- **PDF 生成**: reportlab
- **图片处理**: Pillow

## 系统要求

- Python 3.14+
- Windows 10/11（预编译版本）

## 开发

```bash
# 添加依赖
uv add <package>

# 添加开发依赖
uv add <package> --dev

# 构建 Windows 可执行文件
uv run pyinstaller pdf_tool.spec --clean
```

## 许可证

MIT License
