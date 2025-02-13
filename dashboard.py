import streamlit as st
import pandas as pd
from pytrends.request import TrendReq
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

class KeywordAnalysisDashboard:
    def __init__(self):
        st.set_page_config(page_title="SEO Keyword Analysis", layout="wide")
        self.pytrends = TrendReq()
        
    def run(self):
        st.title("SEO Keyword Analysis Dashboard")
        
        # Sidebar controls
        with st.sidebar:
            st.header("Settings")
            timeframe = st.selectbox(
                "Select Timeframe",
                ["Past 12 months", "Past 30 days", "Past 7 days", "Past 24 hours"],
                index=0
            )
            
            # Convert friendly names to pytrends format
            timeframe_map = {
                "Past 12 months": "today 12-m",
                "Past 30 days": "today 1-m",
                "Past 7 days": "now 7-d",
                "Past 24 hours": "now 1-d"
            }
            
            # Keyword input
            st.subheader("Enter Keywords")
            keywords_input = st.text_area(
                "Enter keywords (one per line, max 5)",
                "python programming\nlearn python\npython tutorial"
            )
            keywords = [k.strip() for k in keywords_input.split('\n') if k.strip()][:5]
            
            # Analysis options
            st.subheader("Analysis Options")
            show_related = st.checkbox("Show Related Keywords", value=True)
            show_regional = st.checkbox("Show Regional Interest", value=True)
            
        try:
            # Main analysis
            if keywords:
                self.pytrends.build_payload(keywords, timeframe=timeframe_map[timeframe])
                
                # Get interest over time
                interest_df = self.pytrends.interest_over_time()
                
                if not interest_df.empty:
                    # Interest over time plot
                    st.header("Interest Over Time")
                    fig = px.line(interest_df, x=interest_df.index, y=keywords)
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Show raw data if requested
                    if st.checkbox("Show raw data"):
                        st.dataframe(interest_df)
                    
                    # Related queries analysis
                    if show_related:
                        st.header("Related Queries")
                        related_queries = self.pytrends.related_queries()
                        
                        for keyword in keywords:
                            if related_queries[keyword]['rising'] is not None:
                                st.subheader(f"Rising queries for '{keyword}'")
                                rising_df = related_queries[keyword]['rising']
                                fig = px.bar(
                                    rising_df.head(10),
                                    x='query',
                                    y='value',
                                    title=f"Top Rising Queries - {keyword}"
                                )
                                st.plotly_chart(fig, use_container_width=True)
                    
                    # Regional interest
                    if show_regional:
                        st.header("Regional Interest")
                        regional_df = self.pytrends.interest_by_region(resolution='COUNTRY')
                        if not regional_df.empty:
                            # Create a choropleth map for each keyword
                            for keyword in keywords:
                                fig = px.choropleth(
                                    regional_df,
                                    locations=regional_df.index,
                                    locationmode='country names',
                                    color=keyword,
                                    title=f"Regional Interest - {keyword}",
                                    color_continuous_scale="Viridis"
                                )
                                st.plotly_chart(fig, use_container_width=True)
                
                # Download options
                st.header("Export Data")
                if st.button("Download Analysis"):
                    csv = interest_df.to_csv()
                    st.download_button(
                        label="Download CSV",
                        data=csv,
                        file_name=f'keyword_analysis_{datetime.now().strftime("%Y%m%d")}.csv',
                        mime='text/csv'
                    )
                    
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            
if __name__ == "__main__":
    dashboard = KeywordAnalysisDashboard()
    dashboard.run()