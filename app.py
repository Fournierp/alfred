import awesome_streamlit as ast
import streamlit as st

import src.home
import src.prediction
import src.research

ast.core.services.other.set_logging_format()

PAGES = {
    'Home': src.home,
    'Research': src.research,
    'Prediction': src.prediction,
}


def main() -> None:
    st.sidebar.title('Navigation')
    selection = st.sidebar.radio('Visit', list(PAGES.keys()))

    page = PAGES[selection]

    with st.spinner(f'Loading {selection} ...'):
        ast.shared.components.write_page(page)


if __name__ == '__main__':
    main()
