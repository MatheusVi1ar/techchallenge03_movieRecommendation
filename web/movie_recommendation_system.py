import streamlit as st
import pandas as pd
from PIL import Image
import requests
from io import BytesIO
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
import ast

load_dotenv()

class MovieDatabase:
    def __init__(self):
        self.engine = self.create_connection()

    def create_connection(self):
        try:
            connection_string = (
                f"postgresql://{os.getenv('RDS_USERNAME')}:{os.getenv('RDS_PASSWORD')}"
                f"@{os.getenv('RDS_HOST')}:{os.getenv('RDS_PORT', '5432')}/{os.getenv('RDS_DB_NAME')}"
            )
            return create_engine(connection_string)
        except Exception as e:
            st.error(f"Database connection error: {str(e)}")
            return None

    def get_movie_data(self, movie_id):
        """Get movie data including similarity scores and vote scores"""
        try:
            query = """
                WITH similar_movies AS (
                    SELECT 
                        m.id,
                        m.original_title as title,
                        m.genres,
                        m.overview as description,
                        m.release_date,
                        m.imdb_id,
                        m.poster_path as image_url,
                        s.similarity_score as similarity,
                        v.vote_score as score
                    FROM similarity_scores s
                    JOIN movies_metadata m ON m.id = s.movie_id_target
                    LEFT JOIN vote_scores v ON v.movie_id = m.id
                    WHERE s.movie_id_base = %(movie_id)s
                )
                SELECT *,
                       (%(weight)s * similarity + (1 - %(weight)s) * COALESCE(score, 0)) as final_score
                FROM similar_movies
                WHERE image_url IS NOT NULL
                  AND genres != '[]'
                ORDER BY final_score DESC
                LIMIT %(limit)s
            """
            
            df = pd.read_sql_query(
                query, 
                self.engine, 
                params={
                    'movie_id': movie_id,
                    'weight': float(os.getenv('SIMILARITY_WEIGHT')),
                    'limit': int(os.getenv('MAX_RESULTS'))
                }
            )
            
            # Process the DataFrame
            if not df.empty:
                df['genres'] = df['genres'].apply(ast.literal_eval)
                df['year'] = pd.to_datetime(df['release_date']).dt.year
                
            return df
        except Exception as e:
            st.error(f"Error fetching movie data: {str(e)}")
            return pd.DataFrame()

    def search_movies(self, search_term):
        """Search movies by title"""
        try:
            query = """
                SELECT 
                    m.id,
                    m.original_title as title,
                    m.genres,
                    m.overview as description,
                    m.release_date,
                    m.poster_path as image_url,
                    m.imdb_id,
                    v.vote_score as score
                FROM movies_metadata m
                LEFT JOIN vote_scores v ON v.movie_id = m.id
                WHERE LOWER(m.original_title) LIKE LOWER(%(search)s)
                  AND m.poster_path IS NOT NULL
                ORDER BY v.vote_score DESC NULLS LAST, m.original_title
                LIMIT 4
            """
            df = pd.read_sql_query(
                query,
                self.engine,
                params={'search': f'%{search_term}%'}
            )
            
            if not df.empty:
                df['genres'] = df['genres'].apply(ast.literal_eval)
                df['year'] = pd.to_datetime(df['release_date']).dt.year
                
            return df
        except Exception as e:
            st.error(f"Error searching movies: {str(e)}")
            return pd.DataFrame()
    
    def search_poster(imdb_id:str):
        URL = 'https://api.themoviedb.org/3/find/{0}?api_key={1}&language=en-US&external_source=imdb_id'.format(imdb_id, os.getenv('API_KEY_TMDB'))

        req = requests.get(URL).json()

        try:
            poster_path = req['movie_results'][0]['poster_path']
            return poster_path
        except:
            return None

# Page configuration
st.set_page_config(
    page_title="Movie Recommendation System",
    page_icon="🎬",
    layout="wide"
)

# Custom CSS
def add_bg_from_url():
    st.markdown(
         """
         <style>
         .stApp {
             background: linear-gradient(to right, #0f2027, #203a43, #2c5364);
             color: white;
         }
         .card {
             background-color: rgba(255, 255, 255, 0.1);
             border-radius: 10px;
             padding: 20px;
             margin: 10px 0px;
             backdrop-filter: blur(10px);
         }
         .movie-title {
             font-size: 18px;
             font-weight: bold;
             margin-bottom: 10px;
         }
         .movie-info {
             font-size: 14px;
             margin-bottom: 5px;
         }
         .score-info {
             font-size: 16px;
             font-weight: bold;
             color: #FFD700;
         }
         .metadata {
             font-size: 12px;
             color: #cccccc;
             margin-top: 5px;
         }
         </style>
         """,
         unsafe_allow_html=True
     )

add_bg_from_url()

# Initialize database connection
db = MovieDatabase()

# Title
st.title("🎬 Movie Recommendation System")
st.markdown(f"### Find similar movies based on similarity and vote scores")

# Search box for movies
search_term = st.text_input("Search for a movie by title:")

if search_term:
    search_results = db.search_movies(search_term)
    
    if not search_results.empty:
        st.markdown("### Select a movie to find similar titles:")
        
        # Display search results in a grid
        cols = st.columns(2)
        for idx, (_, movie) in enumerate(search_results.iterrows()):
            with cols[idx % 2]:
                st.markdown(f"<div class='card'>", unsafe_allow_html=True)
                
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    poster_path = MovieDatabase.search_poster(movie['imdb_id'])
                    image_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
                    try:
                        if poster_path is None:
                            raise Exception
                        response = requests.get(image_url)
                        img = Image.open(BytesIO(response.content))
                        st.image(img, width=150)
                    except:
                        st.image("https://images.justwatch.com/poster/142071397/s718/error-404.jpg", width=150)
                
                with col2:
                    st.markdown(f"<div class='movie-title'>{movie['title']} ({movie['year']})</div>", 
                              unsafe_allow_html=True)
                    st.markdown(f"<div class='movie-info'>Genres: {', '.join(movie['genres'])}</div>", 
                              unsafe_allow_html=True)
                    if pd.notna(movie['score']):
                        st.markdown(f"<div class='score-info'>Vote Score: {movie['score']:.2f}</div>", 
                                  unsafe_allow_html=True)
                    
                    if st.button(f"Find Similar Movies", key=f"btn_{movie['id']}"):
                        st.session_state.selected_movie = movie
                
                st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.warning("No movies found matching your search.")

# Show similar movies if a movie is selected
if 'selected_movie' in st.session_state:
    movie = st.session_state.selected_movie
    st.markdown("## Similar Movies")
    st.markdown(f"Showing movies similar to **{movie['title']}** ({movie['year']})")
    
    similar_movies = db.get_movie_data(movie['id'])
    
    if not similar_movies.empty:
        for _, similar_movie in similar_movies.iterrows():
            st.markdown(f"<div class='card'>", unsafe_allow_html=True)
            
            col1, col2 = st.columns([1, 3])
            
            with col1:
                poster_path = MovieDatabase.search_poster(similar_movie['imdb_id'])
                image_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
                try:
                    if poster_path is None:
                            raise Exception
                    response = requests.get(image_url)
                    img = Image.open(BytesIO(response.content))
                    st.image(img, width=200)
                except:
                    st.image("https://images.justwatch.com/poster/142071397/s718/error-404.jpg", width=150)
            
            with col2:
                st.markdown(f"<div class='movie-title'>{similar_movie['title']} ({similar_movie['year']})</div>", 
                          unsafe_allow_html=True)
                st.markdown(f"<div class='movie-info'>Genres: {', '.join(similar_movie['genres'])}</div>", 
                          unsafe_allow_html=True)
                st.markdown(f"<div class='score-info'>Similarity Score: {similar_movie['similarity']:.2%}</div>", 
                          unsafe_allow_html=True)
                if pd.notna(similar_movie['score']):
                    st.markdown(f"<div class='score-info'>Vote Score: {similar_movie['score']:.2f}</div>", 
                              unsafe_allow_html=True)
                st.markdown(f"<div class='score-info'>Final Score: {similar_movie['final_score']:.2f}</div>", 
                          unsafe_allow_html=True)
                st.markdown(f"<div class='movie-info'>{similar_movie['description']}</div>", 
                          unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.warning("No similar movies found.")

    if st.button("Clear Selection"):
        del st.session_state.selected_movie

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center'>
        <p>Movie recommendations are based on content similarity and user votes</p>
    </div>
""", unsafe_allow_html=True)