"""
UI Viewer cho Hybrid Ranking Results
Hiển thị kết quả hybrid ranking trong bảng giao diện
"""

import tkinter as tk
from tkinter import ttk
import pandas as pd


class HybridResultsViewer:
    """
    Hiển thị hybrid ranking results trong Treeview table
    """
    
    def __init__(self, root, hybrid_df):
        """
        Parameters:
        -----------
        root : tk.Tk
            Tkinter root window
        hybrid_df : pd.DataFrame
            DataFrame với hybrid rankings
        """
        self.root = root
        self.hybrid_df = hybrid_df
        
        # Setup window
        self.root.title('Hybrid Recommendation Results')
        self.root.geometry('1400x700')
        
        # Header
        header_label = tk.Label(root, 
                               text='HYBRID RECOMMENDATION RESULTS', 
                               font=('Arial', 18, 'bold'), 
                               fg='blue', 
                               bg='lightgray')
        header_label.pack(pady=10)
        
        # Info label
        info_text = f"Total Recommendations: {len(hybrid_df)} games"
        info_label = tk.Label(root, text=info_text, font=('Arial', 12), fg='green')
        info_label.pack(pady=5)
        
        # Create frame for treeview và scrollbars
        tree_frame = tk.Frame(root)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create Treeview
        columns = list(hybrid_df.columns)
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=25)
        
        # Define column widths
        column_widths = {
            'rank': 60,
            'app_id': 100,
            'title': 400,
            'hybrid_score': 120,
            'knn_score': 100,
            'knn_rank': 100,
            'cb_score': 100,
            'cb_rank': 100
        }
        
        # Setup columns
        for col in columns:
            width = column_widths.get(col, 150)
            self.tree.heading(col, text=col.replace('_', ' ').title())
            self.tree.column(col, width=width, anchor='center')
        
        # Add scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid layout
        self.tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # Configure tags for highlighting
        self.tree.tag_configure('top3', background='#90EE90')  # Light green
        self.tree.tag_configure('top10', background='#E6F3FF')  # Light blue
        self.tree.tag_configure('both_scores', foreground='blue')
        
        # Insert data
        self.populate_tree()
        
        # Footer
        footer_label = tk.Label(root, 
                               text='Hybrid Ranking combines KNN (Collaborative) and Content-Based recommendations | Top 3: Green | Top 10: Blue', 
                               font=('Arial', 10), fg='gray')
        footer_label.pack(pady=5)
    
    def populate_tree(self):
        """Populate treeview với data từ DataFrame"""
        for idx, row in self.hybrid_df.iterrows():
            values = []
            tags = []
            
            # Determine tags
            rank = row.get('rank', idx + 1)
            if rank <= 3:
                tags.append('top3')
            elif rank <= 10:
                tags.append('top10')
            
            # Check if has both scores
            has_knn = pd.notna(row.get('knn_rank'))
            has_cb = pd.notna(row.get('cb_rank'))
            if has_knn and has_cb:
                tags.append('both_scores')
            
            for col in self.hybrid_df.columns:
                value = row[col]
                # Format values
                if pd.isna(value):
                    values.append('N/A')
                elif isinstance(value, float):
                    if 'score' in col.lower():
                        values.append(f"{value:.2f}")
                    else:
                        values.append(f"{int(value)}" if value == int(value) else f"{value:.1f}")
                else:
                    values.append(str(value))
            
            self.tree.insert('', tk.END, values=values, tags=tags)


def show_hybrid_results(hybrid_df):
    """
    Hiển thị hybrid results trong UI window
    
    Parameters:
    -----------
    hybrid_df : pd.DataFrame
        DataFrame với hybrid rankings
    """
    root = tk.Tk()
    app = HybridResultsViewer(root, hybrid_df)
    root.mainloop()

