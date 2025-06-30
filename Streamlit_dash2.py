import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import os

# Page configuration
st.set_page_config(
    page_title="Soccer Analytics Dashboard",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main {
        padding-top: 1rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    .stMetric {
        background-color: #f0f2f6;
        border: 1px solid #e1e5e9;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load and process CSV data files using pandas"""
    try:
        # Method 1: Direct relative path (recommended for GitHub deployment)
        perf_data = pd.read_csv("Performance_Dropoff_Per_Player.csv")
        sub_data = pd.read_csv("sub_optimizer 2.csv")
        
        # Alternative Method 2: Using pathlib for cross-platform compatibility
        # base_path = Path(__file__).parent
        # perf_data = pd.read_csv(base_path / "perf_Drop.csv")
        # sub_data = pd.read_csv(base_path / "sub_op.csv")
        
        # Alternative Method 3: Using os.path.join for absolute paths
        # current_dir = os.path.dirname(os.path.abspath(__file__))
        # perf_data = pd.read_csv(os.path.join(current_dir, "perf_Drop.csv"))
        # sub_data = pd.read_csv(os.path.join(current_dir, "sub_op.csv"))
        
        # Data processing and merging
        merged_data = pd.merge(
            sub_data, 
            perf_data[['Player', 'Actual Impact', 'Predicted Impact']], 
            on='Player', 
            how='left'
        )
        
        # Calculate overperformance metric
        merged_data['Overperformance'] = (
            merged_data['Actual Impact'] - merged_data['Predicted Impact']
        )
        
        # Clean column names for better display
        merged_data.columns = merged_data.columns.str.replace('_', ' ').str.title()
        
        return merged_data
        
    except FileNotFoundError as e:
        st.error(f"CSV files not found: {e}")
        st.info("Please ensure 'perf_Drop.csv' and 'sub_op.csv' are in the same directory as your app.py")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

def get_fatigue_color(score):
    """Return color based on fatigue score"""
    if score > 2:
        return "🔴"
    elif score > 1:
        return "🟡"
    else:
        return "🟢"

def get_recommendation_color(recommendation):
    """Return color styling for recommendations"""
    colors = {
        'Sub Early': '#ff4444',
        'Monitor': '#ffaa00', 
        'Keep In Game': '#44ff44'
    }
    return colors.get(recommendation, '#666666')

# Load data
data = load_data()

if not data.empty:
    # Dashboard header
    st.title("⚽ Soccer Analytics Dashboard")
    st.markdown("*Data-driven performance analysis using dynamic CSV processing*")
    
    # Sidebar controls
    st.sidebar.header("📊 Dashboard Controls")
    
    # Dynamic filtering options
    unique_recommendations = ['All'] + sorted(data['Sub Recommendation'].unique().tolist())
    unique_positions = ['All'] + sorted(data['Position'].unique().tolist())
    
    # Filters
    top_n = st.sidebar.slider("Show Top N Players", 5, 30, 10)
    selected_recommendation = st.sidebar.selectbox(
        "Filter by Recommendation", 
        unique_recommendations
    )
    selected_position = st.sidebar.selectbox(
        "Filter by Position", 
        unique_positions
    )
    
    # Apply filters
    filtered_data = data.copy()
    
    if selected_recommendation != 'All':
        filtered_data = filtered_data[
            filtered_data['Sub Recommendation'] == selected_recommendation
        ]
    
    if selected_position != 'All':
        filtered_data = filtered_data[
            filtered_data['Position'].str.contains(selected_position, na=False)
        ]
    
    # Get top performers based on overperformance
    top_performers = filtered_data.nlargest(top_n, 'Overperformance')
    
    # Key metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_fatigue = filtered_data['Fatigue Score'].mean()
        st.metric(
            "Average Fatigue Score", 
            f"{avg_fatigue:.2f}",
            delta=f"{avg_fatigue - data['Fatigue Score'].mean():.2f}"
        )
    
    with col2:
        high_fatigue_count = len(filtered_data[filtered_data['Fatigue Score'] > 2])
        st.metric("High Fatigue Players", high_fatigue_count)
    
    with col3:
        sub_recommended = len(filtered_data[filtered_data['Sub Recommendation'] == 'Sub Early'])
        st.metric("Sub Recommendations", sub_recommended)
    
    with col4:
        avg_overperformance = filtered_data['Overperformance'].mean()
        st.metric(
            "Avg Overperformance", 
            f"{avg_overperformance:.3f}",
            delta=f"{avg_overperformance:.3f}"
        )
    
    # Main dashboard layout
    col_left, col_right = st.columns([3, 1])
    
    with col_left:
        st.subheader(f"🎯 Top {top_n} Overperforming Players")
        
        # Interactive bar chart
        fig = px.bar(
            top_performers,
            x='Overperformance',
            y='Player',
            orientation='h',
            color='Fatigue Score',
            color_continuous_scale='RdYlGn_r',
            title=f"Player Overperformance Analysis ({len(top_performers)} players)",
            labels={'Overperformance': 'Overperformance Value', 'Player': 'Player Name'}
        )
        
        fig.update_layout(
            height=max(400, len(top_performers) * 25),
            showlegend=True,
            xaxis_title="Overperformance Value",
            yaxis_title="Player"
        )
        
        # Add hover template
        fig.update_traces(
            hovertemplate="<b>%{y}</b><br>" +
                         "Overperformance: %{x:.4f}<br>" +
                         "Fatigue Score: %{customdata:.2f}<br>" +
                         "<extra></extra>",
            customdata=top_performers['Fatigue Score']
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col_right:
        st.subheader("🚨 Featured Player")
        
        # Highest fatigue player
        if not filtered_data.empty:
            highest_fatigue_player = filtered_data.loc[filtered_data['Fatigue Score'].idxmax()]
            
            fatigue_emoji = get_fatigue_color(highest_fatigue_player['Fatigue Score'])
            
            st.markdown(f"""
            <div class="metric-card">
                <h3>{highest_fatigue_player['Player']}</h3>
                <h1>{fatigue_emoji} {highest_fatigue_player['Fatigue Score']:.2f}</h1>
                <p><strong>Fatigue Score</strong></p>
                <hr style="border-color: rgba(255,255,255,0.3);">
                <p><strong>Position:</strong> {highest_fatigue_player['Position']}</p>
                <p><strong>Minutes:</strong> {highest_fatigue_player['Minutes']:,}</p>
                <p><strong>Overperformance:</strong> {highest_fatigue_player['Overperformance']:.4f}</p>
                <p><strong>Recommendation:</strong> {highest_fatigue_player['Sub Recommendation']}</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Data table section
    st.subheader("📋 Player Performance Analysis")
    
    # Sorting options
    sort_col1, sort_col2 = st.columns(2)
    with sort_col1:
        sort_column = st.selectbox(
            "Sort by:", 
            ['Overperformance', 'Fatigue Score', 'Minutes', 'Actual Impact']
        )
    with sort_col2:
        sort_order = st.radio("Order:", ['Descending', 'Ascending'], horizontal=True)
    
    # Sort data
    ascending = sort_order == 'Ascending'
    display_data = filtered_data.sort_values(sort_column, ascending=ascending)
    
    # Format data for display
    display_columns = [
        'Player', 'Position', 'Minutes', 'Actual Impact', 
        'Predicted Impact', 'Overperformance', 'Fatigue Score', 'Sub Recommendation'
    ]
    
    formatted_data = display_data[display_columns].copy()
    
    # Format numeric columns
    numeric_columns = ['Actual Impact', 'Predicted Impact', 'Overperformance']
    for col in numeric_columns:
        formatted_data[col] = formatted_data[col].apply(lambda x: f"{x:.4f}")
    
    formatted_data['Fatigue Score'] = formatted_data['Fatigue Score'].apply(lambda x: f"{x:.2f}")
    formatted_data['Minutes'] = formatted_data['Minutes'].apply(lambda x: f"{x:,}")
    
    # Display interactive table
    st.dataframe(
        formatted_data,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Player": st.column_config.TextColumn("Player", width="medium"),
            "Position": st.column_config.TextColumn("Position", width="small"),
            "Minutes": st.column_config.TextColumn("Minutes", width="small"),
            "Fatigue Score": st.column_config.TextColumn("Fatigue Score", width="small"),
            "Sub Recommendation": st.column_config.TextColumn("Recommendation", width="medium")
        }
    )
    
    # Download functionality
    st.subheader("📥 Export Data")
    col1, col2 = st.columns(2)
    
    with col1:
        csv_data = formatted_data.to_csv(index=False)
        st.download_button(
            label="📁 Download Filtered Data as CSV",
            data=csv_data,
            file_name=f"soccer_analytics_filtered_{len(formatted_data)}_players.csv",
            mime="text/csv"
        )
    
    with col2:
        full_csv = data.to_csv(index=False)
        st.download_button(
            label="📁 Download Full Dataset as CSV", 
            data=full_csv,
            file_name="soccer_analytics_full_dataset.csv",
            mime="text/csv"
        )
    
    # Summary statistics
    st.subheader("📊 Dataset Summary")
    
    summary_col1, summary_col2 = st.columns(2)
    
    with summary_col1:
        st.write("**Recommendation Distribution:**")
        recommendation_counts = filtered_data['Sub Recommendation'].value_counts()
        
        fig_pie = px.pie(
            values=recommendation_counts.values,
            names=recommendation_counts.index,
            title="Recommendation Distribution"
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with summary_col2:
        st.write("**Fatigue Score Distribution:**")
        
        fig_hist = px.histogram(
            filtered_data,
            x='Fatigue Score',
            nbins=20,
            title="Fatigue Score Distribution"
        )
        fig_hist.add_vline(x=1, line_dash="dash", line_color="yellow", 
                          annotation_text="Moderate Fatigue")
        fig_hist.add_vline(x=2, line_dash="dash", line_color="red", 
                          annotation_text="High Fatigue")
        
        st.plotly_chart(fig_hist, use_container_width=True)

else:
    st.error("❌ No data available. Please check your CSV files.")
    st.info("Expected files: 'perf_Drop.csv' and 'sub_op.csv' in the same directory as app.py")
