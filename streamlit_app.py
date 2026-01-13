# Import python packages
import requests
import streamlit as st
from snowflake.snowpark.functions import col
# Write directly to the app
_ = st.title("🥤 Customize Your Smoothie!")

st.write(
  """Choose the fruits you want in your custom Smoothie!."""
)
name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be:", name_on_order)

# option = st.selectbox(
#     'How would you like to be contacted?',
#     ('Email','Home Phone','Mobile Phone'))

# st.write('You selected:',option)

# option = st.selectbox(
#     'What is your favorite fruit?',
#     ('Banana','Strawberries','Peaches'))
# st.write('Your favorite fruit is:',option)


cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))
# st.dataframe(data=my_dataframe, use_container_width=True)

my_dataframe = session.table("smoothies.public.fruit_options") \
    .select(col("FRUIT_NAME")) \
    .collect()

fruit_list = [row["FRUIT_NAME"] for row in my_dataframe]

ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_list,
    max_selections=5
)


if ingredients_list:
    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

        smoothiefroot_response = requests.get(
            "https://my.smoothiefroot.com/api/fruit/" + fruit_chosen.lower()
        )

        st.dataframe(
            data=smoothiefroot_response.json(),
            use_container_width=True
        )

    my_insert_stmt = """ insert into smoothies.public.orders(ingredients, name_on_order)
        values ('""" + ingredients_string + """','""" + name_on_order + """')"""

    st.write(my_insert_stmt)

time_to_insert = st.button("Submit Order")

if time_to_insert:
    session.sql(my_insert_stmt).collect()
    st.success("Your Smoothie is ordered, " + name_on_order + "!", icon="✅")


