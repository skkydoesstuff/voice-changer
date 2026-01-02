import customtkinter as ct

ct.set_appearance_mode("System")
ct.set_default_color_theme("blue")

app = ct.CTk()
app.geometry("720x480")
app.title("Voice Changer")

state = {}

def add_toggle(name):
    var = ct.BooleanVar(master=app, value=False)
    state[name] = False

    def on_change(*_):
        state[name] = var.get()

    var.trace_add("write", on_change)
    ct.CTkSwitch(app, text=name, variable=var).pack()

def add_entry(name, default):
    var = ct.StringVar(master=app, value=str(default))
    state[name] = default

    def on_change(*_):
        try:
            state[name] = float(var.get())
        except ValueError:
            pass  # ignore invalid input

    var.trace_add("write", on_change)

    ct.CTkEntry(app, textvariable=var).pack()
    ct.CTkLabel(app, text=name).pack()
