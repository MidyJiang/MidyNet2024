import subprocess

scripts = [
    # "01_get_myft.py", # 爬取数据，保存成csv
    # "02_data_processing.py", # 文本分词，保存成txt
    # "03_get_price.py", # 获取盘内数据，保存成csv
    "04_dataset.py", # 制作dataset，保存成csv
    "05_main.py",
    "06+07inmarket.py",
    "08_plot.py",
    "09_sharp_drawdown.py"
] # 主函数，训练并验证模型，保存在wandb平台

for script in scripts:
    try:
        print(f"正在运行 {script}...")
        subprocess.run(["python", script], check=True)
        print(f"{script} 运行成功")
    except subprocess.CalledProcessError as e:
        print(f"{script} 运行失败: {e}")
        break
