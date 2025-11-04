import streamlit as st
import requests
from typing import Dict, List, Optional

# Page configuration
st.set_page_config(
    page_title="MET Museum Explorer",
    page_icon="🎨",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .artwork-title {
        font-size: 1.8rem;
        font-weight: bold;
        margin-top: 1rem;
    }
    .metadata {
        font-size: 1.1rem;
        margin: 0.3rem 0;
    }
    .stImage {
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    </style>
""", unsafe_allow_html=True)

# API Functions
@st.cache_data(ttl=3600)
def search_met(query: str, has_images: bool = True) -> Optional[Dict]:
    """Search the MET Museum collection"""
    url = f"https://collectionapi.metmuseum.org/public/collection/v1/search"
    params = {
        "q": query,
        "hasImages": str(has_images).lower()
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error searching: {e}")
        return None

@st.cache_data(ttl=3600)
def get_object_details(object_id: int) -> Optional[Dict]:
    """Get detailed information about a specific object"""
    url = f"https://collectionapi.metmuseum.org/public/collection/v1/objects/{object_id}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching object details: {e}")
        return None

def display_artwork(artwork: Dict):
    """Display artwork with details"""
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Display image
        if artwork.get('primaryImage'):
            st.image(artwork['primaryImage'], use_container_width=True)
        elif artwork.get('primaryImageSmall'):
            st.image(artwork['primaryImageSmall'], use_container_width=True)
        else:
            st.info("No image available for this artwork")
    
    with col2:
        # Display metadata
        st.markdown(f"<div class='artwork-title'>{artwork.get('title', 'Untitled')}</div>", 
                   unsafe_allow_html=True)
        
        if artwork.get('artistDisplayName'):
            st.markdown(f"<div class='metadata'><b>Artist:</b> {artwork['artistDisplayName']}</div>", 
                       unsafe_allow_html=True)
        
        if artwork.get('culture'):
            st.markdown(f"<div class='metadata'><b>Culture:</b> {artwork['culture']}</div>", 
                       unsafe_allow_html=True)
        
        if artwork.get('objectDate'):
            st.markdown(f"<div class='metadata'><b>Date:</b> {artwork['objectDate']}</div>", 
                       unsafe_allow_html=True)
        
        if artwork.get('medium'):
            st.markdown(f"<div class='metadata'><b>Medium:</b> {artwork['medium']}</div>", 
                       unsafe_allow_html=True)
        
        if artwork.get('dimensions'):
            st.markdown(f"<div class='metadata'><b>Dimensions:</b> {artwork['dimensions']}</div>", 
                       unsafe_allow_html=True)
        
        if artwork.get('department'):
            st.markdown(f"<div class='metadata'><b>Department:</b> {artwork['department']}</div>", 
                       unsafe_allow_html=True)
        
        if artwork.get('classification'):
            st.markdown(f"<div class='metadata'><b>Classification:</b> {artwork['classification']}</div>", 
                       unsafe_allow_html=True)
        
        if artwork.get('creditLine'):
            st.markdown(f"<div class='metadata'><b>Credit:</b> {artwork['creditLine']}</div>", 
                       unsafe_allow_html=True)
        
        # Link to MET website
        if artwork.get('objectURL'):
            st.markdown(f"[View on MET Museum Website]({artwork['objectURL']})")

# Main App
def main():
    st.markdown("<div class='main-header'>🎨 MET Museum Explorer</div>", unsafe_allow_html=True)
    
    # Search bar
    search_query = st.text_input(
        "Search the collection",
        placeholder="e.g., flower, Van Gogh, Chinese ceramics...",
        help="Search for artworks by keyword, artist, culture, or time period"
    )
    
    # Sidebar filters
    with st.sidebar:
        st.header("⚙️ Settings")
        results_per_page = st.slider("Results per page", 5, 50, 20)
        only_with_images = st.checkbox("Only show items with images", value=True)
        
        st.markdown("---")
        st.markdown("### About")
        st.markdown("""
        This app uses the [Metropolitan Museum of Art Collection API](https://metmuseum.github.io/) 
        to explore over 400,000 artworks from their collection.
        """)
    
    if search_query:
        with st.spinner("Searching the collection..."):
            search_results = search_met(search_query, only_with_images)
        
        if search_results and search_results.get('total', 0) > 0:
            total_results = search_results['total']
            object_ids = search_results['objectIDs']
            
            st.success(f"Found {total_results:,} artworks")
            
            # Pagination
            if 'page' not in st.session_state:
                st.session_state.page = 0
            
            total_pages = (len(object_ids) - 1) // results_per_page + 1
            
            # Page navigation
            col1, col2, col3 = st.columns([1, 2, 1])
            with col1:
                if st.button("⬅️ Previous") and st.session_state.page > 0:
                    st.session_state.page -= 1
                    st.rerun()
            with col2:
                st.markdown(f"<div style='text-align: center'>Page {st.session_state.page + 1} of {total_pages}</div>", 
                           unsafe_allow_html=True)
            with col3:
                if st.button("Next ➡️") and st.session_state.page < total_pages - 1:
                    st.session_state.page += 1
                    st.rerun()
            
            # Display results for current page
            start_idx = st.session_state.page * results_per_page
            end_idx = min(start_idx + results_per_page, len(object_ids))
            page_object_ids = object_ids[start_idx:end_idx]
            
            for idx, object_id in enumerate(page_object_ids):
                with st.spinner(f"Loading artwork {idx + 1}/{len(page_object_ids)}..."):
                    artwork = get_object_details(object_id)
                    if artwork:
                        display_artwork(artwork)
                        st.markdown("---")
        
        elif search_results and search_results.get('total', 0) == 0:
            st.warning("No results found. Try a different search term.")
        else:
            st.error("Unable to perform search. Please try again.")
    
    else:
        # Welcome message
        st.info("👆 Enter a search term above to explore the MET Museum collection")
        
        # Example searches
        st.markdown("### 💡 Try searching for:")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("- Impressionism")
            st.markdown("- Ancient Egypt")
            st.markdown("- Samurai")
        with col2:
            st.markdown("- Van Gogh")
            st.markdown("- Chinese porcelain")
            st.markdown("- Renaissance")
        with col3:
            st.markdown("- Flowers")
            st.markdown("- Sculpture")
            st.markdown("- Landscape")

if __name__ == "__main__":
    main()
