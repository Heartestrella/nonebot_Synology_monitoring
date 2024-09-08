# Synology_monitoring/tool.py
import asyncio
import os
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

import aiofiles
import nonebot
from synology_api import core_sys_info, filestation

from .config import SynologyConfig

plugin_config = nonebot.get_driver().config.model_dump()
config_ = SynologyConfig(**plugin_config)
login_data = (
    config_.synology_ip,
    config_.synology_port,
    config_.synology_user,
    config_.synology_password,
    config_.secure,
    config_.dsm_version,
)

executor = ThreadPoolExecutor()


class Static_tools:
    @staticmethod
    def parse_system_info(data: dict):
        info = data["data"]
        result = []

        # 基本信息
        result.append(f"系统型号: {info['model']}")
        result.append(f"序列号: {info['serial']}")
        result.append(f"固件版本: {info['firmware_ver']}")
        result.append(f"固件日期: {info['firmware_date']}")
        result.append(f"系统时间: {info['time']}")
        result.append(f"时区: {info['time_zone']} ({info['time_zone_desc']})")
        result.append(f"运行时间: {info['up_time']}")

        # CPU 信息
        result.append("\nCPU 信息:")
        result.append(f" - 频率: {info['cpu_clock_speed']} MHz")
        result.append(f" - 核心数: {info['cpu_cores']}")
        result.append(f" - 系列: {info['cpu_series']}")
        result.append(f" - 家族: {info['cpu_family']}")
        result.append(f" - 供应商: {info['cpu_vendor']}")

        # 内存信息
        result.append(f"\n内存大小: {info['ram_size']} MB")

        # 温度信息
        result.append(f"\n系统温度: {info['sys_temp']}°C")
        result.append(f"温度警告: {'有' if info['temperature_warning'] else '无'}")
        result.append(f"系统警告: {'有' if info['systempwarn'] else '无'}")

        # NTP 信息
        result.append(f"\nNTP 服务器: {info['ntp_server']}")
        result.append(f"NTP 启用: {'是' if info['enabled_ntp'] else '否'}")

        # PCI 插槽信息
        result.append("\nPCI 插槽信息:")
        for slot in info["external_pci_slot_info"]:
            result.append(
                f" - 插槽 {slot['slot']}: {slot['cardName']} (占用: {slot['Occupied']}, 识别: {slot['Recognized']})"
            )

        # USB 设备信息
        result.append("\nUSB 设备信息:")
        for usb in info["usb_dev"]:
            result.append(
                f" - 产品: {usb['product']}, 生产商: {usb['producer']}, VID: {usb['vid']}, PID: {usb['pid']}, 类别: {usb['cls']}, 版本: {usb['rev']}"
            )

        # SATA 设备信息
        result.append("\nSATA 设备信息:")
        if info["sata_dev"]:
            for sata in info["sata_dev"]:
                result.append(f" - {sata}")
        else:
            result.append(" - 无")

        # eSATA 支持信息
        result.append(
            f"\neSATA 支持: {'有' if info['support_esata'] == 'yes' else '无'}"
        )

        return "\n".join(result)

    @staticmethod
    async def get_file_tree():
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(os.getcwd(), f"{current_time}_file_tree.txt")
        file_type_count = defaultdict(int)
        total_files = 0

        file_info = filestation.FileStation(*login_data)

        # 使用 run_in_executor 来异步调用同步的阻塞操作
        share_folders = await asyncio.get_event_loop().run_in_executor(
            executor, file_info.get_list_share
        )

        tree_structure = ""

        # 定义递归函数用于遍历目录
        async def traverse_directory(path, level=0, tree_str=""):
            nonlocal total_files  # 使用外部变量 total_files

            # 使用 run_in_executor 来异步调用 get_file_list
            folder_content = await asyncio.get_event_loop().run_in_executor(
                executor, file_info.get_file_list, path
            )

            if folder_content.get("success"):
                for item in folder_content["data"]["files"]:
                    # 根据缩进级别生成树形结构
                    tree_str += "    " * level + "|-- " + item["name"] + "\n"

                    if item["isdir"]:
                        # 如果是文件夹，递归遍历
                        tree_str = await traverse_directory(
                            item["path"], level + 1, tree_str
                        )
                    else:
                        # 如果是文件，增加文件类型计数
                        file_extension = os.path.splitext(item["name"])[1].lower()
                        file_type_count[file_extension] += 1
                        total_files += 1

            return tree_str

        # 遍历共享文件夹
        if share_folders.get("success"):
            for share in share_folders["data"]["shares"]:
                tree_structure += share["name"] + "\n"
                tree_structure = await traverse_directory(
                    share["path"], 1, tree_structure
                )

        # 异步将树形结构写入文件
        async with aiofiles.open(output_file, "w", encoding="utf-8") as f:
            await f.write(tree_structure)

        # 打印文件类型占比统计
        print("\n文件类型占比:")
        for file_type, count in file_type_count.items():
            percentage = (count / total_files) * 100 if total_files > 0 else 0
            print(f"{file_type}: {count} files, 占比: {percentage:.2f}%")

        # 异步将文件类型统计写入文件
        async with aiofiles.open(output_file, "a", encoding="utf-8") as f:
            await f.write("\n\n文件类型占比:\n")
            for file_type, count in file_type_count.items():
                percentage = (count / total_files) * 100 if total_files > 0 else 0
                await f.write(f"{file_type}: {count} files, 占比: {percentage:.2f}%\n")

        return output_file

    @staticmethod
    async def get_disks_info():
        core = core_sys_info.SysInfo(*login_data)
        disks = 0
        reports = []

        data = core.storage()
        for disk in data["data"]["disks"]:
            device = disk.get("device", "未知")
            model = disk.get("model", "未知")
            size_total = int(disk.get("size_total", 0)) / (1024**3)  # 转换为 GB
            drive_status_key = disk.get("drive_status_key", "未知")
            status = disk.get("status", "未知")
            temp = disk.get("temp", "未知")

            report = (
                f"硬盘: {model}；挂载于 {device}；总大小 {size_total:.2f} GB \n"
                f"当前健康状态：{drive_status_key}；运行状态：{status} 温度；{temp} 度\n"
            )

            reports.append(report)
            disks += 1
        return reports, disks

    @staticmethod
    async def get_pools_info():
        core = core_sys_info.SysInfo(*login_data)
        pools = 0
        reports = []

        data = core.storage()
        for pool in data["data"]["storagePools"]:
            pool_id = pool.get("id", "未知")
            description = pool.get("desc", "无描述")
            disks = ", ".join(pool.get("disks", []))
            total_size = float(pool["size"]["total"]) / (1024**3)  # 转换为 GB
            raid_status = pool.get("raidType", "未知")
            status = pool.get("status", "未知")
            scrubbing_status = pool.get("scrubbingStatus", "未知")

            report = (
                f"存储池 ID: {pool_id}\n"
                f"描述: {description}\n"
                f"包含硬盘: {disks}\n"
                f"总大小: {total_size:.2f} GB\n"
                f"RAID 状态: {raid_status}\n"
                f"当前状态: {status}\n"
                f"数据检查状态: {scrubbing_status}\n"
            )

            reports.append(report)
            pools += 1
        return reports, pools
