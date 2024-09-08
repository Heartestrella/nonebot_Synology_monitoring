# Synology_monitoring/__init__.py

import nonebot
from nonebot import get_driver

from . import main, tool
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


def try_login() -> bool:
    global system_info
    from synology_api import core_sys_info

    try:
        sy_info = core_sys_info.SysInfo(*login_data)
        system_info = tool.Static_tools.parse_system_info(sy_info.get_system_info())
        return True
    except:
        KeyError(
            "登录失败，可能的原因：群晖IP错误，账密错误，尝试禁用https与验证证书和检查账密后重试"
        )


async def notify_user() -> None:
    q_id = next(iter(plugin_config["superusers"]))
    bot = nonebot.get_bot()
    await bot.send_private_msg(user_id=q_id, message="登录成功，系统详情为：")
    await bot.send_private_msg(user_id=q_id, message=system_info)


driver = get_driver()


@driver.on_bot_connect
async def on_startup():
    if try_login():
        print("登录成功")
        if plugin_config["superusers"]:
            await notify_user()
        else:
            print("未配置超级用户，将不会通知")


#################################  初始化完成 #######################################
