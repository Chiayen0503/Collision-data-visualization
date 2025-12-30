"""
Askew Road Collision Analysis Package

A Python package for analyzing traffic collisions along roads using GPS sampling
and UK DfT collision data.

Main features:
- Sample GPS locations along a road at regular intervals
- Find collisions within a specified radius
- Statistical analysis of collision patterns
- Interactive map visualization
"""

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .road_sampler import RoadSampler
from .collision_analyzer import CollisionAnalyzer
from .map_visualizer import MapVisualizer
from .utils import load_collision_data, filter_collisions

__all__ = [
    'RoadSampler',
    'CollisionAnalyzer',
    'MapVisualizer',
    'load_collision_data',
    'filter_collisions'
]
