from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QGridLayout, QFrame, QHBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView, QSizePolicy
)
from PySide6.QtCore import Qt
from modules.reports_logic import (
    get_sales_report, get_gst_report, get_monthly_sales_data, get_monthly_purchase_data, get_cash_flow_data
)
from database.db import execute_read_query
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import datetime

class DashboardPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Scroll Area for the entire dashboard
        from PySide6.QtWidgets import QScrollArea
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content_widget = QWidget()
        self.content_layout = QVBoxLayout(content_widget)
        self.content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Receivables & Payables Section
        rec_pay_layout = QHBoxLayout()
        self.receivables_widget = self.create_summary_widget("Total Receivables", "Total Unpaid Invoices")
        self.payables_widget = self.create_summary_widget("Total Payables", "Total Unpaid Bills")
        
        rec_pay_layout.addWidget(self.receivables_widget)
        rec_pay_layout.addWidget(self.payables_widget)
        self.content_layout.addLayout(rec_pay_layout)

        # Key Metrics Cards
        metrics_layout = QGridLayout()
        
        self.sales_card = self.create_card("Total Sales (This Month)", "₹0.00")
        self.purchase_card = self.create_card("Total Purchases (This Month)", "₹0.00")
        self.gst_payable_card = self.create_card("GST Payable (This Month)", "₹0.00")
        
        self.items_card = self.create_card("Total Items", "0")
        self.stock_value_card = self.create_card("Total Stock Value", "₹0.00")
        self.low_stock_card = self.create_card("Low Stock Items", "0")
        
        metrics_layout.addWidget(self.sales_card, 0, 0)
        metrics_layout.addWidget(self.purchase_card, 0, 1)
        metrics_layout.addWidget(self.gst_payable_card, 0, 2)
        
        metrics_layout.addWidget(self.items_card, 1, 0)
        metrics_layout.addWidget(self.stock_value_card, 1, 1)
        metrics_layout.addWidget(self.low_stock_card, 1, 2)
        
        self.content_layout.addLayout(metrics_layout)
        
        # Cash Flow Section (New)
        self.cash_flow_widget = self.create_cash_flow_widget()
        self.content_layout.addWidget(self.cash_flow_widget)
        
        # Charts
        chart_layout = QHBoxLayout()
        self.sales_chart = self.create_sales_chart()
        self.purchase_chart = self.create_purchase_chart()
        
        chart_layout.addWidget(self.sales_chart)
        chart_layout.addWidget(self.purchase_chart)
        
        self.content_layout.addLayout(chart_layout)
        
        # Upcoming Due Dates Section
        due_dates_layout = QVBoxLayout()
        due_label = QLabel("Upcoming Due Invoices (Next 7 Days)")
        due_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-top: 10px;")
        due_dates_layout.addWidget(due_label)
        
        self.due_table = QTableWidget()
        self.due_table.setColumnCount(4)
        self.due_table.setHorizontalHeaderLabels(["Date", "Due Date", "Customer", "Amount"])
        header = self.due_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.due_table.setAlternatingRowColors(True)
        self.due_table.setMinimumHeight(200)
        due_dates_layout.addWidget(self.due_table)
        
        self.content_layout.addLayout(due_dates_layout)
        
        scroll.setWidget(content_widget)
        layout.addWidget(scroll)
        
        self.setLayout(layout)
        # refresh_data will be called in showEvent
        
    def showEvent(self, event):
        self.refresh_data()
        super().showEvent(event)

    def create_summary_widget(self, title, subtitle):
        widget = QFrame()
        widget.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #E2E8F0;
            }
        """)
        layout = QVBoxLayout(widget)
        
        # Header
        header = QHBoxLayout()
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("font-weight: bold; font-size: 16px; border: none;")
        header.addWidget(title_lbl)
        header.addStretch()
        layout.addLayout(header)
        
        # Subtitle
        sub_lbl = QLabel(subtitle)
        sub_lbl.setStyleSheet("color: #64748B; font-size: 12px; border: none;")
        layout.addWidget(sub_lbl)
        
        # Amount
        amt_lbl = QLabel("₹0.00")
        amt_lbl.setStyleSheet("font-size: 24px; font-weight: bold; color: #1E293B; border: none;")
        layout.addWidget(amt_lbl)
        
        # Progress Bar (Custom using QFrame)
        progress_bg = QFrame()
        progress_bg.setFixedHeight(8)
        progress_bg.setStyleSheet("background-color: #F1F5F9; border-radius: 4px; border: none;")
        progress_layout = QHBoxLayout(progress_bg)
        progress_layout.setContentsMargins(0,0,0,0)
        progress_layout.setSpacing(0)
        
        # Current portion
        current_bar = QFrame()
        current_bar.setStyleSheet("background-color: #3B82F6; border-top-left-radius: 4px; border-bottom-left-radius: 4px; border: none;")
        
        # Overdue portion
        overdue_bar = QFrame()
        overdue_bar.setStyleSheet("background-color: #F97316; border-top-right-radius: 4px; border-bottom-right-radius: 4px; border: none;")
        
        progress_layout.addWidget(current_bar, 1) # Default ratio
        progress_layout.addWidget(overdue_bar, 0)
        
        layout.addWidget(progress_bg)
        
        # Legend
        legend_layout = QHBoxLayout()
        
        current_lbl = QLabel("Current: ₹0.00")
        current_lbl.setStyleSheet("color: #3B82F6; font-size: 12px; border: none;")
        overdue_lbl = QLabel("Overdue: ₹0.00")
        overdue_lbl.setStyleSheet("color: #F97316; font-size: 12px; border: none;")
        
        legend_layout.addWidget(current_lbl)
        legend_layout.addStretch()
        legend_layout.addWidget(overdue_lbl)
        
        layout.addLayout(legend_layout)
        
        return widget

    def update_summary_widget(self, widget, total, current, overdue):
        # Update labels
        # Layout index: 0=Header, 1=Subtitle, 2=Amount, 3=Progress, 4=Legend
        
        # Amount
        widget.layout().itemAt(2).widget().setText(f"₹{total:,.2f}")
        
        # Legend
        legend_layout = widget.layout().itemAt(4).layout()
        legend_layout.itemAt(0).widget().setText(f"Current: ₹{current:,.2f}")
        legend_layout.itemAt(2).widget().setText(f"Overdue: ₹{overdue:,.2f}")
        
        # Update Progress Bar Ratio
        progress_layout = widget.layout().itemAt(3).widget().layout()
        current_bar = progress_layout.itemAt(0).widget()
        overdue_bar = progress_layout.itemAt(1).widget()
        
        if total > 0:
            current_ratio = int((current / total) * 100)
            overdue_ratio = 100 - current_ratio
            progress_layout.setStretch(0, current_ratio)
            progress_layout.setStretch(1, overdue_ratio)
        else:
            progress_layout.setStretch(0, 0)
            progress_layout.setStretch(1, 0)

    def create_card(self, title_text, value_text):
        card = QFrame()
        card.setObjectName("Card")
        card.setMinimumWidth(250)
        card.setStyleSheet("""
            #Card {
                background-color: white;
                border-radius: 10px;
                border: 1px solid #E2E8F0;
            }
        """)
        card_layout = QVBoxLayout(card)
        
        title = QLabel(title_text)
        title.setStyleSheet("color: #64748B; font-size: 14px;")
        
        value = QLabel(value_text)
        value.setStyleSheet("color: #1E293B; font-size: 24px; font-weight: bold;")
        
        card_layout.addWidget(title)
        card_layout.addWidget(value)
        return card

    def create_cash_flow_widget(self):
        widget = QFrame()
        widget.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #E2E8F0;
            }
        """)
        # Use QHBoxLayout for responsiveness (reverted from FlowLayout)
        layout = QHBoxLayout() 
        widget.setLayout(layout)
        
        # Chart Section (Left)
        chart_container = QWidget()
        chart_container.setMinimumWidth(500)
        chart_layout = QVBoxLayout(chart_container)
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Cash Flow")
        title.setStyleSheet("font-size: 16px; font-weight: bold; border: none;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        self.fiscal_year_lbl = QLabel("This Fiscal Year")
        self.fiscal_year_lbl.setStyleSheet("color: #64748B; font-size: 12px; border: none;")
        header_layout.addWidget(self.fiscal_year_lbl)
        
        chart_layout.addLayout(header_layout)
        
        # Matplotlib Figure
        fig = Figure(figsize=(8, 3), dpi=100)
        self.cash_flow_canvas = FigureCanvas(fig)
        self.ax_cash_flow = fig.add_subplot(111)
        self.ax_cash_flow.set_facecolor('#F8FAFC')
        fig.patch.set_facecolor('white')
        chart_layout.addWidget(self.cash_flow_canvas)
        
        layout.addWidget(chart_container)
        
        # Stats Section (Right)
        stats_container = QWidget()
        stats_container.setMinimumWidth(250)
        stats_layout = QVBoxLayout(stats_container)
        stats_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        stats_layout.setSpacing(20)
        
        # Opening
        self.lbl_opening_date = QLabel("Cash as on ...")
        self.lbl_opening_date.setStyleSheet("color: #64748B; font-size: 12px; border: none;")
        self.lbl_opening_amt = QLabel("₹0.00")
        self.lbl_opening_amt.setStyleSheet("font-size: 18px; font-weight: bold; border: none;")
        
        stats_layout.addWidget(self.lbl_opening_date)
        stats_layout.addWidget(self.lbl_opening_amt)
        
        # Incoming
        lbl_inc = QLabel("Incoming")
        lbl_inc.setStyleSheet("color: #10B981; font-size: 12px; border: none;") # Green
        self.lbl_incoming_amt = QLabel("₹0.00 ( + )")
        self.lbl_incoming_amt.setStyleSheet("font-size: 18px; font-weight: bold; border: none;")
        
        stats_layout.addWidget(lbl_inc)
        stats_layout.addWidget(self.lbl_incoming_amt)
        
        # Outgoing
        lbl_out = QLabel("Outgoing")
        lbl_out.setStyleSheet("color: #EF4444; font-size: 12px; border: none;") # Red
        self.lbl_outgoing_amt = QLabel("₹0.00 ( - )")
        self.lbl_outgoing_amt.setStyleSheet("font-size: 18px; font-weight: bold; border: none;")
        
        stats_layout.addWidget(lbl_out)
        stats_layout.addWidget(self.lbl_outgoing_amt)
        
        # Closing
        self.lbl_closing_date = QLabel("Cash as on ...")
        self.lbl_closing_date.setStyleSheet("color: #3B82F6; font-size: 12px; border: none;") # Blue
        self.lbl_closing_amt = QLabel("₹0.00 ( = )")
        self.lbl_closing_amt.setStyleSheet("font-size: 18px; font-weight: bold; border: none;")
        
        stats_layout.addWidget(self.lbl_closing_date)
        stats_layout.addWidget(self.lbl_closing_amt)
        
        layout.addWidget(stats_container)
        
        return widget

    def update_cash_flow_chart(self):
        try:
            # Determine Fiscal Year Start
            today = datetime.date.today()
            if today.month >= 4:
                fy_start = today.year
            else:
                fy_start = today.year - 1
            
            data = get_cash_flow_data(fy_start)
            
            # Update Labels
            self.fiscal_year_lbl.setText(f"FY {data['fiscal_year']}")
            self.lbl_opening_date.setText(f"Cash as on {fy_start}-04-01")
            self.lbl_opening_amt.setText(f"₹{data['opening_balance']:,.2f}")
            
            self.lbl_incoming_amt.setText(f"₹{data['total_incoming']:,.2f} ( + )")
            self.lbl_outgoing_amt.setText(f"₹{data['total_outgoing']:,.2f} ( - )")
            
            self.lbl_closing_date.setText(f"Cash as on {fy_start+1}-03-31")
            self.lbl_closing_amt.setText(f"₹{data['closing_balance']:,.2f} ( = )")
            
            # Update Chart
            self.ax_cash_flow.clear()
            
            # Plot Net Cash Flow Trend (or Cumulative Balance)
            # The screenshot shows a line chart. Let's plot the cumulative balance trend.
            months = data['months']
            trend = data['balance_trend']
            
            # Create integer indices for x-axis
            x = range(len(months))
            
            self.ax_cash_flow.plot(x, trend, marker='o', color='#3B82F6', linewidth=2, label='Net Cash')
            self.ax_cash_flow.fill_between(x, trend, color='#3B82F6', alpha=0.1)
            
            self.ax_cash_flow.set_xticks(x)
            self.ax_cash_flow.set_xticklabels(months, fontsize=8)
            
            # Format y-axis labels
            self.ax_cash_flow.grid(True, linestyle='--', alpha=0.5)
            self.ax_cash_flow.spines['top'].set_visible(False)
            self.ax_cash_flow.spines['right'].set_visible(False)
            
            self.cash_flow_canvas.draw()
            
        except Exception as e:
            print(f"Error updating cash flow chart: {e}")

    def create_sales_chart(self):
        # Create a matplotlib figure
        fig = Figure(figsize=(5, 4), dpi=100)
        self.canvas = FigureCanvas(fig)
        self.canvas.setMinimumWidth(400)
        self.canvas.setMinimumHeight(300)
        self.ax = fig.add_subplot(111)
        self.ax.set_title('Monthly Sales')
        self.ax.set_xlabel('Month')
        self.ax.set_ylabel('Sales (₹)')
        fig.tight_layout()
        return self.canvas

    def create_purchase_chart(self):
        # Create a matplotlib figure
        fig = Figure(figsize=(5, 4), dpi=100)
        self.purchase_canvas = FigureCanvas(fig)
        self.purchase_canvas.setMinimumWidth(400)
        self.purchase_canvas.setMinimumHeight(300)
        self.ax_purchase = fig.add_subplot(111)
        self.ax_purchase.set_title('Monthly Purchases')
        self.ax_purchase.set_xlabel('Month')
        self.ax_purchase.set_ylabel('Purchases (₹)')
        fig.tight_layout()
        return self.purchase_canvas
    
    def update_charts(self):
        try:
            current_year = datetime.datetime.now().year
            months = range(1, 13)
            
            # Sales Chart
            sales_data = get_monthly_sales_data(current_year)
            self.ax.clear()
            self.ax.bar(months, sales_data, color='#3B82F6')
            self.ax.set_title(f'Monthly Sales ({current_year})')
            self.ax.set_xlabel('Month')
            self.ax.set_ylabel('Sales (₹)')
            self.ax.set_xticks(months)
            self.canvas.draw()
            
            # Purchase Chart
            purchase_data = get_monthly_purchase_data(current_year)
            self.ax_purchase.clear()
            self.ax_purchase.bar(months, purchase_data, color='#EF4444')
            self.ax_purchase.set_title(f'Monthly Purchases ({current_year})')
            self.ax_purchase.set_xlabel('Month')
            self.ax_purchase.set_ylabel('Purchases (₹)')
            self.ax_purchase.set_xticks(months)
            self.purchase_canvas.draw()
        except Exception as e:
            print(f"Error updating charts: {e}")

    def refresh_data(self):
        # Update Charts
        self.update_charts()
        self.update_cash_flow_chart()
        
        # Fetch data for current month
        now = datetime.datetime.now()
        start_date = now.replace(day=1).strftime("%Y-%m-%d")
        # Simple end date (next month 1st - 1 day)
        if now.month == 12:
            next_month = now.replace(year=now.year+1, month=1, day=1)
        else:
            next_month = now.replace(month=now.month+1, day=1)
        end_date = (next_month - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        
        # --- Receivables (Invoices) ---
        try:
            # Total Unpaid Invoices
            # We assume 'Paid' is the only fully paid status.
            # In a real app, calculate (total - paid_amount).
            # For now, summing grand_total of non-Paid invoices.
            invoices_query = """
                SELECT grand_total, due_date 
                FROM invoices 
                WHERE status != 'Paid'
            """
            unpaid_invoices = execute_read_query(invoices_query)
            
            total_receivables = 0.0
            current_receivables = 0.0
            overdue_receivables = 0.0
            today_date = datetime.date.today()
            
            for inv in unpaid_invoices:
                amt = inv['grand_total']
                due = inv['due_date'] # String YYYY-MM-DD
                total_receivables += amt
                
                # Parse date
                try:
                    due_dt = datetime.datetime.strptime(due, "%Y-%m-%d").date()
                    if due_dt < today_date:
                        overdue_receivables += amt
                    else:
                        current_receivables += amt
                except:
                    # If date invalid, treat as current? or overdue?
                    current_receivables += amt
                    
            self.update_summary_widget(self.receivables_widget, total_receivables, current_receivables, overdue_receivables)
            
        except Exception as e:
            print(f"Error calculating receivables: {e}")

        # --- Payables (Bills) ---
        try:
            # Total Unpaid Bills
            bills_query = """
                SELECT grand_total, due_date 
                FROM bills 
                WHERE status != 'Paid'
            """
            unpaid_bills = execute_read_query(bills_query)
            
            total_payables = 0.0
            current_payables = 0.0
            overdue_payables = 0.0
            
            for bill in unpaid_bills:
                amt = bill['grand_total']
                due = bill['due_date']
                total_payables += amt
                
                try:
                    due_dt = datetime.datetime.strptime(due, "%Y-%m-%d").date()
                    if due_dt < today_date:
                        overdue_payables += amt
                    else:
                        current_payables += amt
                except:
                    current_payables += amt
                    
            self.update_summary_widget(self.payables_widget, total_payables, current_payables, overdue_payables)
            
        except Exception as e:
            print(f"Error calculating payables: {e}")

        # Get GST Report
        gst_data = get_gst_report(start_date, end_date)
        
        # Update Cards
        # Since get_gst_report returns tax, not total sales, we need total sales from get_sales_report
        # But get_sales_report returns list of rows.
        # We should probably have a get_dashboard_stats function in reports_logic.
        # For now, I'll just use what I have.
        
        sales_rows = get_sales_report(start_date, end_date)
        total_sales = sum(row['grand_total'] for row in sales_rows)
        
        self.update_card_value(self.sales_card, f"₹{total_sales:,.2f}")
        
        # Purchases Update
        try:
             purchase_res = execute_read_query("SELECT SUM(grand_total) FROM bills WHERE date BETWEEN ? AND ?", (start_date, end_date))[0][0]
             total_purchases = purchase_res if purchase_res is not None else 0.0
             self.update_card_value(self.purchase_card, f"₹{total_purchases:,.2f}")
        except Exception as e:
             # Table might not exist or other error
             self.update_card_value(self.purchase_card, "₹0.00")

        # New Metrics
        try:
            item_count = execute_read_query("SELECT COUNT(*) FROM items")[0][0] or 0
            self.update_card_value(self.items_card, str(item_count))
            
            stock_val_res = execute_read_query("SELECT SUM(quantity_remaining * purchase_rate) FROM stock_batches")[0][0]
            stock_val = stock_val_res if stock_val_res is not None else 0.0
            self.update_card_value(self.stock_value_card, f"₹{stock_val:,.2f}")
            
            low_stock = execute_read_query("SELECT COUNT(*) FROM items WHERE track_inventory = 1 AND stock_on_hand <= reorder_point")[0][0] or 0
            self.update_card_value(self.low_stock_card, str(low_stock))
            
        except Exception as e:
            print(f"Error updating dashboard metrics: {e}")
            
        # GST Update (fix GST card update which was missing in original snippet or I might have missed it)
        # The original code had: self.update_card_value(self.gst_payable_card, f"₹{gst_data['net_gst_payable']:,.2f}")
        # I will keep it but ensure it's there.
        self.update_card_value(self.gst_payable_card, f"₹{gst_data['net_gst_payable']:,.2f}")
        
        # Update Due Dates Table
        try:
            today_str = datetime.date.today().strftime("%Y-%m-%d")
            next_week = (datetime.date.today() + datetime.timedelta(days=7)).strftime("%Y-%m-%d")
            
            query = """
                SELECT i.date, i.due_date, c.name, i.grand_total 
                FROM invoices i
                JOIN customers c ON i.customer_id = c.id
                WHERE i.status != 'Paid' 
                AND i.due_date BETWEEN ? AND ?
                ORDER BY i.due_date ASC
                LIMIT 20
            """
            due_invoices = execute_read_query(query, (today_str, next_week))
            
            self.due_table.setRowCount(len(due_invoices))
            for r, row in enumerate(due_invoices):
                self.due_table.setItem(r, 0, QTableWidgetItem(str(row['date'])))
                self.due_table.setItem(r, 1, QTableWidgetItem(str(row['due_date'])))
                self.due_table.setItem(r, 2, QTableWidgetItem(row['name']))
                self.due_table.setItem(r, 3, QTableWidgetItem(f"₹{row['grand_total']:.2f}"))
                
        except Exception as e:
            print(f"Error updating due dates: {e}")

    def update_card_value(self, card, value):
        # 2nd item in layout is value label
        card.layout().itemAt(1).widget().setText(value)
