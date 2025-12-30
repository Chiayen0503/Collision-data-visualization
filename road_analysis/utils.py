"""
Utility Functions

Helper functions for data loading and processing.
"""

import pandas as pd
import geopandas as gpd
from typing import Optional
import numpy as np


def load_collision_data(filepath: str, 
                       filter_zero_vehicles: bool = True) -> gpd.GeoDataFrame:
    """
    Load collision data from CSV file and convert to GeoDataFrame.
    
    Args:
        filepath: Path to the collision CSV file
        filter_zero_vehicles: If True, filter out collisions with 0 vehicles
        
    Returns:
        GeoDataFrame containing collision data
    """
    print(f"Loading collision data from {filepath}...")
    
    # Load CSV
    df = pd.read_csv(filepath, low_memory=False)
    print(f"Total collisions loaded: {len(df):,}")
    
    # Filter out zero vehicle collisions if requested
    if filter_zero_vehicles:
        df = df[df['number_of_vehicles'] > 0]
        print(f"After filtering (vehicles > 0): {len(df):,}")
    
    # Convert to GeoDataFrame
    gdf = gpd.GeoDataFrame(
        df,
        geometry=gpd.points_from_xy(df.longitude, df.latitude),
        crs="EPSG:4326"
    )
    
    return gdf


def filter_collisions(collisions_gdf: gpd.GeoDataFrame,
                     bounds: Optional[tuple] = None,
                     date_range: Optional[tuple] = None,
                     severity: Optional[list] = None) -> gpd.GeoDataFrame:
    """
    Filter collision data by various criteria.
    
    Args:
        collisions_gdf: GeoDataFrame containing collision data
        bounds: Tuple of (min_lon, min_lat, max_lon, max_lat) to filter by
        date_range: Tuple of (start_date, end_date) as strings
        severity: List of severity values to include (1=Fatal, 2=Serious, 3=Slight)
        
    Returns:
        Filtered GeoDataFrame
    """
    filtered = collisions_gdf.copy()
    
    # Filter by bounds
    if bounds:
        min_lon, min_lat, max_lon, max_lat = bounds
        filtered = filtered[
            (filtered.longitude >= min_lon) &
            (filtered.longitude <= max_lon) &
            (filtered.latitude >= min_lat) &
            (filtered.latitude <= max_lat)
        ]
        print(f"After bounds filter: {len(filtered):,} collisions")
    
    # Filter by date range
    if date_range:
        start_date, end_date = date_range
        filtered['date_parsed'] = pd.to_datetime(filtered['date'], format='%d/%m/%Y')
        filtered = filtered[
            (filtered.date_parsed >= start_date) &
            (filtered.date_parsed <= end_date)
        ]
        filtered = filtered.drop('date_parsed', axis=1)
        print(f"After date filter: {len(filtered):,} collisions")
    
    # Filter by severity
    if severity:
        filtered = filtered[filtered['collision_severity'].isin(severity)]
        print(f"After severity filter: {len(filtered):,} collisions")
    
    return filtered


def save_summary_report(analyzer, sampler, output_path: str):
    """
    Save a text summary report of the analysis.
    
    Args:
        analyzer: CollisionAnalyzer object with calculated statistics
        sampler: RoadSampler object with road information
        output_path: Path to save the summary file
    """
    from datetime import datetime
    
    stats = analyzer.statistics
    road_info = sampler.get_summary()
    
    with open(output_path, 'w') as f:
        f.write("=" * 80 + "\n")
        f.write("ROAD COLLISION ANALYSIS SUMMARY\n")
        f.write("=" * 80 + "\n\n")
        
        f.write(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Search Radius: {analyzer.radius} meters\n")
        f.write(f"Sample Points: {road_info['num_sample_points']}\n")
        f.write(f"Road Length: {road_info['road_length_m']:.0f} meters\n\n")
        
        f.write("SUMMARY STATISTICS\n")
        f.write("-" * 80 + "\n")
        for key, value in stats['summary'].items():
            f.write(f"{key.replace('_', ' ').title()}: {value:.2f}\n")
        
        f.write("\nSEVERITY BREAKDOWN\n")
        f.write("-" * 80 + "\n")
        for severity, data in stats['severity'].items():
            f.write(f"{severity}: {data['count']} ({data['percentage']:.1f}%)\n")
        
        f.write("\nTIME ANALYSIS\n")
        f.write("-" * 80 + "\n")
        if stats['time']['most_common_hour']:
            f.write(f"Most Common Hour: {stats['time']['most_common_hour']}:00\n\n")
        for time_range, data in stats['time']['time_distribution'].items():
            f.write(f"{time_range}: {data['count']} ({data['percentage']:.1f}%)\n")
        
        f.write("\nDAY OF WEEK BREAKDOWN\n")
        f.write("-" * 80 + "\n")
        for day, data in stats['day_of_week'].items():
            f.write(f"{day}: {data['count']} ({data['percentage']:.1f}%)\n")
        
        f.write("\nWEATHER CONDITIONS\n")
        f.write("-" * 80 + "\n")
        for weather, data in list(stats['weather'].items())[:5]:
            f.write(f"{weather}: {data['count']} ({data['percentage']:.1f}%)\n")
        
        f.write("\nLIGHT CONDITIONS\n")
        f.write("-" * 80 + "\n")
        for light, data in stats['light'].items():
            f.write(f"{light}: {data['count']} ({data['percentage']:.1f}%)\n")
    
    print(f"✅ Summary report saved to: {output_path}")


def get_road_coordinates(road_name: str) -> list:
    """
    Get predefined coordinates for known roads.
    
    Args:
        road_name: Name of the road
        
    Returns:
        List of (lon, lat) coordinate tuples
    """
    # Predefined road coordinates
    ROAD_COORDS = {
        'askew_road': [
            (-0.2328, 51.5180),
            (-0.2320, 51.5182),
            (-0.2310, 51.5184),
            (-0.2300, 51.5186),
            (-0.2290, 51.5188),
            (-0.2280, 51.5190),
            (-0.2270, 51.5192),
            (-0.2260, 51.5194),
            (-0.2250, 51.5196),
            (-0.2240, 51.5198),
            (-0.2230, 51.5200),
            (-0.2220, 51.5202),
            (-0.2210, 51.5204),
            (-0.2200, 51.5206),
            (-0.2190, 51.5208),
            (-0.2180, 51.5210),
        ]
    }
    
    road_key = road_name.lower().replace(' ', '_')
    
    if road_key in ROAD_COORDS:
        return ROAD_COORDS[road_key]
    else:
        raise ValueError(f"No coordinates found for road: {road_name}")



import numpy as np

def format_collision_data(data):
    """
    Extract and format collision data into human-readable information.
    
    Args:
        data: Dictionary containing collision statistics
    
    Returns:
        Formatted string with collision summary
    """
    
    # 1) Total number of collisions
    total_collisions = data['summary']['total_collisions']
    
    # 2) Total casualties
    total_casualties = data['summary']['total_casualties']
    
    # 3) Severity percentages
    severity = data['severity']
    slight_pct = severity.get('Slight', {}).get('percentage', 0)
    serious_pct = severity.get('Serious', {}).get('percentage', 0)
    fatal_pct = severity.get('Fatal', {}).get('percentage', 0)
    
    # 4) Most common hour
    most_common_hour = data['time']['most_common_hour']
    # Convert 24-hour format to readable format
    hour_12 = most_common_hour % 12
    hour_12 = 12 if hour_12 == 0 else hour_12
    am_pm = "AM" if most_common_hour < 12 else "PM"
    hour_readable = f"{hour_12}:00 {am_pm} ({most_common_hour}:00)"
    
    # 5) Most common weekday
    day_of_week = data['day_of_week']
    most_common_day = max(day_of_week.items(), key=lambda x: x[1]['count'])
    day_name = most_common_day[0]
    day_percentage = most_common_day[1]['percentage']
    
    # 6) Most common weather
    weather = data['weather']
    most_common_weather = max(weather.items(), key=lambda x: x[1]['count'])
    weather_condition = most_common_weather[0]
    weather_percentage = most_common_weather[1]['percentage']
    
    # 7) Most common light condition
    light = data['light']
    most_common_light = max(light.items(), key=lambda x: x[1]['count'])
    light_condition = most_common_light[0]
    light_percentage = most_common_light[1]['percentage']
    
    # Format output
    output = f"""
{'='*60}
COLLISION DATA SUMMARY
{'='*60}

1) Total number of collisions: {total_collisions}

2) Total casualties: {total_casualties}

3) Severity breakdown:
   - Slight: {slight_pct:.2f}%
   - Serious: {serious_pct:.2f}%
   - Fatal: {fatal_pct:.2f}%

4) Most common hour: {hour_readable}

5) Most common weekday: {day_name} ({day_percentage:.2f}% of collisions)

6) Most common weather: {weather_condition} ({weather_percentage:.2f}% of collisions)

7) Most common light condition: {light_condition} ({light_percentage:.2f}% of collisions)

{'='*60}
"""
    
    return output