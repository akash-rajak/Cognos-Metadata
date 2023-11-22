
import xml.etree.ElementTree as ET

# Load and parse the XML file
tree = ET.parse('Life Cycle of Matter Type.xml')
root = tree.getroot()

# Extract information
report_details = {}

# Assuming you want to extract modelPath, reportName, and expressionLocale
model_path = root.find("report").text
report_name = root.find(".//reportName").text
expression_locale = root.find(".//_expressionLocale").text

report_details["modelPath"] = model_path
report_details["reportName"] = report_name
report_details["expressionLocale"] = expression_locale

# You can continue extracting other details in a similar manner
# For more complex structures, you may need to iterate and navigate the XML tree

# Print extracted details
for key, value in report_details.items():
    print(f"{key}: {value}")

