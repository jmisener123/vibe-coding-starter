import streamlit as st
import pandas as pd
import numpy as np

# Set page configuration
st.set_page_config(
    page_title="IMDB Movie Finder",
    page_icon="🎬",
    layout="wide"
)

# Cache the data loading function
@st.cache_data
def load_data():
    """Load and preprocess the IMDB dataset"""
    try:
        df = pd.read_csv('imdb_top_1000.csv')
        
        # Clean column names by stripping whitespace
        df.columns = df.columns.str.strip()
        
        # Convert runtime to minutes (extract number from "142 min" format)
        df['Runtime_Minutes'] = df['Runtime'].str.extract('(\d+)').astype(int)
        
        # Create decade column
        df['Decade'] = (df['Released_Year'] // 10) * 10
        
        # Split genres and create a set of all unique genres
        all_genres = set()
        for genres_str in df['Genre'].dropna():
            genres = [g.strip() for g in genres_str.split(',')]
            all_genres.update(genres)
        
        return df, sorted(list(all_genres))
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None, None

def filter_movies(df, selected_genres, max_runtime, selected_decades):
    """Filter movies based on user selections"""
    filtered_df = df.copy()
    
    # Filter by genres
    if selected_genres:
        genre_mask = filtered_df['Genre'].apply(
            lambda x: any(genre in str(x) for genre in selected_genres) if pd.notna(x) else False
        )
        filtered_df = filtered_df[genre_mask]
    
    # Filter by runtime
    if max_runtime:
        filtered_df = filtered_df[filtered_df['Runtime_Minutes'] <= max_runtime]
    
    # Filter by decades
    if selected_decades:
        filtered_df = filtered_df[filtered_df['Decade'].isin(selected_decades)]
    
    return filtered_df

def main():
    # Header
    st.title("🎬 IMDB Top 1000 Movie Finder")
    st.markdown("Find your next movie to watch from IMDB's top-rated films!")
    
    # Load data
    df, genres = load_data()
    if df is None:
        st.stop()
    
    # Sidebar for filters
    st.sidebar.header("🎯 Filter Your Movies")
    
    # Genre selection
    st.sidebar.subheader("Select Genres")
    selected_genres = st.sidebar.multiselect(
        "Choose one or more genres:",
        options=genres,
        help="Select genres you're interested in. Leave empty to include all genres."
    )
    
    # Runtime filter
    st.sidebar.subheader("Runtime Preference")
    runtime_option = st.sidebar.radio(
        "Runtime preference:",
        ["Any length", "Under 2 hours (< 120 min)", "Custom max runtime"]
    )
    
    max_runtime = None
    if runtime_option == "Under 2 hours (< 120 min)":
        max_runtime = 120
    elif runtime_option == "Custom max runtime":
        max_runtime = st.sidebar.slider(
            "Maximum runtime (minutes):",
            min_value=60,
            max_value=300,
            value=120,
            step=10
        )
    
    # Decade selection
    st.sidebar.subheader("Select Decades")
    available_decades = sorted(df['Decade'].unique())
    selected_decades = st.sidebar.multiselect(
        "Choose decades:",
        options=available_decades,
        help="Select decades you're interested in. Leave empty to include all decades."
    )
    
    # Apply filters
    filtered_df = filter_movies(df, selected_genres, max_runtime, selected_decades)
    
    # Display results
    st.header(f"🎯 Found {len(filtered_df)} movies matching your criteria")
    
    if len(filtered_df) == 0:
        st.warning("No movies match your current filters. Try adjusting your criteria!")
        return
    
    # Sort by IMDB rating (highest first)
    filtered_df = filtered_df.sort_values('IMDB_Rating', ascending=False)
    
    # Display options
    col1, col2 = st.columns([3, 1])
    with col2:
        display_count = st.selectbox(
            "Movies to display:",
            [10, 25, 50, 100, "All"],
            index=0
        )
        
        if display_count != "All":
            display_df = filtered_df.head(display_count)
        else:
            display_df = filtered_df
    
    # Display movies in a nice format
    for idx, movie in display_df.iterrows():
        with st.container():
            col1, col2 = st.columns([1, 4])
            
            with col1:
                # Display poster if available
                if pd.notna(movie['Poster_Link']) and movie['Poster_Link'].startswith('http'):
                    try:
                        st.image(movie['Poster_Link'], width=120)
                    except:
                        st.text("🎬\nPoster\nNot\nAvailable")
                else:
                    st.text("🎬\nPoster\nNot\nAvailable")
            
            with col2:
                # Movie details
                st.subheader(f"{movie['Series_Title']} ({movie['Released_Year']})")
                
                # Rating and basic info
                col2_1, col2_2, col2_3, col2_4 = st.columns(4)
                with col2_1:
                    st.metric("IMDB Rating", f"⭐ {movie['IMDB_Rating']}")
                with col2_2:
                    st.metric("Runtime", movie['Runtime'])
                with col2_3:
                    st.metric("Year", movie['Released_Year'])
                with col2_4:
                    if pd.notna(movie['Meta_score']):
                        st.metric("Metacritic", f"{int(movie['Meta_score'])}")
                
                # Genre and Director
                st.write(f"**Genre:** {movie['Genre']}")
                st.write(f"**Director:** {movie['Director']}")
                
                # Cast
                cast = []
                for star_col in ['Star1', 'Star2', 'Star3', 'Star4']:
                    if pd.notna(movie[star_col]):
                        cast.append(movie[star_col])
                if cast:
                    st.write(f"**Cast:** {', '.join(cast)}")
                
                # Overview
                if pd.notna(movie['Overview']):
                    st.write(f"**Plot:** {movie['Overview']}")
                
                # Additional info
                if pd.notna(movie['No_of_Votes']):
                    st.caption(f"👥 {movie['No_of_Votes']:,} votes")
                
            st.divider()
    
    # Summary statistics
    if len(filtered_df) > 0:
        st.header("📊 Summary Statistics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Average Rating", f"{filtered_df['IMDB_Rating'].mean():.1f}")
        with col2:
            st.metric("Average Runtime", f"{filtered_df['Runtime_Minutes'].mean():.0f} min")
        with col3:
            most_common_decade = filtered_df['Decade'].mode().iloc[0] if not filtered_df['Decade'].mode().empty else "N/A"
            st.metric("Most Common Decade", f"{most_common_decade}s")
        with col4:
            st.metric("Total Movies", len(filtered_df))

if __name__ == "__main__":
    main()
