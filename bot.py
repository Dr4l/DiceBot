import os
import re
import secrets
from dataclasses import dataclass

import discord
from discord import app_commands
from dotenv import load_dotenv


MAX_DICE = 100
MAX_SIDES = 1_000_000
MAX_TERMS = 20
DICE_TERM = re.compile(r"(?P<count>\d*)d(?P<sides>\d+)", re.IGNORECASE)
ROLL_EXPRESSION = re.compile(r"^(?P<terms>[0-9dD+\-]+)$")


@dataclass(frozen=True)
class DiceTerm:
    count: int
    sides: int


@dataclass(frozen=True)
class RollResult:
    expression: str
    rolls: tuple[int, ...]
    modifier: int

    @property
    def total(self) -> int:
        return sum(self.rolls) + self.modifier


def parse_expression(expression: str) -> tuple[list[DiceTerm], int]:
    """Parse expressions such as d20, 2d6+1d8-2."""
    compact = expression.replace(" ", "")
    if not ROLL_EXPRESSION.fullmatch(compact):
        raise ValueError("Use dice notation such as `d20`, `2d6`, or `2d6+1d8-2`.")

    terms: list[DiceTerm] = []
    modifier = 0
    position = 0
    sign = 1
    for match in re.finditer(r"[+-]?\d*d\d+|[+-]\d+", compact, re.IGNORECASE):
        if match.start() != position:
            raise ValueError("That expression has an invalid term.")
        token = match.group()
        position = match.end()
        if token[0] in "+-":
            sign = -1 if token[0] == "-" else 1
            token = token[1:]
        dice_match = DICE_TERM.fullmatch(token)
        if dice_match:
            if sign < 0:
                raise ValueError("Negative dice are not supported; subtract a numeric modifier instead.")
            count = int(dice_match.group("count") or 1)
            sides = int(dice_match.group("sides"))
            if count < 1 or sides < 1:
                raise ValueError("Dice count and sides must be positive.")
            terms.append(DiceTerm(count, sides))
        else:
            modifier += sign * int(token)
        sign = 1

    if position != len(compact) or not terms:
        raise ValueError("Include at least one die, for example `d20`.")
    if len(terms) > MAX_TERMS:
        raise ValueError(f"Use at most {MAX_TERMS} dice groups per roll.")
    if any(term.sides > MAX_SIDES for term in terms):
        raise ValueError(f"Each die can have at most {MAX_SIDES:,} sides.")
    if sum(term.count for term in terms) > MAX_DICE:
        raise ValueError(f"Use at most {MAX_DICE} dice per roll.")
    return terms, modifier


def roll_expression(expression: str) -> RollResult:
    terms, modifier = parse_expression(expression)
    rolls = tuple(
        secrets.randbelow(term.sides) + 1
        for term in terms
        for _ in range(term.count)
    )
    return RollResult(expression.replace(" ", ""), rolls, modifier)


def format_result(result: RollResult) -> str:
    detail = ", ".join(str(value) for value in result.rolls)
    modifier = f" {result.modifier:+d}" if result.modifier else ""
    return f"**{result.expression}** -> [{detail}]{modifier} = **{result.total}**"


class DiceBot(discord.Client):
    def __init__(self) -> None:
        intents = discord.Intents.none()
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self) -> None:
        await self.tree.sync()


load_dotenv()
bot = DiceBot()


@bot.tree.command(name="roll", description="Roll fair cryptographically secure dice.")
@app_commands.describe(expression="Examples: d6, d10, d20, 2d6+3, or d100")
async def roll(interaction: discord.Interaction, expression: str = "d20") -> None:
    try:
        result = roll_expression(expression)
    except ValueError as error:
        await interaction.response.send_message(str(error), ephemeral=True)
        return
    await interaction.response.send_message(format_result(result))


@bot.tree.command(name="dicehelp", description="Show common dice and roll examples.")
async def dicehelp(interaction: discord.Interaction) -> None:
    await interaction.response.send_message(
        "**Common dice**\n"
        "`d4`  `d6`  `d8`  `d10`  `d12`  `d20`  `d100`\n\n"
        "**Examples**\n"
        "`/roll` rolls a d20\n"
        "`/roll d10` rolls a ten-sided die\n"
        "`/roll 2d6+3` rolls two d6 and adds 3\n"
        "`/roll d20+5` rolls a d20 and adds 5\n\n"
        "All results use a cryptographically secure random generator."
    )

def main() -> None:
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        raise RuntimeError("DISCORD_TOKEN is not set. Copy .env.example to .env and fill it in.")
    try:
        bot.run(token)
    except discord.LoginFailure as error:
        raise RuntimeError(
            "Discord rejected the token. Use the Bot Token from Developer Portal > Bot, "
            "not the Application ID or Server ID. Update .env and run the launcher again."
        ) from error


if __name__ == "__main__":
    main()