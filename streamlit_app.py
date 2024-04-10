import streamlit as st
from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col, when_matched

st.title(":cup_with_straw: Pending SMOOTHIE Orders :cup_with_straw:")
st.write(
    """Orders that need to be filled."""
)

session = get_active_session()

cnx = st.connection("snowflake", session=session)
st.write("Snowflake Connection:", cnx)

session = cnx.session()
st.write("Snowpark Session:", session)

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
