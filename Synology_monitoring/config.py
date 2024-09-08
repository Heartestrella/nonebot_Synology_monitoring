# Synology_monitoring/config.py

from pydantic import BaseModel, validator


class SynologyConfig(BaseModel):
    synology_ip: str
    synology_port: int = 5000
    synology_user: str
    synology_password: str
    dsm_version: int = 7
    secure: bool = False
    verify_cert: bool = False

    @validator("synology_port")
    def check_synology_port(cls, value):
        if value <= 0:
            raise ValueError("synology_port 必须是正整数")
        return value

    @validator("dsm_version")
    def check_dsm_version(cls, value):
        if value not in [6, 7]:
            raise ValueError("dsm_version 必须是 6 或 7")
        return value

    @validator("secure", "verify_cert", pre=True, always=True)
    def check_boolean(cls, value):
        if isinstance(value, str):
            if value.lower() in ["true", "1"]:
                return True
            elif value.lower() in ["false", "0"]:
                return False
        elif isinstance(value, bool):
            return value
        raise ValueError("secure 和 verify_cert 必须是布尔值（True 或 False）")
