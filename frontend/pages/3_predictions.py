import sys
from pathlib import Path

FRONTEND_DIR = str(Path(__file__).resolve().parents[1])
if FRONTEND_DIR not in sys.path:
    sys.path.insert(0, FRONTEND_DIR)

import streamlit as st

from api import get_fields, get_machines, predict_machine


st.title("Risk Prediction")

try:
    fields = get_fields()
    machines = get_machines()
except RuntimeError as exc:
    st.error(str(exc))
    st.stop()

if not machines:
    st.info("Create a machine before requesting a prediction.")
    st.stop()

name_key = next(
    (
        field["key"]
        for field in fields
        if field["name"].casefold() == "machine name"
    ),
    None,
)

machine_by_id = {machine["id"]: machine for machine in machines}

selected_id = st.selectbox(
    "Choose a machine",
    options=list(machine_by_id),
    format_func=lambda machine_id: (
        f"{(machine_by_id[machine_id].get('data') or {}).get(name_key, 'Machine')} "
        f"(ID {machine_id})"
    ),
)

machine = machine_by_id[selected_id]
machine_data = machine.get("data") or {}

st.subheader("Machine values")
st.json(machine_data)

if st.button("Run prediction"):
    try:
        result = predict_machine(selected_id)
    except RuntimeError as exc:
        st.error(str(exc))
    else:
        risk = result["risk_level"]

        if risk == "Low":
            st.success(f"Risk level: {risk}")
        elif risk == "Medium":
            st.warning(f"Risk level: {risk}")
        else:
            st.error(f"Risk level: {risk}")

        st.caption(
            "Features used: " + ", ".join(result["features_used"])
        )

        ignored = result.get("ignored_fields", [])
        if ignored:
            st.info(
                "Fields not used by this model: "
                + ", ".join(ignored)
            )