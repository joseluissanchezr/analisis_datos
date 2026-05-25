import pandas as pd
import matplotlib.pyplot as plt
import base64
from io import BytesIO
import os
import webbrowser

# ==========================================
# 1. DATA LOADING
# ==========================================
# Adjust these paths if Final_visualisation.py is in a different relative location

base_path = "group_3_2026/src/data/processed/"

try:
    df_fr = pd.read_csv(f"{base_path}france_cleaned.csv")
    df_de = pd.read_csv(f"{base_path}germany_cleaned.csv")
    df_es = pd.read_csv(f"{base_path}spain_cleaned.csv")

    for df in [df_fr, df_de, df_es]:
        df["datetime"] = pd.to_datetime(df["datetime"])
except FileNotFoundError:
    print("Data files not found. Please ensure you are running this script from the correct directory.")
    # For testing purposes, you might want to create dummy data here if paths fail

# ==========================================
# 2. HELPER FUNCTIONS
# ==========================================
def find_local_maxima(df, value_col="demand_mwh"):
    """Detects local maxima in the demand data."""
    df = df.sort_values("datetime").reset_index(drop=True)
    local_maxima = df[
        (df[value_col] > df[value_col].shift(1)) &
        (df[value_col] > df[value_col].shift(-1))
    ]
    return local_maxima

def fig_to_base64(fig):
    """Converts a matplotlib figure to a base64 encoded HTML img tag."""
    buf = BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode("utf-8")
    plt.close(fig) # Close the figure to free up memory
    return f'<img src="data:image/png;base64,{img_base64}" alt="Data Plot" style="max-width: 100%; height: auto; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); margin-bottom: 20px;">'

# ==========================================
# 3. PLOTTING FUNCTIONS
# ==========================================
def create_peaks_plot(df, country):
    """Generates the peaks plot and returns the matplotlib figure."""
    df = df.sort_values("datetime").reset_index(drop=True)
    global_peak_idx = df["demand_mwh"].idxmax()
    local_maxima = find_local_maxima(df)

    # Use plt.subplots() to keep track of the specific figure
    fig, ax = plt.subplots(figsize=(14, 5))

    ax.plot(df["datetime"], df["demand_mwh"], label="Demand", color="blue")
    
    ax.scatter(local_maxima["datetime"], local_maxima["demand_mwh"], 
               color="green", s=25, label="Local maxima", zorder=4)
               
    ax.scatter(df.loc[global_peak_idx, "datetime"], df.loc[global_peak_idx, "demand_mwh"], 
               color="red", s=80, label="Global maximum", zorder=5)

    ax.set_title(f"Demand Peaks - {country}")
    ax.set_xlabel("Date")
    ax.set_ylabel("Demand (MWh)")
    ax.legend()
    fig.tight_layout()
    
    return fig

# --- PLACEHOLDERS FOR TEAMMATES' FUNCTIONS ---
# Import their functions here or paste them. Make sure they return a 'fig' object.
# Example: 
# from demand_ramps_PM.demand_ramps import create_ramps_plot

def create_placeholder_plot(title):
    """A temporary function until other metrics are added."""
    fig, ax = plt.subplots(figsize=(14, 3))
    ax.text(0.5, 0.5, f"{title} Plot Coming Soon", ha='center', va='center', fontsize=14)
    ax.axis('off')
    return fig

# ==========================================
# 4. HTML GENERATION
# ==========================================
def generate_html_report():
    print("Generating plots and building HTML report...")
    
    countries = {
        "France": df_fr,
        "Germany": df_de,
        "Spain": df_es
    }

    # Start building the HTML string with some basic CSS for a clean look
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
            h1 { text-align: center; color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }
            h2 { color: #2980b9; margin-top: 40px; border-left: 4px solid #3498db; padding-left: 10px; }
            h3 { color: #34495e; }
            .plot-container { text-align: center; margin-bottom: 40px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Electrical Demand Analysis Report</h1>
            <p style="text-align: center;">Comparative analysis of France, Germany, and Spain.</p>
    """

    for country_name, df in countries.items():
        html_content += f"<h2>{country_name} Analysis</h2>"
        
        # 1. Peaks
        html_content += f"<h3>Demand Peaks</h3>"
        fig_peaks = create_peaks_plot(df, country_name)
        html_content += f"<div class='plot-container'>{fig_to_base64(fig_peaks)}</div>"
        
        # 2. Ramps (Plug in your teammate's function here)
        html_content += f"<h3>Demand Ramps</h3>"
        fig_ramps = create_placeholder_plot(f"Ramps - {country_name}")
        html_content += f"<div class='plot-container'>{fig_to_base64(fig_ramps)}</div>"

        # 3. Flexibility Index
        html_content += f"<h3>Flexibility Index</h3>"
        fig_flex = create_placeholder_plot(f"Flexibility - {country_name}")
        html_content += f"<div class='plot-container'>{fig_to_base64(fig_flex)}</div>"
        
        # 4. Residual Demand
        html_content += f"<h3>Residual Demand</h3>"
        fig_res = create_placeholder_plot(f"Residual Demand - {country_name}")
        html_content += f"<div class='plot-container'>{fig_to_base64(fig_res)}</div>"
        
        # 5. Variability
        html_content += f"<h3>Variability</h3>"
        fig_var = create_placeholder_plot(f"Variability - {country_name}")
        html_content += f"<div class='plot-container'>{fig_to_base64(fig_var)}</div>"

    # Close HTML tags
    html_content += """
        </div>
    </body>
    </html>
    """

    # Write the HTML string to a file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_filename = os.path.join(script_dir, "final_dashboard.html")
    with open(output_filename, "w", encoding="utf-8") as file:
        file.write(html_content)
    
    print(f"Success! Report generated as: {os.path.abspath(output_filename)}")

    webbrowser.open(f"file://{os.path.abspath(output_filename)}")

# Run the generation
if __name__ == "__main__":
    generate_html_report()