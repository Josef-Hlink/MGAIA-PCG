# Procedural Content Generation in Minecraft

_J.D. Hamelink, 2023_

This repository contains all the source code for the submission of the first project for the course "Modern Game AI" (_Mike Preuss_) in the Master Artificial Intelligence at Leiden University.

The task was to use the [GDPC](https://pypi.org/project/gdpc/) Python package to generate a structure in Minecraft that is somewhat adaptable to the environment.
To be completely honest, my design is not necessarily the most adaptable, as I emphasized the design of the structure over the adaptability.
What I did implement however, is a very short little puzzle that the player has to solve in survival mode.

## Instructions

To run the code, you will need to have the following software installed:

- Minecraft 1.19.2 (Java Edition)
- Forge for Minecraft 1.19.2 [download](https://files.minecraftforge.net/net/minecraftforge/forge/index_1.19.2.html)
- The GDMC HTTP interface mod [download](https://github.com/Niels-NTG/gdmc_
http_interface/releases/tag/v1.0.0)
- The GPDC Python package [download](https://github.com/avdstaaij/gdpc)
- Python 3.10.9 ^
- NumPy 1.24.2 ^

When you do, open a Minecraft world with the mods enabled.
Run the following command in the chat:

```bash
\setbuildarea ~ ~ ~ ~100 ~100 ~100 (or whatever build area you want)
```

Finally, clone this repo and do the following commands:

```bash
pip install -r requirements.txt
cd src/app/
python main.py
```

Depending on your hardware, this may take a couple of minutes.
When it is done, you should see a structure in the build area.

## Minecraft minigame

The structure contains a little minigame.
You will notice that only one of the four towers has a stairway to get into the structure.
The other towers are only reachable via the bridges that connect them.
You might also notice that the castle in the middle is not accessible from the ground.
The first goal is to figure out how to get into this castle (without completely destroying the structure, of course).
On your way, please enjoy the different interiors of the towers.
