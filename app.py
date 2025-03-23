import os
import ollama # type: ignore
import json
import pandas as pd
import matplotlib.pyplot as plt # type: ignore
import seaborn as sns # type: ignore
from fpdf import FPDF # type: ignore
from fpdf.enums import XPos, YPos # type: ignore

OLLAMA_MODEL = "llama3.1"

DATA_FOLDER = "Data"

STRUCTURED_DATA_FILE = 'SampleTabularData.csv'
UNSTRUCTURED_DATA_FILE = 'SampleTextUnstructuredData.txt'
JSON_DATA_FILE = 'SampleJSONData.json'

with open(os.path.join(DATA_FOLDER, UNSTRUCTURED_DATA_FILE), "r", encoding="utf-8") as file:
    unstructured_data = file.read().strip()

structured_df = pd.read_csv(os.path.join(DATA_FOLDER, STRUCTURED_DATA_FILE))

structured_data = structured_df.to_string(index=False)

with open(os.path.join(DATA_FOLDER, JSON_DATA_FILE), "r", encoding="utf-8") as file:
    json_data = json.load(file)

json_text = json.dumps(json_data, indent=4)

prompt = f"""
Using the following data, generate a well-structured, insightful monthly departmental report:

Structured Data:
{structured_data}

Unstructured Data:
{unstructured_data}

JSON Data:
{json_text}

Provide an executive summary, key insights, and recommendations.
"""

response = ollama.chat(model=OLLAMA_MODEL, messages=[  
    {"role": "system", "content": "You are an AI report generator."},  
    {"role": "user", "content": "Generate a detailed report based on the following data:\n\n" + prompt}  
])

if hasattr(response, "message") and hasattr(response.message, "content"):
    generated_report = response.message.content
else:
    generated_report = "No report generated. Please check the AI response."

generated_report = generated_report.encode("utf-8", "ignore").decode("utf-8")

def create_visualizations():
    # # Ensure first column is treated as a string (category labels)
    # structured_df.iloc[:, 0] = structured_df.iloc[:, 0].astype(str)

    # plt.figure(figsize=(8, 5))
    # sns.barplot(x=structured_df.iloc[:, 0], y=structured_df.iloc[:, 1].astype(float), color='blue', label='Allocated')
    # sns.barplot(x=structured_df.iloc[:, 0], y=structured_df.iloc[:, 2].astype(float), color='green', label='Utilized')
    
    # plt.ylabel("Amount (in Cr)")
    # plt.title("Budget Allocation vs Utilization")
    # plt.xticks(rotation=30)
    # plt.legend()
    # plt.savefig("budget_chart.png", bbox_inches='tight')
    structured_df["Percentage Achieved"] = (
        structured_df["Percentage Achieved"]
        .astype(str)  # Convert all values to string
        .str.extract(r"(\d+)")  # Extract only numeric part
        .astype(float)  # Convert to float
    )

    plt.figure(figsize=(8, 5))

    sns.barplot(
        x=structured_df["Item"], 
        y=structured_df["Percentage Achieved"], 
        color="blue"
    )

    plt.ylabel("Percentage Achieved (%)")
    plt.title("Progress of Different Initiatives")
    plt.xticks(rotation=30, ha="right")  # Rotate labels for better readability
    plt.savefig("progress_chart.png", bbox_inches="tight")


create_visualizations()

class PDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 14)
        self.cell(200, 10, "Monthly Departmental Report", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 10)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

    def chapter_title(self, title):
        self.set_font("Helvetica", "B", 12)
        self.cell(0, 10, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="L")
        self.ln(5)

    def chapter_body(self, body):
        self.set_font("Helvetica", size=11)
        self.multi_cell(0, 8, body)
        self.ln()

    def add_image(self, image_path, width=180, height=90):
        self.image(image_path, x=15, w=width, h=height)
        self.ln(10)

pdf = PDF()
pdf.set_auto_page_break(auto=True, margin=15)
pdf.add_page()

pdf.chapter_title("Executive Summary")
pdf.chapter_body(generated_report)

pdf.chapter_title("Budget Allocation vs Utilization")
pdf.add_image("budget_chart.png")

output_pdf_path = "./reports/AI_Generated_Report_from_Files_005.pdf"
pdf.output(output_pdf_path)

print(f"✅ Report generated using data from files (including TXT & CSV) and saved as {output_pdf_path}")
