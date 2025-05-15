# -*- coding: utf-8 -*-

import streamlit as st


#%%
st.set_page_config(
    page_title="Dashboard for Shift Schedule",
    page_icon="⏱️",
    layout="wide",
    initial_sidebar_state="expanded")

#%%

st.sidebar.markdown("Click the pages ☝️ to navigate between Interface.")


st.markdown(""" 
 
# ⏱️ Workforce Scheduling Dashboard           
Welcome to the Workforce Scheduling Dashboard, your all‑in‑one tool for solving staffing problems with fairness and efficiency. This app enables interactive shift planning and uses optimization to create equitable, demand-driven work schedules based on user-defined preferences.
            
---
            
## 🚀 Key Features

- 📅 **Date Range Selector** : Choose a custom planning window from 1–14 days with a clear calendar interface.

- 👤 **Employee-Specific Availability** : Select daily availability for each employee through a streamlined sidebar.

- 🧮 **Shift Demand Input** : Define required number of workers per shift.

- ✅ **Auto-Fill Option** : Automatically assign full availability to unedited workers.

- ⚙️ Optimized Scheduling Engine (PuLP):

    - **Primary Objective** : Minimize unfilled shifts ("slack").

    - **Secondary Objective** : Balance workload by minimizing shift count disparities among employees.

- 📊 Visual Schedule Output:

    - ✓ Green = Scheduled to work

    - ✗ Red = Not scheduled

---
            
## 📚 Assumptions & Methodology

- 🕐 One Shift Per Day: Each day corresponds to one full-time shift.

- 🔢 Binary Assignments: Workers are either assigned (1) or not (0).

- ❗ Slack Calculation: Additional staffing needs (if unmet) are modeled via slack variables.

- ⚖️ Lexicographic Optimization:

    - Phase 1: Minimize slack (unfilled shifts).

    - Phase 2: Minimize shift imbalance (maxShifts - minShifts).

- 📦 Integer Linear Programming: All decision variables are integers to reflect actual headcounts.
            
 
            
 
            
 
            
 
            
""")