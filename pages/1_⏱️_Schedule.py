# -*- coding: utf-8 -*-
"""
Created on Wed May 14 19:32:46 2025

@author: alann
"""

#%%
import streamlit as st
from datetime import datetime, timedelta
from pulp import LpProblem, LpMinimize, LpVariable, LpBinary, LpInteger, lpSum

import pandas as pd


#%%


    
    
#%%
def build_and_solve_model(workers, shifts, availability, shiftRequirements):
    # Create the model
    model = LpProblem("workforce", LpMinimize)

    # Decision Variables
    x = LpVariable.dicts("x", availability, cat=LpBinary)
    slacks = LpVariable.dicts("Slack", shifts, lowBound=0, cat=LpInteger)

    # Total variables
    totSlack = LpVariable("totSlack", lowBound=0, cat=LpInteger)
    totShifts = LpVariable.dicts("TotShifts", workers, lowBound=0, cat=LpInteger)
    minShift = LpVariable("minShift", lowBound=0, cat=LpInteger)
    maxShift = LpVariable("maxShift", lowBound=0, cat=LpInteger)

    # Constraints
    for w in workers:
        model += (minShift <= totShifts[w], f"minShift_bound_{w}")
        model += (maxShift >= totShifts[w], f"maxShift_bound_{w}")

    for s in shifts:
        model += (
            lpSum(x[(w, s)] for (w, sh) in availability if sh == s) + slacks[s] == shiftRequirements[s],
            f"shiftRequirement_{s}"
        )

    model += (totSlack == lpSum(slacks[s] for s in shifts), "totSlack_sum")

    for w in workers:
        model += (
            totShifts[w] == lpSum(x[(w, s)] for (w2, s) in availability if w2 == w),
            f"totShifts_{w}"
        )
        
    for w in workers:
        model += (minShift <= totShifts[w], f"minShift_bound_{w}_low")
        model += (maxShift >= totShifts[w], f"maxShift_bound_{w}_high")

    # Phase 1: Primary objective — minimize total slack
    model += totSlack, "TotalSlack"
    model.solve()

    best_slack = totSlack.varValue

    # Phase 2: Add relaxation for total slack, set fairness as objective
    model += (totSlack <= 1.2 * best_slack, "SlackRelTol")
    fairness = maxShift - minShift
    model.objective = fairness
    model.solve()

    return {
        "model": model,
        "x": x,
        "totSlack": totSlack,
        "totShifts": totShifts,
        "minShift": minShift,
        "maxShift": maxShift,
        "slacks": slacks,
        "fairness": fairness,
    }


#%%
# =============================================================================
#                                   MAIN
# =============================================================================

def main():
    
    # --- Streamlit Side Bar ---

    #                         Parameters
    # Date selection
    st.sidebar.header("Schedule Parameters")
    start_date = st.sidebar.date_input("Calendar start date", datetime.today().date())
    num_days = st.sidebar.slider("Number of Shifts", min_value=7, max_value=14, value=14)

#%%
    st.sidebar.markdown("---")

    # shifts
    date_format = '%Y-%m-%d'
    dates = [start_date + timedelta(days=i) for i in range(num_days)]
    date_strs = [d.strftime(date_format) for d in dates]

    # Generate shifts like "Mon1", "Tue2", ..., "Sun14"
    shifts = [
        datetime.strptime(date_str, "%Y-%m-%d").strftime("%a") + str(i + 1)
        for i, date_str in enumerate(date_strs)
    ]

    shift_dates = dict(zip(shifts, dates))
    date_to_shift = {d.strftime(date_format): sh for sh, d in shift_dates.items()}



    # list of workers
    workers = ["Amy", "Bob", "Cathy", "Dan", "Ed", "Fred", "Gu"]


    # User selects availability per worker
    st.sidebar.subheader("Set Worker Availability")
    valid_input = True
    availability = []
    for w in workers:
        selected_dates = st.sidebar.multiselect(f"{w}", options=date_strs)
        st.sidebar.write(f"Selected for {w}: {len(selected_dates)}/{len(date_strs)} shifts")
        for d in selected_dates:
            if d not in date_to_shift:
                st.error(f"Invalid date selected for {w}: {d}")
                valid_input = False
                
            else: 
                availability.append((w, date_to_shift[d]))
            


    # Require all shifts if no availability selected
    enforce_all = st.sidebar.checkbox("Assume full availability for unselected workers", value=False)
    if enforce_all:
        for w in workers:
            if not any(av[0] == w for av in availability):
                for sh in shifts:
                    availability.append((w, sh))
                    
#%%               
    st.sidebar.markdown("---")
                    

    # Shift requirements input
    # requirements = [3, 2, 4, 4, 5, 6, 5, 2, 2, 3, 4, 6, 7, 5]
    # shiftRequirements = dict(zip(shifts, requirements))

    st.sidebar.subheader("Shift Requirements")
    shiftRequirements = {}

    for i, date_str in enumerate(date_strs):
        shift = shifts[i]
        label = f"Required staff on {date_str} ({shift})"
        val = st.sidebar.number_input(label, min_value=0, value=1)
        shiftRequirements[shift] = val
    
    
    
#%%    

    df = pd.DataFrame(list(date_to_shift.items()), columns=["Date", "Shift"])
    with st.expander("⏱️ Scheduling Horizon", expanded=True):
        st.write(df)
    
    
    if valid_input and availability and all(date_to_shift.get(d) for d in date_strs):
    
        results = build_and_solve_model(workers, shifts, availability, shiftRequirements)
    
        # Access individual variables
        x = results["x"]
        totSlack = results["totSlack"].varValue
        totShifts = results["totShifts"]
    
    
    
#%%
    
      #                            Results output
        solution = {"Total number of extra workers required to satisfy shift requirements": str(totSlack)}
        assignments = {}
        
        for (w, s) in availability:
            if x[(w, s)].varValue > 0.5:
                assignments.setdefault(w, []).append(s)
            
#%%
        with st.expander("📈 KPI", expanded=False):
            st.write(pd.DataFrame.from_records(list(solution.items()), columns=['KPI', 'Value']))
            
#%%    
        assignments_all = {}
        shifts_sol = {}
        for w in workers:
            shifts_sol[w] = totShifts[w].varValue
            assignments_all[w] = assignments.get(w, [])
            
            
        with st.expander("🏢 Shifts", expanded=False):
            st.write(pd.DataFrame.from_records(list(shifts_sol.items()), columns=['Worker', 'Number of shifts']))
         
     
#%%
      
    # Visualization
        st.header("Workforce Schedule")
        
        data = []
        for w in workers:
            row = {"Worker": w}
            for d in date_strs:
                sh = date_to_shift[d]
                status = '✓' if (w, sh) in availability and x.get((w, sh), None) and x[(w, sh)].value() == 1 else '✗'
                color = 'green' if status == '✓' else 'red'
                row[d] = f"<span style='color:{color}; font-weight:bold'>{status}</span>"
            data.append(row)
            
        # Add shift requirements as final row
        req_row = {"Worker": "Required"}
        for d in date_strs:
            sh = date_to_shift[d]
            req_row[d] = f"<span style='color:blue; font-weight:bold'>{shiftRequirements[sh]}</span>"
        data.append(req_row)

    
        df = pd.DataFrame(data).set_index('Worker')
        st.write(df.to_html(escape=False), unsafe_allow_html=True)
        st.write("##### Legend:\n✓ working, ✗ not working")
        
    
     
     
#%%     
    else:
        st.warning("Please complete all sidebar inputs correctly before generating the schedule.") 
     
     
 
#%%
if __name__ == "__main__":
     main()

