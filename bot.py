#!/usr/bin/env python

"""
Bot for playing tic tac toe game with multiple CallbackQueryHandlers.
"""
from copy import deepcopy
import logging
import random

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
)
import os


# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

# get token using BotFather
TOKEN = os.getenv("TG_TOKEN")

CONTINUE_GAME, FINISH_GAME = range(2)

FREE_SPACE = "."
CROSS = "X"
ZERO = "O"


DEFAULT_STATE = [[FREE_SPACE for _ in range(3)] for _ in range(3)]


def get_default_state():
    """Helper function to get default state of the game"""
    return deepcopy(DEFAULT_STATE)


def generate_keyboard(state: list[list[str]]) -> list[list[InlineKeyboardButton]]:
    """Generate tic tac toe keyboard 3x3 (telegram buttons)"""
    return [
        [InlineKeyboardButton(state[r][c], callback_data=f"{r}{c}") for r in range(3)]
        for c in range(3)
    ]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Send message on `/start`."""
    context.user_data["keyboard_state"] = get_default_state()
    keyboard = generate_keyboard(context.user_data["keyboard_state"])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "X (your) turn! Please, put X to the free place", reply_markup=reply_markup
    )
    return CONTINUE_GAME


async def update_markup(
    update: Update, context: ContextTypes.DEFAULT_TYPE, new_text: str
) -> None:
    keyboard = generate_keyboard(context.user_data["keyboard_state"])
    await update.callback_query.edit_message_text(
        text=new_text,
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


async def game(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Main processing of the game"""
    state = context.user_data["keyboard_state"]

    row, column = map(int, update.callback_query.data)
    if state[row][column] is not FREE_SPACE:
        return CONTINUE_GAME
    state[row][column] = CROSS
    if won(state):
        await update_markup(
            update, context, "You win! Please, enter /start to start a new game"
        )
        return FINISH_GAME

    possible_zero_positions = [
        (c, r) for r in range(3) for c in range(3) if state[c][r] is FREE_SPACE
    ]
    if not possible_zero_positions:
        await update_markup(
            update, context, "Tie! Please, enter /start to start a new game"
        )
        return FINISH_GAME

    row, column = random.choice(possible_zero_positions)
    state[row][column] = ZERO
    if won(state):
        await update_markup(
            update, context, "You lose! Please, enter /start to start a new game"
        )
        return FINISH_GAME

    await update_markup(
        update, context, "X (your) turn! Please, put X to the free place"
    )
    return CONTINUE_GAME


def won(state: list[list[str]]) -> bool:
    """Check if crosses or zeros have won the game"""
    for row in range(3):
        if state[row][0] != FREE_SPACE and all(
            state[row][col] == state[row][2] for col in range(2)
        ):
            return True
    for col in range(3):
        if state[0][col] != FREE_SPACE and all(
            state[row][col] == state[2][col] for row in range(2)
        ):
            return True
    if state[1][1] != FREE_SPACE and (
        len(set([state[i][i] for i in range(3)])) == 1
        or len(set([state[i][2 - i] for i in range(3)])) == 1
    ):
        return True
    return False


async def end(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Returns `ConversationHandler.END`, which tells the
    ConversationHandler that the conversation is over.
    """
    # reset state to default so you can play again with /start
    context.user_data["keyboard_state"] = get_default_state()
    return ConversationHandler.END


def main() -> None:
    """Run the bot"""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TOKEN).build()

    # Setup conversation handler with the states CONTINUE_GAME and FINISH_GAME
    # Use the pattern parameter to pass CallbackQueries with specific
    # data pattern to the corresponding handlers.
    # ^ means "start of line/string"
    # $ means "end of line/string"
    # So ^ABC$ will only allow 'ABC'
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CONTINUE_GAME: [
                CallbackQueryHandler(game, pattern="^" + f"{r}{c}" + "$")
                for r in range(3)
                for c in range(3)
            ],
            FINISH_GAME: [
                CallbackQueryHandler(end, pattern="^" + f"{r}{c}" + "$")
                for r in range(3)
                for c in range(3)
            ],
        },
        fallbacks=[CommandHandler("start", start)],
    )

    # Add ConversationHandler to application that will be used for handling updates
    application.add_handler(conv_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
