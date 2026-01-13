# Import python packages
import requests
import streamlit as st
import pandas as pd
from snowflake.snowpark.functions import col

# Write directly to the app
st.title("🥤 Customize Your Smoothie!")
st.write("Choose the fruits you want in your custom Smoothie!")

name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be:", name_on_order)

# Connect to Snowflake
cnx = st.connection("snowflake")
session = cnx.session()

# Get dataframe with SEARCH_ON
my_dataframe = session.table("smoothies.public.fruit_options") \
    .select(col("FRUIT_NAME"), col("SEARCH_ON")) \
    .collect()

# Convert Snowpark DF → Pandas DF
pd_df = pd.DataFrame(my_dataframe)

# Multiselect list
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    pd_df["FRUIT_NAME"].tolist(),
    max_selections=5
)

# When user selects fruits
if ingredients_list:
    ingredients_string = ""

    for fruit_chosen in ingredients_list:

        ingredients_string += fruit_chosen + " "

        # 🔥 Get SEARCH_ON value using pandas
        search_on = pd_df.loc[
            pd_df["FRUIT_NAME"] == fruit_chosen,
            "SEARCH_ON"
        ].iloc[0]

        st.write("The search value for ", fruit_chosen, " is ", search_on)

        st.subheader(fruit_chosen + " Nutrition Information")

        response = requests.get(
            "https://my.smoothiefroot.com/api/fruit/" + search_on.lower()
        )

        if response.status_code == 200:
            st.dataframe(response.json(), use_container_width=True)
        else:
            st.write("Sorry, that fruit is not in our database.")

    # Insert statement
    my_insert_stmt = f"""
        insert into smoothies.public.orders(ingredients, name_on_order)
        values ('{ingredients_string}','{name_on_order}')
    """

    st.write(my_insert_stmt)

# Submit button
time_to_insert = st.button("Submit Order")

if time_to_insert:
    session.sql(my_insert_stmt).collect()
    st.success("Your Smoothie is ordered, " + name_on_order + "!", icon="✅")
