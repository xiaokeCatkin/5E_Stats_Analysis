import requests
import pandas as pd
import time
import urllib3
from datetime import datetime, timezone
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import openpyxl
from pathlib import Path
import os
import sys
import argparse


# ======================
# 动态路径配置
# ======================
# 获取当前脚本所在目录
SCRIPT_DIR = Path(__file__).parent.resolve()
# 项目根目录设为脚本目录的父目录
PROJECT_ROOT = SCRIPT_DIR.parent
# 保存目录设为项目根目录下的stats_saved
SAVE_DIR = PROJECT_ROOT / "stats_saved"

# 确保保存目录存在
os.makedirs(SAVE_DIR, exist_ok=True)


# ======================
# 配置参数
# ======================
API_BASE = "https://gate.5eplay.com/crane/http/api/data"
BEARER_TOKEN = ""
UUID = "3cea4f9e-a7ca-11ea-8109-ec0d9a7185b0"  # 用户唯一标识

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ======================
# 增强请求会话配置
# ======================
session = requests.Session()
retry_strategy = Retry(
    total=5,
    backoff_factor=0.5,
    status_forcelist=[500, 502, 503, 504],
    allowed_methods=["GET"]
)
adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("https://", adapter)

# ======================
# API请求工具函数
# ======================
def make_api_request(endpoint, params=None):
    """带重试机制的API请求"""
    headers = {
        # "Authorization": f"Bearer {BEARER_TOKEN}",
        "Authorization": f"", 
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://view-arena.5eplay.com/"
    }

    try:
        response = session.get(
            f"{API_BASE}/{endpoint}",
            params=params,
            headers=headers,
            timeout=15,
            verify=False  # 关闭SSL验证
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"API请求失败: {str(e)}")
        return None


# ======================
# 数据转换函数
# ======================
def convert_timestamp(ts):
    """修复时区警告的时间转换"""
    try:
        return datetime.fromtimestamp(int(ts), tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
    except (ValueError, TypeError):
        return "N/A"

# ======================
# 字段映射字典
# ======================
FIELD_MAPPING = {
    "match_id": "比赛ID",
    "map": "地图",
    "is_win": "胜负",
    "start_time": "开始时间",
    "end_time": "结束时间",
    "kill": "击杀数",
    "death": "死亡数",
    "rws": "RWS评分",
    "change_elo": "ELO变动",
    "origin_elo": "初始ELO",
    "level_name": "当前段位",
    "adr": "ADR",
    "rating": "Rating",
    "per_headshot": "爆头率",
    "awp_kill": "AWP击杀",
    "assist": "助攻",
    "flash_enemy": "闪光助攻",
    "is_mvp": "MVP次数",
    "round_total": "总回合数",
     "group1_all_score": "我方得分",
    "group2_all_score": "敌方得分",
    "match_code": "比赛代码",
     "match_mode": "比赛模式",
    "most_1v2_uid": "最佳1v2玩家ID",
    "most_assist_uid": "最佳助攻玩家ID",
    "most_awp_uid": "最佳AWP玩家ID",
    "most_end_uid": "最佳终结玩家ID",
    "most_first_kill_uid": "最佳首杀玩家ID",
    "most_headshot_uid": "最佳爆头玩家ID",
     "most_jump_uid": "最佳跳杀玩家ID",
   "knife_winner_role": "刀战胜利方阵营",
   "knife_winner": "刀战胜利方",
    "group1_fh_score": "上半场我方得分",
    "group2_fh_score": "上半场敌方得分",
    "group1_sh_score": "下半场我方得分",
    "group2_sh_score": "下半场敌方得分",
    "location": "比赛服务器位置",
    "location_full": "比赛服务器完整位置",
    "season": "比赛赛季",
     "server_ip": "服务器IP地址",
    "server_port": "服务器端口",
   "status": "比赛状态",
    "waiver":"弃赛",
    "year":"比赛年份",
    "cs_type":"比赛类型",
     "priority_show_type":"优先显示类型",
     "pug10m_show_type":"Pug 10m显示类型",
     "credit_match_status":"积分赛状态",
    "demo_url":"比赛demo地址",
     "game_mode":"比赛模式",
    "game_name":"比赛名称",
     "group1_change_elo":"我方ELO变化",
     "group2_change_elo":"敌方ELO变化",
    "group1_fh_role":"上半场我方阵营",
    "group2_fh_role":"上半场敌方阵营",
    "group1_sh_role":"下半场我方阵营",
    "group2_sh_role":"下半场敌方阵营",
     "group1_tid":"我方队伍ID",
    "group2_tid":"敌方队伍ID",
    "group1_uids":"我方玩家UID",
    "group2_uids":"敌方玩家UID",
     "id":"比赛ID",
    "map_desc":"地图描述",
    "match_winner":"比赛胜利者",
    "data_tips_detail":"数据提示详情",
     "challenge_status":"挑战状态",
     "map_reward_status":"地图奖励状态",
      "change_rank":"排名变动",
      "origin_level_id":"初始等级ID",
      "rank_change_type":"排名变动类型",
      "level_id":"等级ID",
      "match_flag":"比赛标志",
    "match_status":"比赛状态",
     "origin_match_total":"初始比赛总数",
    "placement":"比赛排名",
    "punishment":"惩罚",
    "rank":"当前排名",
    "origin_rank":"初始排名",
    "special_data":"特殊数据",
    "uid":"玩家UID",
    "domain":"玩家domain",
    "nickname":"玩家昵称",
     "avatarUrl":"玩家头像地址",
     "avatarAuditStatus":"玩家头像审核状态",
     "rgbAvatarUrl":"RGB玩家头像地址",
     "photoUrl":"玩家照片地址",
     "gender":"玩家性别",
     "birthday":"玩家生日",
     "countryId":"玩家国家ID",
     "regionId":"玩家区域ID",
     "cityId":"玩家城市ID",
     "language":"玩家语言",
      "recommendUrl":"玩家推荐地址",
      "groupId":"玩家分组ID",
     "status":"玩家状态",
      "expire":"玩家过期时间",
      "cancellationStatus":"玩家注销状态",
      "newUser":"是否新用户",
     "loginBannedTime":"登录禁止时间",
      "anticheatType":"反作弊类型",
      "flagStatus1":"旗帜状态1",
      "anticheatStatus":"反作弊状态",
     "FlagHonor":"荣誉旗帜",
      "level":"平台等级",
      "exp":"平台经验",
    "steamId":"steamID",
      "steamAccount":"steam账号",
      "tradeUrl":"交易地址",
      "credit":"信用分",
      "creditLevel":"信用等级",
      "score":"玩家评分",
      "creditStatus":"信用状态",
      "idType":"身份证类型",
      "age":"年龄",
      "realName":"真实姓名",
       "uidList":"玩家ID列表",
      "auditStatus":"审核状态",
     "type":"身份类型",
      "extras":"附加信息",
      "slogan":"标语",
     "usernameAuditStatus":"用户名审核状态",
    "Accid":"账号ID",
    "teamID":"队伍ID",
    "trumpetCount":"喇叭数量",
     "is_plus":"是否plus",
     "plus_icon":"plus图标",
      "plus_icon_short":"plus短图标",
      "vip_level":"VIP等级",
      "plus_grade":"plus等级",
     "growth_score":"成长分数",
      "map_exp":"地图经验",
       "add_exp":"额外经验",
    "plat_level_exp":"平台等级经验",
       "is_most_1v2":"是否最佳1v2",
        "is_most_assist":"是否最佳助攻",
       "is_most_awp":"是否最佳AWP",
        "is_most_end":"是否最佳终结者",
        "is_most_first_kill":"是否最佳首杀",
        "is_most_headshot":"是否最佳爆头",
         "is_most_jump":"是否最佳跳杀",
      "many_assists_cnt1":"1助攻次数",
        "many_assists_cnt2":"2助攻次数",
        "many_assists_cnt3":"3助攻次数",
         "many_assists_cnt4":"4助攻次数",
        "many_assists_cnt5":"5助攻次数",
        "perfect_kill":"完美击杀",
      "assisted_kill":"助攻击杀",
     "revenge_kill":"复仇击杀",
    "team_kill":"队友击杀",
        "throw_harm":"投掷伤害",
     "throw_harm_enemy":"对敌投掷伤害",
    "defused_bomb":"拆包数",
    "end_1v1":"1v1残局次数",
     "end_1v2":"1v2残局次数",
     "end_1v3":"1v3残局次数",
     "end_1v4":"1v4残局次数",
    "end_1v5":"1v5残局次数",
     "explode_bomb":"炸弹爆炸数",
    "first_death":"首死次数",
    "first_kill":"首杀次数",
    "flash_enemy_time":"闪光对敌时间",
     "flash_team":"闪光队友次数",
    "flash_team_time":"闪光队友时间",
    "flash_time":"闪光次数",
     "group_id":"分组ID",
     "hold_total":"总持枪时间",
    "is_highlight":"是否高光",
     "jump_total":"跳跃次数",
     "kast":"KAST评分",
    "planted_bomb":"安装炸弹数",
    "rating2":"rating2评分",
     "level_elo":"等级ELO",
    "max_level":"最大等级",
    "origin_level_id":"初始等级ID",
     "special_bo":"特殊加成",
     "rise_type":"上升类型",
     "tie_status":"平局状态",
    "is_tie": "是否平局",
     "kill_1":"一杀次数",
      "kill_2":"二杀次数",
    "kill_3":"三杀次数",
    "kill_4":"四杀次数",
     "kill_5":"五杀次数"
}
def process_match_list(matches):
    """处理比赛列表数据"""
    processed = []
    for match in matches:
      try:
        processed_match = {}
        for key, value in match.items():
           if key in FIELD_MAPPING:
             if key == "start_time" or key == "end_time":
                processed_match[FIELD_MAPPING.get(key)] = convert_timestamp(value)
             elif key == "is_win":
                processed_match[FIELD_MAPPING.get(key)] = "胜利" if value else "失败"
             elif key == "level_name":
                  processed_match[FIELD_MAPPING.get(key)] = match.get("level_info", {}).get("level_name", "N/A")
             else:
                 processed_match[FIELD_MAPPING.get(key)] = value
           elif key == "level_info":
              processed_match[FIELD_MAPPING.get("origin_elo")] = float(match.get("level_info", {}).get("origin_elo", 0)) + float(match.get("change_elo", 0))
        if processed_match.get("开始时间") and processed_match.get("结束时间"):
           processed_match["持续时间(分钟)"] = (datetime.fromisoformat(processed_match.get("结束时间")).timestamp() -  datetime.fromisoformat(processed_match.get("开始时间")).timestamp()) // 60
        processed.append(processed_match)

      except Exception as e:
          print(f"处理比赛列表数据时出错: {str(e)}")

    return pd.DataFrame(processed)


def process_match_detail(detail):
    """处理单场比赛详情，提取所有信息"""
    players_data = []
    match_info = {}
    try:
        match_id = detail.get("data", {}).get("main", {}).get("match_code", "N/A")
         # Extract match main information
        main_data = detail.get("data", {}).get("main", {})
        match_info = {f"比赛_{FIELD_MAPPING.get(k, k)}":v for k,v in main_data.items()}
        match_info["比赛ID"] = match_id
        
        # Process player data for group_1 and group_2
        for group in ["group_1", "group_2"]:
           for player in detail.get("data", {}).get(group, []):
                player_data = {"比赛ID": match_id} # Add MatchID

                # Flatten user_info
                user_data = player.get("user_info", {}).get("user_data",{})
                for k, v in user_data.items():
                    if isinstance(v, dict):
                        for k2, v2 in v.items():
                            player_data[f"玩家_{FIELD_MAPPING.get(k, k)}_{FIELD_MAPPING.get(k2, k2)}"] = v2
                    else:
                         player_data[f"玩家_{FIELD_MAPPING.get(k, k)}"] = v
                        
                # Flatten other player data
                for k, v in player.items():
                     if k not in ["user_info","sts", "level_info","fight_t", "fight_ct"]:
                         if isinstance(v, dict):
                            for k2, v2 in v.items():
                                player_data[f"玩家_{FIELD_MAPPING.get(k, k)}_{FIELD_MAPPING.get(k2, k2)}"] = v2
                         else:
                             player_data[f"玩家_{FIELD_MAPPING.get(k, k)}"] = v

                # Flatten fight data
                fight_data = player.get("fight", {})
                if fight_data:
                    for k, v in fight_data.items():
                         if isinstance(v,str) and k in ["per_headshot", "adr", "rating", "rating2", "rws"]:
                             try:
                                player_data[f"fight_{FIELD_MAPPING.get(k, k)}"] = float(v)
                             except ValueError:
                                player_data[f"fight_{FIELD_MAPPING.get(k, k)}"] = v
                         else:
                             player_data[f"fight_{FIELD_MAPPING.get(k, k)}"] = v

                players_data.append(player_data)
                
        if not players_data:
            print(f"警告: 比赛 {match_id} 没有玩家数据")
    except Exception as e:
        print(f"处理比赛详情时发生严重错误: {str(e)}")
        return pd.DataFrame(), {}

    return pd.DataFrame(players_data), match_info



# ======================
# 主程序逻辑
# ======================
def generate_report(start_time=1000000000, end_time=9999999999, limit=3, 
                   UUID="3cea4f9e-a7ca-11ea-8109-ec0d9a7185b0", 
                   max_pages=3, match_type=-1, cs_type=0, date=0):
    """生成CSGO比赛报告
    Args:
        start_time: 开始时间戳(默认1000000000)
        end_time: 结束时间戳(默认9999999999)
        limit: 每页限制数量(默认3)
        UUID: 用户唯一标识符
        max_pages: 最大页数(默认3)
        match_type: 比赛类型(默认-1表示全部)
        cs_type: CS类型(默认0)
        date: 日期筛选(默认0)
    """
    all_matches = []
    all_details = []
    match_infos = []

    page = 1
    # max_pages = 1  # 安全限制

    while page <= max_pages:
        print(f"正在获取第 {page} 页数据...")
        params = {
            "match_type": match_type,
            "page": page,
            "date": date,
            "start_time": start_time,
            "end_time": end_time,
            "uuid": UUID,
            "limit": limit,
            "cs_type": cs_type
        }

        data = make_api_request("match/list", params)

        if not data or not data.get("data"):
            print(f"第 {page} 页无有效数据，终止分页")
            break

        # 处理比赛列表
        df_matches = process_match_list(data["data"])
        if not df_matches.empty:
            all_matches.append(df_matches)
            print(f"成功处理 {len(df_matches)} 条比赛汇总数据")
        else:
            print(f"第 {page} 页比赛汇总数据格式异常")

        # 处理比赛详情
        total_matches = len(data["data"])
        for idx, match in enumerate(data["data"], 1):
            match_id = match.get('match_id', None)
            if not match_id:
                print(f"警告：比赛 {idx} 没有 'match_id'，跳过")
                continue

            print(f"正在处理比赛 {idx}/{total_matches}：{match_id}...")
            detail = make_api_request(f"match/{match_id}")
            if detail:
                df_players, info = process_match_detail(detail)
                if not df_players.empty:
                    all_details.append(df_players)
                    print(f"比赛 {idx}/{total_matches}: 成功处理 {len(df_players)} 条玩家数据")
                else:
                     print(f"比赛 {idx}/{total_matches}: 没有玩家数据")
                if info:
                    match_infos.append(info)
            else:
                 print(f"比赛 {idx}/{total_matches} 数据获取失败，跳过")
            time.sleep(1.2)  # 降低请求频率

        page += 1
        time.sleep(1)  # 页间延迟

    # 安全合并数据
    try:
        final_matches = pd.concat(all_matches, ignore_index=True) if all_matches else pd.DataFrame(columns=["比赛ID"])
        final_details = pd.concat(all_details, ignore_index=True) if all_details else pd.DataFrame(columns=["比赛ID"])
        final_infos = pd.DataFrame(match_infos) if match_infos else pd.DataFrame(columns=["比赛ID"])
            
        # 处理玩家数据并获取玩家名称
        if not final_details.empty:
            # 删除第4列到第68列
            columns_to_drop = final_details.columns[4:138]
            final_details = final_details.drop(columns=columns_to_drop)
            # 只保留UUID匹配的行
            target_uuid = UUID
            filtered_details = final_details[final_details['玩家_uuid'] == target_uuid]
            player_name = filtered_details['玩家_username'].iloc[0] if not filtered_details.empty else "未知玩家"
            current_date = datetime.now().strftime("%Y%m%d")
            
            # 保存玩家数据文件
            filtered_details.to_csv(str(SAVE_DIR / f"filtered_csgo_report_players_{player_name}_{current_date}.csv"), index=False, encoding='utf_8_sig')
            print(f"已写入 {len(filtered_details)} 条过滤后的玩家数据到 {str(SAVE_DIR / f'filtered_csgo_report_players_{player_name}_{current_date}.csv')}")
            final_details.to_csv(str(SAVE_DIR / f"csgo_report_players_{player_name}_{current_date}.csv"), index=False, encoding='utf_8_sig')
            print(f"已写入 {len(final_details)} 条玩家数据到 {str(SAVE_DIR / f'csgo_report_players_{player_name}_{current_date}.csv')}")
        else:
            player_name = "未知玩家"
            current_date = datetime.now().strftime("%Y%m%d")
            print("警告：无玩家数据")
        
        # 处理比赛汇总数据
        if not final_matches.empty:
            final_matches.to_csv(str(SAVE_DIR / f"csgo_report_matches_{player_name}_{current_date}.csv"), index=False, encoding='utf_8_sig')
            print(f"已写入 {len(final_matches)} 条比赛汇总数据到 {str(SAVE_DIR / f'csgo_report_matches_{player_name}_{current_date}.csv')}")
        else:
            print("警告：无比赛汇总数据")
        
        # 处理比赛详情数据
        if not final_infos.empty:
            final_infos.to_csv(str(SAVE_DIR / f"csgo_report_info_{player_name}_{current_date}.csv"), index=False, encoding='utf_8_sig')
            print(f"已写入 {len(final_infos)} 条比赛详情到 {str(SAVE_DIR / f'csgo_report_info_{player_name}_{current_date}.csv')}")
        else:
            print("警告：无比赛详情数据")
            
        # 生成Excel报告
        if not final_matches.empty or not final_details.empty or not final_infos.empty:
            with pd.ExcelWriter(str(SAVE_DIR / f'csgo_report_{player_name}_{current_date}.xlsx')) as writer:
                pd.read_csv(str(SAVE_DIR / f'csgo_report_matches_{player_name}_{current_date}.csv')).to_excel(writer, sheet_name='比赛汇总', index=False)
                pd.read_csv(str(SAVE_DIR / f'csgo_report_players_{player_name}_{current_date}.csv')).to_excel(writer, sheet_name='玩家数据', index=False)
                pd.read_csv(str(SAVE_DIR / f'csgo_report_info_{player_name}_{current_date}.csv')).to_excel(writer, sheet_name='比赛详情', index=False)
                print(f"已写入Excel文件 {str(SAVE_DIR / f'csgo_report_{player_name}_{current_date}.xlsx')}")

        print("报告生成完成！")
    except Exception as e:
        print(f"最终数据合并失败: {str(e)}")
        raise


def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='CS:GO比赛数据分析工具')
    parser.add_argument('--uuid', required=True, help='玩家UUID')
    parser.add_argument('--start_time', type=int, default=1000000000, help='开始时间戳')
    parser.add_argument('--end_time', type=int, default=9999999999, help='结束时间戳')
    parser.add_argument('--limit', type=int, default=3, help='每页限制数量')
    parser.add_argument('--max_pages', type=int, default=3, help='最大页数')
    parser.add_argument('--match_type', type=int, default=-1, help='比赛类型')
    parser.add_argument('--cs_type', type=int, default=0, help='CS类型')
    parser.add_argument('--date', type=int, default=0, help='日期筛选')
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    generate_report(
        start_time=args.start_time,
        end_time=args.end_time,
        limit=args.limit,
        UUID=args.uuid,
        max_pages=args.max_pages,
        match_type=args.match_type,
        cs_type=args.cs_type,
        date=args.date
    )