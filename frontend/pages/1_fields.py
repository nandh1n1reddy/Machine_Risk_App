import sys
from pathlib import Path

FRONTEND_DIR = str(Path(__file__).resolve().parents[1])
if FRONTEND_DIR not in sys.path:
    sys.path.insert(0, FRONTEND_DIR)

import pandas as pd
import streamlit as st

from api import create_field, delete_field, get_fields, update_field


st.title("Field Configuration")
st.caption(
    "Fields added here appear automatically in machine forms and tables."
)

if "field_notice" in st.session_state:
    st.success(st.session_state.pop("field_notice"))


def show_notice(message: str):
    st.session_state["field_notice"] = message
    st.rerun()


try:
    fields = get_fields()
except RuntimeError as exc:
    st.error(str(exc))
    st.stop()


# Show the fields currently configured.
st.subheader("Configured fields")

if fields:
    display_rows = [
        {
            "Name": field["name"],
            "Type": field["field_type"].title(),
            "Required": "Yes" if field["required"] else "No",
            "Dropdown options": ", ".join(field.get("options") or []),
        }
        for field in fields
    ]
    st.dataframe(
        pd.DataFrame(display_rows),
        hide_index=True,
        use_container_width=True,
    )
else:
    st.info("No fields are configured yet.")


st.subheader("Add a field")

field_type_labels = {
    "Text": "text",
    "Number": "number",
    "Dropdown": "dropdown",
}

selected_type = st.selectbox(
    "Field type",
    options=list(field_type_labels),
    key="new_field_type",
)

with st.form("add_field_form"):
    field_name = st.text_input("Field name")
    required = st.checkbox("Required")

    if selected_type == "Dropdown":
        options_text = st.text_input(
            "Dropdown options",
            placeholder="Low, Medium, High",
        )
    else:
        options_text = ""

    add_submitted = st.form_submit_button("Add field")

if add_submitted:
    options = None

    if selected_type == "Dropdown":
        options = [
            option.strip()
            for option in options_text.split(",")
            if option.strip()
        ]

        if not options:
            st.error("Enter at least one dropdown option.")
            st.stop()

    try:
        result = create_field(
            name=field_name.strip(),
            field_type=field_type_labels[selected_type],
            required=required,
            options=options,
        )
        show_notice(result["message"])
    except RuntimeError as exc:
        st.error(str(exc))

if fields:
    st.subheader("Update a field")

    field_by_id = {field["id"]: field for field in fields}

    selected_field_id = st.selectbox(
        "Choose a field to update",
        options=list(field_by_id),
        format_func=lambda field_id: field_by_id[field_id]["name"],
        key="field_to_update",
    )
    selected_field = field_by_id[selected_field_id]

    with st.form("update_field_form"):
        updated_required = st.checkbox(
            "Required",
            value=selected_field["required"],
        )

        if selected_field["field_type"] == "dropdown":
            current_options = ", ".join(
                selected_field.get("options") or []
            )
            updated_options_text = st.text_input(
                "Dropdown options",
                value=current_options,
            )
        else:
            updated_options_text = ""

        update_submitted = st.form_submit_button("Save field settings")

    if update_submitted:
        updated_options = None

        if selected_field["field_type"] == "dropdown":
            updated_options = [
                option.strip()
                for option in updated_options_text.split(",")
                if option.strip()
            ]

            if not updated_options:
                st.error("A dropdown must have at least one option.")
                st.stop()

        try:
            result = update_field(
                field_id=selected_field_id,
                required=updated_required,
                options=updated_options,
            )
            show_notice(result["message"])
        except RuntimeError as exc:
            st.error(str(exc))


# Delete a field 

if fields:
    st.subheader("Delete a field")

    selected_delete_id = st.selectbox(
        "Choose a field to delete",
        options=list(field_by_id),
        format_func=lambda field_id: field_by_id[field_id]["name"],
        key="field_to_delete",
    )

    delete_name = field_by_id[selected_delete_id]["name"]
    confirm_delete = st.checkbox(
        f"I understand this deletes the '{delete_name}' field definition.",
        key="confirm_field_delete",
    )

    if st.button("Delete field", disabled=not confirm_delete):
        try:
            result = delete_field(selected_delete_id)
            show_notice(result["message"])
        except RuntimeError as exc:
            st.error(str(exc))