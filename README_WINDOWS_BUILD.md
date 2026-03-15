# FinDataHub Windows 打包指南

## 前置要求

### Windows系统
- Windows 10 或 Windows 11（32位或64位）
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

#### 3. 使用PyInstaller打包
```bash
cd backend
pyinstaller --clean build.spec
```

#### 4. 准备发布包
```bash
# 创建发布目录
mkdir -p dist/FinDataHub_v1.0.0_Windows

# 复制文件
cp backend/dist/FinDataHub.exe dist/FinDataHub_v1.0.0_Windows/

# 创建README和启动脚本（参考build_windows.bat）

# 创建压缩包
cd dist
powershell Compress-Archive -Path FinDataHub_v1.0.0_Windows -DestinationPath FinDataHub_v1.0.0_Windows.zip
```

## 发布包结构

```
FinDataHub_v1.0.0_Windows.zip
├── FinDataHub.exe          # 主程序（单文件）
├── 启动.bat                 # 启动脚本
└── README.txt              # 使用说明
```

## 用户使用说明

### 安装和运行
1. 下载 `FinDataHub_v1.0.0_Windows.zip`
2. 解压到任意文件夹
3. 双击 `启动.bat` 或直接运行 `FinDataHub.exe`
4. 程序会自动打开浏览器访问 http://127.0.0.1:5001

### 数据存储
- 数据库文件自动保存在程序运行目录
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
- 默认端口：5001
- 绑定地址：127.0.0.1（仅本地访问）

### 兼容性
- Windows 10/11 (32位/64位)
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
