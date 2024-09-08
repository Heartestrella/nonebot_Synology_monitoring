
# Synology Monitoring 插件

`Synology Monitoring` 插件用于监控和报告 Synology NAS 设备的系统信息、文件树、硬盘状态和存储池状态。该插件集成了 NoneBot 框架，并与 Synology 的 API 交互以获取相关信息。

## 功能

- **系统信息**: 提供设备的基本信息、CPU、内存、温度、NTP 服务器等详细信息。
- **文件树**: 生成并下载 Synology NAS 上的文件树。
- **硬盘状态**: 获取并报告硬盘的健康状态、总大小和温度。
- **存储池状态**: 获取并报告存储池的详细信息，包括 RAID 状态和数据检查状态。

## 安装

PASS

## 配置
``` markdown
SYNOLOGY_IP=
SYNOLOGY_PORT=5000
SYNOLOGY_USER=
SYNOLOGY_PASSWORD=
DSM_VERSION=7
SECURE=False
VERIFY_CERT=False
```
将上述内容添加到bot根目录的.env文件中

## 使用

1. **启动插件**: 在 NoneBot 启动时，插件会尝试登录到 Synology NAS 并进行初始化。
2. **查看系统信息**: 信息将在第一次成功启动并连接上群晖时发送到配置文件或环境变量中的SUPERUSERS QQ中
3. **生成文件树**: 发送命令 `/file_tree` 或 `文件树` 到机器人，生成并发送文件树 以txt文件。
4. **查看硬盘状态**: 发送命令 `/硬盘状态` 或 `disks_info` 到机器人获取每块硬盘的概况。
5. **查看存储池状态**: 发送命令 `/储存池状态` 或 `pools_info` 到机器人获取每个储存池的概况。

## 注意事项

- 确保你的 Synology NAS 已启用相应的 API 权限。
- 确保你的网络配置允许从 NoneBot 服务器访问 Synology NAS。
- 请根据你的具体需求和环境调整配置和命令。

## 贡献

欢迎提交问题和 pull requests。请遵循 [贡献指南](CONTRIBUTING.md) 以便我们更好地协作。

## 许可证

本项目使用 [MIT 许可证](LICENSE)。

## 联系

如有问题，请联系 [1726732091@qq.com] 或在项目的 [Issues](https://github.com/Heartestrella/nonebot_Synology_monitoring/issues) 中提出问题。

