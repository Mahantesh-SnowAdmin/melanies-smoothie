import streamlit as st
import requests
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col, when_matched

st.title(":cup_with_straw: Customise Your Smoothie! :cup_with_straw:")
st.write(
    """Choose the Fruits You Want in Custom Smoothie."""
)

name_on_order = st.text_input('Name on Smoothie')
st.write('The Name on your Smoothie will be:', name_on_order)

from snowflake.snowpark.functions import col

cnx = st.connection("snowflake")
st.write("Snowflake Connection:", cnx)

session = cnx.session()
st.write("Snowpark Session:", session)

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
                       VALUES (%s, %s)"""
   
    time_to_insert = st.button('Submit Order')
    if time_to_insert:
        try:
            session.execute(my_insert_stmt, (ingredients_string, name_on_order))
            st.success("✅ Your Smoothie is ordered, " + name_on_order + "!")
        except Exception as e:
            st.error("Failed to submit the order: " + str(e))

# Write directly to the app
st.title(":cup_with_straw: Pending SMOOTHIE Orders :cup_with_straw:")
st.write(
    """Orders that need to be filled."""
)

try:
    my_dataframe = session.table("smoothies.public.ORDERS").filter(col('ORDER_FILLED')==0).collect()
    st.write("Pending Orders DataFrame:", my_dataframe)

    if my_dataframe:
        editable_df = st.data_editor(my_dataframe)
        submitted = st.button('Submit')
        if submitted:
            og_dataset = session.table("smoothies.public.orders")
            edited_dataset = session.create_dataframe(editable_df)
            og_dataset.merge(edited_dataset,
                             (og_dataset['order_uid'] == edited_dataset['order_uid']),
                             [when_matched().update({'ORDER_FILLED': edited_dataset['ORDER_FILLED']})])
            st.success('Order(s) Updated', icon="👍")
    
    else:
        st.success('There are no pending Orders right now', icon="👍")

except Exception as e:
    st.error("An error occurred: " + str(e))
