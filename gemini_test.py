import google.generativeai as genai

# Configure Gemini API
genai.configure(api_key="AIzaSyDbB_BRDzz9Sd1Rv2tew-CSpdQx1im5TXs")

# Load Gemini model
model = genai.GenerativeModel("gemini-2.0-flash")
# User Question
user_query = "Show highest revenue product"

# Prompt
prompt = f"""
You are an SQL generator.

Table name: sales

Columns:
id
product_name
quantity
revenue

Convert the following question into SQL query:

{user_query}
"""

# Generate Response
response = model.generate_content(prompt)

# Print SQL Query
print("Generated SQL:")
print(response.text)