import requests
import re

# Fetch the API data from Google's public Discovery API
API_URL = "https://www.googleapis.com/discovery/v1/apis"
response = requests.get(API_URL)
if response.status_code != 200:
    print("Failed to fetch API data from Google. Exiting.")
    exit()

data = response.json()
services = data.get("items", [])

# Create a dictionary to store the latest version of each service
latest_versions = {}

def extract_version_number(version_str):
    """Extract numeric parts of the version string for sorting."""
    match = re.findall(r'\d+', version_str)
    return [int(v) for v in match] if match else [0]

for service in services:
    name = service.get("name")
    version = service.get("version", "N/A")

    if name not in latest_versions or extract_version_number(version) > extract_version_number(latest_versions[name]["version"]):
        latest_versions[name] = service

# Generate HTML content
html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GCP Services</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f9f9f9; text-align: center; }
        h1 { text-align: center; }
        .search-container { margin-bottom: 20px; }
        #searchInput { width: 50%; padding: 10px; font-size: 16px; border: 1px solid #ccc; border-radius: 5px; 
                       text-align: center; display: block; margin: 0 auto; }
        .filter-container { display: flex; justify-content: center; margin-top: 10px; }
        .filter-container label { font-size: 14px; margin-left: 5px; }
        .count-container { font-size: 14px; font-style: italic; }
        .container { display: flex; flex-wrap: wrap; justify-content: center; }
        .service-card { background: white; padding: 15px; margin: 10px; width: 300px; border-radius: 8px; 
                        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); text-align: center; position: relative; overflow: hidden; }
        .service-card img { width: 32px; height: 32px; margin-top: 10px; }
        .service-card h2 { font-size: 18px; margin: 10px 0; }
        .service-card p { font-size: 14px; color: #666; }
        .service-card a, .service-card button { font-size: small; display: inline-block; margin-top: 10px; padding: 8px 12px; 
                          background: #0073e6; color: white; text-decoration: none; border-radius: 5px; border: none; cursor: pointer; }
        .service-card button { background: #28a745; }
        .service-card a:hover, .service-card button:hover { opacity: 0.8; }
        .badge-container { position: absolute; top: 10px; left: 10px; right: 10px; display: flex; justify-content: space-between; align-items: center; }
        .preferred-badge { background: #28a745; color: white; padding: 4px 10px; border-radius: 12px; font-size: 12px; font-weight: bold; }
        .version-badge { background: #333; color: white; padding: 4px 10px; border-radius: 12px; font-size: 12px; font-weight: bold; }

        /* Modal Styles */
        .modal { display: none; position: fixed; z-index: 1000; left: 0; top: 0; width: 100%; height: 100%; background-color: rgba(0, 0, 0, 0.5); text-align: left; }
        .modal-content { background-color: white; margin: 10% auto; padding: 20px; width: 60%; max-height: 80vh; overflow: auto; border-radius: 8px; }
        .modal-close { float: right; font-size: 20px; cursor: pointer; color: red; }

        /* Tabs */
        .tab-container { display: flex; border-bottom: 2px solid #ccc; }
        .tab-button { flex: 1; padding: 10px; background: #ddd; border: none; cursor: pointer; font-weight: bold; }
        .tab-button.active { background: #0073e6; color: white; }
        .tab-content { display: none; padding: 10px; border-top: none; }
        .tab-content.active { display: block; }

        pre { background: #f4f4f4; padding: 10px; border-radius: 5px; overflow-x: auto; white-space: pre-wrap; word-wrap: break-word; }
    </style>
    <script>
        function filterServices() {
            let input = document.getElementById("searchInput").value.toLowerCase();
            let uniqueOnly = document.getElementById("uniqueCheckbox").checked;
            let cards = document.getElementsByClassName("service-card");

            for (let card of cards) {
                let title = card.getAttribute("data-title").toLowerCase();
                let description = card.getAttribute("data-description").toLowerCase();
                let isLatest = card.getAttribute("data-latest") === "true";

                let matchesSearch = title.includes(input) || description.includes(input);
                let matchesFilter = !uniqueOnly || isLatest;

                if (matchesSearch && matchesFilter) {
                    card.style.display = "block";
                } else {
                    card.style.display = "none";
                }
            }
            
            setVisibleServiceCardsCount();
        }
        
        function setVisibleServiceCardsCount() {
          const countSpan = document.getElementById('count');
          const allElements = document.querySelectorAll('.service-card');
          const visibleElements = [];

          allElements.forEach(element => {
            const style = window.getComputedStyle(element);
            if (style.display !== 'none' && style.visibility !== 'hidden' && element.offsetWidth > 0 && element.offsetHeight > 0) {
              visibleElements.push(element);
            }
          });

          countSpan.innerText = visibleElements.length;
        }
        
        document.addEventListener('DOMContentLoaded', function() {
          setVisibleServiceCardsCount();
        });

        function openModal(apiUrl) {
            fetch(apiUrl)
                .then(response => response.json())
                .then(data => {
                    let tabs = {
                        'General': data.name ? `<p><strong>Title:</strong> ${data.title}</p><p><strong>Name:</strong> ${data.name}</p><p><strong>Version:</strong> ${data.version}</p><p><strong>Owner:</strong> ${data.ownerName}</p>` : '',
                        'Full': `<pre>${JSON.stringify(data, null, 2)}</pre>`,
                        'Authentication': data.auth ? `<pre>${JSON.stringify(data.auth, null, 2)}</pre>` : '',
                        'Resources': data.resources ? `<pre>${JSON.stringify(data.resources, null, 2)}</pre>` : '',
                        'Schemas': data.schemas ? `<pre>${JSON.stringify(data.schemas, null, 2)}</pre>` : ''
                    };

                    let tabButtons = '';
                    let tabContents = '';
                    let isFirst = true;
                    for (let tab in tabs) {
                        if (tabs[tab]) {
                            tabButtons += `<button class="tab-button ${isFirst ? 'active' : ''}" onclick="showTab('${tab}')">${tab}</button>`;
                            tabContents += `<div id="tab-${tab}" class="tab-content ${isFirst ? 'active' : ''}">${tabs[tab]}</div>`;
                            isFirst = false;
                        }
                    }

                    document.getElementById("modalContent").innerHTML = `<div class="tab-container">${tabButtons}</div>${tabContents}`;
                    document.getElementById("modal").style.display = "block";
                })
                .catch(() => {
                    document.getElementById("modalContent").innerHTML = "<p>Failed to load API details.</p>";
                });
        }

        function showTab(tabName) {
            document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.tab-button').forEach(el => el.classList.remove('active'));
            document.getElementById(`tab-${tabName}`).classList.add('active');
            document.querySelector(`button[onclick="showTab('${tabName}')"]`).classList.add('active');
        }

        function closeModal() {
            document.getElementById("modal").style.display = "none";
        }
    </script>
</head>
<body>
    <h1>Google Cloud Platform Services</h1>
    <div class="search-container">
        <input type="text" id="searchInput" onkeyup="filterServices()" placeholder="Search GCP services...">
    </div>
    <div class="filter-container">
        <input type="checkbox" id="uniqueCheckbox" onclick="filterServices()">
        <label for="uniqueCheckbox">Unique (Latest Versions Only)</label>
    </div>
    <div class="count-container">
        <span id="count">100</span> visible
    </div>
    <div class="container">
"""

# Service cards generation
for service in services:
    title = service.get("title") or"Unknown Service"
    description = service.get("description") or "No description available."
    version = service.get("version") or "N/A"
    preferred = service.get("preferred") or False
    name = service.get("name")
    icon = service.get("icons", {}).get("x32", "https://www.gstatic.com/images/branding/product/1x/googleg_32dp.png")
    doc_link = service.get("documentationLink", service.get("discoveryRestUrl", "#"))
    discovery_url = service.get("discoveryRestUrl", "#")
    is_latest = latest_versions[name]["version"] == version

    html_content += f"""
        <div class="service-card" data-title="{title}" data-description="{description}" data-latest="{'true' if is_latest else 'false'}">
            <div class="badge-container">
                <span class="version-badge">{version}</span>
                {"<span class='preferred-badge'>Preferred</span>" if preferred else ""}
            </div>
            <img src="{icon}" alt="{title}">
            <h2>{title}</h2>
            <p>{description}</p>
            <a href="{doc_link}" target="_blank">Learn More</a>
            <button onclick="openModal('{discovery_url}')">View API Details</button>
        </div>
    """

html_content += """
    </div>
    <div id="modal" class="modal">
        <div class="modal-content">
            <span class="modal-close" onclick="closeModal()">&times;</span>
            <div id="modalContent"></div>
        </div>
    </div>
</body>
</html>
"""

with open("index.html", "w", encoding="utf-8") as file:
    file.write(html_content)

print("HTML file 'index.html' has been generated successfully.")
