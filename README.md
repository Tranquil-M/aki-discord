# Akinator Discord Command

## Table of Contents

| Category | Description |
|----------|------------|
| [What does it do?](#looks) | What is this? |
| [Installation](#install) | Directions to clone and use this repository |
| [Features](#feat) | Included features |
| [Used Packages](#pkgs) | All packages used |

<a name="looks"></a>
## What is this?
I've been looking for good akinator commands for a discord bot, but couldn't find one. This is a full, functional akinator game built with [discord.py](https://pypi.org/project/discord.py/) that serves as a simple cog for even simpler implementation in your pre-existing discord bot.

<a name="install"></a>
## Installation

1. Add this repository as a submodule into your desired location:
    ```bash
    git submodule add https://github.com/Tranquil-M/aki-discord.git cogs/aki-discord
    ```
2. Load this cog in your main file:
    ```python  
    await bot.load_extension("cogs/aki-discord/akinatoror.py")
    ```

> [!IMPORTANT]
> Everybody's load function will likely work in different ways, but this is a simple way to load this cog. **This is NOT drop-in code.**

<a name="feat"></a>
## Features

This project is built using [akipy](https://github.com/advnpzn/akipy); as akipy adds more features I will update this repository to include them.

<a name="pkgs">

## Packages

* [`discord.py`](https://discordpy.readthedocs.io/en/stable/)
* [`akipy`](https://github.com/advnpzn/akipy)

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/I2I61Z3QJH)
