# Import python packages
import streamlit as st
import requests 
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col


# Write directly to the app
st.title(":cup_with_straw: Customise Your Smoothie! :cup_with_straw:")
st.write(
    """Choose the Fruits You Want in Custome Smoothie."""
)

name_on_order = st.text_input('Name on Smoothie')
st.write('The Name on your Smoothie will be:', name_on_order)

cnx = st.connection("snowflake")
session = cnx.session()

    
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))
#st.dataframe(data=my_dataframe, use_container_width=True)
#st.Stop()

#Convert the Snowpark dataframe to a Pandas Dataframe so we can use the Loc function
pd_df = my_dataframe.to_pandas()
#st.dataframe(pd_df)
#st.stop()

ingredients_list=st.multiselect(
    'Choose upto 5 ingredients',
    my_dataframe,
    max_selections=5
)

if ingredients_list: 
    ingredients_string=''
    
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
        
        SEARCH_ON=pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        #st.write('The search value for ', fruit_chosen,' is ', SEARCH_ON, '.')
        
        st.subheader(fruit_chosen + 'Nutrition Information')
        fruityvice_response = requests.get("https://fruityvice.com/api/fruit/" + SEARCH_ON)
        fd_df = st.dataframe(data=fruityvice_response.json(), use_container_width=True)
        st.write(ingredients_string)
        my_insert_stmt = """ insert into smoothies.public.orders(ingredients,name_on_order)
        values ('""" + ingredients_string + """','""" +name_on_order + """')"""
        
    #st.write(my_insert_stmt)
    #st.stop()  
   
    time_to_insert = st.button('Submit Order')
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        my_dataframe = session.table("smoothies.public.orders").filter(col("ORDER_FILLED")==0).collect()
        if my_dataframe:
            editable_df=st.data_editor(my_dataframe)
            submitted = st.button('SUBMIT')
            if submitted:
                og_dataset = session.table("smoothies.public.orders")
                edited_dataset = session.create_dataframe(editable_df)
                try:  
                    og_dataset.merge(edited_dataset
                     , (og_dataset['order_uid'] == edited_dataset['order_uid'])
                     , [when_matched().update({'ORDER_FILLED': edited_dataset['ORDER_FILLED']})]
                    )
                    st.success("Order(s) Updated",icon = "👍")
                except:
                    st.write('Something went Wrong.')
        else:
            st.success('There are no PENDING ORDERS Right Now',icon = "👍")
    st.success("✅"'Your Smoothie is ordered,'+ name_on_order +'!')

