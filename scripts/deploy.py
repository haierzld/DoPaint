# -*- coding: utf-8 -*-
"""部署/重启远程服务器 DoPaint 服务"""
import paramiko, io, sys, time

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

HOST, USER, PWD = "47.253.177.168", "root", "zld.123456"

c = paramiko.SSHClient()
c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
c.connect(HOST, 22, USER, PWD, timeout=30)

print("=== 停止旧服务 ===")
c.exec_command("pkill -f 'uvicorn main:app' 2>/dev/null; echo done")

print("=== 拉取代码 ===")
_, o, _ = c.exec_command("cd /root/DoPaint && git pull")
print(o.read().decode(errors='replace'))

print("=== 安装依赖 ===")
_, o, _ = c.exec_command("cd /root/DoPaint && ./venv/bin/pip install -r requirements.txt -q 2>&1 | tail -3")
print(o.read().decode(errors='replace'))

print("=== 启动服务 ===")
c.exec_command("cd /root/DoPaint && nohup ./venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8000 > /tmp/dopaint.log 2>&1 &")
time.sleep(3)

print("=== 服务状态 ===")
_, o, _ = c.exec_command("ps aux | grep 'uvicorn main:app' | grep -v grep")
out = o.read().decode(errors='replace')
if out.strip():
    print(out)
else:
    print("WARNING: 服务未运行！")
    _, o, _ = c.exec_command("tail -20 /tmp/dopaint.log")
    print(o.read().decode(errors='replace'))

c.close()
print("\n部署完成！")
