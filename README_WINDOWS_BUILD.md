# FinDataHub 桌面端打包指南

## GitHub 自动构建发布

项目已内置 `.github/workflows/desktop-release.yml`，支持在 GitHub Actions 中自动构建：

- Windows x86_64: `FinDataHub_v<版本>_Windows.zip`
- macOS Intel: `FinDataHub_v<版本>_macOS_x86_64.tar.gz`
- macOS Apple Silicon: `FinDataHub_v<版本>_macOS_arm64.tar.gz`

触发方式：

1. 推送版本标签，例如 `v1.1.0`，Actions 会构建 Windows/macOS 包并发布到 GitHub Releases。
2. 推送带后缀的版本标签，例如 `v1.1.0-rc.1`，Actions 会构建并标记为预发布版本。
3. 在 GitHub Actions 页面手动运行 `Desktop Release`，填写 tag，例如 `v1.1.0`，也可生成预发布版本。

自动流程包含：

1. 安装 Node 和 Python 环境。
2. 在 `frontend/` 执行 `npm ci` 与 `npm run build`。
3. 将前端 `dist` 复制到 `backend/static`。
4. 安装后端依赖和 PyInstaller。
5. 使用 `backend/build.spec` 构建单文件桌面程序。
6. 实际启动桌面程序，验证健康接口、首页和前端静态资源。
7. 使用 `scripts/package_desktop.py` 生成发布包并上传 Release。

## 前置要求

### Windows 系统
- Windows 10 或 Windows 11
- Python 3.8 或更高版本

### macOS 系统
- macOS 12 或更高版本
- Python 3.8 或更高版本

### 安装Python依赖
```bash
pip install -r backend/requirements.txt
pip install pyinstaller
```

## 打包步骤

### 方法一：使用批处理脚本（推荐）

1. 确保已完成前端构建和静态文件复制
2. 双击运行 `build_windows.bat`
3. 等待打包完成
4. 生成的压缩包位于 `dist/FinDataHub_v1.0.0_Windows.zip`

### 方法二：手动打包

#### 1. 构建前端
```bash
cd frontend
npm install
npm run build
```

#### 2. 复制前端静态文件到后端
```bash
# Windows
xcopy /E /I frontend\dist backend\static

# macOS/Linux
cp -r frontend/dist/* backend/static/
```

#### 3. 使用 PyInstaller 打包
```bash
cd backend
pyinstaller --clean build.spec
```

#### 4. 准备发布包
```bash
python scripts/package_desktop.py --platform windows --arch x86_64 --version 1.1.0
python scripts/package_desktop.py --platform macos --arch x86_64 --version 1.1.0
python scripts/package_desktop.py --platform macos --arch arm64 --version 1.1.0
```

## 发布包结构

```
FinDataHub_v1.0.0_Windows.zip
├── FinDataHub.exe          # 主程序（单文件）
├── start.bat               # 启动脚本
└── README.txt              # 使用说明

FinDataHub_v1.0.0_macOS_<架构>.tar.gz
├── FinDataHub              # 主程序（单文件）
├── start.command           # 启动脚本
└── README.txt              # 使用说明
```

## 用户使用说明

### 安装和运行
1. 下载 `FinDataHub_v1.0.0_Windows.zip`
2. 解压到任意文件夹
3. 双击 `start.bat` 或直接运行 `FinDataHub.exe`
4. 程序会自动打开浏览器访问 http://127.0.0.1:5001

### 数据存储
- 数据库文件自动保存在程序运行目录的 `data/` 下
- 无需额外配置

### 退出程序
- 在控制台窗口按 `Ctrl+C`

## 技术细节

### 打包配置
- 使用 PyInstaller 单文件模式
- 包含所有依赖（Flask、SQLAlchemy、pandas等）
- 内置前端静态文件
- 自动打开浏览器

### 端口配置
- 桌面包默认端口：5001
- 绑定地址：127.0.0.1（仅本地访问）

### 兼容性
- Windows 10/11
- macOS Intel 与 Apple Silicon 分包发布
- 无需预装Python
- 零依赖运行

## 常见问题

### Q: 程序无法启动？
A: 请确保：
- Windows Defender或杀毒软件未拦截
- 程序有读写权限
- 端口5001未被占用

### Q: 如何修改端口？
A: 目前端口在代码中固定为5001，如需修改请重新打包。

### Q: 数据库文件在哪里？
A: 数据库文件保存在程序运行目录下，文件名为 `findatahub.db`。

### Q: 如何备份数据？
A: 直接复制 `findatahub.db` 文件即可。
