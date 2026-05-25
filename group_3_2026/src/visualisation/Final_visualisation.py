import matplotlib.pyplot as plt
import base64
from io import BytesIO
import runpy
import os
import webbrowser

# ==========================================
# 1. SETUP THE HIJACK
# ==========================================
# We will store the HTML image tags here
html_plots = []

def silent_show(*args, **kwargs):
    """
    This function intercepts plt.show().
    Instead of opening a window, it grabs all open figures, 
    converts them to HTML, and closes them.
    """
    # plt.get_fignums() gets all the plots created since the last show()
    for i in plt.get_fignums():
        fig = plt.figure(i)
        
        # Convert to base64
        buf = BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight")
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode("utf-8")
        
        # Create HTML tag
        html_tag = f'<div class="plot-container" style="text-align: center; margin-bottom: 40px;"><img src="data:image/png;base64,{img_base64}" style="max-width: 100%; height: auto; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);"></div>'
        html_plots.append(html_tag)
    
    # Close all intercepted plots so they don't pop up on screen
    plt.close('all')

# OVERRIDE: Replace standard matplotlib show() with our silent one
plt.show = silent_show

# ==========================================
# 2. RUN TEAMMATES' SCRIPTS
# ==========================================
# Get the directory where this visualization script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Define the paths to their scripts relative to this file's location
# 
#os.path.join(script_dir, "../demand/residual_demand_FP/residual_demand_france.py"),
#os.path.join(script_dir, "../demand/residual_demand_FP/residual_demand_germany.py"),
# os.path.join(script_dir, "../demand/residual_demand_FP/residual_demand_spain.py"),
scripts_to_run = [
    os.path.join(script_dir, "../demand/demand_peaks_GB/demand_picks.py"),
    os.path.join(script_dir, "../demand/demand_ramps_PM/demand_ramps.py"),
    os.path.join(script_dir, "../demand/flexibility_index_LS/flexibility_index.py"),
    os.path.join(script_dir, "../demand/variability AP/variability.py")
]

print("Executing teammates' scripts and capturing plots...\n")

for script in scripts_to_run:
    if os.path.exists(script):
        print(f"--> Running {os.path.basename(script)}...")
        # runpy runs the file exactly as if you typed `python script.py` in the terminal
        runpy.run_path(script)
    else:
        print(f"WARNING: Could not find {script}")

# ==========================================
# 3. GENERATE THE HTML DASHBOARD
# ==========================================
print("\nBuilding HTML Dashboard...")

html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Electrical Demand Analysis</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f7f6; color: #333; margin: 0; padding: 20px; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); }
        h1 { text-align: center; color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; margin-bottom: 40px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Combined Electrical Demand Analysis</h1>
"""

# Insert all the plots we captured
for plot_html in html_plots:
    html_content += plot_html

html_content += """
    </div>
</body>
</html>
"""

# Save in the same folder as this script
output_filename = os.path.join(script_dir, "final_dashboard.html")

with open(output_filename, "w", encoding="utf-8") as file:
    file.write(html_content)

print(f"\nSuccess! Report generated as: {output_filename}")

# Auto-open the HTML file in your web browser
webbrowser.open(f"file://{output_filename}")