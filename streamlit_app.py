import streamlit as st
import requests
from snowflake.snowpark.context import get_active_session

st.title(":cup_with_straw: Customise Your Smoothie! :cup_with_straw:")
st.write(
    """Choose the Fruits You Want in Custom Smoothie."""
)

name_on_order = st.text_input('Name on Smoothie')
st.write('The Name on your Smoothie will be:', name_on_order)

from snowflake.snowpark.functions import col

cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))

pd_df = my_dataframe.to_pandas()

ingredients_list = st.multiselect(
    'Choose up to five ingredients',
    my_dataframe,
    max_selections=5)

if ingredients_list:
    ingredients_string = ''
    
    for fruit_choosen in ingredients_list:
        ingredients_string += fruit_choosen + ' '
        
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_choosen, 'SEARCH_ON'].iloc[0]
        
        try:
            fruityvice_response = requests.get("https://fruityvice.com/api/fruit/" + search_on)
            if fruityvice_response.status_code == 200:
                fv_data = fruityvice_response.json()
                if fv_data:
                    st.subheader(fruit_choosen + ' Nutrition Information')
                    fv_df = st.dataframe(data=fv_data, use_container_width=True)
                else:
                    st.warning("No data found for " + fruit_choosen)
            else:
                st.error("Failed to fetch data for " + fruit_choosen + ". Status code: " + str(fruityvice_response.status_code))
        except Exception as e:
            st.error("An error occurred while fetching data for " + fruit_choosen + ": " + str(e))

    st.write(ingredients_string)

    my_insert_stmt = """INSERT INTO smoothies.public.orders(ingredients, name_on_order)
                       VALUES ('{}', '{}')""".format(ingredients_string, name_on_order)
   
    time_to_insert = st.button('Submit Order')
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success("✅ Your Smoothie is ordered, " + name_on_order + "!")
        session.sql(my_insert_stmt).collect()
        st.success("✅" 'Your Smoothie is ordered,' + name_on_order + '!')
