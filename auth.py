import tkinter as tk
from tkinter import ttk, messagebox
import hashlib
from datetime import datetime
from pymongo import MongoClient
from bson.objectid import ObjectId

# Color and Font Themes
DARK_BG_1 = "#121212"
DARK_BG_2 = "#1E1E1E"
DARK_BG_3 = "#2D2D2D"
ACCENT_COLOR = "#BB86FC"
ACCENT_COLOR_2 = "#3700B3"
TEXT_COLOR = "#FFFFFF"
TEXT_COLOR_2 = "#E0E0E0"
ERROR_COLOR = "#CF6679"
SUCCESS_COLOR = "#03DAC6"

TITLE_FONT = ("Segoe UI", 24, "bold")
HEADER_FONT = ("Segoe UI", 16, "bold")
BODY_FONT = ("Segoe UI", 12)
SMALL_FONT = ("Segoe UI", 10)

class GradientFrame(tk.Canvas):
    def __init__(self, parent, color1=DARK_BG_1, color2=DARK_BG_2, **kwargs):
        tk.Canvas.__init__(self, parent, **kwargs)
        self._color1 = color1
        self._color2 = color2
        self.bind("<Configure>", self._draw_gradient)
        self._draw_gradient()

    def _draw_gradient(self, event=None):
        self.delete("gradient")
        width = self.winfo_width()
        height = self.winfo_height()
        for i in range(height):
            color = self._interpolate(self._color1, self._color2, i/height)
            self.create_line(0, i, width, i, tags=("gradient",), fill=color)
        self.lower("gradient")

    def _interpolate(self, color1, color2, ratio):
        r1, g1, b1 = self._hex_to_rgb(color1)
        r2, g2, b2 = self._hex_to_rgb(color2)
        r = int(r1 + (r2 - r1) * ratio)
        g = int(g1 + (g2 - g1) * ratio)
        b = int(b1 + (b2 - b1) * ratio)
        return self._rgb_to_hex(r, g, b)

    def _hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def _rgb_to_hex(self, r, g, b):
        return f'#{r:02x}{g:02x}{b:02x}'

class AuthWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Expense Tracker - Authentication")
        self.geometry("800x600")
        self.minsize(400, 500)

        self.client = MongoClient("mongodb+srv://<username>:<db-password>@expense-tracker.xvmac2e.mongodb.net/?retryWrites=true&w=majority&appName=expense-tracker")
        self.db = self.client["expense_tracker"]
        self.users_collection = self.db["users"]

        self.gradient = GradientFrame(self, color1=DARK_BG_1, color2=DARK_BG_2)
        self.gradient.pack(fill="both", expand=True)

        self.create_auth_ui()
        self.bind('<Configure>', self.on_resize)

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def on_resize(self, event):
        self.container.place_configure(relx=0.5, rely=0.5, anchor="center",
                                       width=min(400, self.winfo_width() - 40),
                                       height=min(500, self.winfo_height() - 40))
        base_size = min(self.winfo_width(), self.winfo_height())
        title_font_size = max(16, min(24, base_size // 25))
        body_font_size = max(10, min(14, base_size // 50))

        self.header.config(font=("Segoe UI", title_font_size, "bold"))

        for widget in [self.login_username, self.login_password,
                       self.signup_username, self.signup_password, self.signup_confirm]:
            widget.config(font=("Segoe UI", body_font_size))

        for label in [self.login_error, self.signup_error]:
            label.config(font=("Segoe UI", max(8, body_font_size - 2)))

    def create_auth_ui(self):
        self.container = tk.Frame(self.gradient, bg=DARK_BG_2, bd=0)
        self.container.place(relx=0.5, rely=0.5, anchor="center", width=400, height=500)

        self.header = tk.Label(self.container, text="Expense Tracker", font=TITLE_FONT,
                               bg=DARK_BG_2, fg=ACCENT_COLOR)
        self.header.pack(pady=(20, 10))

        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TNotebook', background=DARK_BG_2, borderwidth=0)
        style.configure('TNotebook.Tab', background=DARK_BG_3, foreground=TEXT_COLOR,
                        padding=[10, 5], font=BODY_FONT)
        style.map('TNotebook.Tab', background=[('selected', ACCENT_COLOR_2)],
                  foreground=[('selected', TEXT_COLOR)])

        self.tab_control = ttk.Notebook(self.container, style='TNotebook')

        self.login_tab = tk.Frame(self.tab_control, bg=DARK_BG_2)
        self.signup_tab = tk.Frame(self.tab_control, bg=DARK_BG_2)

        self.tab_control.add(self.login_tab, text="Login")
        self.tab_control.add(self.signup_tab, text="Sign Up")
        self.tab_control.pack(expand=1, fill="both", padx=20, pady=(0, 20))

        self.create_login_form()
        self.create_signup_form()

    def create_login_form(self):
        tk.Label(self.login_tab, text="Username", font=BODY_FONT,
             bg=DARK_BG_2, fg=TEXT_COLOR).pack(pady=(20, 5), anchor="w")

        self.login_username = tk.Entry(self.login_tab, font=BODY_FONT, bg=DARK_BG_3,
                                   fg=TEXT_COLOR, insertbackground=TEXT_COLOR,
                                   borderwidth=0, highlightthickness=1,
                                   highlightbackground=DARK_BG_3, highlightcolor=ACCENT_COLOR)
        self.login_username.pack(fill="x", padx=20, ipady=8, pady=(0, 10))

        tk.Label(self.login_tab, text="Password", font=BODY_FONT,
             bg=DARK_BG_2, fg=TEXT_COLOR).pack(pady=(5, 5), anchor="w")

        pw_frame = tk.Frame(self.login_tab, bg=DARK_BG_2)
        pw_frame.pack(fill="x", padx=20, pady=(0, 10))

        self.login_password = tk.Entry(pw_frame, font=BODY_FONT, show="*",
                                   bg=DARK_BG_3, fg=TEXT_COLOR, insertbackground=TEXT_COLOR,
                                   borderwidth=0, highlightthickness=1,
                                   highlightbackground=DARK_BG_3, highlightcolor=ACCENT_COLOR)
        self.login_password.pack(side="left", fill="x", expand=True, ipady=8)

        self.show_login_pw = False
        self.login_toggle = tk.Button(pw_frame, text="👁", width=4, height=1,
                                  bg=DARK_BG_3, fg=TEXT_COLOR,
                                  bd=0, command=self.toggle_login_password, cursor="hand2")
        self.login_toggle.pack(side="right", ipady=8)

        login_btn = tk.Button(self.login_tab, text="Login", font=BODY_FONT,
                          bg=ACCENT_COLOR_2, fg=TEXT_COLOR,
                          activebackground=ACCENT_COLOR,
                          activeforeground=TEXT_COLOR, borderwidth=0,
                          relief="flat", cursor="hand2",
                          command=self.handle_login)
        login_btn.pack(fill="x", padx=20, pady=(10, 5), ipady=10)

        self.login_error = tk.Label(self.login_tab, text="", font=SMALL_FONT,
                                bg=DARK_BG_2, fg=ERROR_COLOR)
        self.login_error.pack(pady=(5, 0))

        # Login tab footer link
        switch_label = tk.Label(self.login_tab, text="Not a user? Register here",
                            fg=ACCENT_COLOR, bg=DARK_BG_2,
                            cursor="hand2", font=SMALL_FONT)
        switch_label.pack(pady=(10, 10))
        switch_label.bind("<Button-1>", lambda e: self.tab_control.select(self.signup_tab))


    def create_signup_form(self):
        tk.Label(self.signup_tab, text="Username", font=BODY_FONT,
             bg=DARK_BG_2, fg=TEXT_COLOR).pack(pady=(15, 5), anchor="w")

        self.signup_username = tk.Entry(self.signup_tab, font=("Segoe UI", 10), bg=DARK_BG_3,
                                    fg=TEXT_COLOR, insertbackground=TEXT_COLOR,
                                    borderwidth=0, highlightthickness=1,
                                    highlightbackground=DARK_BG_3, highlightcolor=ACCENT_COLOR)
        self.signup_username.pack(fill="x", padx=20, ipady=6, pady=(0, 10))

        tk.Label(self.signup_tab, text="Password", font=BODY_FONT,
             bg=DARK_BG_2, fg=TEXT_COLOR).pack(pady=(5, 5), anchor="w")

        pw_frame = tk.Frame(self.signup_tab, bg=DARK_BG_2)
        pw_frame.pack(fill="x", padx=20, pady=(0, 10))

        self.signup_password = tk.Entry(pw_frame, font=("Segoe UI", 10), show="*",
                                    bg=DARK_BG_3, fg=TEXT_COLOR, insertbackground=TEXT_COLOR,
                                    borderwidth=0, highlightthickness=1,
                                    highlightbackground=DARK_BG_3, highlightcolor=ACCENT_COLOR)
        self.signup_password.pack(side="left", fill="x", expand=True, ipady=6)

        self.show_signup_pw = False
        self.signup_toggle = tk.Button(pw_frame, text="👁", width=4, height=1,
                                   bg=DARK_BG_3, fg=TEXT_COLOR,
                                   bd=0, command=self.toggle_signup_password, cursor="hand2")
        self.signup_toggle.pack(side="right", ipady=6)

        tk.Label(self.signup_tab, text="Confirm Password", font=BODY_FONT,
             bg=DARK_BG_2, fg=TEXT_COLOR).pack(pady=(5, 5), anchor="w")

        cpw_frame = tk.Frame(self.signup_tab, bg=DARK_BG_2)
        cpw_frame.pack(fill="x", padx=20, pady=(0, 10))

        self.signup_confirm = tk.Entry(cpw_frame, font=("Segoe UI", 10), show="*",
                                   bg=DARK_BG_3, fg=TEXT_COLOR, insertbackground=TEXT_COLOR,
                                   borderwidth=0, highlightthickness=1,
                                   highlightbackground=DARK_BG_3, highlightcolor=ACCENT_COLOR)
        self.signup_confirm.pack(side="left", fill="x", expand=True, ipady=6)

        self.show_confirm_pw = False
        self.confirm_toggle = tk.Button(cpw_frame, text="👁", width=4, height=1,
                                    bg=DARK_BG_3, fg=TEXT_COLOR,
                                    bd=0, command=self.toggle_confirm_password, cursor="hand2")
        self.confirm_toggle.pack(side="right", ipady=6)

        signup_btn = tk.Button(self.signup_tab, text="Sign Up", font=("Segoe UI", 12),
                           bg=ACCENT_COLOR_2, fg=TEXT_COLOR,
                           activebackground=ACCENT_COLOR,
                           activeforeground=TEXT_COLOR, borderwidth=0,
                           relief="flat", cursor="hand2",
                           command=self.handle_signup)
        signup_btn.pack(fill="x", padx=20, pady=(10, 0), ipady=3)

        self.signup_error = tk.Label(self.signup_tab, text="", font=SMALL_FONT,
                                 bg=DARK_BG_2, fg=ERROR_COLOR)
        self.signup_error.pack(pady=(5, 0))

        # Signup tab footer link
        switch_label = tk.Label(self.signup_tab, text="Already a user? Login here",
                            fg=ACCENT_COLOR, bg=DARK_BG_2,
                            cursor="hand2", font=SMALL_FONT)
        switch_label.pack(pady=(0, 0))
        switch_label.bind("<Button-1>", lambda e: self.tab_control.select(self.login_tab))

    # Add these toggle methods in your AuthWindow class
    def toggle_login_password(self):
        self.show_login_pw = not self.show_login_pw
        self.login_password.config(show="" if self.show_login_pw else "*")
        self.login_toggle.config(text="🙈" if self.show_login_pw else "👁")

    def toggle_signup_password(self):
        self.show_signup_pw = not self.show_signup_pw
        self.signup_password.config(show="" if self.show_signup_pw else "*")
        self.signup_toggle.config(text="🙈" if self.show_signup_pw else "👁")

    def toggle_confirm_password(self):
        self.show_confirm_pw = not self.show_confirm_pw
        self.signup_confirm.config(show="" if self.show_confirm_pw else "*")
        self.confirm_toggle.config(text="🙈" if self.show_confirm_pw else "👁")

    def handle_login(self):
        username = self.login_username.get().strip()
        password = self.login_password.get().strip()

        if not username or not password:
            self.login_error.config(text="Please enter both username and password")
            return

        try:
            user = self.users_collection.find_one({"username": username})
            if not user:
                self.login_error.config(text="Username not found. Redirecting to Sign Up...")
                self.after(1500, lambda: self.tab_control.select(self.signup_tab))
                return

            hashed_password = self.hash_password(password)
            if user["password"] != hashed_password:
                self.login_error.config(text="Incorrect password")
                return

            self.destroy()
            from main_app import ExpenseTrackerApp
            ExpenseTrackerApp(username)

        except Exception as e:
            self.login_error.config(text=f"Error: {str(e)}")
            messagebox.showerror("Login Failed", str(e), parent=self)

    def handle_signup(self):
        username = self.signup_username.get().strip()
        password = self.signup_password.get().strip()
        confirm = self.signup_confirm.get().strip()

        if not username or not password or not confirm:
            self.signup_error.config(text="Please fill all fields")
            return

        if password != confirm:
            self.signup_error.config(text="Passwords don't match")
            return

        if len(password) < 6:
            self.signup_error.config(text="Password must be at least 6 characters")
            return

        if self.users_collection.find_one({"username": username}):
            self.signup_error.config(text="Username already exists")
            return

        new_user = {
            "username": username,
            "password": self.hash_password(password),
            "created_at": datetime.now(),
            "expenses": [],
            "budgets": {}
        }

        try:
            self.users_collection.insert_one(new_user)
            self.signup_error.config(text="Account created successfully!", fg=SUCCESS_COLOR)
            self.tab_control.select(self.login_tab)
            self.signup_username.delete(0, tk.END)
            self.signup_password.delete(0, tk.END)
            self.signup_confirm.delete(0, tk.END)
        except Exception as e:
            self.signup_error.config(text=f"Error: {str(e)}")

if __name__ == '__main__':
    auth = AuthWindow()
    auth.mainloop()
