# current

current is a storm-related outage preparedness and utility restoration planning prototype built for the AEP HackOHI/O challenge.

## Resident experience
- Household outage estimates distinguished from circuit-wide expected impact.
- Open-Meteo forecasts, an interactive map and recorded upstream power connections.
- Backup battery runtime, personalized preparation and accessibility settings.
- Local Ollama explanations; trusted contact storage and direct dial links.
- Limited offline access to previously loaded maps, forecasts and prediction snapshots.
- Android companion application.

## Utility planning
Equipment inspection views, manual assignment of nine organizer-provided reference drawings, resource and damage scenarios, restoration sequence comparisons and task exports.

## Methods and limitations
Published-parameter wind fragility and LiDAR-derived tree exposure inform engineering scenarios connected to recorded customer dependencies. AEP labor references support restoration simulation. Terrain provides context; it has no validated numerical risk multiplier. Probabilities are not locally calibrated, and restoration ranges are not official AEP estimates. Notification drafts do not send SMS/email. Trusted contacts stay on the device.

Twenty controlled ablation scenarios explore tree and wind-direction sensitivity; they do not establish real-world predictive accuracy. See reports/ablation/.

## Running
Requires Python dependencies, the separately supplied challenge dataset and generated private data artifacts. See REPRODUCE.md and the preparation scripts. Run `python server.py` and visit http://127.0.0.1:8765/. Ollama is optional and runs locally on port 11434.

## Data distribution
This source package excludes the local Python environment, original challenge data, private/generated network data, large recordings and derived map/topology payloads. It is not a self-contained data distribution; those files remain on the development machine. The original project was not deleted or moved.

## References
- AEP HackOHI/O challenge data and labor workbook.
- Roanoke Trees 3D: https://services.arcgis.com/jIL9msH9OI208GCb/arcgis/rest/services/Roanoke_Trees_3D/FeatureServer/0
- USGS 3DEP: https://elevation.nationalmap.gov/arcgis/rest/services/3DEPElevation/ImageServer
- Hou and Muraleetharan (2023), DOI: https://doi.org/10.1007/s13753-023-00478-x
- Open-Meteo, OpenStreetMap contributors and OpenFreeMap; retain applicable attribution and licenses.
