import pandas as pd
import matplotlib.pyplot as plt
import pathlib
import subprocess

figure_size = (12, 8)
fps = 10

__loc__ = pathlib.Path().absolute()
respath = __loc__ / "resources"
pro_path = respath / ".progress.csv"

prodf = pd.read_csv(pro_path)
prodf["Date"] = pd.to_datetime(prodf["Date"], format="%d/%m/%Y")
prodf.sort_values("Date", inplace=True)

fig, ax = plt.subplots(1)
color = "dodgerblue"
ax.set_ylabel("Words", color=color)
ax.tick_params(axis="y", labelcolor=color)
fig.autofmt_xdate()
fig.set_size_inches(figure_size[0], figure_size[1])
plt.plot_date(prodf["Date"], prodf["Words"], color=color)
ax2 = ax.twinx()
color = "darkviolet"
ax2.set_ylabel("Kanji", color=color)
ax2.plot_date(prodf["Date"], prodf["Kanji"], color=color)
ax2.tick_params(axis="y", labelcolor=color)
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
    "crop=2496:3430:0:0, format=yuv420p, scale=iw/2:ih/2",
    "-c:v",
    "libvpx-vp9",
    "-crf",
    "22",
    "KanjiProgress.webm",
]

subprocess.run(command)

if pathlib.Path("in.ffconcat").is_file():
    pathlib.Path("in.ffconcat").unlink()
