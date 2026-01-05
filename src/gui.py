import customtkinter as ct

ct.set_appearance_mode("System")
ct.set_default_color_theme("blue")

app = ct.CTk()
app.geometry("720x480")
app.title("Voice Changer")

main = ct.CTkScrollableFrame(app, width=700, height=440)
main.pack(padx=10, pady=10, fill="both", expand=True)

state = {}

def get_state(index):
    return state.get(index)
    
def add_toggle(name):
    var = ct.BooleanVar(master=main, value=False)
    state[name] = False

    def on_change(*_):
        state[name] = var.get()

    var.trace_add("write", on_change)
    ct.CTkSwitch(main, text=name, variable=var).pack()

def add_entry(name, default):
    var = ct.StringVar(master=main, value=str(default))
    state[name] = default

    def on_change(*_):
        try:
            state[name] = float(var.get())
        except ValueError:
            pass  # ignore invalid input

    var.trace_add("write", on_change)

    ct.CTkLabel(main, text=name).pack()
    ct.CTkEntry(main, textvariable=var).pack()
