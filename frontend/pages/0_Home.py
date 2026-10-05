import sys
from pathlib import Path

FRONTEND_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = FRONTEND_DIR.parent

if str(FRONTEND_DIR) not in sys.path:
    sys.path.insert(0, str(FRONTEND_DIR))

import pandas as pd
import streamlit as st

from api import get_fields, get_machines


st.title("⚙️ Machine Risk App")
st.write(
    "Configure machine fields, manage records, and run a local risk prediction."
)
st.caption("Risk levels: Low · Medium · High")

try:
    fields = get_fields()
    machines = get_machines()
    backend_available = True
except RuntimeError as exc:
    fields = []
    machines = []
    backend_available = False
    st.warning(
        "The backend is not available, so live counts and machine records "
        "cannot be loaded. Start Uvicorn to connect the dashboard."
    )
    st.caption(str(exc))

model_path = PROJECT_ROOT / "ml" / "risk_model.joblib"
model_ready = model_path.exists()

metric_columns = st.columns(3)
metric_columns[0].metric("Machine records", len(machines))
metric_columns[1].metric("Configured fields", len(fields))
metric_columns[2].metric(
    "Risk model",
    "Ready" if model_ready else "Not trained",
)

if not model_ready:
    st.info(
        "To create the local model, run "
        "`python -m ml.train_model` from the project folder."
    )

st.subheader("Quick links")
link_columns = st.columns(3)
with link_columns[0]:
    st.page_link(
        "pages/1_fields.py",
        label="Configure fields",
        icon="🧩",
        help="Add or update the fields used by machine records.",
    )
with link_columns[1]:
    st.page_link(
        "pages/2_Machines.py",
        label="Manage machines",
        icon="🏭",
        help="Create, edit, view, or delete machine records.",
    )
with link_columns[2]:
    st.page_link(
        "pages/3_predictions.py",
        label="Run a prediction",
        icon="📊",
        help="Select a saved machine and display its risk level.",
    )

st.subheader("Recent machines")
if not backend_available:
    st.caption("Recent machine records will appear when the backend is running.")
elif not machines:
    st.info("No machine records yet. Add your first machine from Manage machines.")
else:
    machine_name_key = next(
        (
            field["key"]
            for field in fields
            if field["name"].casefold() == "machine name"
        ),
        None,
    )

    recent_rows = []
    for machine in reversed(machines[-5:]):
        machine_data = machine.get("data") or {}
        row = {
            "ID": machine["id"],
            "Machine": machine_data.get(
                machine_name_key,
                f"Machine {machine['id']}",
            ),
        }
        for field in fields:
            if field["key"] != machine_name_key:
                row[field["name"]] = machine_data.get(field["key"], "")
        recent_rows.append(row)

    st.dataframe(
        pd.DataFrame(recent_rows),
        hide_index=True,
        use_container_width=True,
    )

st.divider()
st.caption(
    "Local assessment app · Machine data stays in the local SQLite database."
)

