import frappe

WORKSPACES_TO_HIDE = [
    "Manufacturing",
    "CRM",
    "Assets",
    "Buying",
    "Selling",
    "Purchase",
]

WORKSPACES_KEEP_VISIBLE = [
    "Inventory",
    "Sales",
    "Juice Shop",
]

def hide_workspaces():
    hidden = []
    not_found = []

    for ws_name in WORKSPACES_TO_HIDE:
        if frappe.db.exists("Workspace", ws_name):
            frappe.db.set_value("Workspace", ws_name, "public", 0)
            hidden.append(ws_name)
        else:
            not_found.append(ws_name)

    for ws_name in WORKSPACES_KEEP_VISIBLE:
        if frappe.db.exists("Workspace", ws_name):
            current = frappe.db.get_value("Workspace", ws_name, "public")
            if not current:
                frappe.db.set_value("Workspace", ws_name, "public", 1)

    frappe.db.commit()

    print("Hidden workspaces (set public=0):")
    for name in hidden:
        print(f"  - {name}")

    if not_found:
        print("\nWorkspaces not found (skipped):")
        for name in not_found:
            print(f"  - {name}")

    print("\nVisible workspaces kept (public=1):")
    for name in WORKSPACES_KEEP_VISIBLE:
        print(f"  - {name}")

if __name__ == "__main__":
    hide_workspaces()
