from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
import os
import json
import datetime

# Detect platform (Android or PC)
try:
    from android.storage import primary_external_storage_path
    download_path = os.path.join(primary_external_storage_path(), "Download")
except ImportError:
    download_path = os.path.expanduser("~/Downloads")  # PC path

class PharmacyApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data_file_path = os.path.join(download_path, "pharmacy_data.json")
        self.log_file_path = os.path.join(download_path, "pharmacy_logs.txt")
        self.medicine_stock = {}
        self.load_data()

    def build(self):
        layout = BoxLayout(orientation="vertical")

        title_label = Label(
            text="Cabiabo Senior High School\nMedicine Stock Inventory",
            font_size="20sp",
            bold=True,
            halign="center"
        )
        layout.add_widget(title_label)

        self.add_medicine_button = Button(text="Add Medicine", on_press=self.add_medicine)
        self.check_stock_button = Button(text="Show Stock", on_press=self.show_stock)
        self.edit_medicine_button = Button(text="Edit Medicine", on_press=self.edit_medicine)
        self.get_medicine_button = Button(text="Get Medicine", on_press=self.get_medicine)
        self.delete_medicine_button = Button(text="Delete Medicine", on_press=self.delete_medicine)

        layout.add_widget(self.add_medicine_button)
        layout.add_widget(self.check_stock_button)
        layout.add_widget(self.edit_medicine_button)
        layout.add_widget(self.get_medicine_button)
        layout.add_widget(self.delete_medicine_button)

        return layout

    def load_data(self):
        if os.path.exists(self.data_file_path):
            with open(self.data_file_path, "r") as file:
                self.medicine_stock = json.load(file)

    def save_data(self):
        with open(self.data_file_path, "w") as file:
            json.dump(self.medicine_stock, file, indent=4)

    def show_error(self, message):
        popup = Popup(title="Error", content=Label(text=message), size_hint=(None, None), size=(400, 200))
        popup.open()

    def add_medicine(self, instance):
        content = BoxLayout(orientation="vertical")
        name_input = TextInput(hint_text="Medicine Name")
        qty_input = TextInput(hint_text="Quantity", input_filter="int")
        expiry_input = TextInput(hint_text="Expiry Date (MM/DD/YYYY)")
        save_button = Button(text="Save")

        expiry_input.bind(text=self.format_expiry_date)

        content.add_widget(name_input)
        content.add_widget(qty_input)
        content.add_widget(expiry_input)
        content.add_widget(save_button)

        popup = Popup(title="Add Medicine", content=content, size_hint=(None, None), size=(400, 300))

        def save_medicine(_):
            name = name_input.text.strip()
            qty = int(qty_input.text) if qty_input.text.isdigit() else 0
            expiry = expiry_input.text.strip()

            if not name or qty <= 0 or len(expiry) != 10:
                self.show_error("Invalid input!")
                return

            if name in self.medicine_stock:
                self.show_error("Medicine already exists! Use 'Edit Medicine'.")
                return

            self.medicine_stock[name] = {"quantity": qty, "expiry": expiry}
            self.save_data()
            popup.dismiss()

        save_button.bind(on_press=save_medicine)
        popup.open()

    def format_expiry_date(self, instance, value):
        numbers = [char for char in value if char.isdigit()]
        if len(numbers) >= 2:
            numbers.insert(2, "/")
        if len(numbers) >= 5:
            numbers.insert(5, "/")
        instance.text = "".join(numbers)[:10]  # Limit to MM/DD/YYYY

    def show_stock(self, instance):
        stock_list = "\n".join([
            f"{name}: {data['quantity']} (Exp: {self.format_date(data['expiry'])})"
            for name, data in self.medicine_stock.items()
        ])
        popup = Popup(title="Medicine Stock", content=Label(text=stock_list or "No stock available"), size_hint=(None, None), size=(400, 300))
        popup.open()

    def format_date(self, date_str):
        try:
            date_obj = datetime.datetime.strptime(date_str, "%m/%d/%Y")
            return date_obj.strftime("%B %d, %Y")
        except ValueError:
            return date_str

    def edit_medicine(self, instance):
        content = BoxLayout(orientation="vertical")
        name_input = TextInput(hint_text="Medicine Name")
        qty_input = TextInput(hint_text="New Quantity", input_filter="int")
        expiry_input = TextInput(hint_text="New Expiry Date (MM/DD/YYYY)")
        save_button = Button(text="Update")

        expiry_input.bind(text=self.format_expiry_date)

        content.add_widget(name_input)
        content.add_widget(qty_input)
        content.add_widget(expiry_input)
        content.add_widget(save_button)

        popup = Popup(title="Edit Medicine", content=content, size_hint=(None, None), size=(400, 300))

        def update_medicine(_):
            name = name_input.text.strip()
            if name not in self.medicine_stock:
                self.show_error("Medicine not found!")
                return

            if qty_input.text.isdigit():
                self.medicine_stock[name]["quantity"] = int(qty_input.text)
            if expiry_input.text:
                self.medicine_stock[name]["expiry"] = expiry_input.text
            self.save_data()
            popup.dismiss()

        save_button.bind(on_press=update_medicine)
        popup.open()

    def get_medicine(self, instance):
        content = BoxLayout(orientation="vertical")
        name_input = TextInput(hint_text="Medicine Name")
        qty_input = TextInput(hint_text="Quantity to Get", input_filter="int")
        person_input = TextInput(hint_text="Person Name")
        reason_input = TextInput(hint_text="Reason")
        get_button = Button(text="Get")

        content.add_widget(name_input)
        content.add_widget(qty_input)
        content.add_widget(person_input)
        content.add_widget(reason_input)
        content.add_widget(get_button)

        popup = Popup(title="Get Medicine", content=content, size_hint=(None, None), size=(400, 300))

        def process_get(_):
            name = name_input.text.strip()
            qty = int(qty_input.text) if qty_input.text.isdigit() else 0
            person = person_input.text.strip()
            reason = reason_input.text.strip()

            if name not in self.medicine_stock or qty <= 0 or self.medicine_stock[name]["quantity"] < qty:
                self.show_error("Invalid request!")
                return

            self.medicine_stock[name]["quantity"] -= qty
            self.log_get(name, qty, person, reason)
            self.save_data()
            popup.dismiss()

        get_button.bind(on_press=process_get)
        popup.open()

    def delete_medicine(self, instance):
        content = BoxLayout(orientation="vertical")
        name_input = TextInput(hint_text="Medicine Name")
        button_layout = GridLayout(cols=2, spacing=10)

        yes_button = Button(text="Yes", background_color=(1, 0, 0, 1))
        no_button = Button(text="No", background_color=(0, 1, 0, 1))

        button_layout.add_widget(yes_button)
        button_layout.add_widget(no_button)

        content.add_widget(name_input)
        content.add_widget(button_layout)

        popup = Popup(title="Confirm Deletion", content=content, size_hint=(None, None), size=(400, 200))

        def confirm_delete(_):
            name = name_input.text.strip()
            if name in self.medicine_stock:
                del self.medicine_stock[name]
                self.save_data()
            popup.dismiss()

        yes_button.bind(on_press=confirm_delete)
        no_button.bind(on_press=popup.dismiss)
        popup.open()

    def log_get(self, medicine_name, quantity, person_name, reason):
        with open(self.log_file_path, "a") as file:
            file.write(f"{datetime.datetime.now()} - {person_name} took {quantity} of {medicine_name} (Reason: {reason})\n")

if __name__ == "__main__":
    PharmacyApp().run()
