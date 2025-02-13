from pytrends.request import TrendReq
import pandas as pd
from datetime import datetime

def analyze_keywords(keywords_list, timeframe='today 12-m'):
    """
    Analyze keywords using Google Trends data
    """
    # Initialize pytrends
    pytrends = TrendReq()
    
    # Create empty DataFrame for results
    results = pd.DataFrame()
    
    # Analyze keywords in batches of 5 (Google Trends limit)
    for i in range(0, len(keywords_list), 5):
        batch = keywords_list[i:i+5]
        
        # Build the payload
        pytrends.build_payload(batch, timeframe=timeframe)
        
        # Get interest over time
        interest = pytrends.interest_over_time()
        
        # Get related queries for each keyword
        for kw in batch:
            related = pytrends.related_queries()[kw]
            if related['rising'] is not None:
                rising_queries = related['rising']['query'].tolist()
                print(f"\nRising queries for {kw}:")
                print(rising_queries)
        
        # Add to results
        if not interest.empty:
            results = pd.concat([results, interest], axis=1)
    
    return results

def main():
    # Example keywords
    keywords = [
        "Chicago Drill",
        "OTF Clothing",
        "Chicago Gangs",
        "OTF Merch",
        "Lil Durk OTF"
    ]
    
    print("Analyzing keywords...")
    results = analyze_keywords(keywords)
    
    # Save results
    filename = f'keyword_trends_{datetime.now().strftime("%Y%m%d")}.csv'
    results.to_csv(filename)
    print(f"\nResults saved to {filename}")
    
    # Show summary
    print("\nTrend Summary:")
    print(results.mean().sort_values(ascending=False))

if __name__ == "__main__":
    main()