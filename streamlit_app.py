# Import python packages
import streamlit as st
import requests
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write(
    """Choose the Fruits You Want in Custom Smoothie."""
)

name_on_order = st.text_input('Name on Smoothie')
st.write('The Name on your Smoothie will be:', name_on_order)

cnx = st.connection("snowflake")
session = cnx.session()

my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))

ingredients_list = st.multiselect(
    'Choose up to 5 ingredients',
    my_dataframe['FRUIT_NAME'].tolist(),  # Extracting only the fruit names
    max_selections=5
)

if ingredients_list: 
    ingredients_string = ''
    
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
        
        # Retrieve nutrition information for the selected fruit
        fruityvice_response = requests.get("https://fruityvice.com/api/fruit/" + fruit_chosen)
        nutrition_info = fruityvice_response.json()
        
        st.subheader(fruit_chosen + ' Nutrition Information')
        st.write(nutrition_info)
        
        my_insert_stmt = """insert into smoothies.public.orders(ingredients, name_on_order)
                            values ('{}', '{}')""".format(ingredients_string, name_on_order)
        
    time_to_insert = st.button('Submit Order')
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success("✅ Your Smoothie is ordered, " + name_on_order + "!")
        
        # Retrieve pending orders
        pending_orders = session.table("smoothies.public.orders").filter(col("ORDER_FILLED") == 0).collect()
        
        if pending_orders:
            st.subheader("Pending Orders")
            # Display pending orders in a data table for editing
            editable_orders = st.dataframe(pending_orders)
            
            # Submit button to update orders
            submitted = st.button('SUBMIT')
            
            if submitted:
                # Update orders in the Snowflake table
                try:
                    session.table("smoothies.public.orders").merge(
                        editable_orders,
                        (session.table("smoothies.public.orders")['order_uid'] == editable_orders['order_uid']),
                        [session.when_matched().update({'ORDER_FILLED': editable_orders['ORDER_FILLED']})]
                    )
                    st.success("✅ Order(s) Updated")
                except Exception as e:
                    st.error("❌ Something went wrong: " + str(e))
        else:
            st.success("✅ There are no pending orders right now.")
