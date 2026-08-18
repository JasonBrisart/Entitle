"""
Entitle GUI — Deploy Tab

Records a governed deployment against a protected entitlement file. Calls
entitle.track.deploy_from_file(...) directly -- the exact same function the
`python main.py track deploy ...` CLI command uses. Deployment is only
recorded when the entitlement verifies, grants can_run, is not revoked, and
its deployment_limit has not been reached.
"""

from tkinter import ttk

from entitle.track import deploy_from_file
from gui.widgets import FormFrame

TAB_TITLE = "Deploy"


def build(parent, app):
    form = FormFrame(parent)
    form.add_entry("issuer", "Issuer ID", default="JasonBrisart")
    form.add_entry("subject", "Subject / Lab ID", default="ResearchLabA")
    form.add_entry("product", "Product ID", default="EntitleDemo")
    form.add_entry("master_key", "Master Key", show="*")
    form.add_entry(
        "entitlement_path",
        "Entitlement file",
        default=str(app.repo_root / "entitlements" / "lab_a.entitle"),
        browse="open",
    )
    form.add_entry("host", "Host / node ID")
    form.add_entry("environment", "Environment (optional)")
    form.add_entry("notes", "Notes (optional)")
    form.add_entry(
        "store",
        "Record store file",
        default=str(app.repo_root / "records" / "entitle_records.log"),
        browse="save",
    )

    def run():
        try:
            outcome = deploy_from_file(
                issuer=form.get("issuer"),
                subject=form.get("subject"),
                product=form.get("product"),
                master_key=form.get("master_key"),
                entitlement_path=form.get("entitlement_path"),
                host=form.get("host"),
                store=form.get("store"),
                environment=form.get("environment") or None,
                notes=form.get("notes") or None,
            )
            app.show_json(outcome)
        except Exception as exc:
            app.show_error(exc)

    ttk.Button(form, text="Record Deployment", command=run).grid(
        row=form.next_row(), column=0, columnspan=3, pady=12, sticky="w"
    )
    return form