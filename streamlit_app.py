import requests
import streamlit as st
import pandas as pd
from snowflake.snowpark.functions import col
from urllib.parse import quote

st.title("🥤 Customize Your Smoothie!")
st.write("Choose the fruits you want in your custom Smoothie!")

name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be:", name_on_order)

# NEW: filled checkbox
order_filled = st.checkbox("Mark order as filled")

# Connect to Snowflake
cnx = st.connection("snowflake")
session = cnx.session()
session.sql("use warehouse ACME_WH").collect()

# Get dataframe with SEARCH_ON
my_dataframe = session.table("smoothies.public.fruit_options") \
    .select(col("FRUIT_NAME"), col("SEARCH_ON")) \
    .collect()

# Convert Snowpark → Pandas
pd_df = pd.DataFrame(my_dataframe)

# Multiselect
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    pd_df["FRUIT_NAME"].tolist(),
    max_selections=5
)

my_insert_stmt = None

if ingredients_list:

    ingredients_string = ""

    for fruit_chosen in ingredients_list:

        ingredients_string += fruit_chosen + " "

        search_on = pd_df.loc[
            pd_df["FRUIT_NAME"] == fruit_chosen,
            "SEARCH_ON"
        ].iloc[0]

        st.write("The search value for ", fruit_chosen, " is ", search_on)

        st.subheader(fruit_chosen + " Nutrition Information")

        encoded_search = quote(search_on.lower())

        response = requests.get(
            "https://my.smoothiefroot.com/api/fruit/" + encoded_search
        )

        if response.status_code == 200:
            st.dataframe(response.json(), use_container_width=True)
        else:
            st.write("Sorry, that fruit is not in our database.")

    # Clean spaces
    ingredients_string = ingredients_string.strip()

    # Escape quotes
    safe_ingredients = ingredients_string.replace("'", "''")
    safe_name = name_on_order.replace("'", "''")

    filled_value = str(order_filled).upper()

    my_insert_stmt = f"""
        insert into smoothies.public.orders(ingredients, name_on_order, order_filled)
        values ('{safe_ingredients}','{safe_name}', {filled_value})
    """

    st.write(my_insert_stmt)

# Submit button
time_to_insert = st.button("Submit Order")

if time_to_insert and my_insert_stmt:
    try:
        session.sql(my_insert_stmt).collect()
        st.success("Your Smoothie is ordered, " + name_on_order + "!", icon="✅")
    except Exception as e:
        st.error("SNOWFLAKE ERROR:")
        st.error(str(e))
