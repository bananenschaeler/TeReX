import streamlit as st
from streamlit_searchbox import st_searchbox
import urllib, urllib.request
import feedparser
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from helper import link_to_id
import pandas as pd
import numpy as np

######### Init firebase connection ###############

if not firebase_admin._apps:
	## Establish firebase connection if not done so before
	cred = credentials.Certificate('data/paperterex-firebase-adminsdk-lj1go-b7e60d4f5c.json')
	app = firebase_admin.initialize_app(cred)

############### API functions ####################

def convert_string(input_string):
	return input_string.replace(" ", "+AND+")

def search_arxiv(search_query):
	"""
	Function that connects to the arXiv API and 
	queries for search_query. Returned are a list of
	max. 30 matches in the form
	Tuple: (string that will be displayed, object that is returned)
	"""

	if not search_query:
		return []

	search_query = convert_string(search_query)

	url_base = 'http://export.arxiv.org/api/query?search_query='
	url_ending = '&sortBy=lastUpdatedDate&sortOrder=descending&max_results=30&searchtype=all&source=header'
	url = url_base + search_query + url_ending
	response = urllib.request.urlopen(url).read()

	feed = feedparser.parse(response)
	
	res = int(feed.feed.opensearch_totalresults)

	results = []
	if res>0:
		for i in range(len(feed.entries)):
			f = feed.entries[i]
			results += [(f.title, link_to_id(f.id))]

	return results

def fetch_arXiv_data(arXiv_id):
	"""
	Function that connects to the arXiv API and 
	queries for arXiv_id. Returned is a dictionary
	with title, authors, abstract, link
	"""

	search_query = arXiv_id

	url_base = 'http://export.arxiv.org/api/query?search_query='
	url_ending = '&max_results=1'
	url = url_base + search_query + url_ending
	response = urllib.request.urlopen(url).read()

	feed = feedparser.parse(response)

	result = {}
	f = feed.entries[0]
	result["title"] = f.title
	result["abstract"] = f.summary
	result["authors"] = f.authors
	result["link"] = f.link

	return result

def retrieve_entry(arxiv_id):
	"""
	Retrieve recommended papers from firebase db
	"""

	db_fire = firestore.client()
	doc_ref = db_fire.collection("paper").document(arxiv_id)

	doc = doc_ref.get()
	if doc.exists:
		dic = doc.to_dict()
		return dic
	else:
	    return None


def retrieve_entry_loc(dics, arxiv_id):
	return next(item for item in dics if item["arXiv_id"] == arxiv_id)["related_papers"]
