import os

# A RELATIVE path is looked up starting from the current working directory.
os.makedirs("logs", exist_ok=True)              # make a sub-folder (fine if it exists)
path = os.path.join("logs", "run_0428.txt")     # joins with the right separator for your OS
with open(path, "w", encoding="utf-8") as f:
    f.write("$GPGGA,,,,,,0,00,,,M,,M,,*66\n")

print(os.path.isabs(path))                 # False: it's relative to the working directory
print(os.path.isabs(os.path.abspath(path)))  # abspath() glues the working directory on front
print(os.path.dirname(path), os.path.basename(path))
print(os.path.exists(path))
print(os.path.exists("run_0428.txt"))      # False: the file is in logs/, not here

with open(path, encoding="utf-8") as f:
    print(f.read().strip())

# Opening a file that isn't there is an error, so check first (or see lesson 0.11).
missing = "logs/run_9999.txt"
if os.path.exists(missing):
    print("found it")
else:
    print(f"no such file: {missing}")
