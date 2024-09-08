import os
import time

from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, Event, MessageSegment

from . import tool

file_tree = on_command("file_tree", aliases={"file tree", "文件树"})


@file_tree.handle()
async def handle_file_tree(bot: Bot, event: Event):
    user_id = event.get_user_id()

    await bot.send(event, message="正在生成文件树... 预计时长：5分钟")
    file_path = await tool.Static_tools.get_file_tree()
    # file_path = "/root/bot/monitors/20240908_133047_file_tree.txt"
    file_name = os.path.basename(file_path)
    print(file_path, file_name)
    if os.path.exists(file_path):
        await bot.call_api(
            "upload_private_file",
            user_id=int(user_id),
            file=file_path,
            name=file_name,
        )
        os.remove(file_path)
    else:
        await bot.send(event, message="文件不存在")


disks_info = on_command("硬盘状态", aliases={"disks_info", "disks info"})


@disks_info.handle()
async def _(bot: Bot, event: Event):
    reports, disks = await tool.Static_tools.get_disks_info()
    await bot.send(event, message=f"共计 {disks}块硬盘 将逐条发送概况")
    for report in reports:
        await bot.send(event, message=report)
        time.sleep(1)
    await bot.send(event, message="发送完成")


pools_info = on_command("储存池状态", aliases={"pools_info", "pools info"})


@pools_info.handle()
async def _(bot: Bot, event: Event):
    reports, pools = await tool.Static_tools.get_pools_info()
    await bot.send(event, message=f"共计 {pools}个储存池 将逐条发送概况")
    for report in reports:
        await bot.send(event, message=report)
        time.sleep(1)
    await bot.send(event, message="发送完成")
