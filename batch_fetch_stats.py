import os
import subprocess
from pathlib import Path

# 配置路径
SCRIPT_DIR = Path(__file__).parent.resolve()
MAIN_SCRIPT = SCRIPT_DIR / "Get_Stats" / "main_script.py"
UUID_FILE = SCRIPT_DIR / "uuid对照表"

def read_uuid_mapping():
    """读取uuid对照表"""
    uuid_map = {}
    with open(UUID_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                name, uuid = line.strip().split()
                uuid_map[name] = uuid
    return uuid_map

def fetch_stats_for_all():
    """为所有玩家获取战绩"""
    uuid_map = read_uuid_mapping()
    
    for name, uuid in uuid_map.items():
        print(f"\n正在获取玩家 {name} (UUID: {uuid}) 的战绩...")
        
        # 调用main_script.py
        cmd = [
            'python', 
            str(MAIN_SCRIPT),
            '--uuid', uuid,
            '--max_pages', '3',
            '--limit', '3'
        ]
        
        try:
            subprocess.run(cmd, check=True)
            print(f"玩家 {name} 的战绩获取完成")
        except subprocess.CalledProcessError as e:
            print(f"获取玩家 {name} 战绩时出错: {str(e)}")

if __name__ == "__main__":
    fetch_stats_for_all()