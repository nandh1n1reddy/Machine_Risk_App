import sys
from pathlib import Path

FRONTEND_DIR = str(Path(__file__).resolve().parents[1])
if FRONTEND_DIR not in sys.path:
    sys.path.insert(0, FRONTEND_DIR)

import pandas as pd
import streamlit as st

from api import (
    create_machine,
    delete_machine,
    get_fields,
    get_machines,
    update_machine,
)
st.title("Machine Records")
st.caption("Forms and columns are generated from the configured fields.")

if "machine_notice" in st.session_state:
    st.success(st.session_state.pop("machine_notice"))

try:
    fields = get_fields()
    machines = get_machines()
except RuntimeError as exc:
    st.error(str(exc))
    st.stop()

if not fields:
    st.warning("Add field definitions before creating machine records.")
    st.stop()


def render_fields(
    field_definitions: list[dict],
    initial_data: dict,
    prefix: str,
) -> dict:
    values = {}

    for field in field_definitions:
        key = field["key"]
        field_type = field["field_type"]
        required = field["required"]
        label = field["name"] + (" *" if required else "")
        current_value = initial_data.get(key)

        widget_key = f"{prefix}_{key}"

        if field_type == "text":
            entered = st.text_input(
                label,
                value=current_value or "",
                key=widget_key,
            )
            values[key] = entered

        elif field_type == "number":
            entered = st.number_input(
                label,
                value=current_value,
                step=0.1,
                key=widget_key,
            )
            values[key] = entered

        elif field_type == "dropdown":
            options = field.get("options") or []
            choices = ["(select)"] + options
            if current_value in options:
                selected_index = choices.index(current_value)
            else:
                selected_index = 0

            selected = st.selectbox(
                label,
                choices,
                index=selected_index,
                key=widget_key,
            )
            values[key] = None if selected == "(select)" else selected

    return values


def show_saved_notice(message: str):
    st.session_state["machine_notice"] = message
    st.rerun()


table_rows = []
for machine in machines:
    row = {"ID": machine["id"]}
    data = machine.get("data") or {}

    for field in fields:
        row[field["name"]] = data.get(field["key"], "")

    table_rows.append(row)

st.subheader("Saved machines")
if table_rows:
    st.dataframe(pd.DataFrame(table_rows), hide_index=True, use_container_width=True)
else:
    st.info("No machine records yet.")

add_tab, manage_tab = st.tabs(["Add machine", "Edit or delete"])

with add_tab:
    with st.form("add_machine_form"):
        new_values = render_fields(fields, {}, "add")
        add_submitted = st.form_submit_button("Create machine")

    if add_submitted:
        try:
            result = create_machine(new_values)
            show_saved_notice(result["message"])
        except RuntimeError as exc:
            st.error(str(exc))


with manage_tab:
    if not machines:
        st.info("Create a machine first, then you can edit or delete it.")
    else:
        machine_by_id = {machine["id"]: machine for machine in machines}
        selected_id = st.selectbox(
            "Choose a machine",
            options=list(machine_by_id),
            format_func=lambda machine_id: (
                f"{(machine_by_id[machine_id].get('data') or {}).get('machine_name', 'Machine')} "
                f"(ID {machine_id})"
            ),
            key="selected_machine_id",
        )
        selected_machine = machine_by_id[selected_id]
        initial_data = selected_machine.get("data") or {}

        with st.form("edit_machine_form"):
            edited_values = render_fields(
                fields,
                initial_data,
                f"edit_{selected_id}",
            )
            edit_submitted = st.form_submit_button("Save changes")

        if edit_submitted:
            try:
                result = update_machine(selected_id, edited_values)
                show_saved_notice(result["message"])
            except RuntimeError as exc:
                st.error(str(exc))

        confirm_delete = st.checkbox(
            "I understand this permanently deletes the selected machine."
        )
        if st.button("Delete selected machine", disabled=not confirm_delete):
            try:
                result = delete_machine(selected_id)
                show_saved_notice(result["message"])
            except RuntimeError as exc:
                st.error(str(exc))