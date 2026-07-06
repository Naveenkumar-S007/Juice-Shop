import frappe


def clear_old_waste_data():
    """
    Delete all existing Waste Entry and Waste Entry Item records.

    This is needed because the Waste Entry Item doctype schema has changed:
    the 'juice_item' field has been removed and replaced with 'raw_material'.
    Any existing records referencing 'juice_item' will break on access.

    Run this script BEFORE running `bench migrate` on a site that has existing
    Waste Entry data (or after, if the migration fails due to old records).

    Usage:
        bench --site your-site-name execute apps/juice_shop/clear_old_waste_data.py
    """
    # Deleting Waste Entry Items first (child table, must come before parent)
    item_count = frappe.db.count("Waste Entry Item")
    frappe.db.delete("Waste Entry Item", {"name": ["is", "set"]})

    # Now delete all Waste Entry records
    entry_count = frappe.db.count("Waste Entry")
    frappe.db.delete("Waste Entry", {"name": ["is", "set"]})

    frappe.db.commit()

    print(f"Deleted {entry_count} Waste Entry records")
    print(f"Deleted {item_count} Waste Entry Item records")
    print("Old waste data cleared. Run `bench migrate` now to apply schema changes.")


if __name__ == "__main__":
    clear_old_waste_data()
