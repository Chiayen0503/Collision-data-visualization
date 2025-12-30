"""
Road Sampler Module

Handles GPS coordinate sampling along road segments.
"""

import geopandas as gpd
from shapely.geometry import LineString, MultiLineString
from shapely.ops import linemerge
from typing import List, Tuple, Optional, Union


class RoadSampler:
    """
    Sample GPS locations along a road at regular intervals.
    
    Can work with either:
    1. Manual coordinates (list of lon/lat tuples)
    2. OSM data (fetch from OpenStreetMap using area and street name)
    
    Attributes:
        road_coords (List[Tuple[float, float]]): Road coordinates as (lon, lat) tuples
        distance_interval (int): Distance between sample points in meters
        crs (str): Coordinate reference system (default: EPSG:4326)
        from_osm (bool): Whether the road was fetched from OSM
        area_name (str): Area name for OSM fetching
        street_name (str): Street name for OSM fetching
    """
    
    def __init__(self, 
                 road_coords: Optional[List[Tuple[float, float]]] = None,
                 distance_interval: int = 50, 
                 crs: str = "EPSG:4326",
                 area_name: Optional[str] = None,
                 street_name: Optional[str] = None):
        """
        Initialize RoadSampler.
        
        Args:
            road_coords: List of (longitude, latitude) tuples defining the road (manual mode)
            distance_interval: Distance between sample points in meters
            crs: Coordinate reference system
            area_name: Area name for OSM fetching (e.g., "Hammersmith and Fulham, London, UK")
            street_name: Street name for OSM fetching (e.g., "Askew Road")
            
        Note:
            Either provide road_coords OR (area_name AND street_name), not both.
        """
        if road_coords is None and (area_name is None or street_name is None):
            raise ValueError("Must provide either road_coords OR (area_name AND street_name)")
        
        if road_coords is not None and (area_name is not None or street_name is not None):
            raise ValueError("Provide either road_coords OR (area_name AND street_name), not both")
        
        self.road_coords = road_coords
        self.distance_interval = distance_interval
        self.crs = crs
        self.area_name = area_name
        self.street_name = street_name
        self.from_osm = area_name is not None and street_name is not None
        
        self.road_line = None
        self.road_gdf = None
        self.road_projected = None
        self.road_projected_gdf = None
        self.sample_points = None
        self.osm_road_data = None
    
    def fetch_from_osm(self) -> LineString:
        """
        Fetch road geometry from OpenStreetMap.
        
        Returns:
            LineString geometry of the road
            
        Raises:
            ImportError: If osmnx is not installed
            ValueError: If road not found in OSM
        """
        try:
            import osmnx as ox
        except ImportError:
            raise ImportError(
                "OSMnx is required for fetching roads from OpenStreetMap. "
                "Install it with: pip install osmnx"
            )
        
        print(f"Fetching '{self.street_name}' from OpenStreetMap in '{self.area_name}'...")
        
        # Fetch all roads in the area
        roads = ox.features_from_place(self.area_name, tags={"highway": True})
        
        # Filter for the specific street
        filtered_road = roads[roads["name"] == self.street_name]
        
        if filtered_road.empty:
            raise ValueError(
                f"No road found named '{self.street_name}' in '{self.area_name}'"
            )
        
        print(f"Found {len(filtered_road)} segments of {self.street_name}")
        
        # Store the full OSM data for visualization
        self.osm_road_data = filtered_road
        
        # Extract LineString geometries
        linestrings = []
        for geom in filtered_road.geometry:
            if geom.geom_type == 'LineString':
                linestrings.append(geom)
            elif geom.geom_type == 'MultiLineString':
                linestrings.extend(list(geom.geoms))
        
        if not linestrings:
            raise ValueError("No LineString geometries found in the road data")
        
        # Create MultiLineString and merge
        multi_line = MultiLineString(linestrings)
        road_line = linemerge(multi_line)
        
        # Handle disconnected segments
        if road_line.geom_type == 'MultiLineString':
            print("Warning: Road consists of multiple disconnected segments")
            road_line = max(road_line.geoms, key=lambda x: x.length)
            print(f"Working with longest segment")
        
        self.road_line = road_line
        return road_line
    
    def create_road_line(self) -> LineString:
        """
        Create a LineString geometry from road coordinates or fetch from OSM.
        
        Returns:
            LineString geometry of the road
        """
        if self.from_osm:
            return self.fetch_from_osm()
        else:
            self.road_line = LineString(self.road_coords)
            self.road_gdf = gpd.GeoDataFrame(geometry=[self.road_line], crs=self.crs)
            return self.road_line
    
    def project_road(self) -> gpd.GeoDataFrame:
        """
        Project road to UTM for accurate distance measurements.
        
        Returns:
            GeoDataFrame with projected road geometry
        """
        if self.road_line is None:
            self.create_road_line()
        
        # Create GeoDataFrame if not already created (OSM mode creates it)
        if self.road_gdf is None:
            self.road_gdf = gpd.GeoDataFrame(geometry=[self.road_line], crs=self.crs)
        
        self.road_projected_gdf = self.road_gdf.to_crs(
            self.road_gdf.estimate_utm_crs()
        )
        self.road_projected = self.road_projected_gdf.geometry.iloc[0]
        return self.road_projected_gdf
    
    def generate_sample_points(self) -> gpd.GeoDataFrame:
        """
        Sample points along the road at specified intervals.
        
        Returns:
            GeoDataFrame containing sampled points in lat/lon
        """
        if self.road_projected is None:
            self.project_road()
        
        # Generate sample points
        points = [
            self.road_projected.interpolate(d) 
            for d in range(0, int(self.road_projected.length), self.distance_interval)
        ]
        
        # Convert back to lat/lon
        points_gdf = gpd.GeoDataFrame(
            geometry=points, 
            crs=self.road_projected_gdf.crs
        )
        self.sample_points = points_gdf.to_crs(self.crs)
        
        return self.sample_points
    
    def get_road_length(self) -> float:
        """
        Get the length of the road in meters.
        
        Returns:
            Road length in meters
        """
        if self.road_projected is None:
            self.project_road()
        return self.road_projected.length
    
    def get_summary(self) -> dict:
        """
        Get summary statistics of the road sampling.
        
        Returns:
            Dictionary containing summary information
        """
        if self.sample_points is None:
            self.generate_sample_points()
        
        summary = {
            'road_length_m': self.get_road_length(),
            'num_sample_points': len(self.sample_points),
            'distance_interval_m': self.distance_interval,
            'from_osm': self.from_osm
        }
        
        if self.from_osm:
            summary['area_name'] = self.area_name
            summary['street_name'] = self.street_name
            if self.osm_road_data is not None:
                summary['num_osm_segments'] = len(self.osm_road_data)
        else:
            summary['num_road_coords'] = len(self.road_coords)
        
        return summary
