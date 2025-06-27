import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from pymongo import MongoClient
from bson.objectid import ObjectId
try:
    from auth import (
        GradientFrame, DARK_BG_1, DARK_BG_2, DARK_BG_3, 
        ACCENT_COLOR, ACCENT_COLOR_2, TEXT_COLOR, TEXT_COLOR_2, 
        ERROR_COLOR, SUCCESS_COLOR, WARNING_COLOR,
        TITLE_FONT, HEADER_FONT, BODY_FONT, SMALL_FONT
    )
except ImportError:
    # Define fallback constants if needed
    DARK_BG_1 = "#121212"
    DARK_BG_2 = "#1E1E1E"
    DARK_BG_3 = "#2D2D2D"
    ACCENT_COLOR = "#BB86FC"
    ACCENT_COLOR_2 = "#3700B3"
    TEXT_COLOR = "#FFFFFF"
    TEXT_COLOR_2 = "#E0E0E0"
    ERROR_COLOR = "#CF6679"
    SUCCESS_COLOR = "#03DAC6"
    WARNING_COLOR = "#FFA000"
    TITLE_FONT = ("Segoe UI", 24, "bold")
    HEADER_FONT = ("Segoe UI", 16, "bold")
    BODY_FONT = ("Segoe UI", 12)
    SMALL_FONT = ("Segoe UI", 10)

class ExpenseTrackerApp(tk.Tk):
    """Main Expense Tracker Application with MongoDB backend"""
    def __init__(self, username):
        super().__init__()
        self.username = username
        
        # Connect to MongoDB
        self.client = MongoClient("mongodb+srv://<username>:<db-password>@expense-tracker.xvmac2e.mongodb.net/?retryWrites=true&w=majority&appName=expense-tracker")
        self.db = self.client["expense_tracker"]
        self.users_collection = self.db["users"]
        
        # Initialize data
        self.expense_categories = ['Food', 'Transport', 'Entertainment', 
                                 'Utilities', 'Shopping', 'Healthcare', 'Education', 'Other']
        
        # Setup UI
        self.setup_ui()
        
        # Start with dashboard
        self.show_dashboard()
        
        # Configure matplotlib style
        plt.style.use('dark_background')
        plt.rcParams['axes.facecolor'] = DARK_BG_3
        plt.rcParams['figure.facecolor'] = DARK_BG_2
        plt.rcParams['text.color'] = TEXT_COLOR
        plt.rcParams['axes.labelcolor'] = TEXT_COLOR
        plt.rcParams['xtick.color'] = TEXT_COLOR
        plt.rcParams['ytick.color'] = TEXT_COLOR
        plt.rcParams['axes.titlecolor'] = TEXT_COLOR
        plt.rcParams['axes.edgecolor'] = TEXT_COLOR_2
    
    def get_user_data(self):
        """Get current user's data from MongoDB"""
        return self.users_collection.find_one({"username": self.username})
    
    def get_expenses(self):
        """Get expenses for current user"""
        user_data = self.get_user_data()
        return user_data.get("expenses", [])
    
    def get_budgets(self):
        """Get budgets for current user"""
        user_data = self.get_user_data()
        return user_data.get("budgets", {})
    
    def add_expense_to_db(self, expense_data):
        """Add new expense to MongoDB"""
        self.users_collection.update_one(
            {"username": self.username},
            {"$push": {"expenses": expense_data}}
        )
    
    def update_expense_in_db(self, expense_id, new_data):
        """Update existing expense in MongoDB"""
        self.users_collection.update_one(
            {"username": self.username, "expenses._id": ObjectId(expense_id)},
            {"$set": {"expenses.$": new_data}}
        )
    
    def delete_expense_from_db(self, expense_id):
        """Delete expense from MongoDB"""
        self.users_collection.update_one(
            {"username": self.username},
            {"$pull": {"expenses": {"_id": ObjectId(expense_id)}}}
        )
    
    def update_budgets_in_db(self, budgets):
        """Update budgets in MongoDB"""
        self.users_collection.update_one(
            {"username": self.username},
            {"$set": {"budgets": budgets}}
        )
    
    def setup_ui(self):
        """Setup the main application UI with modern styling"""
        self.title(f"Expense Tracker - {self.username}")
        self.geometry("1200x750")
        self.minsize(1000, 650)
        
        # Configure grid layout
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        # Sidebar with sliding animation
        self.sidebar = tk.Frame(self, bg=DARK_BG_2, width=250)
        self.sidebar.grid(row=0, column=0, sticky="ns")
        
        # Main content area with gradient background
        self.main_content = GradientFrame(self, color1=DARK_BG_1, color2=DARK_BG_2)
        self.main_content.grid(row=0, column=1, sticky="nsew")
        
        # Create sidebar widgets
        self.create_sidebar()
        
        # Header stats
        self.create_header_stats()
        
        # Configure styles
        self.configure_styles()
    
    def configure_styles(self):
        """Configure ttk styles for the application"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure Treeview style
        style.configure("Treeview", 
                        background=DARK_BG_3,
                        foreground=TEXT_COLOR,
                        rowheight=25,
                        fieldbackground=DARK_BG_3,
                        borderwidth=0)
        style.map('Treeview', background=[('selected', ACCENT_COLOR_2)])
        
        style.configure("Treeview.Heading", 
                       background=DARK_BG_2,
                       foreground=TEXT_COLOR,
                       relief="flat",
                       font=BODY_FONT)
        style.map("Treeview.Heading", 
                 background=[('active', DARK_BG_3)])
        
        # Configure Combobox style
        style.configure('TCombobox', 
                       background=DARK_BG_3,
                       foreground=TEXT_COLOR,
                       fieldbackground=DARK_BG_3,
                       selectbackground=ACCENT_COLOR_2,
                       selectforeground=TEXT_COLOR,
                       borderwidth=0,
                       arrowsize=15)
        style.map('TCombobox', 
                 fieldbackground=[('readonly', DARK_BG_3)],
                 selectbackground=[('readonly', ACCENT_COLOR_2)])
        
        # Configure Notebook style
        style.configure('TNotebook', background=DARK_BG_2, borderwidth=0)
        style.configure('TNotebook.Tab', 
                      background=DARK_BG_3,
                      foreground=TEXT_COLOR,
                      padding=[10, 5],
                      font=BODY_FONT)
        style.map('TNotebook.Tab', 
                 background=[('selected', ACCENT_COLOR_2)],
                 foreground=[('selected', TEXT_COLOR)])
    
    def create_sidebar(self):
        """Create sidebar navigation with modern styling"""
        # User info
        user_frame = tk.Frame(self.sidebar, bg=DARK_BG_2, pady=20)
        user_frame.pack(fill="x")
        
        tk.Label(user_frame, text=self.username, font=HEADER_FONT, 
             bg=DARK_BG_2, fg=TEXT_COLOR).pack(pady=(0, 5))
        
        current_month = datetime.now().strftime("%B %Y")
        tk.Label(user_frame, text=current_month, font=SMALL_FONT, 
             bg=DARK_BG_2, fg=ACCENT_COLOR).pack()
        
        # Navigation buttons
        nav_buttons = [
            ("Dashboard", "📊", self.show_dashboard),
            ("Add Expense", "➕", self.show_add_expense),
            ("View Expenses", "📝", self.show_view_expenses),
            ("Budget", "💰", self.show_budget),
            ("Reports", "📈", self.show_reports),
            ("Logout", "🚪", self.logout)
        ]
        
        for text, icon, command in nav_buttons:
            btn = tk.Button(self.sidebar, text=f"{icon}  {text}", font=BODY_FONT, 
                        bg=DARK_BG_2, fg=TEXT_COLOR, 
                        activebackground=DARK_BG_3,
                        activeforeground=TEXT_COLOR, 
                        borderwidth=0, anchor="w",
                        relief="flat", cursor="hand2",
                        command=command)
            btn.pack(fill="x", padx=10, pady=5, ipady=10)
        
        # Add a separator
        separator = tk.Frame(self.sidebar, height=2, bg=DARK_BG_3)
        separator.pack(fill="x", padx=10, pady=10)
        
        # Quick stats
        stats_frame = tk.Frame(self.sidebar, bg=DARK_BG_2, padx=10, pady=10)
        stats_frame.pack(fill="x")
        
        tk.Label(stats_frame, text="Quick Stats", font=SMALL_FONT, 
             bg=DARK_BG_2, fg=TEXT_COLOR_2).pack(anchor="w", pady=(0, 10))
        
        # Monthly spending
        self.sidebar_monthly = tk.Label(stats_frame, text="This Month: $0.00", 
                                   font=SMALL_FONT, bg=DARK_BG_2, fg=TEXT_COLOR)
        self.sidebar_monthly.pack(anchor="w", pady=(0, 5))
        
        # Top category
        self.sidebar_category = tk.Label(stats_frame, text="Top Category: None", 
                                    font=SMALL_FONT, bg=DARK_BG_2, fg=TEXT_COLOR)
        self.sidebar_category.pack(anchor="w", pady=(0, 5))
        
        # Budget status
        self.sidebar_budget = tk.Label(stats_frame, text="Budget: No Data", 
                                  font=SMALL_FONT, bg=DARK_BG_2, fg=TEXT_COLOR)
        self.sidebar_budget.pack(anchor="w", pady=(0, 5))
        
        # Update sidebar stats
        self.update_sidebar_stats()
    
    def update_sidebar_stats(self):
        """Update the sidebar statistics"""
        try:
            expenses = self.get_expenses()
            if expenses:
                # Convert to DataFrame for easier calculations
                import pandas as pd
                df = pd.DataFrame(expenses)
                df['date'] = pd.to_datetime(df['date'])
            
                # Monthly expenses
                current_month = datetime.now().strftime("%Y-%m")
                monthly = df[df['date'].dt.strftime("%Y-%m") == current_month]['amount'].sum()
                self.sidebar_monthly.config(text=f"This Month: ${monthly:.2f}")
            
                # Top category
                if not df.empty:
                    top_category = df.groupby("category")['amount'].sum().idxmax()
                    self.sidebar_category.config(text=f"Top Category: {top_category}")
                else:
                    self.sidebar_category.config(text="Top Category: None")
            
                # Budget status
                budgets = self.get_budgets()
                if budgets:
                    total_budget = sum(budgets.values())
                    if monthly > total_budget:
                        self.sidebar_budget.config(text="Budget: Over", fg=ERROR_COLOR)
                    else:
                        self.sidebar_budget.config(text="Budget: Within", fg=SUCCESS_COLOR)
                else:
                    self.sidebar_budget.config(text="Budget: Not Set", fg=TEXT_COLOR_2)
        
            # Force update the UI
            self.sidebar.update_idletasks()
        except Exception as e:
            print(f"Error updating sidebar stats: {e}")
    
    def create_header_stats(self):
        """Create header statistics cards with modern styling"""
        header_frame = tk.Frame(self.main_content, bg=DARK_BG_2, padx=20, pady=20)
        header_frame.pack(fill="x")
    
        # Container for cards
        cards_container = tk.Frame(header_frame, bg=DARK_BG_2)
        cards_container.pack(fill="x")
    
        # Initialize stat_labels dictionary here
        self.stat_labels = {}

        # Total Expenses card
        self.total_card = self.create_stat_card(cards_container, "Total Expenses", "$0.00", ACCENT_COLOR)
        self.total_card.pack(side="left", fill="x", expand=True, padx=5)

        # Monthly Expenses card
        self.monthly_card = self.create_stat_card(cards_container, "This Month", "$0.00", "#4CAF50")
        self.monthly_card.pack(side="left", fill="x", expand=True, padx=5)

        # Top Category card
        self.category_card = self.create_stat_card(cards_container, "Top Category", "None", "#2196F3")
        self.category_card.pack(side="left", fill="x", expand=True, padx=5)

        # Budget Status card
        self.budget_card = self.create_stat_card(cards_container, "Budget Status", "No Budget", "#FF9800")
        self.budget_card.pack(side="left", fill="x", expand=True, padx=5)

        # Update stats
        self.update_stats()
    
    def create_stat_card(self, parent, title, value, color):
        """Create a modern statistic card"""
        card = tk.Frame(parent, bg=DARK_BG_3, padx=15, pady=15, 
                    highlightbackground=DARK_BG_3, highlightthickness=1)

        # Title
        tk.Label(card, text=title, font=SMALL_FONT, 
             bg=DARK_BG_3, fg=TEXT_COLOR_2).pack(anchor="w", pady=(0, 5))

        # Value with color accent
        value_frame = tk.Frame(card, bg=DARK_BG_3)
        value_frame.pack(anchor="w")

        # Colored dot
        dot = tk.Frame(value_frame, bg=color, width=10, height=10)
        dot.pack(side="left", padx=(0, 10))

        label = tk.Label(value_frame, text=value, font=HEADER_FONT, 
                     bg=DARK_BG_3, fg=TEXT_COLOR)
        label.pack(side="left")

        # Store label for updating
        self.stat_labels[title] = label

        return card

    
    def update_stats(self):
        """Update the header statistics"""
        expenses = self.get_expenses()
        if expenses:
            import pandas as pd
            df = pd.DataFrame(expenses)
            df['date'] = pd.to_datetime(df['date'])
            
            # Total expenses
            total = df['amount'].sum()
            self.stat_labels["Total Expenses"].config(text=f"${total:.2f}")
            
            # Monthly expenses
            current_month = datetime.now().strftime("%Y-%m")
            monthly = df[df['date'].dt.strftime("%Y-%m") == current_month]['amount'].sum()
            self.stat_labels["This Month"].config(text=f"${monthly:.2f}")
            
            # Top category
            top_category = df.groupby("category")['amount'].sum().idxmax()
            self.stat_labels["Top Category"].config(text=top_category)
            
            # Budget status
            budgets = self.get_budgets()
            if budgets:
                total_budget = sum(budgets.values())
                if monthly > total_budget:
                    self.stat_labels["Budget Status"].config(text="Over Budget", fg=ERROR_COLOR)
                else:
                    self.stat_labels["Budget Status"].config(text="Within Budget", fg=SUCCESS_COLOR)
            else:
                self.stat_labels["Budget Status"].config(text="No Budget Set", fg=TEXT_COLOR_2)
        
        # Update sidebar stats as well
        self.update_sidebar_stats()
    
    def clear_main_content(self):
        """Clear the main content area except header"""
        for widget in self.main_content.winfo_children():
            if widget not in [child for child in self.main_content.winfo_children() 
                            if isinstance(child, tk.Frame) and child.winfo_children()[0] in self.main_content.winfo_children()]:
                widget.destroy()
    
    def show_dashboard(self):
        """Show interactive dashboard view"""
        self.clear_main_content()

        # Main container with scrollbar
        container = tk.Frame(self.main_content, bg=DARK_BG_2)
        container.pack(fill="both", expand=True)
        
        # Create a canvas and scrollbar
        canvas = tk.Canvas(container, bg=DARK_BG_2, highlightthickness=0)
        scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=DARK_BG_2)

        self.stat_labels = {}

        header_frame = tk.Frame(scrollable_frame, bg=DARK_BG_2, padx=20, pady=20)
        header_frame.pack(fill="x")

        cards_container = tk.Frame(header_frame, bg=DARK_BG_2)
        cards_container.pack(fill="x")

        self.total_card = self.create_stat_card(cards_container, "Total Expenses", "$0.00", ACCENT_COLOR)
        self.total_card.pack(side="left", fill="x", expand=True, padx=5)

        self.monthly_card = self.create_stat_card(cards_container, "This Month", "$0.00", "#4CAF50")
        self.monthly_card.pack(side="left", fill="x", expand=True, padx=5)

        self.category_card = self.create_stat_card(cards_container, "Top Category", "None", "#2196F3")
        self.category_card.pack(side="left", fill="x", expand=True, padx=5)

        self.budget_card = self.create_stat_card(cards_container, "Budget Status", "No Budget", "#FF9800")
        self.budget_card.pack(side="left", fill="x", expand=True, padx=5)

        # Update the header stats
        self.update_stats()
        
        # Configure the canvas
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        # Pack everything
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        # Make mouse wheel scroll
        scrollable_frame.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", 
            lambda event: canvas.yview_scroll(int(-1*(event.delta/120)), "units")))
        scrollable_frame.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))
        
        # Recent transactions
        recent_frame = tk.Frame(scrollable_frame, bg=DARK_BG_2, padx=20, pady=10)
        recent_frame.pack(fill="x")
        
        tk.Label(recent_frame, text="Recent Transactions", font=HEADER_FONT, 
             bg=DARK_BG_2, fg=TEXT_COLOR).pack(anchor="w", pady=(0, 10))
        
        # Transaction list with modern styling
        self.transaction_list = tk.Listbox(recent_frame, bg=DARK_BG_3, fg=TEXT_COLOR, 
                                      selectbackground=ACCENT_COLOR_2, font=BODY_FONT,
                                      borderwidth=0, highlightthickness=0,
                                      activestyle="none")
        self.transaction_list.pack(fill="x", expand=True, ipady=5)
        
        # Add scrollbar
        list_scrollbar = tk.Scrollbar(recent_frame, orient="vertical")
        list_scrollbar.config(command=self.transaction_list.yview)
        list_scrollbar.pack(side="right", fill="y")
        self.transaction_list.config(yscrollcommand=list_scrollbar.set)
        
        # Add recent transactions with alternating colors
        expenses = sorted(self.get_expenses(), key=lambda x: x['date'], reverse=True)[:10]
        for i, expense in enumerate(expenses):
            bg_color = DARK_BG_3 if i % 2 == 0 else DARK_BG_2
            self.transaction_list.insert("end", 
                f"{expense['date'].strftime('%Y-%m-%d')} | {expense['category']} | ${expense['amount']:.2f} | {expense.get('description', '')}")
            self.transaction_list.itemconfig("end", {'bg': bg_color})
        
        # Charts frame
        charts_frame = tk.Frame(scrollable_frame, bg=DARK_BG_2, padx=20, pady=10)
        charts_frame.pack(fill="x")
        
        # Monthly spending chart
        monthly_chart_frame = tk.Frame(charts_frame, bg=DARK_BG_2)
        monthly_chart_frame.pack(side="left", fill="both", expand=True, padx=5)
        
        tk.Label(monthly_chart_frame, text="Monthly Spending", font=BODY_FONT, 
             bg=DARK_BG_2, fg=TEXT_COLOR).pack()
        
        self.monthly_chart_canvas = tk.Canvas(monthly_chart_frame, bg=DARK_BG_2, 
                                         highlightthickness=0)
        self.monthly_chart_canvas.pack(fill="both", expand=True, pady=(5, 0))
        
        # Category breakdown chart
        category_chart_frame = tk.Frame(charts_frame, bg=DARK_BG_2)
        category_chart_frame.pack(side="left", fill="both", expand=True, padx=5)
        
        tk.Label(category_chart_frame, text="Category Breakdown", font=BODY_FONT, 
             bg=DARK_BG_2, fg=TEXT_COLOR).pack()
        
        self.category_chart_canvas = tk.Canvas(category_chart_frame, bg=DARK_BG_2, 
                                          highlightthickness=0)
        self.category_chart_canvas.pack(fill="both", expand=True, pady=(5, 0))
        
        # Budget progress frame
        budget_frame = tk.Frame(scrollable_frame, bg=DARK_BG_2, padx=20, pady=10)
        budget_frame.pack(fill="x")
        
        tk.Label(budget_frame, text="Budget Progress", font=HEADER_FONT, 
             bg=DARK_BG_2, fg=TEXT_COLOR).pack(anchor="w", pady=(0, 10))
        
        self.budget_progress_canvas = tk.Canvas(budget_frame, bg=DARK_BG_2, highlightthickness=0)
        self.budget_progress_canvas.pack(fill="x", expand=True, pady=(5, 0))
        
        # Update charts
        self.update_charts()
    
    def update_charts(self):
        """Update dashboard charts with better visibility"""
        # Clear previous charts
        for widget in self.monthly_chart_canvas.winfo_children():
            widget.destroy()
        for widget in self.category_chart_canvas.winfo_children():
            widget.destroy()
        for widget in self.budget_progress_canvas.winfo_children():
            widget.destroy()
    
        expenses = self.get_expenses()
        if not expenses:
            tk.Label(self.monthly_chart_canvas, text="No data available", 
                font=BODY_FONT, bg=DARK_BG_2, fg=TEXT_COLOR).pack(fill="both", expand=True)
            tk.Label(self.category_chart_canvas, text="No data available", 
                font=BODY_FONT, bg=DARK_BG_2, fg=TEXT_COLOR).pack(fill="both", expand=True)
            tk.Label(self.budget_progress_canvas, text="No budget data available", 
                font=BODY_FONT, bg=DARK_BG_2, fg=TEXT_COLOR).pack(fill="x", expand=True)
            return
    
        import pandas as pd
        df = pd.DataFrame(expenses)
        df['date'] = pd.to_datetime(df['date'])
    
        # Monthly spending chart - smaller size
        fig1, ax1 = plt.subplots(figsize=(4, 2.5))  # Reduced from (5, 3)
    
        df["Month"] = df["date"].dt.to_period("M")
        monthly_data = df.groupby("Month")["amount"].sum()
    
        ax1.plot(monthly_data.index.astype(str), monthly_data.values, 
            color=ACCENT_COLOR, marker="o", linewidth=2)
        ax1.set_title("Monthly Spending", color=TEXT_COLOR, fontsize=10)  # Smaller font
        ax1.set_ylabel("Amount ($)", color=TEXT_COLOR, fontsize=8)
    
        # Style the chart
        ax1.set_facecolor(DARK_BG_3)
        fig1.patch.set_facecolor(DARK_BG_2)
        for spine in ax1.spines.values():
            spine.set_color(TEXT_COLOR_2)
        ax1.tick_params(axis='x', colors=TEXT_COLOR, rotation=45, labelsize=8)
        ax1.tick_params(axis='y', colors=TEXT_COLOR, labelsize=8)
        ax1.grid(color=DARK_BG_3, linestyle='--', alpha=0.5)
    
        # Embed in Tkinter with tight layout
        canvas1 = FigureCanvasTkAgg(fig1, master=self.monthly_chart_canvas)
        canvas1.draw()
        canvas1.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)
        fig1.tight_layout()
    
        # Category breakdown chart - smaller size
        fig2, ax2 = plt.subplots(figsize=(4, 2.5))  # Reduced from (5, 3)
    
        category_data = df.groupby("category")["amount"].sum()
        colors = plt.cm.tab20.colors[:len(category_data)]
        explode = [0.05] * len(category_data)
    
        wedges, texts, autotexts = ax2.pie(category_data, 
                                     labels=category_data.index, 
                                     autopct="%1.1f%%",
                                     startangle=90, 
                                     colors=colors, 
                                     explode=explode,
                                     textprops={"color": TEXT_COLOR, "fontsize": 8},
                                     wedgeprops={"edgecolor": DARK_BG_2, "linewidth": 1})
    
        ax2.set_title("Category Breakdown", color=TEXT_COLOR, fontsize=10)
    
        # Make autopct text more visible
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(8)
    
        # Embed in Tkinter with tight layout
        canvas2 = FigureCanvasTkAgg(fig2, master=self.category_chart_canvas)
        canvas2.draw()
        canvas2.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)
        fig2.tight_layout()
    
        # Budget progress chart - smaller size
        budgets = self.get_budgets()
        if budgets:
            fig3, ax3 = plt.subplots(figsize=(8, 1.5))  # Reduced from (10, 2)
        
            current_month = datetime.now().strftime("%Y-%m")
            monthly_spending = df[
                df["date"].dt.strftime("%Y-%m") == current_month
            ].groupby("category")["amount"].sum()
        
            # Prepare data for comparison
            categories = list(budgets.keys())
            budget_amounts = [budgets[cat] for cat in categories]
            spent = [monthly_spending.get(cat, 0) for cat in categories]
            remaining = [max(0, budget - spent[i]) for i, budget in enumerate(budget_amounts)]
        
            # Create stacked bar chart
            bar_width = 0.6
            index = range(len(categories))
        
            ax3.bar(index, spent, bar_width, color=ACCENT_COLOR, label='Spent')
            ax3.bar(index, remaining, bar_width, bottom=spent, color=SUCCESS_COLOR, label='Remaining')
        
            # Style the chart
            ax3.set_facecolor(DARK_BG_3)
            fig3.patch.set_facecolor(DARK_BG_2)
            ax3.set_title("Budget Progress", color=TEXT_COLOR, fontsize=10)
            ax3.set_xticks(index)
            ax3.set_xticklabels(categories, rotation=45, color=TEXT_COLOR, fontsize=8)
            ax3.tick_params(axis='y', colors=TEXT_COLOR, fontsize=8)
        
            # Add value labels
            for i, (s, r) in enumerate(zip(spent, remaining)):
                total = s + r
                if total > 0:
                    ax3.text(i, s/2, f"${s:.0f}", ha='center', va='center', color='white', fontsize=8)
                    ax3.text(i, s + r/2, f"${r:.0f}", ha='center', va='center', color='white', fontsize=8)
        
            ax3.legend(facecolor=DARK_BG_3, labelcolor=TEXT_COLOR, fontsize=8)
        
            # Embed in Tkinter with tight layout
            canvas3 = FigureCanvasTkAgg(fig3, master=self.budget_progress_canvas)
            canvas3.draw()
            canvas3.get_tk_widget().pack(fill="x", expand=True, padx=5, pady=5)
            fig3.tight_layout()
    
    def show_add_expense(self):
        """Show add expense form with modern styling"""
        self.clear_main_content()
        
        form_frame = tk.Frame(self.main_content, bg=DARK_BG_2, padx=20, pady=20)
        form_frame.pack(fill="both", expand=True)
        
        tk.Label(form_frame, text="Add New Expense", font=HEADER_FONT, 
             bg=DARK_BG_2, fg=TEXT_COLOR).pack(anchor="w", pady=(0, 20))
        
        # Date
        tk.Label(form_frame, text="Date", font=BODY_FONT, 
             bg=DARK_BG_2, fg=TEXT_COLOR).pack(anchor="w", pady=(0, 5))
        
        self.expense_date = tk.Entry(form_frame, font=BODY_FONT, bg=DARK_BG_3, 
                                fg=TEXT_COLOR, insertbackground=TEXT_COLOR, 
                                borderwidth=0, highlightthickness=1,
                                highlightbackground=DARK_BG_3,
                                highlightcolor=ACCENT_COLOR)
        self.expense_date.pack(fill="x", pady=(0, 15), ipady=8)
        self.expense_date.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        # Category
        tk.Label(form_frame, text="Category", font=BODY_FONT, 
             bg=DARK_BG_2, fg=TEXT_COLOR).pack(anchor="w", pady=(0, 5))
        
        self.expense_category = ttk.Combobox(form_frame, values=self.expense_categories, 
                                           font=BODY_FONT)
        self.expense_category.pack(fill="x", pady=(0, 15), ipady=8)
        
        # Amount
        tk.Label(form_frame, text="Amount", font=BODY_FONT, 
             bg=DARK_BG_2, fg=TEXT_COLOR).pack(anchor="w", pady=(0, 5))
        
        self.expense_amount = tk.Entry(form_frame, font=BODY_FONT, bg=DARK_BG_3, 
                                  fg=TEXT_COLOR, insertbackground=TEXT_COLOR,
                                  borderwidth=0, highlightthickness=1,
                                  highlightbackground=DARK_BG_3,
                                  highlightcolor=ACCENT_COLOR)
        self.expense_amount.pack(fill="x", pady=(0, 15), ipady=8)
        
        # Description
        tk.Label(form_frame, text="Description", font=BODY_FONT, 
             bg=DARK_BG_2, fg=TEXT_COLOR).pack(anchor="w", pady=(0, 5))
        
        self.expense_desc = tk.Entry(form_frame, font=BODY_FONT, bg=DARK_BG_3, 
                                fg=TEXT_COLOR, insertbackground=TEXT_COLOR,
                                borderwidth=0, highlightthickness=1,
                                highlightbackground=DARK_BG_3,
                                highlightcolor=ACCENT_COLOR)
        self.expense_desc.pack(fill="x", pady=(0, 20), ipady=8)
        
        # Add button with modern styling
        add_btn = tk.Button(form_frame, text="Add Expense", font=BODY_FONT, 
                        bg=ACCENT_COLOR_2, fg=TEXT_COLOR, 
                        activebackground=ACCENT_COLOR,
                        activeforeground=TEXT_COLOR, 
                        borderwidth=0, relief="flat",
                        cursor="hand2", command=self.add_expense)
        add_btn.pack(fill="x", ipady=10)
    
    def add_expense(self):
        """Add new expense to the tracker"""
        date = self.expense_date.get().strip()
        category = self.expense_category.get().strip()
        amount = self.expense_amount.get().strip()
        description = self.expense_desc.get().strip()
        
        # Validate inputs
        if not all([date, category, amount]):
            messagebox.showerror("Error", "Please fill all required fields", parent=self)
            return
        
        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError("Amount must be positive")
            
            # Validate date
            date_obj = datetime.strptime(date, "%Y-%m-%d")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input: {str(e)}", parent=self)
            return
        
        # Create expense document
        expense_data = {
            "_id": ObjectId(),
            "date": date_obj,
            "category": category,
            "amount": amount,
            "description": description
        }
        
        # Add to MongoDB
        self.add_expense_to_db(expense_data)
        
        # Update UI
        self.update_stats()
        self.show_dashboard()
        
        messagebox.showinfo("Success", "Expense added successfully!", parent=self)
    
    def show_view_expenses(self):
        """Show all expenses in a table with modern styling and search functionality"""
        self.clear_main_content()
        
        # Main container
        container = tk.Frame(self.main_content, bg=DARK_BG_2, padx=20, pady=20)
        container.pack(fill="both", expand=True)
        
        tk.Label(container, text="All Expenses", font=HEADER_FONT, 
             bg=DARK_BG_2, fg=TEXT_COLOR).pack(anchor="w", pady=(0, 20))
        
        # Search and filter frame
        search_frame = tk.Frame(container, bg=DARK_BG_2)
        search_frame.pack(fill="x", pady=(0, 15))
        
        # Search label and entry
        tk.Label(search_frame, text="Search:", font=BODY_FONT, 
             bg=DARK_BG_2, fg=TEXT_COLOR).pack(side="left", padx=(0, 10))
        
        self.search_entry = tk.Entry(search_frame, font=BODY_FONT, bg=DARK_BG_3, 
                                fg=TEXT_COLOR, insertbackground=TEXT_COLOR,
                                borderwidth=0, highlightthickness=1,
                                highlightbackground=DARK_BG_3,
                                highlightcolor=ACCENT_COLOR)
        self.search_entry.pack(side="left", fill="x", expand=True, ipady=5)
        self.search_entry.bind("<KeyRelease>", self.filter_expenses)
        
        # Filter by category
        tk.Label(search_frame, text="Category:", font=BODY_FONT, 
             bg=DARK_BG_2, fg=TEXT_COLOR).pack(side="left", padx=(20, 10))
        
        self.category_filter = ttk.Combobox(search_frame, 
                                          values=["All"] + self.expense_categories,
                                          font=BODY_FONT)
        self.category_filter.pack(side="left", fill="x", expand=False, ipady=5)
        self.category_filter.set("All")
        self.category_filter.bind("<<ComboboxSelected>>", self.filter_expenses)
        
        # Table container with scrollbars
        table_container = tk.Frame(container, bg=DARK_BG_2)
        table_container.pack(fill="both", expand=True)
        
        # Treeview for expenses
        self.expenses_tree = ttk.Treeview(table_container, 
                                        columns=("date", "category", "amount", "desc", "id"), 
                                        show="headings", selectmode="extended")
        
        # Configure columns
        self.expenses_tree.heading("date", text="Date", anchor="center")
        self.expenses_tree.heading("category", text="Category", anchor="center")
        self.expenses_tree.heading("amount", text="Amount", anchor="center")
        self.expenses_tree.heading("desc", text="Description", anchor="w")
        self.expenses_tree.heading("id", text="ID", anchor="center")
        
        self.expenses_tree.column("date", width=100, anchor="center")
        self.expenses_tree.column("category", width=120, anchor="center")
        self.expenses_tree.column("amount", width=120, anchor="center")
        self.expenses_tree.column("desc", width=200, anchor="w")
        self.expenses_tree.column("id", width=0, stretch=tk.NO)  # Hidden ID column
        
        # Add scrollbars
        y_scroll = ttk.Scrollbar(table_container, orient="vertical", command=self.expenses_tree.yview)
        x_scroll = ttk.Scrollbar(table_container, orient="horizontal", command=self.expenses_tree.xview)
        self.expenses_tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        
        # Grid layout
        self.expenses_tree.grid(row=0, column=0, sticky="nsew")
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll.grid(row=1, column=0, sticky="ew")
        
        # Configure grid weights
        table_container.grid_rowconfigure(0, weight=1)
        table_container.grid_columnconfigure(0, weight=1)
        
        # Action buttons frame
        btn_frame = tk.Frame(container, bg=DARK_BG_2)
        btn_frame.pack(fill="x", pady=(15, 0))
        
        # Edit button
        edit_btn = tk.Button(btn_frame, text="Edit Selected", font=BODY_FONT, 
                         bg=WARNING_COLOR, fg=TEXT_COLOR, 
                         activebackground="#FFC107",
                         activeforeground=TEXT_COLOR, 
                         borderwidth=0, relief="flat",
                         cursor="hand2", command=self.edit_selected_expense)
        edit_btn.pack(side="left", padx=(0, 10), ipady=5)
        
        # Delete button
        delete_btn = tk.Button(btn_frame, text="Delete Selected", font=BODY_FONT, 
                           bg=ERROR_COLOR, fg=TEXT_COLOR, 
                           activebackground="#E57373",
                           activeforeground=TEXT_COLOR, 
                           borderwidth=0, relief="flat",
                           cursor="hand2", command=self.delete_selected_expenses)
        delete_btn.pack(side="left", ipady=5)
        
        # Load data
        self.load_expenses_table()
    
    def filter_expenses(self, event=None):
        """Filter expenses based on search criteria"""
        search_term = self.search_entry.get().lower()
        category_filter = self.category_filter.get()
        
        # Clear existing items
        for item in self.expenses_tree.get_children():
            self.expenses_tree.delete(item)
        
        # Get all expenses
        expenses = self.get_expenses()
        
        # Filter expenses
        filtered = []
        for expense in expenses:
            # Apply category filter
            if category_filter != "All" and expense['category'] != category_filter:
                continue
            
            # Apply search term filter
            if search_term:
                desc = expense.get('description', '').lower()
                if (search_term not in expense['category'].lower() and 
                    search_term not in str(expense['amount']) and 
                    search_term not in desc):
                    continue
            
            filtered.append(expense)
        
        # Add filtered expenses
        for expense in filtered:
            self.expenses_tree.insert("", "end", values=(
                expense['date'].strftime("%Y-%m-%d"),
                expense['category'],
                f"${expense['amount']:.2f}",
                expense.get('description', ''),
                str(expense['_id'])  # Hidden ID
            ))
    
    def load_expenses_table(self):
        """Load expenses into the table"""
        # Clear existing items
        for item in self.expenses_tree.get_children():
            self.expenses_tree.delete(item)
        
        # Add expenses
        for expense in self.get_expenses():
            self.expenses_tree.insert("", "end", values=(
                expense['date'].strftime("%Y-%m-%d"),
                expense['category'],
                f"${expense['amount']:.2f}",
                expense.get('description', ''),
                str(expense['_id'])  # Hidden ID
            ))
    
    def edit_selected_expense(self):
        """Edit selected expense"""
        selection = self.expenses_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an expense to edit", parent=self)
            return
        
        if len(selection) > 1:
            messagebox.showwarning("Warning", "Please select only one expense to edit", parent=self)
            return
        
        item = self.expenses_tree.item(selection[0])
        expense_id = item['values'][4]  # Get the hidden ID
        
        # Find the expense in MongoDB
        expense = None
        for exp in self.get_expenses():
            if str(exp['_id']) == expense_id:
                expense = exp
                break
        
        if not expense:
            messagebox.showerror("Error", "Expense not found", parent=self)
            return
        
        # Create edit dialog
        self.edit_dialog = tk.Toplevel(self)
        self.edit_dialog.title("Edit Expense")
        self.edit_dialog.geometry("400x400")
        self.edit_dialog.resizable(False, False)
        self.edit_dialog.transient(self)
        self.edit_dialog.grab_set()
        
        # Gradient background
        GradientFrame(self.edit_dialog, color1=DARK_BG_1, color2=DARK_BG_2).pack(fill="both", expand=True)
        
        # Main container
        container = tk.Frame(self.edit_dialog, bg=DARK_BG_2)
        container.place(relx=0.5, rely=0.5, anchor="center", width=360, height=360)
        
        tk.Label(container, text="Edit Expense", font=HEADER_FONT, 
             bg=DARK_BG_2, fg=TEXT_COLOR).pack(pady=(0, 10))
        
        # Date
        tk.Label(container, text="Date", font=BODY_FONT, 
             bg=DARK_BG_2, fg=TEXT_COLOR).pack(anchor="w", pady=(0, 5))
        
        self.edit_date = tk.Entry(container, font=BODY_FONT, bg=DARK_BG_3, 
                             fg=TEXT_COLOR, insertbackground=TEXT_COLOR,
                             borderwidth=0, highlightthickness=1,
                             highlightbackground=DARK_BG_3,
                             highlightcolor=ACCENT_COLOR)
        self.edit_date.pack(fill="x", pady=(0, 10), ipady=5)
        self.edit_date.insert(0, expense["date"].strftime("%Y-%m-%d"))
        
        # Category
        tk.Label(container, text="Category", font=BODY_FONT, 
             bg=DARK_BG_2, fg=TEXT_COLOR).pack(anchor="w", pady=(0, 5))
        
        self.edit_category = ttk.Combobox(container, values=self.expense_categories, 
                                        font=BODY_FONT)
        self.edit_category.pack(fill="x", pady=(0, 10), ipady=5)
        self.edit_category.set(expense["category"])
        
        # Amount
        tk.Label(container, text="Amount", font=BODY_FONT, 
             bg=DARK_BG_2, fg=TEXT_COLOR).pack(anchor="w", pady=(0, 5))
        
        self.edit_amount = tk.Entry(container, font=BODY_FONT, bg=DARK_BG_3, 
                              fg=TEXT_COLOR, insertbackground=TEXT_COLOR,
                              borderwidth=0, highlightthickness=1,
                              highlightbackground=DARK_BG_3,
                              highlightcolor=ACCENT_COLOR)
        self.edit_amount.pack(fill="x", pady=(0, 10), ipady=5)
        self.edit_amount.insert(0, expense["amount"])
        
        # Description
        tk.Label(container, text="Description", font=BODY_FONT, 
             bg=DARK_BG_2, fg=TEXT_COLOR).pack(anchor="w", pady=(0, 5))
        
        self.edit_desc = tk.Entry(container, font=BODY_FONT, bg=DARK_BG_3, 
                             fg=TEXT_COLOR, insertbackground=TEXT_COLOR,
                             borderwidth=0, highlightthickness=1,
                             highlightbackground=DARK_BG_3,
                             highlightcolor=ACCENT_COLOR)
        self.edit_desc.pack(fill="x", pady=(0, 15), ipady=5)
        self.edit_desc.insert(0, expense.get("description", ""))
        
        # Button frame
        btn_frame = tk.Frame(container, bg=DARK_BG_2)
        btn_frame.pack(fill="x")
        
        # Save button
        save_btn = tk.Button(btn_frame, text="Save Changes", font=BODY_FONT, 
                         bg=SUCCESS_COLOR, fg=TEXT_COLOR, 
                         activebackground="#4CAF50",
                         activeforeground=TEXT_COLOR, 
                         borderwidth=0, relief="flat",
                         cursor="hand2", 
                         command=lambda: self.save_edited_expense(expense_id))
        save_btn.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        # Cancel button
        cancel_btn = tk.Button(btn_frame, text="Cancel", font=BODY_FONT, 
                           bg=ERROR_COLOR, fg=TEXT_COLOR, 
                           activebackground="#F44336",
                           activeforeground=TEXT_COLOR, 
                           borderwidth=0, relief="flat",
                           cursor="hand2", 
                           command=self.edit_dialog.destroy)
        cancel_btn.pack(side="left", fill="x", expand=True)
    
    def save_edited_expense(self, expense_id):
        """Save the edited expense"""
        date = self.edit_date.get().strip()
        category = self.edit_category.get().strip()
        amount = self.edit_amount.get().strip()
        description = self.edit_desc.get().strip()
        
        # Validate inputs
        if not all([date, category, amount]):
            messagebox.showerror("Error", "Please fill all required fields", parent=self.edit_dialog)
            return
        
        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError("Amount must be positive")
            
            # Validate date
            date_obj = datetime.strptime(date, "%Y-%m-%d")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input: {str(e)}", parent=self.edit_dialog)
            return
        
        # Update the expense in MongoDB
        new_data = {
            "date": date_obj,
            "category": category,
            "amount": amount,
            "description": description
        }
        
        self.update_expense_in_db(expense_id, new_data)
        
        # Update UI
        self.update_stats()
        self.load_expenses_table()
        self.filter_expenses()
        
        messagebox.showinfo("Success", "Expense updated successfully!", parent=self.edit_dialog)
        self.edit_dialog.destroy()
    
    def delete_selected_expenses(self):
        """Delete selected expenses"""
        selection = self.expenses_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select expenses to delete", parent=self)
            return
        
        # Confirm deletion
        confirm = messagebox.askyesno(
            "Confirm Deletion", 
            f"Are you sure you want to delete {len(selection)} expense(s)?",
            parent=self
        )
        
        if not confirm:
            return
        
        # Get IDs of selected expenses
        ids_to_delete = [self.expenses_tree.item(item)['values'][4] for item in selection]
        
        # Delete from MongoDB
        for expense_id in ids_to_delete:
            self.delete_expense_from_db(expense_id)
        
        # Update UI
        self.update_stats()
        self.load_expenses_table()
        self.filter_expenses()
        
        messagebox.showinfo("Success", f"{len(selection)} expense(s) deleted", parent=self)
    
    def show_budget(self):
        """Show budget management with modern styling"""
        self.clear_main_content()
        
        # Budget frame
        budget_frame = tk.Frame(self.main_content, bg=DARK_BG_2, padx=20, pady=20)
        budget_frame.pack(fill="both", expand=True)
        
        tk.Label(budget_frame, text="Budget Management", font=HEADER_FONT, 
             bg=DARK_BG_2, fg=TEXT_COLOR).pack(anchor="w", pady=(0, 20))
        
        # Budget form
        form_frame = tk.Frame(budget_frame, bg=DARK_BG_2)
        form_frame.pack(fill="x", pady=(0, 20))
        
        tk.Label(form_frame, text="Category", font=BODY_FONT, 
             bg=DARK_BG_2, fg=TEXT_COLOR).pack(anchor="w", pady=(0, 5))
        
        self.budget_category = ttk.Combobox(form_frame, values=self.expense_categories, 
                                         font=BODY_FONT)
        self.budget_category.pack(fill="x", pady=(0, 10), ipady=5)
        
        tk.Label(form_frame, text="Amount", font=BODY_FONT, 
             bg=DARK_BG_2, fg=TEXT_COLOR).pack(anchor="w", pady=(0, 5))
        
        self.budget_amount = tk.Entry(form_frame, font=BODY_FONT, bg=DARK_BG_3, 
                                fg=TEXT_COLOR, insertbackground=TEXT_COLOR,
                                borderwidth=0, highlightthickness=1,
                                highlightbackground=DARK_BG_3,
                                highlightcolor=ACCENT_COLOR)
        self.budget_amount.pack(fill="x", pady=(0, 10), ipady=5)
        
        # Buttons frame
        btn_frame = tk.Frame(form_frame, bg=DARK_BG_2)
        btn_frame.pack(fill="x")
        
        set_btn = tk.Button(btn_frame, text="Set Budget", font=BODY_FONT, 
                        bg=ACCENT_COLOR_2, fg=TEXT_COLOR, 
                        activebackground=ACCENT_COLOR,
                        activeforeground=TEXT_COLOR, 
                        borderwidth=0, relief="flat",
                        cursor="hand2", command=self.set_budget)
        set_btn.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        edit_btn = tk.Button(btn_frame, text="Edit Budget", font=BODY_FONT, 
                         bg=WARNING_COLOR, fg=TEXT_COLOR, 
                         activebackground="#FFC107",
                         activeforeground=TEXT_COLOR, 
                         borderwidth=0, relief="flat",
                         cursor="hand2", command=self.edit_budget)
        edit_btn.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        clear_btn = tk.Button(btn_frame, text="Clear Budget", font=BODY_FONT, 
                          bg=ERROR_COLOR, fg=TEXT_COLOR, 
                          activebackground="#F44336",
                          activeforeground=TEXT_COLOR, 
                          borderwidth=0, relief="flat",
                          cursor="hand2", command=self.clear_budget)
        clear_btn.pack(side="left", fill="x", expand=True)
        
        # Budget list container with scrollbar
        list_container = tk.Frame(budget_frame, bg=DARK_BG_2)
        list_container.pack(fill="both", expand=True)
        
        tk.Label(list_container, text="Current Budgets", font=BODY_FONT, 
             bg=DARK_BG_2, fg=TEXT_COLOR).pack(anchor="w", pady=(0, 10))
        
        # Treeview for budgets
        self.budget_tree = ttk.Treeview(list_container, 
                                      columns=("category", "amount", "spent", "remaining"), 
                                      show="headings", selectmode="browse")
        
        # Configure columns
        self.budget_tree.heading("category", text="Category", anchor="center")
        self.budget_tree.heading("amount", text="Budget Amount", anchor="center")
        self.budget_tree.heading("spent", text="Spent", anchor="center")
        self.budget_tree.heading("remaining", text="Remaining", anchor="center")
        
        self.budget_tree.column("category", width=150, anchor="center")
        self.budget_tree.column("amount", width=120, anchor="center")
        self.budget_tree.column("spent", width=120, anchor="center")
        self.budget_tree.column("remaining", width=120, anchor="center")
        
        # Add scrollbars
        y_scroll = ttk.Scrollbar(list_container, orient="vertical", command=self.budget_tree.yview)
        self.budget_tree.configure(yscrollcommand=y_scroll.set)
        
        # Grid layout
        self.budget_tree.grid(row=0, column=0, sticky="nsew")
        y_scroll.grid(row=0, column=1, sticky="ns")
        
        # Configure grid weights
        list_container.grid_rowconfigure(0, weight=1)
        list_container.grid_columnconfigure(0, weight=1)
        
        # Load budgets
        self.load_budget_tree()
    
    def load_budget_tree(self):
        """Load budgets into the treeview"""
        # Clear existing items
        for item in self.budget_tree.get_children():
            self.budget_tree.delete(item)
    
        budgets = self.get_budgets()
        if not budgets:
            return
    
        # Get current month's spending by category
        expenses = self.get_expenses()
        current_month = datetime.now().strftime("%Y-%m")
        monthly_spending = {}
    
        for expense in expenses:
            if expense['date'].strftime("%Y-%m") == current_month:
                category = expense['category']
                monthly_spending[category] = monthly_spending.get(category, 0) + expense['amount']
    
        # Add budgets to treeview
        for category, amount in budgets.items():
            spent = monthly_spending.get(category, 0)
            remaining = max(0, amount - spent)
        
            # Determine row color based on budget status
            tags = ('over',) if spent > amount else ('under',)
        
            self.budget_tree.insert("", "end", values=(
                category,
                f"${amount:.2f}",
                f"${spent:.2f}",
                f"${remaining:.2f}"
            ), tags=tags)
    
        # Configure tag colors
        self.budget_tree.tag_configure('over', foreground=ERROR_COLOR)
        self.budget_tree.tag_configure('under', foreground=SUCCESS_COLOR)
    
        # Force update the UI
        self.budget_tree.update_idletasks()
    
    def set_budget(self):
        """Set budget for a category"""
        category = self.budget_category.get().strip()
        amount = self.budget_amount.get().strip()
    
        if not category or not amount:
            messagebox.showerror("Error", "Please select a category and enter an amount", parent=self)
            return
    
        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError("Amount must be positive")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid positive number", parent=self)
            return
    
        # Update budgets in MongoDB
        budgets = self.get_budgets()
        budgets[category] = amount
        self.update_budgets_in_db(budgets)
    
        # Update all relevant UI components
        self.load_budget_tree()
        self.update_sidebar_stats()
        self.update_stats()
        self.update_charts()  # Add this to refresh charts
    
        messagebox.showinfo("Success", f"Budget for {category} set to ${amount:.2f}", parent=self)
    
        # Clear form
        self.budget_category.set('')
        self.budget_amount.delete(0, tk.END)
    
    def edit_budget(self):
        """Edit selected budget"""
        selection = self.budget_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a budget to edit", parent=self)
            return
        
        if len(selection) > 1:
            messagebox.showwarning("Warning", "Please select only one budget to edit", parent=self)
            return
        
        item = self.budget_tree.item(selection[0])
        category = item['values'][0]
        current_amount = float(item['values'][1][1:])  # Remove $ and convert to float
        
        # Create edit dialog
        self.edit_budget_dialog = tk.Toplevel(self)
        self.edit_budget_dialog.title("Edit Budget")
        self.edit_budget_dialog.geometry("300x200")
        self.edit_budget_dialog.resizable(False, False)
        self.edit_budget_dialog.transient(self)
        self.edit_budget_dialog.grab_set()
        
        # Gradient background
        GradientFrame(self.edit_budget_dialog, color1=DARK_BG_1, color2=DARK_BG_2).pack(fill="both", expand=True)
        
        # Main container
        container = tk.Frame(self.edit_budget_dialog, bg=DARK_BG_2)
        container.place(relx=0.5, rely=0.5, anchor="center", width=280, height=160)
        
        tk.Label(container, text=f"Edit {category} Budget", font=HEADER_FONT, 
             bg=DARK_BG_2, fg=TEXT_COLOR).pack(pady=(0, 10))
        
        # Amount
        tk.Label(container, text="New Amount", font=BODY_FONT, 
             bg=DARK_BG_2, fg=TEXT_COLOR).pack(anchor="w", pady=(0, 5))
        
        self.edit_budget_amount = tk.Entry(container, font=BODY_FONT, bg=DARK_BG_3, 
                                      fg=TEXT_COLOR, insertbackground=TEXT_COLOR,
                                      borderwidth=0, highlightthickness=1,
                                      highlightbackground=DARK_BG_3,
                                      highlightcolor=ACCENT_COLOR)
        self.edit_budget_amount.pack(fill="x", pady=(0, 10), ipady=5)
        self.edit_budget_amount.insert(0, current_amount)
        
        # Button frame
        btn_frame = tk.Frame(container, bg=DARK_BG_2)
        btn_frame.pack(fill="x")
        
        # Save button
        save_btn = tk.Button(btn_frame, text="Save Changes", font=BODY_FONT, 
                         bg=SUCCESS_COLOR, fg=TEXT_COLOR, 
                         activebackground="#4CAF50",
                         activeforeground=TEXT_COLOR, 
                         borderwidth=0, relief="flat",
                         cursor="hand2", 
                         command=lambda: self.save_edited_budget(category))
        save_btn.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        # Cancel button
        cancel_btn = tk.Button(btn_frame, text="Cancel", font=BODY_FONT, 
                           bg=ERROR_COLOR, fg=TEXT_COLOR, 
                           activebackground="#F44336",
                           activeforeground=TEXT_COLOR, 
                           borderwidth=0, relief="flat",
                           cursor="hand2", 
                           command=self.edit_budget_dialog.destroy)
        cancel_btn.pack(side="left", fill="x", expand=True)
    
    def save_edited_budget(self, category):
        """Save the edited budget"""
        amount = self.edit_budget_amount.get().strip()
        
        if not amount:
            messagebox.showerror("Error", "Please enter an amount", parent=self.edit_budget_dialog)
            return
        
        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError("Amount must be positive")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid positive number", parent=self.edit_budget_dialog)
            return
        
        # Update the budget in MongoDB
        budgets = self.get_budgets()
        budgets[category] = amount
        self.update_budgets_in_db(budgets)
        
        # Update UI
        self.load_budget_tree()
        self.update_stats()
        
        messagebox.showinfo("Success", f"Budget for {category} updated to ${amount:.2f}", 
                          parent=self.edit_budget_dialog)
        self.edit_budget_dialog.destroy()
    
    def clear_budget(self):
        """Clear selected budget"""
        selection = self.budget_tree.selection()
        if not selection:
            messagebox.showerror("Error", "Please select a budget to clear", parent=self)
            return
        
        # Get all selected categories
        categories = [self.budget_tree.item(item)['values'][0] for item in selection]
        
        # Confirm deletion
        confirm = messagebox.askyesno(
            "Confirm Deletion", 
            f"Are you sure you want to clear {len(categories)} budget(s)?",
            parent=self
        )
        
        if not confirm:
            return
        
        # Remove budgets from MongoDB
        budgets = self.get_budgets()
        for category in categories:
            budgets.pop(category, None)
        
        self.update_budgets_in_db(budgets)
        
        # Update UI
        self.load_budget_tree()
        self.update_stats()
        
        messagebox.showinfo("Success", f"{len(categories)} budget(s) cleared", parent=self)
    
    def show_reports(self):
        """Show reports view with modern styling"""
        self.clear_main_content()
        
        reports_frame = tk.Frame(self.main_content, bg=DARK_BG_2, padx=20, pady=20)
        reports_frame.pack(fill="both", expand=True)
        
        tk.Label(reports_frame, text="Reports", font=HEADER_FONT, 
             bg=DARK_BG_2, fg=TEXT_COLOR).pack(anchor="w", pady=(0, 20))
        
        # Report type selection
        type_frame = tk.Frame(reports_frame, bg=DARK_BG_2)
        type_frame.pack(fill="x", pady=(0, 20))
        
        tk.Label(type_frame, text="Report Type:", font=BODY_FONT, 
             bg=DARK_BG_2, fg=TEXT_COLOR).pack(side="left", padx=(0, 10))
        
        self.report_type = ttk.Combobox(type_frame, 
                                      values=["Monthly Summary", "Category Breakdown", "Spending Trend"], 
                                      font=BODY_FONT)
        self.report_type.pack(side="left", padx=(0, 10), fill="x", expand=True)
        self.report_type.set("Monthly Summary")
        
        # Time period selection
        period_frame = tk.Frame(reports_frame, bg=DARK_BG_2)
        period_frame.pack(fill="x", pady=(0, 20))
        
        tk.Label(period_frame, text="Time Period:", font=BODY_FONT, 
             bg=DARK_BG_2, fg=TEXT_COLOR).pack(side="left", padx=(0, 10))
        
        self.time_period = ttk.Combobox(period_frame, 
                                       values=["Last Month", "Last 3 Months", "Last 6 Months", "Last Year", "All Time"], 
                                       font=BODY_FONT)
        self.time_period.pack(side="left", padx=(0, 10), fill="x", expand=True)
        self.time_period.set("Last 3 Months")
        
        # Generate button
        gen_btn = tk.Button(reports_frame, text="Generate Report", font=BODY_FONT, 
                        bg=ACCENT_COLOR_2, fg=TEXT_COLOR, 
                        activebackground=ACCENT_COLOR,
                        activeforeground=TEXT_COLOR, 
                        borderwidth=0, relief="flat",
                        cursor="hand2", command=self.generate_report)
        gen_btn.pack(fill="x", pady=(0, 20), ipady=10)
        
        # Report canvas with scrollbar
        report_container = tk.Frame(reports_frame, bg=DARK_BG_2)
        report_container.pack(fill="both", expand=True)
        
        canvas = tk.Canvas(report_container, bg=DARK_BG_2, highlightthickness=0)
        scrollbar = tk.Scrollbar(report_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=DARK_BG_2)
        
        # Configure the canvas
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        # Pack everything
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        # Make mouse wheel scroll
        scrollable_frame.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", 
            lambda event: canvas.yview_scroll(int(-1*(event.delta/120)), "units")))
        scrollable_frame.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))
        
        self.report_canvas = scrollable_frame
    
    def generate_report(self):
        """Generate the selected report with improved visibility"""
        report_type = self.report_type.get()
        time_period = self.time_period.get()
        
        if not report_type or not time_period:
            messagebox.showerror("Error", "Please select both report type and time period", parent=self)
            return
        
        # Clear previous report
        for widget in self.report_canvas.winfo_children():
            widget.destroy()
        
        # Filter data based on time period
        today = datetime.now()
        start_date = {
            "Last Month": today - pd.DateOffset(months=1),
            "Last 3 Months": today - pd.DateOffset(months=3),
            "Last 6 Months": today - pd.DateOffset(months=6),
            "Last Year": today - pd.DateOffset(years=1),
            "All Time": datetime.min
        }.get(time_period, datetime.min)
        
        expenses = [exp for exp in self.get_expenses() if exp['date'] >= start_date]
        
        if not expenses:
            tk.Label(self.report_canvas, text="No data available for the selected period", 
                 font=BODY_FONT, bg=DARK_BG_2, fg=TEXT_COLOR).pack(fill="both", expand=True)
            return
        
        # Generate report
        if report_type == "Monthly Summary":
            self.generate_monthly_report(expenses)
        elif report_type == "Category Breakdown":
            self.generate_category_report(expenses)
        elif report_type == "Spending Trend":
            self.generate_trend_report(expenses)
    
    def generate_monthly_report(self, expenses):
        """Generate monthly summary report with improved styling"""
        # Create figure with dark theme
        fig, ax = plt.subplots(figsize=(10, 5))
        
        # Convert to DataFrame for easier manipulation
        import pandas as pd
        df = pd.DataFrame(expenses)
        df['date'] = pd.to_datetime(df['date'])
        
        # Group by month and category
        df["Month"] = df["date"].dt.to_period("M")
        monthly_data = df.groupby(["Month", "category"])["amount"].sum().unstack().fillna(0)
        
        # Plot stacked bar chart
        colors = plt.cm.tab20.colors[:len(monthly_data.columns)]
        monthly_data.plot(kind="bar", stacked=True, ax=ax, color=colors)
        
        # Style the chart
        ax.set_title("Monthly Spending by Category", color=TEXT_COLOR)
        ax.set_ylabel("Amount ($)", color=TEXT_COLOR)
        ax.set_xlabel("Month", color=TEXT_COLOR)
        
        # Custom legend
        legend = ax.legend(title="Category", facecolor=DARK_BG_3, 
                          edgecolor=DARK_BG_3, labelcolor=TEXT_COLOR)
        plt.setp(legend.get_title(), color=TEXT_COLOR)
        
        # Grid and spines
        ax.grid(color=DARK_BG_3, linestyle='--', alpha=0.5)
        for spine in ax.spines.values():
            spine.set_color(TEXT_COLOR_2)
        
        # Rotate x-axis labels
        ax.tick_params(axis='x', colors=TEXT_COLOR, rotation=45)
        ax.tick_params(axis='y', colors=TEXT_COLOR)
        
        # Embed in Tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.report_canvas)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="x", expand=True, pady=10)
        
        # Add total spending label
        total_spending = monthly_data.sum(axis=1).sum()
        tk.Label(self.report_canvas, 
             text=f"Total Spending: ${total_spending:.2f} over {len(monthly_data)} months", 
             font=BODY_FONT, bg=DARK_BG_2, fg=TEXT_COLOR).pack(anchor="w", padx=20)
    
    def generate_category_report(self, expenses):
        """Generate category breakdown report with improved styling"""
        # Create figure with dark theme
        fig, ax = plt.subplots(figsize=(8, 8))
        
        # Convert to DataFrame for easier manipulation
        import pandas as pd
        df = pd.DataFrame(expenses)
        
        # Group by category
        category_data = df.groupby("category")["amount"].sum()
        
        # Plot pie chart with improved visibility
        colors = plt.cm.tab20.colors[:len(category_data)]
        explode = [0.05] * len(category_data)  # Add slight separation between slices
        
        wedges, texts, autotexts = ax.pie(category_data, 
                                         labels=category_data.index, 
                                         autopct="%1.1f%%",
                                         startangle=90, 
                                         colors=colors, 
                                         explode=explode,
                                         textprops={"color": TEXT_COLOR},
                                         wedgeprops={"edgecolor": DARK_BG_2, "linewidth": 1})
        
        ax.set_title("Category Spending Breakdown", color=TEXT_COLOR)
        
        # Make autopct text more visible
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(10)
        
        # Embed in Tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.report_canvas)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="x", expand=True, pady=10)
        
        # Add total spending label
        total_spending = category_data.sum()
        tk.Label(self.report_canvas, 
             text=f"Total Spending: ${total_spending:.2f} across {len(category_data)} categories", 
             font=BODY_FONT, bg=DARK_BG_2, fg=TEXT_COLOR).pack(anchor="w", padx=20)
    
    def generate_trend_report(self, expenses):
        """Generate spending trend report with improved styling"""
        # Create figure with dark theme
        fig, ax = plt.subplots(figsize=(10, 5))
        
        # Convert to DataFrame for easier manipulation
        import pandas as pd
        df = pd.DataFrame(expenses)
        df['date'] = pd.to_datetime(df['date'])
        
        # Group by month
        df["Month"] = df["date"].dt.to_period("M")
        trend_data = df.groupby("Month")["amount"].sum()
        
        # Plot trend line with markers
        ax.plot(trend_data.index.astype(str), trend_data.values, 
               color=ACCENT_COLOR, marker="o", linewidth=2, markersize=8)
        
        # Style the chart
        ax.set_title("Spending Trend Over Time", color=TEXT_COLOR)
        ax.set_ylabel("Amount ($)", color=TEXT_COLOR)
        ax.set_xlabel("Month", color=TEXT_COLOR)
        
        # Grid and spines
        ax.grid(color=DARK_BG_3, linestyle='--', alpha=0.5)
        for spine in ax.spines.values():
            spine.set_color(TEXT_COLOR_2)
        
        # Rotate x-axis labels
        ax.tick_params(axis='x', colors=TEXT_COLOR, rotation=45)
        ax.tick_params(axis='y', colors=TEXT_COLOR)
        
        # Add value annotations
        for x, y in zip(trend_data.index.astype(str), trend_data.values):
            ax.text(x, y, f"${y:.0f}", ha='center', va='bottom', color=TEXT_COLOR)
        
        # Embed in Tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.report_canvas)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="x", expand=True, pady=10)
        
        # Add stats labels
        avg_spending = trend_data.mean()
        max_spending = trend_data.max()
        min_spending = trend_data.min()
        
        stats_frame = tk.Frame(self.report_canvas, bg=DARK_BG_2)
        stats_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        tk.Label(stats_frame, text=f"Average: ${avg_spending:.2f}", 
             font=BODY_FONT, bg=DARK_BG_2, fg=TEXT_COLOR).pack(side="left", padx=(0, 20))
        tk.Label(stats_frame, text=f"Maximum: ${max_spending:.2f}", 
             font=BODY_FONT, bg=DARK_BG_2, fg=ERROR_COLOR).pack(side="left", padx=(0, 20))
        tk.Label(stats_frame, text=f"Minimum: ${min_spending:.2f}", 
             font=BODY_FONT, bg=DARK_BG_2, fg=SUCCESS_COLOR).pack(side="left")
    
    def logout(self):
        """Logout and return to authentication window"""
        self.destroy()
        from auth import AuthWindow
        AuthWindow()

if __name__ == '__main__':
    # This should not be run directly - use auth.py to start the application
    messagebox.showerror("Error", "Please run auth.py to start the application")
