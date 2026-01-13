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
    .select(col("FRUIT_NAME"), col("SEARCH_ON")) \
    .collect()

fruit_dict = {row["FRUIT_NAME"]: row["SEARCH_ON"] for row in my_dataframe}

fruit_list = list(fruit_dict.keys())

ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_list,
    max_selections=5
)


if ingredients_list:
    ingredients_string = ''

    for fruit_chosen in ingredients_list:
    ingredients_string += fruit_chosen + ' '

    st.subheader(fruit_chosen + " Nutrition Information")

    search_value = fruit_dict[fruit_chosen]   # 🔥 THIS LINE WAS MISSING

    smoothiefroot_response = requests.get(
        "https://my.smoothiefroot.com/api/fruit/" + search_value.lower()
    )

    if smoothiefroot_response.status_code == 200:
        st.dataframe(
            data=smoothiefroot_response.json(),
            use_container_width=True
        )
    else:
        st.write("Sorry, that fruit is not in our database.")

    my_insert_stmt = """ insert into smoothies.public.orders(ingredients, name_on_order)
        values ('""" + ingredients_string + """','""" + name_on_order + """')"""

    st.write(my_insert_stmt)

time_to_insert = st.button("Submit Order")

if time_to_insert:
    session.sql(my_insert_stmt).collect()
    st.success("Your Smoothie is ordered, " + name_on_order + "!", icon="✅")


