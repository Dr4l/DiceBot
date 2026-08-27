# Secure Dice Discord Bot

[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![discord.py](https://img.shields.io/badge/discord.py-2.6.0-5865F2?style=for-the-badge&logo=discord&logoColor=white)](https://discordpy.readthedocs.io/)
[![CSPRNG](https://img.shields.io/badge/RNG-CSPRNG-2EA44F?style=for-the-badge&logo=letsencrypt&logoColor=white)](https://docs.python.org/3/library/secrets.html)
[![Tests](https://img.shields.io/badge/tests-unittest-25A162?style=for-the-badge&logo=python&logoColor=white)](https://docs.python.org/3/library/unittest.html)

This bot provides fair, cryptographically secure dice through Discord slash commands. `/roll` defaults to a d20, so it can be used without an argument.

## Dice

Common dice:

`d4`, `d6`, `d8`, `d10`, `d12`, `d20`, and `d100`

Examples:

- `/roll` rolls one d20
- `/roll d10` rolls one ten-sided die
- `/roll 2d6+3` rolls two d6 and adds 3
- `/roll 2d6+1d8-2` combines dice and subtracts 2
- `/dicehelp` displays the examples inside Discord

Each die uses Python's `secrets.randbelow`, which is backed by the operating system's cryptographic random source and returns every face with equal probability. The bot keeps no database or persistent state, which keeps its VPS footprint small.

## Run

The easiest option is to use the launcher for your operating system. On the first run it creates the virtual environment, installs dependencies, asks for the Discord bot token once, saves it to `.env`, and starts the bot. Later runs reuse the saved token.

Windows:

```text
run.bat
```

Linux/macOS:

```text
chmod +x run.sh
./run.sh
```

The manual setup is:

1. Use Python 3.11 or newer.
2. Create an environment and install dependencies:

   ```text
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Copy `.env.example` to `.env` and set `DISCORD_TOKEN`.
4. Invite the bot with the `bot` and `applications.commands` scopes.
5. Start it with `python bot.py`.

Run the tests with:

```text
python -m unittest discover -s tests
```

The bot accepts any positive number of sides, including unusual dice such as `d7` or `d30`. It limits a roll to 100 dice, 20 dice groups, and 1,000,000 sides per die to prevent accidental or abusive resource use.