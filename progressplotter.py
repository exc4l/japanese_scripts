import pandas as pd
import matplotlib.pyplot as plt
import pathlib
import subprocess
import numpy as np
figure_size = (12, 8)
fps = 15

__loc__ = pathlib.Path().absolute()
respath = __loc__ / "resources"
pro_path = respath / ".progress.csv"

prodf = pd.read_csv(pro_path)
prodf["Date"] = pd.to_datetime(prodf["Date"], format="%d/%m/%Y")
prodf.sort_values("Date", inplace=True)
pdf = prodf.groupby(["Date"])
ppdf = pdf.agg(Word_Max=("Words", np.max), Kanji_Max=("Kanji", np.max))
fig, ax = plt.subplots(1)
color = "dodgerblue"
ax.set_ylabel("Words", color=color)
ax.tick_params(axis="y", labelcolor=color)
# ax.set_ylim(4000,10000)
fig.autofmt_xdate()
fig.set_size_inches(figure_size[0], figure_size[1])
plt.plot_date(ppdf.index, ppdf["Word_Max"], color=color)
ax2 = ax.twinx()
color = "darkviolet"
ax2.set_ylabel("Kanji", color=color)
ax2.plot_date(ppdf.index, ppdf["Kanji_Max"], color=color, marker="v")
ax2.tick_params(axis="y", labelcolor=color)
# ax2.set_ylim(1400, 2500)
fig.tight_layout()
plt.savefig(
    "Progress.png", dpi=150, facecolor="white", bbox_inches="tight", pad_inches=0.5
)


imglist = [f.name for f in respath.glob("*.png")]

if pathlib.Path("in.ffconcat").is_file():
    pathlib.Path("in.ffconcat").unlink()

with open("in.ffconcat", "w", encoding="utf-8") as wr:
    wr.write("ffconcat version 1.0\n")
    for img in imglist:
        wr.write(f"file {respath.name}/{img}\n")
        wr.write(f"duration {1 / fps:.3f}\n")

command = [
    "ffmpeg.exe",
    "-y",
    "-i",
    "in.ffconcat",
    "-vf",
    "crop=2496:3180:0:0, format=yuv420p, scale=iw/2:ih/2",
    "-c:v",
    "libvpx-vp9",
    "-crf",
    "31",
    "-b:v",
    "0",
    "-r",
    f"{fps}",
    "KanjiProgress.webm",
]

subprocess.run(command)

if pathlib.Path("in.ffconcat").is_file():
    pathlib.Path("in.ffconcat").unlink()
