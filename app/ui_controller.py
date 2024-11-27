import pyautogui
import tkinter as tk
from tkinter import ttk
from bounty_processor import BountyProcessor
from database_handler import DatabaseHandler

class UIController:
    def __init__(self, window):
        self.window = window
        self.bounty_processor = BountyProcessor()
        self.db_handler = DatabaseHandler()

        self._initialize_ui()
        self._load_inputs()

    def _initialize_ui(self):
        # Input frame
        input_frame = ttk.Frame(self.window, padding="10")
        input_frame.pack(fill="x")

        # Run button
        self.start_button = ttk.Button(input_frame, text="Run", command=self.on_button_click)
        self.start_button.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        # Add a checkbox to toggle visibility of inputs and labels
        self.show_inputs_var = tk.BooleanVar(value=True)  # Default to show inputs
        toggle_button = ttk.Checkbutton(input_frame, text="Show/Hide Inputs", variable=self.show_inputs_var, command=self.toggle_visibility)
        toggle_button.grid(row=0, column=1, padx=5, pady=5, sticky="e")

        # Region row
        self.region_label = ttk.Label(input_frame, text="Region (x,y,width,height):")
        self.region_label.grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.region_entry = ttk.Entry(input_frame)
        self.region_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        # Inventory Space row
        self.inventory_space_label = ttk.Label(input_frame, text="Inventory Space:")
        self.inventory_space_label.grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.inventory_space_var = tk.StringVar(value="24")  # Default value
        self.inventory_space_dropdown = ttk.Combobox(input_frame, textvariable=self.inventory_space_var, state="readonly")
        self.inventory_space_dropdown['values'] = ("18", "24")
        self.inventory_space_dropdown.grid(row=2, column=1, sticky="ew", padx=5, pady=5)

        # Detective Level row
        self.detective_level_label = ttk.Label(input_frame, text="Detective Level (1-500):")
        self.detective_level_label.grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.detective_level_var = tk.StringVar()
        validate_command = self.window.register(self._validate_numeric_input)
        self.detective_level_entry = ttk.Entry(
            input_frame,
            textvariable=self.detective_level_var,
            validate="key",
            validatecommand=(validate_command, "%P")
        )
        self.detective_level_entry.grid(row=3, column=1, sticky="ew", padx=5, pady=5)

        # Battle of Fortunehold row
        self.battle_of_fortunehold_label = ttk.Label(input_frame, text="Battle of Fortunehold:")
        self.battle_of_fortunehold_label.grid(row=4, column=0, sticky="w", padx=5, pady=5)
        self.battle_of_fortunehold_var = tk.BooleanVar(value=False)
        self.battle_of_fortunehold_checkbox = ttk.Checkbutton(
            input_frame,
            variable=self.battle_of_fortunehold_var
        )
        self.battle_of_fortunehold_checkbox.grid(row=4, column=1, sticky="w", padx=5, pady=5)

        # Configure column weights for better layout
        input_frame.columnconfigure(1, weight=1)

        # Output frame
        output_frame = ttk.Frame(self.window, padding="10")
        output_frame.pack(fill="both", expand=True)

        # Treeview for results
        columns = ("Distance", "Action", "Location")
        self.treeview = ttk.Treeview(output_frame, columns=columns, show="headings")
        self.treeview.heading("Distance", text="Time")
        self.treeview.heading("Action", text="Action")
        self.treeview.heading("Location", text="Location")
        self.treeview.column("Distance", width=50, anchor="w")
        self.treeview.column("Action", width=40, anchor="w")
        self.treeview.column("Location", width=100, anchor="w")
        self.treeview.pack(fill="both", expand=True)

    def _validate_numeric_input(self, new_value):
        if new_value == "":  # Allow empty input
            return True
        try:
            value = int(new_value)
            return 1 <= value <= 500
        except ValueError:
            return False

    def _save_inputs(self):
        data = {
            "region": self.region_entry.get(),
            "inventory_space": self.inventory_space_var.get(),
            "detective_level": self.detective_level_var.get(),
            "battle_of_fortunehold": str(self.battle_of_fortunehold_var.get())
        }
        self.db_handler.save_data(data)

    def _load_inputs(self):
        data = self.db_handler.load_data()
        self.region_entry.insert(0, data.get("region", ""))
        self.inventory_space_var.set(data.get("inventory_space", "24"))
        self.detective_level_var.set(data.get("detective_level", ""))
        self.battle_of_fortunehold_var.set(data.get("battle_of_fortunehold", "False") == "True")

    def on_button_click(self):
        self.start_button.config(state=tk.DISABLED)  # Disable button during processing

        # Get the region input
        region_input = self.region_entry.get()
        try:
            if not region_input.strip():  # If the input is empty
                # Set region to full screen
                screen_width, screen_height = pyautogui.size()
                region = (0, 0, screen_width, screen_height)
            else:
                region = tuple(map(int, region_input.split(',')))
                if len(region) != 4 or region[2] <= 0 or region[3] <= 0:
                    raise ValueError("Invalid region dimensions")
        except ValueError:
            print("Invalid region input. Expected format: x,y,width,height")
            self.start_button.config(state=tk.NORMAL)
            return

        # Get inventory space input
        inventory_space = int(self.inventory_space_var.get())

        # Get detective level input
        try:
            detective_level = int(self.detective_level_var.get())
        except ValueError:
            print("Detective level must be a numeric value between 1 and 500")
            self.start_button.config(state=tk.NORMAL)
            return

        # Get Battle of Fortunehold checkbox value
        battle_of_fortunehold_completed = self.battle_of_fortunehold_var.get()

        # Save all inputs to the database
        self._save_inputs()

        # Process the bounties
        self.window.after(100, self.process_bounties, region, detective_level, battle_of_fortunehold_completed, inventory_space)

    def process_bounties(self, region, detective_level, battle_of_fortunehold_completed, inventory_space):
        bounties, result, elapsed_time = self.bounty_processor.process(
            region, detective_level, battle_of_fortunehold_completed, inventory_space
        )
        self.update_results(bounties, result, elapsed_time)
        self.start_button.config(state=tk.NORMAL)

    def update_results(self, bounties, result, elapsed_time):
        # Clear existing rows
        for row in self.treeview.get_children():
            self.treeview.delete(row)

        # Populate results
        if result:
            for action in result.get('actions', []):
                if action['type'] == 'walk':
                    continue
                distance = self._format_time(action['distance'])
                action_type = action['type'] if action['type'] != 'teleport' else 'tp'
                location = action['location']
                self.treeview.insert("", tk.END, values=(distance, action_type, location))

    @staticmethod
    def _format_time(seconds):
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes}m{seconds}s"

    def toggle_visibility(self):
        """Toggle the visibility of the input fields based on the checkbox state."""
        if self.show_inputs_var.get():
            # Show all input fields
            self.region_label.grid(row=1, column=0, sticky="w", padx=5, pady=5)
            self.region_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
            self.inventory_space_label.grid(row=2, column=0, sticky="w", padx=5, pady=5)
            self.inventory_space_dropdown.grid(row=2, column=1, sticky="ew", padx=5, pady=5)
            self.detective_level_label.grid(row=3, column=0, sticky="w", padx=5, pady=5)
            self.detective_level_entry.grid(row=3, column=1, sticky="ew", padx=5, pady=5)
            self.battle_of_fortunehold_label.grid(row=4, column=0, sticky="w", padx=5, pady=5)
            self.battle_of_fortunehold_checkbox.grid(row=4, column=1, sticky="w", padx=5, pady=5)
        else:
            # Hide all input fields
            self.region_label.grid_forget()
            self.region_entry.grid_forget()
            self.inventory_space_label.grid_forget()
            self.inventory_space_dropdown.grid_forget()
            self.detective_level_label.grid_forget()
            self.detective_level_entry.grid_forget()
            self.battle_of_fortunehold_label.grid_forget()
            self.battle_of_fortunehold_checkbox.grid_forget()
