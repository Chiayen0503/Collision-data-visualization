# Road Collision Analysis Tool

A Python package for analyzing traffic collisions along roads using GPS sampling and UK Department for Transport (DfT) collision data. This tool enables comprehensive analysis of collision patterns, including spatial distribution, temporal trends, and environmental factors.

## Features

- **GPS Road Sampling**: Sample GPS locations along roads at regular intervals
- **Collision Detection**: Find collisions within a specified radius of road sample points
- **Statistical Analysis**: Comprehensive analysis of collision patterns including:
  - Severity breakdown (Fatal, Serious, Slight)
  - Temporal analysis (hour of day, day of week)
  - Weather and lighting conditions
  - Distance from road calculations
- **Interactive Visualization**: Create interactive maps with Folium showing:
  - Road geometry
  - Sample points
  - Color-coded collision markers by severity
  - Detailed popup information for each collision
- **Multiple Data Sources**: Support for both manual coordinate input and OpenStreetMap (OSM) data fetching

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Basic Installation

```bash
# Clone or download the repository
cd check_collision_places

# Install required dependencies
pip install -r requirements.txt
```

### Optional: OSM Support

For fetching road data directly from OpenStreetMap:

```bash
pip install osmnx
```

## Required Dependencies

```
pandas>=2.0.0
numpy>=1.24.0
geopy>=2.3.0
geopandas
shapely
folium
```

Optional:
```
osmnx  # For fetching roads from OpenStreetMap
```

## Project Structure

```
check_collision_places/
├── road_analysis/              # Main package directory
│   ├── __init__.py            # Package initialization
│   ├── road_sampler.py        # GPS sampling along roads
│   ├── collision_analyzer.py  # Collision analysis and statistics
│   ├── map_visualizer.py      # Interactive map creation
│   └── utils.py               # Utility functions
├── sample gps along the road.ipynb                    # Tutorial notebook for road sampling
├── collect collision data with multiple roads.ipynb   # Example: Multiple roads analysis
├── requirements.txt           # Python dependencies
├── Askew Road map.html        # Example output map
├── Mile End Road map.html     # Example output map
├── Cobbold Road map.html      # Example output map
└── Stronsa Road map.html      # Example output map
```

## Quick Start

### Method 1: Manual Coordinates

```python
from road_analysis import RoadSampler, CollisionAnalyzer, MapVisualizer
from road_analysis.utils import load_collision_data

# Define road coordinates (longitude, latitude)
road_coords = [
    (-0.2328, 51.5180),
    (-0.2320, 51.5182),
    (-0.2310, 51.5184),
    (-0.2300, 51.5186),
    # ... more coordinates
]

# Sample points along the road
sampler = RoadSampler(road_coords=road_coords, distance_interval=50)
sample_points = sampler.generate_sample_points()

# Load collision data
collisions = load_collision_data('path/to/collision_data.csv')

# Analyze collisions
analyzer = CollisionAnalyzer(
    collisions_gdf=collisions,
    sample_points=sample_points,
    road_line=sampler.road_line,
    radius=50
)
nearby_collisions = analyzer.find_nearby_collisions()
stats = analyzer.calculate_statistics()
analyzer.print_statistics()

# Create interactive map
visualizer = MapVisualizer(road_coords, sample_points, nearby_collisions)
map_obj = visualizer.build_map()
visualizer.save('output_map.html')
```

### Method 2: OpenStreetMap (OSM) Data

```python
from road_analysis import RoadSampler, CollisionAnalyzer, MapVisualizer
from road_analysis.utils import load_collision_data

# Fetch road from OSM
sampler = RoadSampler(
    area_name="Hammersmith and Fulham, London, UK",
    street_name="Askew Road",
    distance_interval=50
)
sample_points = sampler.generate_sample_points()

# Get road coordinates for visualization
road_coords = [(point.x, point.y) for point in sampler.road_line.coords]

# Load and analyze collision data
collisions = load_collision_data('path/to/collision_data.csv')
analyzer = CollisionAnalyzer(collisions, sample_points, sampler.road_line, radius=50)
nearby_collisions = analyzer.find_nearby_collisions()
stats = analyzer.calculate_statistics()

# Create map
visualizer = MapVisualizer(road_coords, sample_points, nearby_collisions)
visualizer.save('askew_road_map.html')
```

## Core Components

### 1. RoadSampler

Handles GPS coordinate sampling along road segments.

**Key Parameters:**
- `road_coords`: List of (longitude, latitude) tuples (manual mode)
- `area_name`: Area name for OSM fetching (e.g., "London, UK")
- `street_name`: Street name for OSM fetching (e.g., "Main Street")
- `distance_interval`: Distance between sample points in meters (default: 50)

**Key Methods:**
- `generate_sample_points()`: Generate GPS sample points along the road
- `get_road_length()`: Get road length in meters
- `get_summary()`: Get summary statistics

### 2. CollisionAnalyzer

Analyzes collision data and calculates comprehensive statistics.

**Key Parameters:**
- `collisions_gdf`: GeoDataFrame containing collision data
- `sample_points`: GeoDataFrame containing road sample points
- `road_line`: Road LineString geometry
- `radius`: Search radius in meters (default: 50)

**Key Methods:**
- `find_nearby_collisions()`: Find collisions within radius
- `calculate_statistics()`: Calculate comprehensive statistics
- `print_statistics()`: Print formatted statistics to console
- `get_export_data()`: Get collision data formatted for export

**Statistics Provided:**
- Total collisions and casualties
- Severity breakdown (Fatal/Serious/Slight)
- Time of day analysis with peak hours
- Day of week patterns
- Weather conditions distribution
- Lighting conditions distribution

### 3. MapVisualizer

Creates interactive Folium maps with collision data visualization.

**Key Parameters:**
- `road_coords`: List of (lon, lat) tuples for the road
- `sample_points`: GeoDataFrame of sample points
- `collisions`: GeoDataFrame of collision data
- `zoom_start`: Initial zoom level (default: 15)

**Key Methods:**
- `build_map()`: Build complete map with all layers
- `save(filepath)`: Save map to HTML file
- `add_road_line()`: Add road geometry to map
- `add_sample_points()`: Add sample points to map
- `add_collision_markers()`: Add collision markers with popups
- `add_legend()`: Add map legend

**Color Coding:**
- 🟢 Light Blue: Sample points
- 🔴 Red: Serious collisions
- 🟠 Orange: Slight collisions
- ⚫ Black: Fatal collisions

### 4. Utility Functions

**load_collision_data(filepath, filter_zero_vehicles=True)**
- Load collision CSV and convert to GeoDataFrame
- Optionally filter out records with zero vehicles

**filter_collisions(collisions_gdf, bounds=None, date_range=None, severity=None)**
- Filter collisions by geographic bounds, date range, or severity

**save_summary_report(analyzer, sampler, output_path)**
- Save detailed text report of analysis

**format_collision_data(data)**
- Format statistics into human-readable summary

## Example Use Cases

### Analyzing a Single Road

```python
from road_analysis import RoadSampler, CollisionAnalyzer
from road_analysis.utils import load_collision_data

# Load collision data
collisions = load_collision_data('collisions.csv')

# Sample road and analyze
sampler = RoadSampler(
    area_name="London, UK",
    street_name="Mile End Road",
    distance_interval=50
)
sample_points = sampler.generate_sample_points()

analyzer = CollisionAnalyzer(collisions, sample_points, sampler.road_line, radius=50)
nearby_collisions = analyzer.find_nearby_collisions()
stats = analyzer.calculate_statistics()

# Print summary
print(f"Road length: {sampler.get_road_length():.0f} meters")
print(f"Sample points: {len(sample_points)}")
print(f"Collisions found: {len(nearby_collisions)}")
analyzer.print_statistics()
```

### Comparing Multiple Roads

```python
roads = {
    'Askew Road': {
        'area': 'Hammersmith and Fulham, London, UK',
        'street': 'Askew Road'
    },
    'Mile End Road': {
        'area': 'Tower Hamlets, London, UK',
        'street': 'Mile End Road'
    }
}

results = {}
for road_name, road_info in roads.items():
    sampler = RoadSampler(
        area_name=road_info['area'],
        street_name=road_info['street'],
        distance_interval=50
    )
    sample_points = sampler.generate_sample_points()
    
    analyzer = CollisionAnalyzer(collisions, sample_points, sampler.road_line, radius=50)
    analyzer.find_nearby_collisions()
    results[road_name] = analyzer.calculate_statistics()
    
    print(f"\n{road_name}:")
    analyzer.print_statistics()
```

### Filtering by Date Range and Severity

```python
from road_analysis.utils import filter_collisions

# Load all collision data
collisions = load_collision_data('collisions.csv')

# Filter for serious and fatal collisions in 2022
filtered_collisions = filter_collisions(
    collisions,
    date_range=('2022-01-01', '2022-12-31'),
    severity=[1, 2]  # 1=Fatal, 2=Serious
)

# Analyze filtered data
analyzer = CollisionAnalyzer(filtered_collisions, sample_points, road_line, radius=50)
analyzer.find_nearby_collisions()
analyzer.print_statistics()
```

## Data Format

### Input Collision Data (CSV)

The collision CSV file should contain the following columns:
- `latitude`: Collision latitude
- `longitude`: Collision longitude
- `collision_index`: Unique collision identifier
- `date`: Date of collision (DD/MM/YYYY format)
- `time`: Time of collision (HH:MM format)
- `collision_severity`: 1=Fatal, 2=Serious, 3=Slight
- `number_of_vehicles`: Number of vehicles involved
- `number_of_casualties`: Number of casualties
- `day_of_week`: 1=Sunday through 7=Saturday
- `weather_conditions`: Weather code (see mapping in code)
- `light_conditions`: Lighting code (see mapping in code)
- `speed_limit`: Speed limit in mph

### Output Data

The tool generates several types of output:

1. **Interactive HTML Maps**: Folium maps with collision markers
2. **Statistics Dictionary**: Python dictionary with comprehensive statistics
3. **Export DataFrame**: Pandas DataFrame with selected collision fields
4. **Text Reports**: Formatted text summaries

## Notebooks

### 1. sample gps along the road.ipynb

Tutorial notebook demonstrating:
- Basic road sampling workflow
- Manual coordinate input
- Point generation and visualization
- Distance calculations

### 2. collect collision data with multiple roads.ipynb

Advanced notebook showing:
- Multiple road analysis
- OSM data fetching
- Comparative statistics
- Batch processing

## Configuration

### Customizing Sample Intervals

```python
# Fine-grained sampling (every 25 meters)
sampler = RoadSampler(road_coords=coords, distance_interval=25)

# Coarse sampling (every 100 meters)
sampler = RoadSampler(road_coords=coords, distance_interval=100)
```

### Adjusting Search Radius

```python
# Small radius (30 meters)
analyzer = CollisionAnalyzer(collisions, sample_points, road_line, radius=30)

# Large radius (100 meters)
analyzer = CollisionAnalyzer(collisions, sample_points, road_line, radius=100)
```

### Map Customization

```python
# Create visualizer with custom zoom
visualizer = MapVisualizer(road_coords, sample_points, collisions, zoom_start=17)

# Build map with custom styling
visualizer.create_base_map()
visualizer.add_road_line(color='red', weight=5, opacity=0.8)
visualizer.add_sample_points(radius=5, color='green', opacity=0.6)
visualizer.add_collision_markers()
visualizer.add_legend()
visualizer.save('custom_map.html')
```

## Troubleshooting

### OSMnx Installation Issues

If you encounter issues installing OSMnx:

```bash
# Using conda (recommended)
conda install -c conda-forge osmnx

# Or with specific versions
pip install osmnx==1.6.0
```

### Road Not Found in OSM

If the street name isn't found:
- Check the spelling and capitalization
- Try a broader area name
- Verify the road exists in OpenStreetMap at openstreetmap.org
- Use manual coordinates as an alternative

### Memory Issues with Large Datasets

For large collision datasets:
- Filter data by geographic bounds first
- Process roads individually
- Use chunked data loading

```python
# Filter to specific geographic area first
bounds = (min_lon, min_lat, max_lon, max_lat)
filtered_collisions = filter_collisions(collisions, bounds=bounds)
```

## Performance Tips

1. **Use appropriate sample intervals**: Smaller intervals increase precision but slow processing
2. **Pre-filter collision data**: Filter by geography and date before analysis
3. **Batch processing**: Analyze multiple roads separately rather than simultaneously
4. **Save intermediate results**: Cache sample points and road geometries

## Data Sources

This tool is designed to work with UK Department for Transport (DfT) road collision data, available from:
- [data.gov.uk](https://data.gov.uk/)
- Road Safety Data portal

Road geometry can be obtained from:
- OpenStreetMap (via OSMnx)
- Manual GPS tracking
- Local authority GIS data

## Contributing

Contributions are welcome! Please ensure:
- Code follows PEP 8 style guidelines
- All functions include docstrings
- New features include example usage
- Tests pass (if implemented)

## License

This project is provided as-is for educational and research purposes.

## Author

For questions or issues, please contact the package maintainer.

## Acknowledgments

- UK Department for Transport for collision data
- OpenStreetMap contributors for road geometry data
- Folium, GeoPandas, and OSMnx development teams

## Version History

- **v1.0.0**: Initial release
  - GPS road sampling
  - Collision analysis with statistics
  - Interactive map visualization
  - OSM integration support
