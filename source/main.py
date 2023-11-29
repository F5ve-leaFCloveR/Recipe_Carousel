import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from utils import config_reader
from data import find_recipes_by_ingredients

logging.basicConfig(level=logging.INFO)

token = config_reader('Telegram', 'token')

bot = Bot(token=token)
dp = Dispatcher(bot)

main_keyboard = ReplyKeyboardMarkup(resize_keyboard=True, selective=True).add(
    KeyboardButton("Найти рецепт"),
    KeyboardButton("Избранное")
)

recipe_navigation_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton("Предыдущий рецепт", callback_data='prev_recipe'),
        InlineKeyboardButton("Назад", callback_data='back'),
        InlineKeyboardButton("Следующий рецепт", callback_data='next_recipe'),
    ],
])

current_recipe_index = 0
found_recipes = None


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await message.answer("Привет! Я бот 'Карусель рецептов'. Я могу помочь тебе найти рецепты на основе продуктов, которые у тебя есть. 🤖🍳\n\n"
                         "Что бы вы хотели сделать?", reply_markup=main_keyboard)


@dp.message_handler(lambda message: message.text == "Найти рецепт")
async def find_recipe(message: types.Message):
    await message.answer("Введите ингредиенты через запятую, например: яйца, мука, молоко")


@dp.message_handler(lambda message: message.text and not message.text.startswith('/'))
async def handle_ingredients(message: types.Message):
    await message.answer("Подбираем подходящие рецепты для вас, немного подождите)")

    global current_recipe_index, found_recipes
    ingredients = message.text.split(', ')
    found_recipes = find_recipes_by_ingredients(ingredients)

    if found_recipes.empty:
        await message.answer("Нет рецептов, соответствующих вашим ингредиентам.")
    else:
        current_recipe_index = 0
        await display_recipe(found_recipes.iloc[current_recipe_index], message.from_user.id)


async def display_recipe(recipe, user_id):
    
    recipe_name = recipe['recipe_name']
    ingredients = eval(recipe['ingredients'])
    formatted_ingredients = "\n".join(["- " + ingredient for ingredient in ingredients])
    source_url = recipe['source_url']
    recipe_text = f"{recipe_name}\n\nИнгредиенты:\n{formatted_ingredients}\n\nСсылка: {source_url}"

    await bot.send_message(user_id, recipe_text, reply_markup=recipe_navigation_keyboard)


@dp.callback_query_handler(lambda query: query.data in {'next_recipe', 'prev_recipe', 'back'})
async def handle_recipe_navigation(query: types.CallbackQuery):
    global current_recipe_index, found_recipes

    if query.data == 'next_recipe':
        current_recipe_index += 1
    elif query.data == 'prev_recipe':
        current_recipe_index -= 1

    if current_recipe_index < 0:
        current_recipe_index = 0
    elif current_recipe_index >= len(found_recipes):
        current_recipe_index = len(found_recipes) - 1

    if query.data in {'next_recipe', 'prev_recipe'}:
        await query.message.delete()
        await display_recipe(found_recipes.iloc[current_recipe_index], query.from_user.id)
    elif query.data == 'back':
        await query.message.answer("Что бы вы хотели сделать?", reply_markup=main_keyboard)
        await query.message.delete()


async def main():
    await dp.start_polling()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
