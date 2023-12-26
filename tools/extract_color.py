import re, json

distro_color = {}


def color(colornum):  # see neofetch color()
    reset = "\e[0m"
    ascii_bold = "\e[1m"
    if colornum == "fg" or colornum == "7":
        return f"\e[37m{reset}"
    if colornum == "#":
        pass  # TODO
    if int(colornum) >= 0 and int(colornum) < 7:
        return f"{reset}\e[3{colornum}m"
    return f"\e38;5;{colornum}m"


with open("neofetch") as f:
    s = f.read()
l = iter(s.split("\n"))
for i in l:
    p = re.search(r'"\D+"\*\)', i)
    if p is None:
        continue
    distros = re.sub(r"\"|\)|\*", "", i.strip(" ")).split("|")
    c = next(l).strip(" ")
    if "set_colors" not in c:
        continue
    colors = c.split(" ")[1:]
    for dist in distros:
        distro_color[dist.strip(" ").rstrip(" ")] = colors
with open("distcolor.json", "w") as f:
    json.dump(distro_color, f)
