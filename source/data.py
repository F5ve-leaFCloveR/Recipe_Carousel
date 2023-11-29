import pandas as pd
import re
import mysql.connector
from utils import config_reader

"""
view_data: This function connects to a MySQL database and retrieves data from a table called 'recipes'.

find_recipes_by_ingredients: This function takes a list of ingredients as input and returns a DataFrame of recipes that match those ingredients.

"""

def view_data():
    db_config = {
        'host': config_reader('MySQL', 'host'),
        'user': config_reader('MySQL', 'user'),
        'password': config_reader('MySQL', 'password'),
        'database': config_reader('MySQL', 'database')
    }

    with mysql.connector.connect(**db_config) as connection, connection.cursor() as cursor:
        cursor.execute("SELECT * FROM recipes_rus")
        result = cursor.fetchall()

        df = pd.DataFrame(result, columns=[i[0] for i in cursor.description])

    return df

def find_recipes_by_ingredients(ingredients):
    df = view_data()

    ingredients_pattern = re.compile('|'.join(map(re.escape, map(str.lower, ingredients))))

    df['ingredient_counts'] = df['ingredients'].apply(lambda x: len(set(ingredients_pattern.findall(x.lower()))))
    df = df[df['ingredient_counts'] > 0]

    sorted_recipes = df.sort_values(by=['ingredient_counts', 'total_ingredients'], ascending=[False, True])

    return sorted_recipes
