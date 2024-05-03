import streamlit as st
from streamlit_searchbox import st_searchbox
import urllib, urllib.request
import feedparser
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from streamlit_lottie import st_lottie_spinner
import db as db
import json
from PIL import Image
import numpy as np
from streamlit_extras.stylable_container import stylable_container 
import display_funcs as displ

#################### Preferences #########################

# How many results are displayed per "show more"
display_chunk_size = 10

################ State vars and funcs ####################

# Initialize state variables
if "button_clicked" not in st.session_state:    
    st.session_state.button_clicked = False

if "button_clicked_more" not in st.session_state:    
    st.session_state.button_clicked_more = False

if "display_button" not in st.session_state:    
    st.session_state.display_button = True

if "show_err" not in st.session_state:    
    st.session_state.show_err = False

# Callback function to toggle button_clicked
def callback():
	st.session_state.button_clicked = True

# Callback function to toggle display_button and button_clicked_more
def callback_disappear():
	st.session_state.display_button = False
	st.session_state.button_clicked_more = True

## Cached functions:
# Load recommendations from database
@st.cache_data(show_spinner=False)
def get_recomms_from_db(select):
	related_papers = db.retrieve_entry(select)
	if related_papers is not None:
		cutoff = 30
		cross_scores = related_papers["cross_scores"][:]
		idx = np.argsort(cross_scores[:])[::-1]
		cs = np.array(cross_scores[:])[idx]
		related_papers_ids = np.array(related_papers["related_arXiv_ids"][:])[idx]
		return related_papers_ids[1:], cs[1:]
	else:
		return None, None

# Add hits to data that is displayed
@st.cache_data(show_spinner=False)
def add_hits(hits, related_papers_ids, start, end):
	## Loop through related papers and fetch data
	for i in range(start, end):
		hits += [db.fetch_arXiv_data(related_papers_ids[i])]
		
	return hits

# Search arxiv function; also toggles state variables
def search_arxiv(search_query):
	"""
	Function that connects to the arXiv API and 
	queries for search_query. Returned are a list of
	max. 50 matches in the form
	Tuple: (string that will be displayed, object that is returned)
	"""

	if not search_query:
		return []

	search_query = db.convert_string(search_query)

	url_base = 'http://export.arxiv.org/api/query?search_query='
	url_ending = '&sortBy=lastUpdatedDate&sortOrder=descending&max_results=50&searchtype=all&source=header'
	url = url_base + search_query + url_ending
	response = urllib.request.urlopen(url).read()

	feed = feedparser.parse(response)
	
	res = int(feed.feed.opensearch_totalresults)

	results = []
	if res>0:
		for i in range(len(feed.entries)):
			f = feed.entries[i]
			results += [(f.title, db.link_to_id(f.id))]

	st.session_state.button_clicked = False
	st.session_state.button_clicked_more = False
	st.session_state.display_button = True
	st.session_state.show_err = False

	return results

##########################################################
###################### App ###############################
##########################################################

# Icon image
img_icon = Image.open("img/icon.png")

# Page setup
st.set_page_config(page_title = "TeReX", page_icon = img_icon, layout = "wide")

# Hide streamlit running man for loading
hide_streamlit_style = displ.hide_st_style()
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Change padding of borders
padding_style = displ.padding_style()
st.markdown(padding_style, unsafe_allow_html=True)

# On top right corner, show ? symbol for app info
_,col = st.columns([30,1])
with col:
	with stylable_container(
	    key="help",
	    css_styles="""
	        button {
	            background-color: white;
	            color: grey;
	            border-radius: 50px;
	        }
	        """,
	):
		st.button("**?**", disabled = True, help="**TeReX (Transformer Enabled Research Explorer) lets you find similar papers based on your input paper using large language models and a multi-step filtering process. You can search through all papers listed on the arXiv and get corresponding recommendations. The database is updated on a weekly basis.**")

# Title image
_, col, _ = st.columns([2.1,1,2.1])
with col:
	st.image("img/title2.png")

# Searchbox and search button
_, col, _ = st.columns([1,2,1])
with col:
	col_inside,b = st.columns([9,1])
	with col_inside:
		select = st_searchbox(label="", search_function=search_arxiv, placeholder = "Search for title, author, arXiv ID...", default_options = [""])
		if select is None:
			st.session_state.button_clicked = False
			st.session_state.button_clicked_more = False
			st.session_state.display_button = True
			st.session_state.show_err = False
	with b:
		search = st.button("Go", type="primary", use_container_width = True, on_click = callback)

if search or st.session_state.button_clicked:

	_, col, _ = st.columns([2,0.7,2])
	with col:
		with open("img/loading2.json","r") as file:
			url = json.load(file)

		with st_lottie_spinner(url):

			# Ping data base to get recommended articles based on selection
			related_papers_ids, cs = get_recomms_from_db(select)

			if related_papers_ids is not None:

					# Create dictionaries with entries fetched from arXiv
					hits = []
					hits = add_hits(hits, related_papers_ids, 0, display_chunk_size)

	if related_papers_ids is None:
			#st.session_state.show_err = True
			_,col,_ = st.columns([1,2,1])
			with col:
				st.error("Paper is not yet in our database ☹️. Try again later or change selection.")

## Show results in containers
if search or st.session_state.button_clicked:
	if related_papers_ids is not None:
		_, col, _ = st.columns([1,6,1])
		with col:
			for i in range(display_chunk_size):
				hit = hits[i]
				if cs[i] > 0.94:
					high_match = True
				else:
					high_match = False
				displ.display(hit, high_match)

		if st.session_state.display_button:
			_, col, _ = st.columns([5,1,5])
			with col:
				more = st.button("Show more", type="secondary", on_click=callback_disappear)
		if st.session_state.button_clicked_more:
			_, col, _ = st.columns([2,0.7,2])
			with col:
				with st_lottie_spinner(url):
					hits = add_hits(hits, related_papers_ids, display_chunk_size, 2*display_chunk_size)

			_, col1, _ = st.columns([1,6,1])
			with col1:
				for i in range(display_chunk_size, 2*display_chunk_size):
					hit = hits[i]
					if cs[i] > 0.94:
						high_match = True
					else:
						high_match = False
					displ.display(hit, high_match)
