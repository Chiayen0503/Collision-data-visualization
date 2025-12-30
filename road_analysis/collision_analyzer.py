"""
Collision Analyzer Module

Analyzes collision data and calculates statistics.
"""

import pandas as pd
import geopandas as gpd
from typing import Dict, List, Tuple


class CollisionAnalyzer:
    """
    Analyze collision data within a specified radius of road sample points.
    
    Attributes:
        collisions_gdf (gpd.GeoDataFrame): Collision data as GeoDataFrame
        sample_points (gpd.GeoDataFrame): Road sample points
        radius (float): Search radius in meters
        nearby_collisions (gpd.GeoDataFrame): Filtered collisions within radius
    """
    
    # Mapping dictionaries
    SEVERITY_MAP = {1: 'Fatal', 2: 'Serious', 3: 'Slight'}
    DAY_MAP = {
        1: 'Sunday', 2: 'Monday', 3: 'Tuesday', 4: 'Wednesday',
        5: 'Thursday', 6: 'Friday', 7: 'Saturday'
    }
    WEATHER_MAP = {
        1: 'Fine no high winds',
        2: 'Raining no high winds',
        3: 'Snowing no high winds',
        4: 'Fine + high winds',
        5: 'Raining + high winds',
        6: 'Snowing + high winds',
        7: 'Fog or mist',
        8: 'Other',
        9: 'Unknown',
        -1: 'Data missing'
    }
    LIGHT_MAP = {
        1: 'Daylight',
        4: 'Darkness - lights lit',
        5: 'Darkness - lights unlit',
        6: 'Darkness - no lighting',
        7: 'Darkness - lighting unknown',
        -1: 'Data missing'
    }
    
    def __init__(self, collisions_gdf: gpd.GeoDataFrame, 
                 sample_points: gpd.GeoDataFrame,
                 road_line,
                 radius: float = 50):
        """
        Initialize CollisionAnalyzer.
        
        Args:
            collisions_gdf: GeoDataFrame containing collision data
            sample_points: GeoDataFrame containing road sample points
            road_line: Road line geometry for distance calculation
            radius: Search radius in meters
        """
        self.collisions_gdf = collisions_gdf
        self.sample_points = sample_points
        self.road_line = road_line
        self.radius = radius
        self.nearby_collisions = None
        self.statistics = {}
    
    def find_nearby_collisions(self) -> gpd.GeoDataFrame:
        """
        Find all collisions within radius of sample points.
        
        Returns:
            GeoDataFrame containing nearby collisions
        """
        # Get UTM CRS from sample points
        utm_crs = self.sample_points.estimate_utm_crs()
        
        # Project data
        collisions_projected = self.collisions_gdf.to_crs(utm_crs)
        sample_points_projected = self.sample_points.to_crs(utm_crs)
        road_projected_gdf = gpd.GeoDataFrame(
            geometry=[self.road_line], 
            crs=self.sample_points.crs
        ).to_crs(utm_crs)
        road_projected = road_projected_gdf.geometry.iloc[0]
        
        # Find collisions within radius
        nearby_indices = set()
        
        for _, sample_point in sample_points_projected.iterrows():
            distances = collisions_projected.geometry.distance(sample_point.geometry)
            within_radius = distances[distances <= self.radius].index
            nearby_indices.update(within_radius)
        
        # Get unique collisions
        self.nearby_collisions = self.collisions_gdf.loc[list(nearby_indices)].copy()
        
        # Calculate distance from each collision to road
        nearby_collisions_proj = self.nearby_collisions.to_crs(utm_crs)
        distances_to_road = []
        
        for _, collision in nearby_collisions_proj.iterrows():
            dist = collision.geometry.distance(road_projected)
            distances_to_road.append(dist)
        
        self.nearby_collisions['distance_to_road_m'] = distances_to_road
        
        # Add mapped columns
        self._add_mapped_columns()
        
        return self.nearby_collisions
    
    def _add_mapped_columns(self):
        """Add human-readable mapped columns to collision data."""
        self.nearby_collisions['severity_name'] = \
            self.nearby_collisions['collision_severity'].map(self.SEVERITY_MAP)
        self.nearby_collisions['day_name'] = \
            self.nearby_collisions['day_of_week'].map(self.DAY_MAP)
        self.nearby_collisions['weather_name'] = \
            self.nearby_collisions['weather_conditions'].map(self.WEATHER_MAP)
        self.nearby_collisions['light_name'] = \
            self.nearby_collisions['light_conditions'].map(self.LIGHT_MAP)
        self.nearby_collisions['hour'] = \
            self.nearby_collisions['time'].str.split(':').str[0].astype(int)
    
    def calculate_statistics(self) -> Dict:
        """
        Calculate comprehensive statistics about collisions.
        
        Returns:
            Dictionary containing statistical analysis
        """
        if self.nearby_collisions is None:
            self.find_nearby_collisions()
        
        total_collisions = len(self.nearby_collisions)
        total_casualties = self.nearby_collisions['number_of_casualties'].sum()
        
        # Basic statistics
        self.statistics['summary'] = {
            'total_collisions': total_collisions,
            'total_casualties': int(total_casualties),
            'avg_casualties_per_collision': total_casualties / total_collisions if total_collisions > 0 else 0,
            'collisions_per_sample_point': total_collisions / len(self.sample_points)
        }
        
        # Severity breakdown
        severity_counts = self.nearby_collisions['severity_name'].value_counts()
        self.statistics['severity'] = {
            severity: {
                'count': int(count),
                'percentage': (count / total_collisions) * 100
            }
            for severity, count in severity_counts.items()
        }
        
        # Time analysis
        hour_counts = self.nearby_collisions['hour'].value_counts().sort_index()
        most_common_hour = self.nearby_collisions['hour'].mode()[0] if len(self.nearby_collisions) > 0 else None
        
        time_ranges = {
            'Night (00-06)': (0, 6),
            'Morning Rush (07-09)': (7, 9),
            'Midday (10-15)': (10, 15),
            'Evening Rush (16-18)': (16, 18),
            'Evening (19-23)': (19, 23)
        }
        
        time_distribution = {}
        for time_range, (start, end) in time_ranges.items():
            count = len(self.nearby_collisions[
                (self.nearby_collisions['hour'] >= start) & 
                (self.nearby_collisions['hour'] <= end)
            ])
            time_distribution[time_range] = {
                'count': count,
                'percentage': (count / total_collisions) * 100 if total_collisions > 0 else 0
            }
        
        self.statistics['time'] = {
            'most_common_hour': int(most_common_hour) if most_common_hour is not None else None,
            'hour_counts': hour_counts.to_dict(),
            'time_distribution': time_distribution
        }
        
        # Day of week
        day_counts = self.nearby_collisions['day_name'].value_counts()
        self.statistics['day_of_week'] = {
            day: {
                'count': int(count),
                'percentage': (count / total_collisions) * 100
            }
            for day, count in day_counts.items()
        }
        
        # Weather conditions
        weather_counts = self.nearby_collisions['weather_name'].value_counts()
        self.statistics['weather'] = {
            weather: {
                'count': int(count),
                'percentage': (count / total_collisions) * 100
            }
            for weather, count in weather_counts.items()
        }
        
        # Light conditions
        light_counts = self.nearby_collisions['light_name'].value_counts()
        self.statistics['light'] = {
            light: {
                'count': int(count),
                'percentage': (count / total_collisions) * 100
            }
            for light, count in light_counts.items()
        }
        
        return self.statistics
    
    def print_statistics(self):
        """Print formatted statistics to console."""
        if not self.statistics:
            self.calculate_statistics()
        
        stats = self.statistics
        
        print("\n" + "=" * 80)
        print("COLLISION ANALYSIS STATISTICS")
        print("=" * 80)
        
        print("\n📊 SUMMARY:")
        for key, value in stats['summary'].items():
            print(f"   {key.replace('_', ' ').title()}: {value:.2f}")
        
        print("\n🚨 SEVERITY:")
        for severity, data in stats['severity'].items():
            print(f"   {severity}: {data['count']} ({data['percentage']:.1f}%)")
        
        print("\n🕐 TIME ANALYSIS:")
        print(f"   Most Common Hour: {stats['time']['most_common_hour']}:00")
        for time_range, data in stats['time']['time_distribution'].items():
            print(f"   {time_range}: {data['count']} ({data['percentage']:.1f}%)")
        
        print("\n📅 DAY OF WEEK:")
        for day, data in stats['day_of_week'].items():
            print(f"   {day}: {data['count']} ({data['percentage']:.1f}%)")
        
        print("\n🌤️ WEATHER:")
        for weather, data in list(stats['weather'].items())[:5]:
            print(f"   {weather}: {data['count']} ({data['percentage']:.1f}%)")
        
        print("\n💡 LIGHT CONDITIONS:")
        for light, data in stats['light'].items():
            print(f"   {light}: {data['count']} ({data['percentage']:.1f}%)")
    
    def get_export_data(self) -> pd.DataFrame:
        """
        Get collision data formatted for export.
        
        Returns:
            DataFrame with selected columns for export
        """
        if self.nearby_collisions is None:
            self.find_nearby_collisions()
        
        export_cols = [
            'collision_index', 'date', 'time', 'latitude', 'longitude',
            'distance_to_road_m', 'severity_name', 'number_of_vehicles',
            'number_of_casualties', 'speed_limit', 'weather_name',
            'light_name', 'day_name', 'hour'
        ]
        
        return self.nearby_collisions[export_cols].copy().sort_values('date')
