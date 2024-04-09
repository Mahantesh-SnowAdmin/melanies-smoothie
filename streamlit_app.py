# Import python packages
import streamlit as st
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col, when_matched

# Write directly to the app
st.title(":cup_with_straw: Customise Your Smoothie! :cup_with_straw:")
st.write(
    """Choose the Fruits You Want in Custome Smoothie."""
)

name_on_order = st.text_input('Name on Smoothie')
st.write('The Name on your Smoothie will be:', name_on_order)

from snowflake.snowpark.functions import col

session = get_active_session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))
#st.dataframe(data=my_dataframe, use_container_width=True)

ingredients_list=st.multiselect(
    'Choose upto five ingredients',
    my_dataframe,
    max_selections=5
)

if ingredients_list:
    ingredients_string=''
    
    for friut_choosen in ingredients_list:
        ingredients_string += friut_choosen + ' '

    st.write(ingredients_string)

    my_insert_stmt = """ insert into smoothies.public.orders(ingredients,name_on_order)
            values ('""" + ingredients_string + """','""" +name_on_order + """')"""
    
    #st.write(my_insert_stmt)
    #st.stop()  
   
    time_to_insert = st.button('Submit Order')
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success("✅"'Your Smoothie is ordered,'+ name_on_order +'!')

session = get_active_session()
my_dataframe = session.table("smoothies.public.ORDERS").filter(col('ORDER_FILLED')==0).collect()

if my_dataframe:
    editable_df = st.data_editor(my_dataframe)
    submitted = st.button('Submit')
    if submitted:
        og_dataset = session.table("smoothies.public.orders")
        edited_dataset = session.create_dataframe(editable_df)
        st.success('Someone Clicked the Button',icon = "👍")
        try:
            og_dataset.merge(edited_dataset
                     , (og_dataset['order_uid'] == edited_dataset['order_uid'])
                     , [when_matched().update({'ORDER_FILLED': edited_dataset['ORDER_FILLED']})]
                    )
            st.success('Order(s) Updataed',icon = "👍")
        except:
            st.write('Someone went Wrong.')
    
else:
    st.success('There is no pending Orders right Now',icon = "👍")
    
