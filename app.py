import streamlit as st
import awesome_streamlit as ast

import src.home
import src.research
import src.prediction


ast.core.services.other.set_logging_format()

# List of pages available for display
PAGES = {
    # "Home": src.home,
    "Research": src.research,
    "Prediction": src.prediction,
}


def main():
    """Core of the app - switches between 'tabs' thanks to the sidebar"""
    st.sidebar.title("Navigation")
    selection = st.sidebar.radio("Visit", list(PAGES.keys()))

    page = PAGES[selection]

    with st.spinner(f"Loading {selection} ..."):
        ast.shared.components.write_page(page)


if __name__ == "__main__":
    main()
