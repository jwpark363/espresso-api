import streamlit as st

pages = [
    st.Page(
        page="pages/components.py",
        title="Basic",
        icon="😊",
        default=True,
    ),
    st.Page(
        page="pages/chat_bot.py",
        title="Best",
        icon="👍",
        default=False,
    )
]

nav = st.navigation(pages)
nav.run()