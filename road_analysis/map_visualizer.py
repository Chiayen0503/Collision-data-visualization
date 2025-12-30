"""
Map Visualizer Module

Creates interactive maps with collision data visualization.
"""

import folium
import geopandas as gpd
from typing import List, Tuple, Optional


class MapVisualizer:
    """
    Create interactive Folium maps with collision data.
    
    Attributes:
        road_coords (List[Tuple[float, float]]): Road coordinates
        sample_points (gpd.GeoDataFrame): Sample points along road
        collisions (gpd.GeoDataFrame): Collision data to visualize
        map_object (folium.Map): The Folium map object
    """
    
    SEVERITY_COLORS = {
        'Fatal': 'black',
        'Serious': 'red',
        'Slight': 'orange'
    }
    
    def __init__(self, road_coords: List[Tuple[float, float]],
                 sample_points: gpd.GeoDataFrame,
                 collisions: gpd.GeoDataFrame,
                 zoom_start: int = 15):
        """
        Initialize MapVisualizer.
        
        Args:
            road_coords: List of (lon, lat) tuples for the road
            sample_points: GeoDataFrame of sample points
            collisions: GeoDataFrame of collision data
            zoom_start: Initial zoom level for the map
        """
        self.road_coords = road_coords
        self.sample_points = sample_points
        self.collisions = collisions
        self.zoom_start = zoom_start
        self.map_object = None
    
    def create_base_map(self) -> folium.Map:
        """
        Create the base map centered on the road.
        
        Returns:
            Folium Map object
        """
        # Calculate center of road
        center_lat = sum([c[1] for c in self.road_coords]) / len(self.road_coords)
        center_lon = sum([c[0] for c in self.road_coords]) / len(self.road_coords)
        
        self.map_object = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=self.zoom_start
        )
        
        return self.map_object
    
    def add_road_line(self, color: str = "blue", 
                      weight: int = 4, 
                      opacity: float = 0.7):
        """
        Add the road line to the map.
        
        Args:
            color: Line color
            weight: Line width
            opacity: Line opacity
        """
        if self.map_object is None:
            self.create_base_map()
        
        folium.PolyLine(
            locations=[(lat, lon) for lon, lat in self.road_coords],
            color=color,
            weight=weight,
            opacity=opacity,
            tooltip="Road"
        ).add_to(self.map_object)
    
    def add_sample_points(self, radius: int = 3,
                          color: str = "lightblue",
                          opacity: float = 0.4):
        """
        Add sample points to the map.
        
        Args:
            radius: Circle marker radius
            color: Marker color
            opacity: Marker opacity
        """
        if self.map_object is None:
            self.create_base_map()
        
        for i, point in enumerate(self.sample_points.geometry):
            folium.CircleMarker(
                location=[point.y, point.x],
                radius=radius,
                color=color,
                fill=True,
                fill_color=color,
                fill_opacity=opacity,
                tooltip=f"Sample Point {i}"
            ).add_to(self.map_object)
    
    def add_collision_markers(self):
        """Add collision markers with detailed popups to the map."""
        if self.map_object is None:
            self.create_base_map()
        
        for _, row in self.collisions.iterrows():
            # Create detailed popup HTML
            popup_html = self._create_popup_html(row)
            
            # Add marker with color based on severity
            folium.CircleMarker(
                location=[row['latitude'], row['longitude']],
                radius=8,
                color=self.SEVERITY_COLORS.get(row['severity_name'], 'gray'),
                fill=True,
                fill_color=self.SEVERITY_COLORS.get(row['severity_name'], 'gray'),
                fill_opacity=0.7,
                popup=folium.Popup(popup_html, max_width=350),
                tooltip=f"{row['severity_name']} - {row['date']}"
            ).add_to(self.map_object)
    
    def _create_popup_html(self, row) -> str:
        """
        Create HTML content for collision popup.
        
        Args:
            row: DataFrame row containing collision data
            
        Returns:
            HTML string for popup
        """
        return f"""
        <div style="width: 320px; font-family: Arial, sans-serif;">
            <h4 style="margin: 0 0 10px 0; color: #333; border-bottom: 2px solid #ddd; padding-bottom: 5px;">
                Collision Details
            </h4>
            <table style="width: 100%; font-size: 13px; line-height: 1.6;">
                <tr><td style="padding: 3px 5px;"><b>Collision Index:</b></td><td style="padding: 3px 5px;">{row['collision_index']}</td></tr>
                <tr style="background-color: #f5f5f5;"><td style="padding: 3px 5px;"><b>Date:</b></td><td style="padding: 3px 5px;">{row['date']} at {row['time']}</td></tr>
                <tr><td style="padding: 3px 5px;"><b>Location:</b></td><td style="padding: 3px 5px;">({row['latitude']:.6f}, {row['longitude']:.6f})</td></tr>
                <tr style="background-color: #f5f5f5;"><td style="padding: 3px 5px;"><b>Distance from road:</b></td><td style="padding: 3px 5px;">{row['distance_to_road_m']:.3f} km ({row['distance_to_road_m']*1000:.0f} meters)</td></tr>
                <tr><td style="padding: 3px 5px;"><b>Severity:</b></td><td style="padding: 3px 5px;"><span style="color: {self.SEVERITY_COLORS.get(row['severity_name'], 'gray')}; font-weight: bold;">{row['severity_name']}</span></td></tr>
                <tr style="background-color: #f5f5f5;"><td style="padding: 3px 5px;"><b>Vehicles involved:</b></td><td style="padding: 3px 5px;">{int(row['number_of_vehicles'])}</td></tr>
                <tr><td style="padding: 3px 5px;"><b>Casualties:</b></td><td style="padding: 3px 5px;">{int(row['number_of_casualties'])}</td></tr>
                <tr style="background-color: #f5f5f5;"><td style="padding: 3px 5px;"><b>Speed limit:</b></td><td style="padding: 3px 5px;">{int(row['speed_limit'])} mph</td></tr>
                <tr><td style="padding: 3px 5px;"><b>Weather:</b></td><td style="padding: 3px 5px;">{row['weather_name']}</td></tr>
                <tr style="background-color: #f5f5f5;"><td style="padding: 3px 5px;"><b>Light:</b></td><td style="padding: 3px 5px;">{row['light_name']}</td></tr>
            </table>
        </div>
        """
    
    def add_legend(self):
        """Add a legend to the map."""
        if self.map_object is None:
            self.create_base_map()
        
        legend_html = f"""
        <div style="position: fixed; 
             bottom: 50px; right: 50px; width: 220px; height: 160px; 
             background-color: white; border:2px solid grey; z-index:9999; 
             font-size:14px; padding: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.2);">
             <p style="margin: 0 0 10px 0; font-weight: bold; font-size: 15px;">Collision Severity</p>
             <p style="margin: 5px 0;"><span style="color: black; font-size: 18px;">●</span> Fatal</p>
             <p style="margin: 5px 0;"><span style="color: red; font-size: 18px;">●</span> Serious</p>
             <p style="margin: 5px 0;"><span style="color: orange; font-size: 18px;">●</span> Slight</p>
             <hr style="margin: 10px 0; border: 1px solid #ddd;">
             <p style="margin: 5px 0;"><span style="color: lightblue; font-size: 14px;">●</span> Sample Points</p>
             <p style="margin: 5px 0; font-size: 11px; color: #666;">Total: {len(self.collisions)} collisions</p>
        </div>
        """
        
        self.map_object.get_root().html.add_child(folium.Element(legend_html))
    
    def build_map(self) -> folium.Map:
        """
        Build the complete map with all layers.
        
        Returns:
            Complete Folium Map object
        """
        self.create_base_map()
        self.add_road_line()
        self.add_sample_points()
        self.add_collision_markers()
        self.add_legend()
        
        return self.map_object
    
    def save(self, filepath: str):
        """
        Save the map to an HTML file.
        
        Args:
            filepath: Path to save the HTML file
        """
        if self.map_object is None:
            self.build_map()
        
        self.map_object.save(filepath)
        print(f"✅ Map saved to: {filepath}")
