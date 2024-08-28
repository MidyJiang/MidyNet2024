import subprocess

scripts = [
    # "01_get_myft.py",
    # "02_data_processing.py", 
    # "03_get_price.py", 
    "04_dataset.py",
    "05_main.py",
    "06+07inmarket.py",
    "08_plot.py",
    "09_sharp_drawdown.py"
] # run this as the integrated main function, train the model ,teset it and pot the figures. trace the training on W&B platform.

for script in scripts:
    try:
        print(f"Running {script}...")
        subprocess.run(["python", script], check=True)
        print(f"{script} succeeded")
    except subprocess.CalledProcessError as e:
        print(f"{script} Failed at: {e}")
        break
