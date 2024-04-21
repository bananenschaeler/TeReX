import streamlit as st
from streamlit_extras.stylable_container import stylable_container 

def hide_st_style():
	hide_streamlit_style = """
	            <style>
	            div[data-testid="stToolbar"] {
	            visibility: hidden;
	            height: 0%;
	            position: fixed;
	            }
	            div[data-testid="stDecoration"] {
	            visibility: hidden;
	            height: 0%;
	            position: fixed;
	            }
	            div[data-testid="stStatusWidget"] {
	            visibility: hidden;
	            height: 0%;
	            position: fixed;
	            }
	            #MainMenu {
	            visibility: hidden;
	            height: 0%;
	            }
	            header {
	            visibility: hidden;
	            height: 0%;
	            }
	            footer {
	            visibility: hidden;
	            height: 0%;
	            }
	            </style>
	            """
	return hide_streamlit_style

def padding_style():
	padding_st = """
		<style>
		       .block-container {
		            padding-top: 0rem;
		            padding-bottom: 5rem;
		            padding-left: 5rem;
		            padding-right: 5rem;
		        }
		</style>
		"""
	return padding_st


def create_container_with_color(id, color="#E4F2EC"):
    # todo: instead of color you can send in any css
    plh = st.container()
    html_code = """<div id = 'my_div_outer'></div>"""
    st.markdown(html_code, unsafe_allow_html=True)

   
    with plh:
        inner_html_code = """<div id = 'my_div_inner_%s'></div>""" % id
        plh.markdown(inner_html_code, unsafe_allow_html=True)

    ## applying style
    chat_plh_style = """
        <style>
            div[data-testid='stVerticalBlock']:has(div#my_div_inner_%s):not(:has(div#my_div_outer)) {
                background-color: %s;
                border-radius: 20px;
                padding: 10px;
            };
        </style>
        """
    chat_plh_style = chat_plh_style % (id, color)

    st.markdown(chat_plh_style, unsafe_allow_html=True)
    return plh


def display(hit, high_match = False):
	with st.container(height=420, border=True):
	#stylable_container(key = "green_container", css_styles="""background-color: green"""):

		if high_match:
			a,b = st.columns([9,1])
			with a:
				st.subheader(hit["title"].replace("\n", " ") , divider='grey')
			with b:
				st.image("img/high_match3.png")
		else:
			st.subheader(hit["title"].replace("\n", " ") , divider='grey')
		#st.markdown("<h2 style='text-align: center; color: black;'>"+hit["title"]+"</h2>", unsafe_allow_html=True)
		authors_str = ""
		authors = hit["authors"]
		if len(authors)>1:
			for i in range(len(hit["authors"])-1):
				author = authors[i]
				name = author["name"] 
				authors_str += name + ", "
			last_author = authors[-1]
			authors_str += "and " + last_author["name"] 
		else:
			authors_str = authors[0]["name"]
		st.markdown("**"+authors_str+"**")
		st.write(hit["abstract"])
		#st.write(hit["abstract"])
		a,col,b = st.columns([2,1,2])
		with col:
			st.link_button(r"$\rightarrow$ View on arXiv", hit["link"])
	st.text("")
