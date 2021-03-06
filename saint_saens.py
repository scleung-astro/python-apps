# this is an exercise for using streamlit to build a query page
# for one of my favourite composers.

from re import RegexFlag
import pandas as pd
import streamlit as st
from PIL import Image

# fetch the data from wikipedia for Saint-Saens's composition list
@st.cache
def load_data():

    # read the data from Wikipedia
    df = pd.read_html("https://en.wikipedia.org/wiki/List_of_compositions_by_Camille_Saint-Sa%C3%ABns")[0]

    # render the internet data
    df.drop("Scoring", axis=1, inplace=True)
    df.drop("Opus", axis=1, inplace=True)
    df["R"] = df["R"].fillna("0").astype(int)

    return df

# load Saint Saens image for decoration of the front page
@st.cache
def load_image():
    return Image.open('saint_saens_portrait.jpg')

def main():

    # build the database
    df = load_data()
    portrait = load_image()
    
    # filter the data for later use
    genres = df["Genre"].unique()

    # build the front page
    title_frame = st.empty()
    title_frame.title("Camille Saint-Saens Composition Query")

    portrait_frame, bibliography_frame = st.beta_columns(2)
    portrait_frame.image(portrait, caption="Saint-Saens; portrait at ca. 1880", width=200)
    bibliography_frame.write("A French composer born in 1835. He is famous for works including " 
                            "the opera Samson et Delilah, symphonic poem Danse Macabre, Symphony No.3 'Organ', "
                            "and Introduction and Rondo Cappricioso for violin and orchestra. "
                            "His music is known for its aristocratic taste and scholarly. His music "
                            "style leans to romanticism, where he showed strong conflicts when "
                            "new trends such as Impressionism and Neoclassicism. \n"
                            "Data source: Wikipedia")

    # sidebar construction
    use_title = st.sidebar.checkbox("Select by title")
    use_opus = st.sidebar.checkbox("Select by opus number")

    display_title = False
    display_opus = False

    # show more option when using title to filter Saint-Saens composition
    if use_title:

        # let the user choose the genre
        st.sidebar.title("Filter by")
        st.sidebar.subheader("Genre")
        genre = st.sidebar.selectbox("Click below to select a genre", genres, index=0)

        # let the user choose the title based on the genre
        comp_list = list(df[df["Genre"] == genre]["French title (original title)"])

        st.sidebar.subheader("Title")
        title = st.sidebar.selectbox("Click below to select a title", comp_list, index=0)
        display_title = st.sidebar.button("Find details by title")

    # show more option when using opus number to filter Saint-Saens composition
    if use_opus:
        st.sidebar.title("Filter by")
        st.sidebar.subheader("Opus Number (R)")
        opus_no = st.sidebar.text_input("Enter the composition number", value=1)
        display_opus = st.sidebar.button("Find details by opus")

    # show the results
    if display_title:
        df_title = df[df["French title (original title)"] == title]
        composition_frame = st.empty()
        composition_frame.write(df_title)
    
    # show the results
    if display_opus:
        df_title = df[df["R"] == int(opus_no)]
        composition_frame = st.empty()
        composition_frame.write(df_title)
    

    st.sidebar.title("About")
    st.sidebar.info("A short StreamLit practice for querying internet database "
                "and filter the selected composition by title or composition number. "
                "Written by Shing Chi Leung at 6 March 2021.")

if __name__== "__main__":
    main()