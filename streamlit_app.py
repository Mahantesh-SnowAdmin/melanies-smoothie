# Import python packages
import streamlit as st
from snowflake.snowpark.context import get_active_session

# Write directly to the app
st.title(":cup_with_straw: Customise Your Smoothie! :cup_with_straw:")
st.write(
    """Choose the Fruits You Want in Custome Smoothie."""
)

name_on_order = st.text_input('Name on Smoothie')
st.write('The Name on your Smoothie will be:', name_on_order)

from snowflake.snowpark.functions import col

cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'),col('search_on'))
#st.dataframe(data=my_dataframe, use_container_width=True)
#st.stop()

#Convert the snowpark datafrane to a pandas dataframe so we can use LOC function
pd_df = my_dataframe.to_pandas()
#st.dataframe = (pd_df)
#st.stop()

ingredients_list=st.multiselect(
    'Choose upto five ingredients',
    my_dataframe,
    max_selections=5
)

if ingredients_list:
    ingredients_string=''
    
    for friut_choosen in ingredients_list:
        ingredients_string += friut_choosen + ' '
        
        search_on=pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write('The search value for ', fruit_chosen,' is ', search_on, '.')

    st.write(ingredients_string)

    my_insert_stmt = """ insert into smoothies.public.orders(ingredients,name_on_order)
            values ('""" + ingredients_string + """','""" +name_on_order + """')"""
    
    #st.write(my_insert_stmt)
    #st.stop()  
   
    time_to_insert = st.button('Submit Order')
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success("✅"'Your Smoothie is ordered,'+ name_on_order +'!')

import requests

if ingredients_list:
    ingredients_string=''
    for friut_choosen in ingredients_list:
        ingredients_string += friut_choosen + ' '
        st.subheader(friut_choosen + 'Nutrition information')
        fruityvice_response = requests.get("https://fruityvice.com/api/fruit/watermelon" + friut_choosen)
        fv_df = st.dataframe(data=fruityvice_response.json() , use_container_width=True)
