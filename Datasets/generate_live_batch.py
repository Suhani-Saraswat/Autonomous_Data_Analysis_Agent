"""
Live dataset refresher for the Autonomous Data Analysis Agent.

Run:
    python generate_live_batch.py

It appends 250 new synthetic Superstore transactions to
superstore_live_stream_10000plus.csv, allowing your agent to
re-run profiling/analysis on changing data.
"""
import pandas as pd
import numpy as np
from datetime import datetime

FILE = "superstore_live_stream_10000plus.csv"
rng = np.random.default_rng()

df = pd.read_csv(FILE)
start_id = int(df["Row_ID"].max()) + 1

states = ["California","Texas","New York","Florida","Washington","Illinois","Georgia","Colorado"]
regions = {"California":"West","Texas":"Central","New York":"East","Florida":"South",
           "Washington":"West","Illinois":"Central","Georgia":"South","Colorado":"West"}
categories = ["Furniture","Office Supplies","Technology"]
subcats = {
    "Furniture":["Chairs","Tables","Bookcases","Furnishings"],
    "Office Supplies":["Binders","Paper","Art","Storage","Appliances"],
    "Technology":["Phones","Accessories","Copiers","Machines"]
}

new = []
for i in range(250):
    state = rng.choice(states)
    category = rng.choice(categories)
    quantity = int(rng.integers(1, 9))
    discount = round(float(rng.uniform(0, .35)), 3)
    sales = round(float(rng.uniform(20, 900) * quantity * (1-discount)), 2)
    profit = round(float(sales * rng.uniform(-.08, .28)), 2)
    now = pd.Timestamp.now().floor("s")
    new.append({
        "Dataset_Type":"LIVE_STREAM_SIMULATION",
        "Row_ID":start_id+i,
        "Order_ID":f"LIVE-{now.strftime('%Y%m%d')}-{start_id+i}",
        "Order_Date":now,
        "Ship_Date":now + pd.Timedelta(days=int(rng.integers(1,7))),
        "Ship_Mode":rng.choice(["Standard Class","Second Class","First Class","Same Day"]),
        "Customer_ID":f"CUST-{rng.integers(1,1801):05d}",
        "Customer_Name":f"Customer {rng.integers(1,1801):04d}",
        "Segment":rng.choice(["Consumer","Corporate","Home Office"]),
        "Country":"United States",
        "City":"Live City",
        "State":state,
        "Postal_Code":int(rng.integers(10000,99999)),
        "Region":regions[state],
        "Product_ID":f"LIVE-PROD-{rng.integers(1000,9999)}",
        "Category":category,
        "Sub_Category":rng.choice(subcats[category]),
        "Product_Name":"Live Product",
        "Sales":sales,
        "Quantity":quantity,
        "Discount":discount,
        "Profit":profit,
        "Last_Updated":now
    })

pd.concat([df, pd.DataFrame(new)], ignore_index=True).to_csv(FILE, index=False)
print(f"Added 250 records. Total records: {len(df)+250}")
