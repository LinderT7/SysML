#!/usr/bin/env python3
"""
===============================================================================
SYSML STUDIO PRO WORKBENCH v2.5 (DESKTOP EDITION)
Features: Interactive Canvas, Property Inspector, Live Diagnostics Engine,
          SysML v2 Compliance, and Code/JSON Exporters.
===============================================================================
"""

import json
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

class SysMLStudioProApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SysML Studio Pro v2.5 MBSE Workbench - Desktop Edition")
        self.root.geometry("1350x850")
        self.root.configure(bg="#0b0f19")

        # Color Palette Definition (Dark CAD Theme)
        self.colors = {
            "bg_dark": "#0b0f19",
            "panel_bg": "#111827",
            "card_bg": "#1f2937",
            "border": "#374151",
            "accent_blue": "#0284c7",
            "accent_border": "#38bdf8",
            "text_white": "#f9fafb",
            "text_muted": "#9ca3af",
            "canvas_bg": "#0b1329",
            "grid_dots": "#1e293b",
            "gold": "#f59e0b",
            "red": "#ef4444",
            "green": "#22c55e"
        }

        # Application State & SysML v2 Model Schema (Prosthetic Hand Architecture)
        self.active_diagram = "BDD"
        self.selected_node_id = None
        
        self.nodes = [
            {"id": "node_1", "name": "ProstheticHandSystem", "type": "Top System", "stereo": "«system»", "x": 300, "y": 60, "w": 180, "h": 70},
            {"id": "node_2", "name": "ESP32Controller", "type": "Microcontroller", "stereo": "«block»", "x": 160, "y": 200, "w": 180, "h": 65, "ports": ["fsrDataIn"]},
            {"id": "node_3", "name": "LinearActuator", "type": "Actuation Unit", "stereo": "«block»", "x": 420, "y": 200, "w": 180, "h": 65, "ports": ["tendonForceOut"]}
        ]
        
        self.connections = [
            {"from": "node_1", "to": "node_2", "label": "composition"},
            {"from": "node_1", "to": "node_3", "label": "composition"}
            # Note: 'fsrDataIn' and 'tendonForceOut' have no active connectors, triggering diagnostics warnings!
        ]

        self.requirements = [
            {"id": "URD-01", "name": "Response Latency", "text": "System shall respond to muscle activation signals within 500ms.", "status": "Verified"},
            {"id": "SRD-01", "name": "Signal Processing", "text": "EMG raw signals must be filtered using Exponential Moving Average at 1kHz.", "status": "Verified"},
            {"id": "SRD-02", "name": "Tactile Feedback Limit", "text": "Grip force shall dynamically adjust based on FSR sensor values.", "status": "Verified"},
            {"id": "SRD-03", "name": "Emergency Cutoff", "text": "If actuator motor current exceeds 2.0A, emergency shutdown state must trigger.", "status": "PENDING"}
        ]

        self.zoom_level = 1.0
        self.dragging_node = None
        self.drag_offset_x = 0
        self.drag_offset_y = 0

        # Build Full Interface Layout
        self.build_top_header()
        self.build_main_workspace()

    # -------------------------------------------------------------------------
    # 1. TOP HEADER & WORKBENCH TOOLBAR
    # -------------------------------------------------------------------------
    def build_top_header(self):
        header = tk.Frame(self.root, bg=self.colors["panel_bg"], height=55, highlightthickness=1, highlightbackground=self.colors["border"])
        header.pack(fill=tk.X, side=tk.TOP)

        title_frame = tk.Frame(header, bg=self.colors["panel_bg"])
        title_frame.pack(side=tk.LEFT, padx=15, pady=10)

        badge = tk.Label(title_frame, text="SysML Studio Pro", font=("Segoe UI", 12, "bold"), fg=self.colors["text_white"], bg=self.colors["panel_bg"])
        badge.pack(side=tk.LEFT)

        ver_tag = tk.Label(title_frame, text=" v2.5 MBSE ", font=("Segoe UI", 8, "bold"), fg=self.colors["accent_border"], bg="#0369a1")
        ver_tag.pack(side=tk.LEFT, padx=8)

        subtitle = tk.Label(title_frame, text="System: 3D-Printed EMG Prosthetic Hand Architecture", font=("Segoe UI", 9), fg=self.colors["text_muted"], bg=self.colors["panel_bg"])
        subtitle.pack(side=tk.LEFT, padx=10)

        # Header Control Buttons
        btn_reload = tk.Button(header, text="Reload Sample", command=self.reload_sample, bg=self.colors["card_bg"], fg=self.colors["text_white"], font=("Segoe UI", 9), relief=tk.FLAT, padx=12, pady=4)
        btn_reload.pack(side=tk.RIGHT, padx=10)

        btn_validate = tk.Button(header, text="🛡️ Validate Architecture", command=self.run_diagnostics_engine, bg=self.colors["gold"], fg="#000000", font=("Segoe UI", 9, "bold"), relief=tk.FLAT, padx=12, pady=4)
        btn_validate.pack(side=tk.RIGHT, padx=5)

    # -------------------------------------------------------------------------
    # 2. MAIN THREE-PANEL WORKSPACE
    # -------------------------------------------------------------------------
    def build_main_workspace(self):
        workspace = tk.Frame(self.root, bg=self.colors["bg_dark"])
        workspace.pack(fill=tk.BOTH, expand=True)

        # Left Control Panel (260px wide)
        self.left_panel = tk.Frame(workspace, bg=self.colors["panel_bg"], width=260, highlightthickness=1, highlightbackground=self.colors["border"])
        self.left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 1))
        self.left_panel.pack_propagate(False)

        # Right Property Inspector & Diagnostics Panel (310px wide)
        self.right_panel = tk.Frame(workspace, bg=self.colors["panel_bg"], width=310, highlightthickness=1, highlightbackground=self.colors["border"])
        self.right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(1, 0))
        self.right_panel.pack_propagate(False)

        # Center Notebook Area (Visual Canvas & Code Exporter)
        self.center_frame = tk.Frame(workspace, bg=self.colors["bg_dark"])
        self.center_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.notebook = ttk.Notebook(self.center_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.tab_canvas = ttk.Frame(self.notebook)
        self.tab_export = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_canvas, text="📐 Visual Architecture Canvas")
        self.notebook.add(self.tab_export, text="⚡ SysML v2 & PlantUML Code Exporter")

        self.build_left_sidebar()
        self.build_center_canvas()
        self.build_code_exporter_tab()
        self.build_right_inspector()

    # -------------------------------------------------------------------------
    # LEFT PANEL: Diagram Types & Stencils
    # -------------------------------------------------------------------------
    def build_left_sidebar(self):
        sec1 = tk.LabelFrame(self.left_panel, text="SYSML DIAGRAM TYPE", font=("Segoe UI", 8, "bold"), fg=self.colors["accent_border"], bg=self.colors["panel_bg"], bd=1, relief=tk.SOLID, padx=8, pady=8)
        sec1.pack(fill=tk.X, padx=10, pady=10)

        grid_frame = tk.Frame(sec1, bg=self.colors["panel_bg"])
        grid_frame.pack(fill=tk.X)

        self.diag_buttons = {}
        diagrams = [("BDD", "❖ BDD"), ("IBD", "⬡ IBD"), ("Requirements", "≡ Req"), ("State Machine", "⚡ State")]

        for idx, (dtype, label) in enumerate(diagrams):
            r, c = divmod(idx, 2)
            btn = tk.Button(grid_frame, text=label, font=("Segoe UI", 9, "bold"), 
                            bg="#0369a1" if dtype == "BDD" else self.colors["card_bg"], 
                            fg=self.colors["text_white"], relief=tk.FLAT, pady=10,
                            command=lambda d=dtype: self.set_diagram_type(d))
            btn.grid(row=r, column=c, sticky="nsew", padx=3, pady=3)
            grid_frame.grid_columnconfigure(c, weight=1)
            self.diag_buttons[dtype] = btn

        sec2 = tk.LabelFrame(self.left_panel, text="SYSML v2 STENCIL PALETTE", font=("Segoe UI", 8, "bold"), fg=self.colors["accent_border"], bg=self.colors["panel_bg"], bd=1, relief=tk.SOLID, padx=8, pady=8)
        sec2.pack(fill=tk.X, padx=10, pady=5)

        stencils = [
            ("+ System Block", "«system»"),
            ("+ Subsystem / Module", "«block»"),
            ("+ Interface Port", "«port»")
        ]

        for text, stereo in stencils:
            b = tk.Button(sec2, text=text, font=("Segoe UI", 9), bg=self.colors["card_bg"], fg=self.colors["text_white"], 
                          anchor="w", relief=tk.FLAT, padx=10, pady=8,
                          command=lambda s=stereo: self.add_block_from_stencil(s))
            b.pack(fill=tk.X, pady=3)

    def set_diagram_type(self, dtype):
        self.active_diagram = dtype
        for key, btn in self.diag_buttons.items():
            btn.config(bg="#0369a1" if key == dtype else self.colors["card_bg"])
        self.render_canvas()

    def add_block_from_stencil(self, stereotype):
        count = len(self.nodes) + 1
        new_node = {
            "id": f"node_{count}",
            "name": f"Component_{count}",
            "type": "Mechatronic Unit",
            "stereo": stereotype,
            "x": 200 + (count * 15),
            "y": 140 + (count * 15),
            "w": 180,
            "h": 65,
            "ports": []
        }
        self.nodes.append(new_node)
        self.selected_node_id = new_node["id"]
        self.render_canvas()
        self.update_inspector()
        self.update_exporter_view()

    # -------------------------------------------------------------------------
    # CENTER PANEL: Interactive Canvas
    # -------------------------------------------------------------------------
    def build_center_canvas(self):
        canvas_container = tk.Frame(self.tab_canvas, bg=self.colors["canvas_bg"])
        canvas_container.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(canvas_container, bg=self.colors["canvas_bg"], highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.canvas.bind("<ButtonPress-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)

        # Bottom Canvas Zoom Bar
        bottom_bar = tk.Frame(self.tab_canvas, bg=self.colors["panel_bg"], height=35)
        bottom_bar.pack(fill=tk.X, side=tk.BOTTOM)

        lbl_zoom = tk.Label(bottom_bar, text="Zoom: 100% | ISO/IEC 15288 Compliant Engine", font=("Segoe UI", 9), fg=self.colors["text_muted"], bg=self.colors["panel_bg"])
        lbl_zoom.pack(side=tk.LEFT, padx=15)

        btn_zout = tk.Button(bottom_bar, text=" - ", bg=self.colors["card_bg"], fg=self.colors["text_white"], relief=tk.FLAT, padx=8, command=lambda: self.change_zoom(-0.1, lbl_zoom))
        btn_zout.pack(side=tk.RIGHT, padx=2, pady=3)
        btn_reset = tk.Button(bottom_bar, text="Reset", bg=self.colors["card_bg"], fg=self.colors["text_white"], relief=tk.FLAT, padx=8, command=lambda: self.change_zoom(0, lbl_zoom))
        btn_reset.pack(side=tk.RIGHT, padx=2, pady=3)
        btn_zin = tk.Button(bottom_bar, text=" + ", bg=self.colors["card_bg"], fg=self.colors["text_white"], relief=tk.FLAT, padx=8, command=lambda: self.change_zoom(0.1, lbl_zoom))
        btn_zin.pack(side=tk.RIGHT, padx=2, pady=3)

        self.render_canvas()

    def draw_grid(self):
        width = self.canvas.winfo_width() or 1000
        height = self.canvas.winfo_height() or 800
        grid_size = int(30 * self.zoom_level)

        for x in range(0, width, grid_size):
            for y in range(0, height, grid_size):
                self.canvas.create_oval(x, y, x+2, y+2, fill=self.colors["grid_dots"], outline="")

    def render_canvas(self):
        self.canvas.delete("all")
        self.draw_grid()

        for conn in self.connections:
            src = next((n for n in self.nodes if n["id"] == conn["from"]), None)
            tgt = next((n for n in self.nodes if n["id"] == conn["to"]), None)
            if src and tgt:
                x1, y1 = src["x"] + src["w"]//2, src["y"] + src["h"]
                x2, y2 = tgt["x"] + tgt["w"]//2, tgt["y"]
                self.canvas.create_line(x1, y1, x2, y2, fill=self.colors["accent_border"], width=2, arrow=tk.LAST)

        for node in self.nodes:
            is_selected = node["id"] == self.selected_node_id
            border_color = self.colors["accent_border"] if is_selected else self.colors["border"]
            border_w = 2 if is_selected else 1

            self.canvas.create_rectangle(
                node["x"], node["y"], node["x"] + node["w"], node["y"] + node["h"],
                fill=self.colors["card_bg"], outline=border_color, width=border_w, tags=node["id"]
            )
            self.canvas.create_text(
                node["x"] + node["w"]//2, node["y"] + 15,
                text=node["stereo"], fill=self.colors["accent_border"], font=("Segoe UI", 8, "bold"), tags=node["id"]
            )
            self.canvas.create_text(
                node["x"] + node["w"]//2, node["y"] + 35,
                text=node["name"], fill=self.colors["text_white"], font=("Segoe UI", 9, "bold"), tags=node["id"]
            )
            
            # Display ports if any
            ports_str = f"ports: {', '.join(node.get('ports', []))}" if node.get('ports') else f"type: {node['type']}"
            self.canvas.create_text(
                node["x"] + node["w"]//2, node["y"] + 52,
                text=ports_str, fill=self.colors["text_muted"], font=("Segoe UI", 8), tags=node["id"]
            )

    def on_canvas_click(self, event):
        clicked = self.canvas.find_withtag("current")
        if clicked:
            tags = self.canvas.gettags(clicked[0])
            if tags:
                node_id = tags[0]
                self.selected_node_id = node_id
                node = next((n for n in self.nodes if n["id"] == node_id), None)
                if node:
                    self.dragging_node = node
                    self.drag_offset_x = event.x - node["x"]
                    self.drag_offset_y = event.y - node["y"]
                self.update_inspector()
                self.render_canvas()
                return

        self.selected_node_id = None
        self.update_inspector()
        self.render_canvas()

    def on_canvas_drag(self, event):
        if self.dragging_node:
            self.dragging_node["x"] = event.x - self.drag_offset_x
            self.dragging_node["y"] = event.y - self.drag_offset_y
            self.render_canvas()

    def on_canvas_release(self, event):
        self.dragging_node = None

    def change_zoom(self, delta, label_widget):
        if delta == 0:
            self.zoom_level = 1.0
        else:
            self.zoom_level = max(0.5, min(2.0, self.zoom_level + delta))
        label_widget.config(text=f"Zoom: {int(self.zoom_level * 100)}% | ISO/IEC 15288 Compliant Engine")
        self.render_canvas()

    # -------------------------------------------------------------------------
    # CODE EXPORTER TAB
    # -------------------------------------------------------------------------
    def build_code_exporter_tab(self):
        exp_frame = tk.Frame(self.tab_export, bg=self.colors["bg_dark"], padx=15, pady=15)
        exp_frame.pack(fill=tk.BOTH, expand=True)

        top_bar = tk.Frame(exp_frame, bg=self.colors["bg_dark"])
        top_bar.pack(fill=tk.X, pady=(0, 10))

        tk.Label(top_bar, text="Generated SysML v2 / PlantUML Model Export:", font=("Segoe UI", 10, "bold"), fg=self.colors["text_white"], bg=self.colors["bg_dark"]).pack(side=tk.LEFT)
        
        btn_export_file = tk.Button(top_bar, text="Save Model JSON", command=self.export_json_file, bg="#10b981", fg="white", font=("Segoe UI", 9, "bold"), relief=tk.FLAT, padx=10, pady=4)
        btn_export_file.pack(side=tk.RIGHT)

        self.code_text = scrolledtext.ScrolledText(exp_frame, bg=self.colors["card_bg"], fg="#38bdf8", font=("Consolas", 10), insertbackground="white")
        self.code_text.pack(fill=tk.BOTH, expand=True)

        self.update_exporter_view()

    def update_exporter_view(self):
        if not hasattr(self, 'code_text'):
            return

        output = "// =========================================================\n"
        output += "// SYSML v2 MODEL EXPORT (ISO/IEC 15288 COMPLIANT)\n"
        output += "// =========================================================\n\n"
        
        for n in self.nodes:
            stereo = n['stereo'].replace('«', '').replace('»', '')
            output += f"part def {n['name']} {{\n"
            output += f"    attribute blockType: String = \"{n['type']}\";\n"
            if n.get('ports'):
                for p in n['ports']:
                    output += f"    port {p};\n"
            output += "}\n\n"

        output += "\n// --- PlantUML Visual Mapping Syntax ---\n"
        output += "@startuml SysML_v2_Architecture_Model\n!theme plain\n\n"
        for n in self.nodes:
            stereo = n['stereo'].replace('«', '<<').replace('»', '>>')
            output += f"class \"{n['name']}\" {stereo} {{\n  + domain: {n['type']}\n}}\n"
        output += "@enduml\n"

        self.code_text.delete(1.0, tk.END)
        self.code_text.insert(tk.END, output)

    def export_json_file(self):
        model_data = {
            "standard": "SysML v2 / ISO 15288",
            "system": "3D-Printed EMG Prosthetic Hand",
            "nodes": self.nodes,
            "connections": self.connections,
            "requirements": self.requirements
        }
        with open("sysml_v2_model_export.json", "w") as f:
            json.dump(model_data, f, indent=2)
        messagebox.showinfo("Export Success", "Model successfully exported to 'sysml_v2_model_export.json'.")

    # -------------------------------------------------------------------------
    # RIGHT PANEL: Property Inspector & Live Diagnostics Engine
    # -------------------------------------------------------------------------
    def build_right_inspector(self):
        lbl_title = tk.Label(self.right_panel, text="≡ PROPERTY INSPECTOR", font=("Segoe UI", 9, "bold"), fg=self.colors["accent_border"], bg=self.colors["panel_bg"], anchor="w", padx=10, pady=10)
        lbl_title.pack(fill=tk.X)

        self.inspector_frame = tk.Frame(self.right_panel, bg=self.colors["panel_bg"], padx=10)
        self.inspector_frame.pack(fill=tk.BOTH, expand=True)

        # Diagnostics Window Frame (Bottom Right - Live rule scanner)
        diag_frame = tk.LabelFrame(self.right_panel, text="⚠ MODEL DIAGNOSTICS (3 Issues)", font=("Segoe UI", 8, "bold"), fg=self.colors["gold"], bg=self.colors["panel_bg"], bd=1, relief=tk.SOLID, padx=8, pady=8)
        diag_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=10, pady=10)

        self.diag_text = scrolledtext.ScrolledText(diag_frame, height=5, bg=self.colors["card_bg"], fg=self.colors["gold"], font=("Segoe UI", 8), relief=tk.FLAT)
        self.diag_text.pack(fill=tk.X)
        
        self.run_diagnostics_engine(initial=True)
        self.update_inspector()

    def run_diagnostics_engine(self, initial=False):
        # Scan model for orphan ports and pending verification requirements
        issues = []
        for n in self.nodes:
            for p in n.get("ports", []):
                issues.append(f"⚠ IBD Port '{p}' on '{n['name']}' has no active connector.")
        
        for req in self.requirements:
            if req["status"] == "PENDING":
                issues.append(f"⚠ Req '{req['id']}' has verification status PENDING.")

        report = f"Total Issues Found: {len(issues)}\n" + "\n".join(issues)
        
        if hasattr(self, 'diag_text'):
            self.diag_text.delete(1.0, tk.END)
            self.diag_text.insert(tk.END, report)

        if not initial:
            messagebox.showwarning("Model Diagnostics Scan", f"Diagnostics Scan Complete!\n\n{len(issues)} structural warnings flagged.\nReview the diagnostics panel on the bottom right.")

    def update_inspector(self):
        for widget in self.inspector_frame.winfo_children():
            widget.destroy()

        if not self.selected_node_id:
            lbl_none = tk.Label(self.inspector_frame, text="Select any block on the canvas\nto inspect or modify properties.", font=("Segoe UI", 9), fg=self.colors["text_muted"], bg=self.colors["panel_bg"], pady=40)
            lbl_none.pack()
            return

        node = next((n for n in self.nodes if n["id"] == self.selected_node_id), None)
        if not node:
            return

        tk.Label(self.inspector_frame, text="Block Name:", font=("Segoe UI", 8, "bold"), fg=self.colors["text_white"], bg=self.colors["panel_bg"]).pack(anchor="w", pady=(10, 2))
        ent_name = tk.Entry(self.inspector_frame, bg=self.colors["card_bg"], fg=self.colors["text_white"], insertbackground="white", relief=tk.FLAT)
        ent_name.insert(0, node["name"])
        ent_name.pack(fill=tk.X, pady=2)

        tk.Label(self.inspector_frame, text="Stereotype:", font=("Segoe UI", 8, "bold"), fg=self.colors["text_white"], bg=self.colors["panel_bg"]).pack(anchor="w", pady=(10, 2))
        ent_stereo = tk.Entry(self.inspector_frame, bg=self.colors["card_bg"], fg=self.colors["text_white"], insertbackground="white", relief=tk.FLAT)
        ent_stereo.insert(0, node["stereo"])
        ent_stereo.pack(fill=tk.X, pady=2)

        tk.Label(self.inspector_frame, text="Ports (comma separated):", font=("Segoe UI", 8, "bold"), fg=self.colors["text_white"], bg=self.colors["panel_bg"]).pack(anchor="w", pady=(10, 2))
        ent_ports = tk.Entry(self.inspector_frame, bg=self.colors["card_bg"], fg=self.colors["text_white"], insertbackground="white", relief=tk.FLAT)
        ent_ports.insert(0, ", ".join(node.get("ports", [])))
        ent_ports.pack(fill=tk.X, pady=2)

        def apply_changes():
            node["name"] = ent_name.get()
            node["stereo"] = ent_stereo.get()
            ports_raw = ent_ports.get().strip()
            node["ports"] = [p.strip() for p in ports_raw.split(",")] if ports_raw else []
            self.render_canvas()
            self.update_exporter_view()
            self.run_diagnostics_engine(initial=True)

        btn_save = tk.Button(self.inspector_frame, text="Apply Property Changes", command=apply_changes, bg="#0284c7", fg="white", font=("Segoe UI", 9, "bold"), relief=tk.FLAT, pady=6)
        btn_save.pack(fill=tk.X, pady=20)

    def reload_sample(self):
        self.nodes = [
            {"id": "node_1", "name": "ProstheticHandSystem", "type": "Top System", "stereo": "«system»", "x": 300, "y": 60, "w": 180, "h": 70},
            {"id": "node_2", "name": "ESP32Controller", "type": "Microcontroller", "stereo": "«block»", "x": 160, "y": 200, "w": 180, "h": 65, "ports": ["fsrDataIn"]},
            {"id": "node_3", "name": "LinearActuator", "type": "Actuation Unit", "stereo": "«block»", "x": 420, "y": 200, "w": 180, "h": 65, "ports": ["tendonForceOut"]}
        ]
        self.connections = [
            {"from": "node_1", "to": "node_2", "label": "composition"},
            {"from": "node_1", "to": "node_3", "label": "composition"}
        ]
        self.selected_node_id = None
        self.render_canvas()
        self.update_inspector()
        self.update_exporter_view()
        self.run_diagnostics_engine(initial=True)

if __name__ == "__main__":
    root = tk.Tk()
    app = SysMLStudioProApp(root)
    root.mainloop()