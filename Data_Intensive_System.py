#!/usr/bin/env python
# coding: utf-8

# In[1]:


get_ipython().system('pip install jupyter pandas pymongo dnspython matplotlib seaborn')


# ### Load Dataset in Jupyter Notebook

# In[2]:


import pandas as pd

# Load dataset
df = pd.read_csv("data.csv", encoding='ISO-8859-1')

# Display the first few rows
df.head()


# ### Check Dataset Information

# In[3]:


# Check dataset structure
df.info()

# Check for missing values
df.isnull().sum()


# ### Data Cleaning & Preprocessing

# In[4]:


# Remove missing CustomerIDs
df_cleaned = df.dropna(subset=['CustomerID'])

# Convert InvoiceDate to datetime
df_cleaned['InvoiceDate'] = pd.to_datetime(df_cleaned['InvoiceDate'])

# Remove negative Quantity and UnitPrice
df_cleaned = df_cleaned[(df_cleaned['Quantity'] > 0) & (df_cleaned['UnitPrice'] > 0)]

# Reset index
df_cleaned.reset_index(drop=True, inplace=True)

# Display cleaned data
df_cleaned.head()


# ### Connect to MongoDB

# In[6]:


from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")

# Create database and collection
db = client["ecommerce_db"]
collection = db["transactions"]


# ### Insert Data into MongoDB

# In[7]:


# Insert data into MongoDB
data_dict = df_cleaned.to_dict(orient="records")
collection.insert_many(data_dict)

print("Data inserted into MongoDB successfully!")


# ### Retrieve One Record

# In[8]:


print(collection.find_one())


# ### Count Total Records

# In[9]:


print(f"Total records in MongoDB: {collection.count_documents({})}")


# ### Top Selling Products

# In[10]:


import matplotlib.pyplot as plt
import seaborn as sns

# Aggregate top 10 products by sales volume
top_products = collection.aggregate([
    {"$group": {"_id": "$Description", "total_sales": {"$sum": "$Quantity"}}},
    {"$sort": {"total_sales": -1}},
    {"$limit": 10}
])

# Convert to DataFrame
top_products_df = pd.DataFrame(list(top_products))

# Plot results
plt.figure(figsize=(10, 6))
sns.barplot(data=top_products_df, x="total_sales", y="_id", palette="viridis")
plt.xlabel("Total Quantity Sold")
plt.ylabel("Product Name")
plt.title("Top 10 Best Selling Products")
plt.show()


# ### Monthly Sales Trend

# In[11]:


# Monthly sales trend
monthly_sales = collection.aggregate([
    {"$group": {"_id": {"year": {"$year": "$InvoiceDate"}, "month": {"$month": "$InvoiceDate"}}, 
                "total_sales": {"$sum": {"$multiply": ["$Quantity", "$UnitPrice"]}}}},
    {"$sort": {"_id": 1}}
])

# Convert to DataFrame
monthly_sales_df = pd.DataFrame(list(monthly_sales))

# Plot
plt.figure(figsize=(10, 5))
sns.lineplot(x=monthly_sales_df.index, y="total_sales", data=monthly_sales_df, marker="o")
plt.xlabel("Month")
plt.ylabel("Total Sales")
plt.title("Monthly Sales Trends")
plt.show()


# ### Customer Segmentation - Top 10 Customers by Revenue

# In[12]:


# Aggregate top 10 customers by total revenue
top_customers = collection.aggregate([
    {"$group": {"_id": "$CustomerID", "total_revenue": {"$sum": {"$multiply": ["$Quantity", "$UnitPrice"]}}}},
    {"$sort": {"total_revenue": -1}},
    {"$limit": 10}
])

# Convert to DataFrame
top_customers_df = pd.DataFrame(list(top_customers))

# Plot results
plt.figure(figsize=(10, 6))
sns.barplot(data=top_customers_df, x="total_revenue", y="_id", palette="coolwarm")
plt.xlabel("Total Revenue (£)")
plt.ylabel("Customer ID")
plt.title("Top 10 Customers by Revenue")
plt.show()


# In[ ]:




