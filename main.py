import csv
import re
import random
import tkinter as tk
from tkinter import messagebox
import os

def read_bestiary(file_path):
    try:
        with open(file_path, mode='r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            database = [row for row in csv_reader]
        return database
    except FileNotFoundError:
        messagebox.showerror("错误", f"未找到文件: {file_path}")
        return []

def find_creature_by_name(database, name):
    name = name.lower()
    pattern = re.compile(name)
    for creature in database:
        if pattern.search(creature['Name'].lower()):
            actions = creature.get('Actions', '')
            bonus_actions = creature.get('Bonus Actions', '')
            reactions = creature.get('Reactions', '')
            legendary_actions = creature.get('Legendary Actions', '')
            mythic_actions = creature.get('Mythic Actions', '')
            return creature, actions, bonus_actions, reactions, legendary_actions, mythic_actions
    return None, '', '', '', '', ''

def extract_attack_bonus(text):
    pattern = r'Attack: \+(\d+) to hit'
    matches = re.findall(pattern, text)
    return matches

def extract_damage(text):
    pattern = r'Hit: (\d+) \((\d+d\d+\s*\+\s*\d+|\d+d\d+)\) \w+\s*damage'
    matches = re.findall(pattern, text)
    return [(int(m[0]), m[1]) for m in matches]

def roll_attack_bonus(bonus):
    return random.randint(1, 20) + int(bonus)

def roll_damage(damage):
    try:
        match = re.match(r'(\d+)d(\d+)\s*\+\s*(\d+)', damage)
        if match:
            num_dice, dice_sides, bonus = map(int, match.groups())
            return sum(random.randint(1, dice_sides) for _ in range(num_dice)) + bonus
        match = re.match(r'(\d+)d(\d+)', damage)
        if match:
            num_dice, dice_sides = map(int, match.groups())
            return sum(random.randint(1, dice_sides) for _ in range(num_dice))
    except Exception as e:
        messagebox.showerror("错误", f"无法解析伤害格式: {damage}\n错误信息: {e}")
    return 0

def format_text(text, words_per_line=30):
    words = text.split()
    lines = [' '.join(words[i:i + words_per_line]) for i in range(0, len(words), words_per_line)]
    return '\n'.join(lines)

def search_creature():
    # 清除之前的按钮和标签
    for widget in result_frame.winfo_children():
        widget.destroy()
    
    name_to_search = entry.get()
    creature, actions, bonus_actions, reactions, legendary_actions, mythic_actions = find_creature_by_name(bestiary_data, name_to_search)
    
    if creature:
        actions_bonuses = extract_attack_bonus(actions)
        actions_damages = extract_damage(actions)
        bonus_actions_bonuses = extract_attack_bonus(bonus_actions)
        bonus_actions_damages = extract_damage(bonus_actions)
        reactions_bonuses = extract_attack_bonus(reactions)
        reactions_damages = extract_damage(reactions)
        legendary_actions_bonuses = extract_attack_bonus(legendary_actions)
        legendary_actions_damages = extract_damage(legendary_actions)
        mythic_actions_bonuses = extract_attack_bonus(mythic_actions)
        mythic_actions_damages = extract_damage(mythic_actions)
        
        # 显示怪物的基本信息
        tk.Label(result_frame, text=f"名称: {creature['Name']}", justify=tk.LEFT).pack(anchor='w')
        tk.Label(result_frame, text=f"来源: {creature['Source']}", justify=tk.LEFT).pack(anchor='w')
        tk.Label(result_frame, text=f"页码: {creature['Page']}", justify=tk.LEFT).pack(anchor='w')
        tk.Label(result_frame, text=f"体型: {creature['Size']}", justify=tk.LEFT).pack(anchor='w')
        tk.Label(result_frame, text=f"生物类型: {creature['Type']}", justify=tk.LEFT).pack(anchor='w')
        tk.Label(result_frame, text=f"阵营: {creature['Alignment']}", justify=tk.LEFT).pack(anchor='w')
        tk.Label(result_frame, text=f"护甲等级: {creature['AC']}", justify=tk.LEFT).pack(anchor='w')
        tk.Label(result_frame, text=f"生命值: {creature['HP']}", justify=tk.LEFT).pack(anchor='w')
        tk.Label(result_frame, text=f"速度: {creature['Speed']}", justify=tk.LEFT).pack(anchor='w')
        
        # 显示 Actions
        formatted_actions = format_text(actions if actions else '无')
        tk.Label(result_frame, text=f"动作: {formatted_actions}", justify=tk.LEFT).pack(anchor='w')
        if actions_bonuses or actions_damages:
            for i in range(max(len(actions_bonuses), len(actions_damages))):
                frame = tk.Frame(result_frame)
                frame.pack(anchor='w')
                if i < len(actions_bonuses):
                    tk.Button(frame, text=f"攻击检定 (+{actions_bonuses[i]})", command=lambda b=actions_bonuses[i]: messagebox.showinfo("攻击检定结果", f"1d20 + {b} = {roll_attack_bonus(b)}")).pack(side='left')
                if i < len(actions_damages):
                    damage_value, damage_roll = actions_damages[i]
                    tk.Button(frame, text=f"伤害掷骰 ({damage_roll})", command=lambda d=damage_roll: messagebox.showinfo("伤害结果", f"{damage_roll} = {roll_damage(d)}")).pack(side='left')
                    tk.Label(frame, text=f"伤害期望值: {damage_value}").pack(side='left')
        
        # 显示 Bonus Actions
        formatted_bonus_actions = format_text(bonus_actions if bonus_actions else '无')
        tk.Label(result_frame, text=f"附赠动作: {formatted_bonus_actions}", justify=tk.LEFT).pack(anchor='w')
        if bonus_actions_bonuses or bonus_actions_damages:
            for i in range(max(len(bonus_actions_bonuses), len(bonus_actions_damages))):
                frame = tk.Frame(result_frame)
                frame.pack(anchor='w')
                if i < len(bonus_actions_bonuses):
                    tk.Button(frame, text=f"攻击检定 (+{bonus_actions_bonuses[i]})", command=lambda b=bonus_actions_bonuses[i]: messagebox.showinfo("攻击检定结果", f"1d20 + {b} = {roll_attack_bonus(b)}")).pack(side='left')
                if i < len(bonus_actions_damages):
                    damage_value, damage_roll = bonus_actions_damages[i]
                    tk.Button(frame, text=f"伤害掷骰 ({damage_roll})", command=lambda d=damage_roll: messagebox.showinfo("伤害结果", f"{damage_roll} = {roll_damage(d)}")).pack(side='left')
                    tk.Label(frame, text=f"伤害期望值: {damage_value}").pack(side='left')
        
        # 显示 Reactions
        formatted_reactions = format_text(reactions if reactions else '无')
        tk.Label(result_frame, text=f"反应: {formatted_reactions}", justify=tk.LEFT).pack(anchor='w')
        if reactions_bonuses or reactions_damages:
            for i in range(max(len(reactions_bonuses), len(reactions_damages))):
                frame = tk.Frame(result_frame)
                frame.pack(anchor='w')
                if i < len(reactions_bonuses):
                    tk.Button(frame, text=f"攻击检定 (+{reactions_bonuses[i]})", command=lambda b=reactions_bonuses[i]: messagebox.showinfo("攻击检定结果", f"1d20 + {b} = {roll_attack_bonus(b)}")).pack(side='left')
                if i < len(reactions_damages):
                    damage_value, damage_roll = reactions_damages[i]
                    tk.Button(frame, text=f"伤害掷骰 ({damage_roll})", command=lambda d=damage_roll: messagebox.showinfo("伤害结果", f"{damage_roll} = {roll_damage(d)}")).pack(side='left')
                    tk.Label(frame, text=f"伤害期望值: {damage_value}").pack(side='left')
        
        # 显示 Legendary Actions
        formatted_legendary_actions = format_text(legendary_actions if legendary_actions else '无')
        tk.Label(result_frame, text=f"传奇动作: {formatted_legendary_actions}", justify=tk.LEFT).pack(anchor='w')
        if legendary_actions_bonuses or legendary_actions_damages:
            for i in range(max(len(legendary_actions_bonuses), len(legendary_actions_damages))):
                frame = tk.Frame(result_frame)
                frame.pack(anchor='w')
                if i < len(legendary_actions_bonuses):
                    tk.Button(frame, text=f"攻击检定 (+{legendary_actions_bonuses[i]})", command=lambda b=legendary_actions_bonuses[i]: messagebox.showinfo("攻击检定结果", f"1d20 + {b} = {roll_attack_bonus(b)}")).pack(side='left')
                if i < len(legendary_actions_damages):
                    damage_value, damage_roll = legendary_actions_damages[i]
                    tk.Button(frame, text=f"伤害掷骰 ({damage_roll})", command=lambda d=damage_roll: messagebox.showinfo("伤害结果", f"{damage_roll} = {roll_damage(d)}")).pack(side='left')
                    tk.Label(frame, text=f"伤害期望值: {damage_value}").pack(side='left')
        
        # 显示 Mythic Actions
        formatted_mythic_actions = format_text(mythic_actions if mythic_actions else '无')
        tk.Label(result_frame, text=f"神话动作: {formatted_mythic_actions}", justify=tk.LEFT).pack(anchor='w')
        if mythic_actions_bonuses or mythic_actions_damages:
            for i in range(max(len(mythic_actions_bonuses), len(mythic_actions_damages))):
                frame = tk.Frame(result_frame)
                frame.pack(anchor='w')
                if i < len(mythic_actions_bonuses):
                    tk.Button(frame, text=f"攻击检定 (+{mythic_actions_bonuses[i]})", command=lambda b=mythic_actions_bonuses[i]: messagebox.showinfo("攻击检定结果", f"1d20 + {b} = {roll_attack_bonus(b)}")).pack(side='left')
                if i < len(mythic_actions_damages):
                    damage_value, damage_roll = mythic_actions_damages[i]
                    tk.Button(frame, text=f"伤害掷骰 ({damage_roll})", command=lambda d=damage_roll: messagebox.showinfo("伤害结果", f"{damage_roll} = {roll_damage(d)}")).pack(side='left')
                    tk.Label(frame, text=f"伤害期望值: {damage_value}").pack(side='left')
    else:
        tk.Label(result_frame, text="未找到对应的生物。", justify=tk.LEFT).pack(anchor='w')

def save_results():
    results = []
    for widget in result_frame.winfo_children():
        if isinstance(widget, tk.Label):
            results.append(widget.cget("text"))
    if results:
        with open("search_results.txt", "w", encoding="utf-8") as file:
            file.write("\n".join(results))
        messagebox.showinfo("保存成功", "搜索结果已保存到 search_results.txt")
    else:
        messagebox.showwarning("无结果", "没有搜索结果可保存")

# 获取当前脚本所在目录
current_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(current_dir, 'Bestiary.csv')

# 读取Bestiary.csv文件
bestiary_data = read_bestiary(file_path)

# 创建主窗口
root = tk.Tk()
root.title("仿FVTT怪物查询与攻击界面")
root.geometry("920x540")
root.resizable(False, False)

# 创建输入框和按钮
input_frame = tk.Frame(root)
input_frame.pack(pady=10)

tk.Label(input_frame, text="请输入要查找的生物名称:").pack(side='left', padx=5)
entry = tk.Entry(input_frame, width=50)
entry.pack(side='left', padx=5)
tk.Button(input_frame, text="查找", command=search_creature).pack(side='left', padx=5)
tk.Button(input_frame, text="保存结果", command=save_results).pack(side='left', padx=5)

# 创建可滚动的结果显示框架
canvas = tk.Canvas(root)
scrollbar_y = tk.Scrollbar(root, orient="vertical", command=canvas.yview, width=20)
scrollbar_x = tk.Scrollbar(root, orient="horizontal", command=canvas.xview, width=20)
scrollable_frame = tk.Frame(canvas)

scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(
        scrollregion=canvas.bbox("all")
    )
)

# 绑定鼠标滚轮事件
def on_mouse_wheel(event):
    canvas.yview_scroll(int(-1*(event.delta/120)), "units")

canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

scrollable_frame.bind_all("<MouseWheel>", on_mouse_wheel)

scrollbar_y.pack(side="right", fill="y")
scrollbar_x.pack(side="bottom", fill="x")
canvas.pack(side="left", fill="both", expand=True)

result_frame = scrollable_frame

# 运行主循环
root.mainloop()