import os
import requests
from datetime import datetime, timedelta
import xarray as xr
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import numpy as np

# --- Clean up old files in grib_files and static/2mtemp directories ---
for folder in [os.path.join("Hrrr", "grib_files"), os.path.join("Hrrr", "static", "2mtemp")]:
    if os.path.exists(folder):
        for f in os.listdir(folder):
            file_path = os.path.join(folder, f)
            if os.path.isfile(file_path):
                os.remove(file_path)

# Directories
base_url = "https://nomads.ncep.noaa.gov/cgi-bin/filter_hrrr_2d.pl"
output_dir = "Hrrr"
grib_dir = os.path.join(output_dir, "grib_files")
temp2m_dir = os.path.join(output_dir, "static", "2mtemp")
os.makedirs(grib_dir, exist_ok=True)
os.makedirs(temp2m_dir, exist_ok=True)

# Get the current UTC date and time and subtract 6 hours
current_utc_time = datetime.utcnow() - timedelta(hours=6)
date_str = current_utc_time.strftime("%Y%m%d")
hour_str = str(current_utc_time.hour // 6 * 6).zfill(2)  # Adjust to nearest 6-hour slot

variable_tmp = "TMP"

# Custom colormap for temperature
custom_cmap = LinearSegmentedColormap.from_list(
    "custom_cmap",
    ["darkblue", "blue", "lightblue", "green", "yellow", "orange", "red"]
)

# Function to download GRIB files
def download_file(hour_str, step):
    file_name = f"hrrr.t{hour_str}z.wrfsfcf{step:02d}.grib2"
    file_path = os.path.join(grib_dir, file_name)
    url_tmp = (f"{base_url}?dir=%2Fhrrr.{date_str}%2Fconus&file={file_name}"
               f"&var_{variable_tmp}=on&lev_2_m_above_ground=on")
    response = requests.get(url_tmp, stream=True)
    if response.status_code == 200:
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        print(f"Downloaded {file_name}")
        return file_path
    else:
        print(f"Failed to download {file_name} (Status Code: {response.status_code})")
        return None

# Function to generate a clean PNG from GRIB file (no map features)
def generate_clean_png(file_path, step):
    ds = xr.open_dataset(file_path, engine="cfgrib")
    data = ds['t2m'].values - 273.15  # Kelvin to Celsius

    # Adjust extent to fit Leaflet's default USA bounds
    leaflet_extent = [-125, -66.5, 24.5, 49.5]  # [west, east, south, north]
    fig, ax = plt.subplots(figsize=(10, 7), dpi=150)
    img = ax.imshow(
        data.squeeze(),
        cmap=custom_cmap,
        extent=leaflet_extent,
        origin='lower',
        interpolation='bilinear',
        aspect='auto'
    )
    ax.set_xlim(leaflet_extent[0], leaflet_extent[1])
    ax.set_ylim(leaflet_extent[2], leaflet_extent[3])
    ax.set_axis_off()
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
    png_path = os.path.join(temp2m_dir, f"2mtemp_{step:02d}.png")
    plt.savefig(png_path, bbox_inches='tight', pad_inches=0, transparent=True)
    plt.close(fig)
    print(f"Generated clean PNG: {png_path}")
    return png_path

# Main process: Download and plot
grib_files = []
png_files = []
for step in range(0, 49):  # Loop through forecast steps (00 to 48 hours)
    grib_file = download_file(hour_str, step)
    if grib_file:
        grib_files.append(grib_file)
        png_file = generate_clean_png(grib_file, step)
        png_files.append(png_file)

print("All GRIB file download and PNG creation tasks complete!")
