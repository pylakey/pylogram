<p align="center">
    <a href="https://github.com/pylakey/pylogram">
        <img src="https://docs.pyrogram.org/_static/pyrogram.png" alt="Pylogram" width="128">
    </a>
</p>

> [!IMPORTANT]
> I want to say thank you to [Pyrogram](https://github.com/pyrogram/pyrogram) and its contributors for the inspiration
> and
> base code. This project is a fork of Pylogram.
> This repository will contain many of incompatible changes with original Pylogram and not positioned as drop-in
> replacement.
> I will not answer any question about this repository and it's code. Issues are also disabled.

# Pylogram

> Elegant, modern and asynchronous Telegram MTProto API framework in Python for users and bots

``` python
from pylogram import Client, filters

app = Client("my_account")


@app.on_message(filters.private)
async def hello(client, message):
    await message.reply("Hello from Pylogram!")


app.run()
```

**Pylogram** is a modern, elegant and asynchronous MTProto API
framework. It enables you to easily interact with the main Telegram API through a user account (custom client) or a bot
identity (bot API alternative) using Python.

### Key Features

- **Ready**: Install Pylogram with pip and start building your applications right away.
- **Easy**: Makes the Telegram API simple and intuitive, while still allowing advanced usages.
- **Elegant**: Low-level details are abstracted and re-presented in a more convenient way.
- **Fast**: Boosted up by [TgCrypto](https://github.com/pylogram/tgcrypto), a high-performance cryptography library
  written in C.
- **Type-hinted**: Types and methods are all type-hinted, enabling excellent editor support.
- **Async**: Fully asynchronous (also usable synchronously if wanted, for convenience).
- **Powerful**: Full access to Telegram's API to execute any official client action and more.

### Installing

``` bash
pip3 install pylogram
```