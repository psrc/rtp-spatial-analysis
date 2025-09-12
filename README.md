## Initial Setup
1. Set up your anaconda environment with `conda env create -f environment.yml`

1. Activate it with `conda activate rtp_spatial_analysis`

1. Install _psrcelmerpy_ with `pip install git+https://github.com/psrc/psrcelmerpy.git`

1. In _/configs/config.yaml_, change the `rtp_transit_data_path` value to the appropriate subfolder in your OneDrive.

1. In _/.vscode/launch.json_, change _configurations[args]_ to the full path to your _configs_ folder.

## Development Notes
**Spatial Analysis Needs for RTP**  
The spatial analysis below will be run on the 2035 and 2050 final networks. For initial development, we will use Scenario 2b for 2050.

All scripts should be stored in the following repository: https://github.com/psrc/rtp-spatial-analysis

**Intersection of transit stops and future density**

*Analysis assumptions*  
⦁	1/4 and 1/2 mile circles  
⦁	simple intersect, either in or not  
⦁	by transit route type (Local, All-Day, Frequent, BRT and HCT)  
⦁	number of people and jobs that are in supportive densities with service and in those in supportive densities without service (Gap)  

*Spatial Layers:*  
⦁	C:\Users\username\Puget Sound Regional Council\GIS - Sharing\Projects\Transportation\RTP_2026\transit\Transit_Network_2050_Scenario2b.gdb (stops layer)  
⦁	C:\Users\username\Puget Sound Regional Council\GIS - Sharing\Projects\Transportation\RTP_2026\activity_units\Activity_Units_2026_RTP.gdb (2050 activity unit density)  

*Output:*  
table of values (csv format)  

**Intersection of transit stops and Equity Focus Areas**  

*Analysis assumptions*  
⦁	1/4 and 1/2 mile circles  
⦁	simple intersect, either in or not  
⦁	by transit route type (Local, All-Day, Frequent, BRT and HCT)  
⦁	number of people by efa using the tract EFA %'s to calculate # of people by census block (block pop from parcels * EFA %)  

*Spatial Layers:*  
⦁	C:\Users\username\Puget Sound Regional Council\GIS - Sharing\Projects\Transportation\RTP_2026\transit\Transit_Network_2050_Scenario2b.gdb (stops layer)  
⦁	C:\Users\username\Puget Sound Regional Council\GIS - Sharing\Projects\Transportation\RTP_2026\equity_focus_areas\efa_3groupings_1SD\equity_focus_areas_2023_acs.gdb  
⦁	C:\Users\username\Puget Sound Regional Council\GIS - Sharing\Projects\Transportation\RTP_2026\activity_units\parcel_data.gdb  
⦁	2020 block layer from ElmerGeo  

*Output:*  
table of values (csv format)

**Paratransit Boundaries**

*Analysis assumptions*  
⦁	3/4 mile buffer around transit routes  
⦁	Sounder, ST Express and Ferries should be removed  

*Spatial Layers:*  
⦁	C:\Users\username\Puget Sound Regional Council\GIS - Sharing\Projects\Transportation\RTP_2026\transit\Transit_Network_2050_Scenario2b.gdb (routes layer)  
⦁	C:\Users\username\Puget Sound Regional Council\GIS - Sharing\Projects\Transportation\RTP_2026\equity_focus_areas\efa_3groupings_1SD\equity_focus_areas_2023_acs.gdb  
⦁	C:\Users\username\Puget Sound Regional Council\GIS - Sharing\Projects\Transportation\RTP_2026\activity_units\parcel_data.gdb  
⦁	2020 block layer from ElmerGeo  

*Output:*  
file geodatabase for mapping (route buffered)  
table of values (population in Paratransit Boundary)  

**Frequent Transit Routes and Signals**  

*Analysis assumptions*  
⦁	Intersection of signals (points) with frequent transit routes (polylines)  
⦁	Want to show the status of tsp (transit signal priority)  

*Spatial Layers:*  
⦁	C:\Users\username\Puget Sound Regional Council\GIS - Sharing\Projects\Transportation\RTP_2026\transit\Transit_Network_2050_Scenario2b.gdb (routes layer)  
⦁	C:\Users\username\Puget Sound Regional Council\GIS - Sharing\Projects\Transportation\RTP_2026\its\ITS_Signals_2024_Final.gdb  

*Output:*  
file geodatabase for mapping of signals that are on a frequent transit route or not  
summary table  

**Frequent Transit Routes and Heavy or Severe Congestion** 

*Analysis assumptions*  
⦁	Intersection of frequent transit routes (polylines) with heavy or severe congestion (polylines from model outputs) or just use model output?  

*Spatial Layers:*  
⦁	C:\Users\username\Puget Sound Regional Council\GIS - Sharing\Projects\Transportation\RTP_2026\transit\Transit_Network_2050_Scenario2b.gdb (routes layer)  
⦁	model outputs  

*Output:*  
summary table  

**Heavy or Severe Congestion and Signals**  

*Analysis assumptions*  
⦁	Intersection of signals (points) with heavy or severe congestion (polylines from model outputs)  
⦁	Want to show the status of coordinated or adaptive signals  

*Spatial Layers:*  
⦁	model outputs  
⦁	C:\Users\username\Puget Sound Regional Council\GIS - Sharing\Projects\Transportation\RTP_2026\its\ITS_Signals_2024_Final.gdb  

*Output:*  
file geodatabase for mapping of signals that are on a congested roadways that have coordinated or adaptive signal controls  
summary table  

**Heavy or Severe Congestion and FGTS routes**  

*Analysis assumptions*  
⦁	Intersection of FGTS routes (polylines) with heavy or severe congestion (polylines from model outputs) or just use model output?  
⦁	only need it for FGTS 1 & 2  

*Spatial Layers:*  
⦁	model outputs  
⦁	C:\Users\username\Puget Sound Regional Council\GIS - Sharing\Projects\Transportation\RTP_2026\freight\FGTSWA.gdb  

*Output:*  
summary table  

**Density and Signals**  

*Analysis assumptions*  
⦁	Intersection of signals (points) with activity unit density (polygons)  
⦁	Want to show the status of signals with accessible pedestrian signals  

*Spatial Layers:*  
⦁	C:\Users\username\Puget Sound Regional Council\GIS - Sharing\Projects\Transportation\RTP_2026\transit\Transit_Network_2050_Scenario2b.gdb (routes layer)  
⦁	C:\Users\username\Puget Sound Regional Council\GIS - Sharing\Projects\Transportation\RTP_2026\its\ITS_Signals_2024_Final.gdb  

*Output:*  
file geodatabase for mapping of signals that are in high density areas that have accessible pedestrian signals  
summary table  

**Density and Freight**  

*Analysis assumptions*  
⦁	Intersection of FGTS routes (polylines) with activity unit density (polygons) - 500' buffer?  
⦁	Want to show the growth near Freight activity  

*Spatial Layers:*  
⦁	C:\Users\username\Puget Sound Regional Council\GIS - Sharing\Projects\Transportation\RTP_2026\freight\FGTSWA.gdb  
⦁	C:\Users\username\Puget Sound Regional Council\GIS - Sharing\Projects\Transportation\RTP_2026\activity_units\Activity_Units_2026_RTP.gdb (2050 activity unit density)  

*Output:*  
summary table  

**At-Grade Rail Crossings**  

*Analysis assumptions*  
⦁	Intersection at grade rail crossings (point) with various networks (polylines)  
⦁	FGTS  
⦁	Frequent Transit 
⦁	HIN  
⦁	Congestion  

*Spatial Layers:*  
⦁	C:\Users\username\Puget Sound Regional Council\GIS - Sharing\Projects\Transportation\RTP_2026\freight\FGTSWA.gdb  
⦁	C:\Users\username\Puget Sound Regional Council\GIS - Sharing\Projects\Transportation\RTP_2026\transit\Transit_Network_2050_Scenario2b.gdb (routes layer)  
⦁	C:\Users\username\Puget Sound Regional Council\GIS - Sharing\Projects\Transportation\RTP_2026\safety\high_injury_networks_2024.gdb  
⦁	model network  

*Output:*  
file geodatabase for mapping of crossings with these networks  
summary table  
