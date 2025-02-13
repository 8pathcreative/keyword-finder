import pandas as pd
import numpy as np
from typing import List, Dict, Tuple
import csv
from datetime import datetime

class KeywordOpportunityAnalyzer:
    def __init__(self, 
                 min_search_volume: int = 1000,
                 max_competition: float = 0.3,
                 min_cpc: float = 0.5):
        """
        Initialize the analyzer with threshold values
        
        Args:
            min_search_volume: Minimum monthly searches
            max_competition: Maximum competition score (0-1)
            min_cpc: Minimum cost per click ($)
        """
        self.min_search_volume = min_search_volume
        self.max_competition = max_competition
        self.min_cpc = min_cpc
        
    def load_keyword_data(self, filepath: str) -> pd.DataFrame:
        """Load keyword data from CSV export"""
        try:
            df = pd.read_csv(filepath)
            required_columns = ['Keyword', 'Avg. monthly searches', 'Competition', 'Top of page bid (low range)']
            
            # Verify all required columns exist
            if not all(col in df.columns for col in required_columns):
                raise ValueError("CSV must contain columns: " + ", ".join(required_columns))
                
            return df
        except Exception as e:
            raise Exception(f"Error loading keyword data: {str(e)}")

    def calculate_opportunity_score(self, 
                                 search_volume: int, 
                                 competition: float, 
                                 cpc: float) -> float:
        """
        Calculate opportunity score based on volume, competition, and CPC
        Higher score = better opportunity
        """
        # Normalize values
        volume_score = np.log10(max(search_volume, 1)) / 5  # Log scale for volume
        competition_score = 1 - competition  # Inverse competition (lower is better)
        cpc_score = min(cpc / 10, 1)  # Cap CPC score at 1
        
        # Weighted average (adjustable weights)
        weights = {
            'volume': 0.4,
            'competition': 0.4,
            'cpc': 0.2
        }
        
        opportunity_score = (
            volume_score * weights['volume'] +
            competition_score * weights['competition'] +
            cpc_score * weights['cpc']
        )
        
        return round(opportunity_score * 100, 2)

    def analyze_keywords(self, df: pd.DataFrame) -> pd.DataFrame:
        """Analyze keywords and identify opportunities"""
        # Clean and prepare data
        df['Competition'] = pd.to_numeric(df['Competition'], errors='coerce')
        df['Avg. monthly searches'] = pd.to_numeric(df['Avg. monthly searches'].str.replace(',', ''), errors='coerce')
        df['Top of page bid (low range)'] = pd.to_numeric(df['Top of page bid (low range)'].str.replace('$', ''), errors='coerce')
        
        # Filter based on thresholds
        mask = (
            (df['Avg. monthly searches'] >= self.min_search_volume) &
            (df['Competition'] <= self.max_competition) &
            (df['Top of page bid (low range)'] >= self.min_cpc)
        )
        
        opportunities = df[mask].copy()
        
        # Calculate opportunity score for each keyword
        opportunities['Opportunity Score'] = opportunities.apply(
            lambda x: self.calculate_opportunity_score(
                x['Avg. monthly searches'],
                x['Competition'],
                x['Top of page bid (low range)']
            ),
            axis=1
        )
        
        # Sort by opportunity score
        opportunities = opportunities.sort_values('Opportunity Score', ascending=False)
        
        return opportunities

    def export_results(self, opportunities: pd.DataFrame, output_filepath: str):
        """Export results to CSV with timestamp"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'keyword_opportunities_{timestamp}.csv'
        if not output_filepath.endswith('.csv'):
            output_filepath += '.csv'
            
        opportunities.to_csv(output_filepath, index=False)
        print(f"Results exported to: {output_filepath}")
        
    def generate_summary(self, opportunities: pd.DataFrame) -> Dict:
        """Generate summary statistics of opportunities"""
        return {
            'total_opportunities': len(opportunities),
            'avg_search_volume': opportunities['Avg. monthly searches'].mean(),
            'avg_competition': opportunities['Competition'].mean(),
            'avg_opportunity_score': opportunities['Opportunity Score'].mean(),
            'top_keywords': opportunities.head(5)['Keyword'].tolist()
        }

def main():
    # Example usage
    analyzer = KeywordOpportunityAnalyzer(
        min_search_volume=1000,
        max_competition=0.3,
        min_cpc=0.5
    )
    
    try:
        # Load data
        print("Loading keyword data...")
        df = analyzer.load_keyword_data('keyword_planner_export.csv')
        
        # Analyze keywords
        print("Analyzing keywords...")
        opportunities = analyzer.analyze_keywords(df)
        
        # Generate summary
        summary = analyzer.generate_summary(opportunities)
        print("\nAnalysis Summary:")
        print(f"Total Opportunities: {summary['total_opportunities']}")
        print(f"Average Search Volume: {summary['avg_search_volume']:.2f}")
        print(f"Average Competition: {summary['avg_competition']:.2f}")
        print(f"Average Opportunity Score: {summary['avg_opportunity_score']:.2f}")
        print("\nTop 5 Keywords:")
        for keyword in summary['top_keywords']:
            print(f"- {keyword}")
        
        # Export results
        analyzer.export_results(opportunities, 'keyword_opportunities.csv')
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
