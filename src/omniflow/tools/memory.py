"""内存操作 Tools."""

from ..engine import com as engine


def read(pid: int, address: int, size: int = 4):
    data = engine.mem_read(pid, address, size)
    return {"data_hex": data.hex(), "size": len(data)}


def write(pid: int, address: int, data_hex: str):
    data = bytes.fromhex(data_hex)
    ok = engine.mem_write(pid, address, data)
    return {"status": "ok", "written": ok}


def get_module_base(pid: int, module_name: str = ""):
    base = engine.get_module_base(pid, module_name)
    return {"base": base}
