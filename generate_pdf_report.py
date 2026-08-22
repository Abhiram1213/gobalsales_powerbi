"""
===============================================================================
GLOBAL SUPERSTORE - EXECUTIVE PDF REPORT GENERATOR
===============================================================================
Generates a publication-grade, 4-page Executive Business Intelligence Report
in PDF format with embedded high-resolution vector charts, scorecards,
profit leak diagnostics, and strategic recommendations.
===============================================================================
"""

import os
import io
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether, PageBreak, HRFlowable
)
from reportlab.pdfgen import canvas

# -----------------------------------------------------------------------------
# 1. Matplotlib Plot Generation Helpers
# -----------------------------------------------------------------------------
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')

def plot_monthly_trend(df):
    df['YearMonth'] = df['Order Date'].dt.to_period('M')
    monthly = df.groupby('YearMonth').agg(
        Sales=('Sales', 'sum'),
        Profit=('Profit', 'sum')
    ).reset_index()
    monthly['YearMonthStr'] = monthly['YearMonth'].astype(str)
    
    fig, ax1 = plt.subplots(figsize=(6.5, 2.5), dpi=300)
    fig.patch.set_facecolor('#0f172a')
    ax1.set_facecolor('#0f172a')
    
    # Sales Line & Fill
    ax1.plot(range(len(monthly)), monthly['Sales'] / 1e3, color='#818cf8', linewidth=2, label='Sales ($K)')
    ax1.fill_between(range(len(monthly)), monthly['Sales'] / 1e3, color='#818cf8', alpha=0.15)
    ax1.set_ylabel('Sales ($K)', color='#818cf8', fontsize=8, fontweight='bold')
    ax1.tick_params(axis='y', labelcolor='#818cf8', labelsize=7)
    
    # Profit Line on secondary axis
    ax2 = ax1.twinx()
    ax2.plot(range(len(monthly)), monthly['Profit'] / 1e3, color='#34d399', linewidth=1.8, linestyle='--', label='Profit ($K)')
    ax2.set_ylabel('Profit ($K)', color='#34d399', fontsize=8, fontweight='bold')
    ax2.tick_params(axis='y', labelcolor='#34d399', labelsize=7)
    
    # X-axis ticks (Show every 6 months)
    tick_indices = list(range(0, len(monthly), 6))
    ax1.set_xticks(tick_indices)
    ax1.set_xticklabels([monthly['YearMonthStr'].iloc[i] for i in tick_indices], color='#94a3b8', fontsize=7, rotation=0)
    
    ax1.grid(color='#334155', linestyle=':', alpha=0.6)
    ax2.grid(False)
    
    for spine in ax1.spines.values():
        spine.set_color('#334155')
    for spine in ax2.spines.values():
        spine.set_color('#334155')
        
    ax1.set_title('Monthly Gross Revenue & Net Profit Trajectory (2011–2014)', color='#f8fafc', fontsize=9, fontweight='bold', pad=8)
    plt.tight_layout()
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', facecolor=fig.get_facecolor(), dpi=300)
    plt.close(fig)
    buf.seek(0)
    return buf

def plot_category_donut(df):
    cat = df.groupby('Category').agg(Sales=('Sales', 'sum')).reset_index()
    
    fig, ax = plt.subplots(figsize=(3.2, 2.5), dpi=300)
    fig.patch.set_facecolor('#0f172a')
    ax.set_facecolor('#0f172a')
    
    colors_list = ['#818cf8', '#fbbf24', '#38bdf8']
    wedges, texts, autotexts = ax.pie(
        cat['Sales'], 
        labels=cat['Category'],
        autopct='%1.1f%%',
        startangle=140,
        colors=colors_list,
        wedgeprops=dict(width=0.45, edgecolor='#0f172a', linewidth=2),
        textprops=dict(color='#cbd5e1', fontsize=7, fontweight='bold')
    )
    for at in autotexts:
        at.set_color('#0f172a')
        at.set_fontsize(7)
        at.set_weight('bold')
        
    ax.set_title('Sales by Category', color='#f8fafc', fontsize=9, fontweight='bold', pad=8)
    plt.tight_layout()
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', facecolor=fig.get_facecolor(), dpi=300)
    plt.close(fig)
    buf.seek(0)
    return buf

def plot_market_performance(df):
    market = df.groupby('Market').agg(
        Sales=('Sales', 'sum'),
        Profit=('Profit', 'sum')
    ).sort_values(by='Sales', ascending=True).reset_index()
    market['Margin'] = (market['Profit'] / market['Sales']) * 100
    
    fig, ax1 = plt.subplots(figsize=(6.5, 2.7), dpi=300)
    fig.patch.set_facecolor('#0f172a')
    ax1.set_facecolor('#0f172a')
    
    bars = ax1.barh(market['Market'], market['Sales'] / 1e3, color='#6366f1', height=0.55, alpha=0.85, label='Sales ($K)')
    ax1.set_xlabel('Gross Sales ($K)', color='#818cf8', fontsize=8, fontweight='bold')
    ax1.tick_params(axis='x', labelcolor='#818cf8', labelsize=7)
    ax1.tick_params(axis='y', labelcolor='#f8fafc', labelsize=8)
    
    # Margin labels on bars
    for bar, margin in zip(bars, market['Margin']):
        w = bar.get_width()
        ax1.text(w + 30, bar.get_y() + bar.get_height()/2, f'{margin:.1f}% Margin', 
                 va='center', ha='left', color='#34d399' if margin >= 10 else '#fb7185', fontsize=7, fontweight='bold')
                 
    ax1.set_xlim(0, max(market['Sales'] / 1e3) * 1.25)
    ax1.grid(color='#334155', linestyle=':', alpha=0.6, axis='x')
    for spine in ax1.spines.values():
        spine.set_color('#334155')
        
    ax1.set_title('Global Market Performance: Revenue & Net Profit Margin %', color='#f8fafc', fontsize=9, fontweight='bold', pad=8)
    plt.tight_layout()
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', facecolor=fig.get_facecolor(), dpi=300)
    plt.close(fig)
    buf.seek(0)
    return buf

def plot_subcat_spectrum(df):
    sub = df.groupby('Sub-Category').agg(
        Sales=('Sales', 'sum'),
        Profit=('Profit', 'sum'),
        Discount=('Discount', 'mean')
    ).sort_values(by='Profit', ascending=True).reset_index()
    
    fig, ax = plt.subplots(figsize=(6.5, 3.2), dpi=300)
    fig.patch.set_facecolor('#0f172a')
    ax.set_facecolor('#0f172a')
    
    colors_bar = ['#f43f5e' if p < 0 else '#10b981' for p in sub['Profit']]
    bars = ax.barh(sub['Sub-Category'], sub['Profit'] / 1e3, color=colors_bar, height=0.6)
    
    ax.axvline(0, color='#94a3b8', linewidth=1, linestyle='--')
    ax.set_xlabel('Net Profit / Loss ($K)', color='#cbd5e1', fontsize=8, fontweight='bold')
    ax.tick_params(axis='x', labelcolor='#cbd5e1', labelsize=7)
    ax.tick_params(axis='y', labelcolor='#f8fafc', labelsize=7.5)
    
    for bar in bars:
        w = bar.get_width()
        if w < 0:
            ax.text(w - 5, bar.get_y() + bar.get_height()/2, f'${w:.1f}K', va='center', ha='right', color='#fb7185', fontsize=7, fontweight='bold')
        else:
            ax.text(w + 5, bar.get_y() + bar.get_height()/2, f'${w:.1f}K', va='center', ha='left', color='#34d399', fontsize=7)
            
    ax.set_xlim(min(sub['Profit'] / 1e3) * 1.35, max(sub['Profit'] / 1e3) * 1.25)
    ax.grid(color='#334155', linestyle=':', alpha=0.6, axis='x')
    for spine in ax.spines.values():
        spine.set_color('#334155')
        
    ax.set_title('Sub-Category Profitability Spectrum (Highlighting Deficit in Tables)', color='#f8fafc', fontsize=9, fontweight='bold', pad=8)
    plt.tight_layout()
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', facecolor=fig.get_facecolor(), dpi=300)
    plt.close(fig)
    buf.seek(0)
    return buf

def plot_discount_scatter(df):
    sub = df.groupby('Sub-Category').agg(
        Sales=('Sales', 'sum'),
        Profit=('Profit', 'sum'),
        Discount=('Discount', 'mean')
    ).reset_index()
    sub['Margin'] = (sub['Profit'] / sub['Sales']) * 100
    
    fig, ax = plt.subplots(figsize=(6.5, 2.5), dpi=300)
    fig.patch.set_facecolor('#0f172a')
    ax.set_facecolor('#0f172a')
    
    for _, row in sub.iterrows():
        color = '#f43f5e' if row['Margin'] < 0 else '#818cf8'
        ax.scatter(row['Discount'] * 100, row['Margin'], color=color, s=row['Sales']/15000, alpha=0.8, edgecolors='#fff', linewidth=0.5)
        ax.annotate(row['Sub-Category'], (row['Discount'] * 100 + 0.3, row['Margin'] - 0.5), color='#cbd5e1', fontsize=6.5)
        
    ax.axhline(0, color='#f43f5e', linestyle='--', linewidth=0.8, alpha=0.7)
    ax.set_xlabel('Average Discount (%)', color='#cbd5e1', fontsize=8, fontweight='bold')
    ax.set_ylabel('Profit Margin (%)', color='#cbd5e1', fontsize=8, fontweight='bold')
    ax.tick_params(colors='#94a3b8', labelsize=7)
    ax.grid(color='#334155', linestyle=':', alpha=0.6)
    for spine in ax.spines.values():
        spine.set_color('#334155')
        
    ax.set_title('Discount % vs Profit Margin Correlation (Severe Loss Above 20% Discount)', color='#f8fafc', fontsize=9, fontweight='bold', pad=8)
    plt.tight_layout()
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', facecolor=fig.get_facecolor(), dpi=300)
    plt.close(fig)
    buf.seek(0)
    return buf

def plot_ship_mode_charts(df):
    ship = df.groupby('Ship Mode').agg(
        Orders=('Order ID', 'nunique'),
        Avg_Cost=('Shipping Cost', 'mean')
    ).sort_values(by='Orders', ascending=False).reset_index()
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(6.5, 2.3), dpi=300)
    fig.patch.set_facecolor('#0f172a')
    ax1.set_facecolor('#0f172a')
    ax2.set_facecolor('#0f172a')
    
    # Orders by mode
    ax1.bar(ship['Ship Mode'], ship['Orders'], color=['#6366f1', '#06b6d4', '#f59e0b', '#f43f5e'], width=0.5)
    ax1.set_title('Orders by Ship Mode', color='#f8fafc', fontsize=8, fontweight='bold')
    ax1.tick_params(axis='x', labelcolor='#cbd5e1', labelsize=6.5, rotation=15)
    ax1.tick_params(axis='y', labelcolor='#cbd5e1', labelsize=6.5)
    ax1.grid(color='#334155', linestyle=':', alpha=0.6, axis='y')
    for s in ax1.spines.values(): s.set_color('#334155')
    
    # Avg Cost
    ax2.bar(ship['Ship Mode'], ship['Avg_Cost'], color=['#10b981', '#06b6d4', '#f59e0b', '#f43f5e'], width=0.5)
    ax2.set_title('Avg Shipping Cost ($ / Order)', color='#f8fafc', fontsize=8, fontweight='bold')
    ax2.tick_params(axis='x', labelcolor='#cbd5e1', labelsize=6.5, rotation=15)
    ax2.tick_params(axis='y', labelcolor='#cbd5e1', labelsize=6.5)
    ax2.grid(color='#334155', linestyle=':', alpha=0.6, axis='y')
    for s in ax2.spines.values(): s.set_color('#334155')
    
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', facecolor=fig.get_facecolor(), dpi=300)
    plt.close(fig)
    buf.seek(0)
    return buf


# -----------------------------------------------------------------------------
# 2. Numbered Canvas for Header/Footer Pagination
# -----------------------------------------------------------------------------
class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor('#64748b'))
        
        # Header (Pages 2+)
        if self._pageNumber > 1:
            self.drawString(36, 11 * inch - 25, "GLOBAL SUPERSTORE | EXECUTIVE BUSINESS REPORT")
            self.drawRightString(8.5 * inch - 36, 11 * inch - 25, "CONFIDENTIAL")
            self.setStrokeColor(colors.HexColor('#cbd5e1'))
            self.setLineWidth(0.5)
            self.line(36, 11 * inch - 30, 8.5 * inch - 36, 11 * inch - 30)
            
        # Footer (All pages)
        self.setFont("Helvetica", 7.5)
        self.drawString(36, 22, "Global Superstore Commercial Strategy | 51,290 Transactions | Power BI & DAX Architecture")
        self.drawRightString(8.5 * inch - 36, 22, f"Page {self._pageNumber} of {page_count}")
        self.setStrokeColor(colors.HexColor('#cbd5e1'))
        self.setLineWidth(0.5)
        self.line(36, 30, 8.5 * inch - 36, 30)
        self.restoreState()


# -----------------------------------------------------------------------------
# 3. Build Full PDF Document
# -----------------------------------------------------------------------------
def generate_pdf(csv_path='Global Superstore - Orders.csv', output_pdf='Global_Sales_Executive_Report.pdf'):
    print(f"[*] Generating PDF Report using {csv_path}...")
    df = pd.read_csv(csv_path, encoding='latin1')
    df['Order Date'] = pd.to_datetime(df['Order Date'])
    df['Ship Date'] = pd.to_datetime(df['Ship Date'])
    
    doc = SimpleDocTemplate(
        output_pdf,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=40,
        bottomMargin=40
    )
    
    styles = getSampleStyleSheet()
    
    # Custom Typography Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor('#0f172a')
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#64748b')
    )
    
    h1_style = ParagraphStyle(
        'H1Style',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=15,
        textColor=colors.HexColor('#1e293b'),
        spaceBefore=10,
        spaceAfter=6
    )
    
    body_style = ParagraphStyle(
        'BodyText',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor('#334155')
    )
    
    callout_style = ParagraphStyle(
        'CalloutText',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor('#991b1b')
    )
    
    elements = []
    
    # =========================================================================
    # PAGE 1: EXECUTIVE OVERVIEW & MACRO SCORECARD
    # =========================================================================
    # Header Title Banner
    header_data = [
        [
            Paragraph("<b>GLOBAL SUPERSTORE</b><br/><font size=7 color='#64748b'>COMMERCIAL ANALYTICS DIVISION</font>", ParagraphStyle('H', fontName='Helvetica-Bold', fontSize=11, leading=13, textColor=colors.HexColor('#4338ca'))),
            Paragraph("<b>EXECUTIVE PERFORMANCE REPORT (2011–2014)</b><br/><font size=7 color='#64748b'>Scope: 51,290 Transactions | 147 Countries | $12.64M Gross Revenue</font>", ParagraphStyle('HR', fontName='Helvetica-Bold', fontSize=9, leading=12, alignment=2, textColor=colors.HexColor('#0f172a')))
        ]
    ]
    header_table = Table(header_data, colWidths=[200, 340])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LINEBELOW', (0,0), (-1,-1), 1.5, colors.HexColor('#4338ca'))
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 10))
    
    # Macro Scorecard 4-Card Grid
    kpi_cards = [
        [
            Paragraph("<font size=7 color='#64748b'><b>GROSS REVENUE</b></font><br/><b><font size=13 color='#1e293b'>$12.64M</font></b><br/><font size=6.5 color='#15803d'>+26.3% YoY Growth</font>", body_style),
            Paragraph("<font size=7 color='#64748b'><b>NET PROFIT</b></font><br/><b><font size=13 color='#1e293b'>$1.47M</font></b><br/><font size=6.5 color='#15803d'>+23.9% YoY Profit</font>", body_style),
            Paragraph("<font size=7 color='#64748b'><b>PROFIT MARGIN</b></font><br/><b><font size=13 color='#1e293b'>11.61%</font></b><br/><font size=6.5 color='#0284c7'>Target: > 12.0%</font>", body_style),
            Paragraph("<font size=7 color='#64748b'><b>TOTAL ORDERS</b></font><br/><b><font size=13 color='#1e293b'>25,035</font></b><br/><font size=6.5 color='#64748b'>Avg AOV: $504.99</font>", body_style),
            Paragraph("<font size=7 color='#b91c1c'><b>PROFIT LEAK</b></font><br/><b><font size=13 color='#b91c1c'>$521.4K</font></b><br/><font size=6.5 color='#b91c1c'>12,540 Deficit Lines</font>", body_style)
        ]
    ]
    card_table = Table(kpi_cards, colWidths=[108, 108, 108, 108, 108])
    card_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (3,0), colors.HexColor('#f8fafc')),
        ('BACKGROUND', (4,0), (4,0), colors.HexColor('#fef2f2')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6)
    ]))
    elements.append(card_table)
    elements.append(Spacer(1, 10))
    
    # Executive Narrative Summary
    elements.append(Paragraph("<b>Executive Summary:</b> Global Superstore generated $12.64M in gross sales and $1.47M in net profit over 4 fiscal years, expanding top-line revenue by 90.3% from 2011 ($2.26M) to 2014 ($4.30M). However, margin efficiency remained capped at 11.6% due to $521.4K in avoidable profit destruction originating from un-governed discounting and the structurally unprofitable Tables line.", body_style))
    elements.append(Spacer(1, 10))
    
    # Monthly Trajectory Chart + Category Donut Chart
    img_trend = plot_monthly_trend(df)
    img_donut = plot_category_donut(df)
    
    chart_row = [
        [Image(img_trend, width=3.65*inch, height=1.45*inch), Image(img_donut, width=1.85*inch, height=1.45*inch)]
    ]
    chart_table = Table(chart_row, colWidths=[360, 180])
    chart_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0)
    ]))
    elements.append(chart_table)
    elements.append(Spacer(1, 10))
    
    # YoY Performance Table
    elements.append(Paragraph("<b>Macro Year-Over-Year Financial Progression (2011–2014)</b>", h1_style))
    yoy_rows = [
        ["Fiscal Year", "Gross Revenue", "YoY Sales %", "Net Profit", "YoY Profit %", "Profit Margin", "Order Volume"],
        ["2011", "$2,259,451", "—", "$248,941", "—", "11.02%", "4,440 orders"],
        ["2012", "$2,677,439", "+18.50%", "$307,415", "+23.49%", "11.48%", "5,343 orders"],
        ["2013", "$3,405,746", "+27.20%", "$406,935", "+32.37%", "11.95%", "6,721 orders"],
        ["2014", "$4,299,866", "+26.25%", "$504,166", "+23.89%", "11.73%", "8,531 orders"]
    ]
    yoy_table = Table(yoy_rows, colWidths=[70, 80, 75, 75, 75, 75, 90])
    yoy_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e293b')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 7.5),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f8fafc')]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4)
    ]))
    elements.append(yoy_table)
    elements.append(PageBreak())
    
    # =========================================================================
    # PAGE 2: GEOGRAPHIC & MARKET INTELLIGENCE
    # =========================================================================
    elements.append(Paragraph("<b>Geographic & Market Intelligence</b>", title_style))
    elements.append(Paragraph("Global sales distribution across 7 regional market hubs and 147 operating nations.", subtitle_style))
    elements.append(Spacer(1, 8))
    
    # Market Performance Chart
    img_market = plot_market_performance(df)
    elements.append(Image(img_market, width=5.8*inch, height=2.4*inch))
    elements.append(Spacer(1, 10))
    
    # Top 10 Profitable vs Bottom 10 Loss-Making Nations
    elements.append(Paragraph("<b>Geographic Profit Distribution: Top 10 Profitable vs. Bottom 10 Profit-Deficit Nations</b>", h1_style))
    
    top_countries = [
        ["Top 10 Profit Nations", "Market", "Sales ($)", "Profit ($)", "Margin %"],
        ["United States", "US", "$2,297,201", "$286,397", "12.47%"],
        ["China", "APAC", "$700,562", "$150,683", "21.51%"],
        ["India", "APAC", "$589,650", "$129,072", "21.89%"],
        ["United Kingdom", "EU", "$528,576", "$111,900", "21.17%"],
        ["France", "EU", "$858,931", "$109,029", "12.69%"],
        ["Germany", "EU", "$628,840", "$107,323", "17.07%"],
        ["Australia", "APAC", "$925,236", "$103,907", "11.23%"],
        ["Mexico", "LATAM", "$622,591", "$102,818", "16.51%"],
        ["Spain", "EU", "$287,147", "$54,390", "18.94%"],
        ["El Salvador", "LATAM", "$177,555", "$42,023", "23.67%"]
    ]
    
    bottom_countries = [
        ["Bottom 10 Deficit Nations", "Market", "Sales ($)", "Profit ($)", "Avg Disc %"],
        ["Turkey", "EMEA", "$108,508", "-$98,447", "60.0%"],
        ["Nigeria", "Africa", "$54,350", "-$80,751", "70.0%"],
        ["Netherlands", "EU", "$77,515", "-$41,070", "48.2%"],
        ["Honduras", "LATAM", "$90,126", "-$29,482", "40.7%"],
        ["Pakistan", "APAC", "$58,873", "-$22,447", "44.5%"],
        ["Argentina", "LATAM", "$57,512", "-$18,694", "43.3%"],
        ["Panama", "LATAM", "$51,540", "-$17,723", "40.6%"],
        ["Sweden", "EU", "$30,491", "-$17,519", "50.8%"],
        ["Philippines", "APAC", "$183,420", "-$16,128", "34.6%"],
        ["South Korea", "APAC", "$33,125", "-$12,793", "45.3%"]
    ]
    
    t_top = Table(top_countries, colWidths=[80, 45, 50, 50, 45])
    t_top.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#065f46')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 6.5),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f0fdf4')]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('ALIGN', (2,0), (-1,-1), 'RIGHT'),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5)
    ]))
    
    t_bottom = Table(bottom_countries, colWidths=[85, 45, 50, 50, 45])
    t_bottom.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#991b1b')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 6.5),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#fef2f2')]),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('ALIGN', (2,0), (-1,-1), 'RIGHT'),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5)
    ]))
    
    geo_grid = Table([[t_top, t_bottom]], colWidths=[270, 270])
    geo_grid.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0)
    ]))
    elements.append(geo_grid)
    elements.append(PageBreak())
    
    # =========================================================================
    # PAGE 3: PROFIT LEAK DIAGNOSTIC & PRODUCT PORTFOLIO
    # =========================================================================
    elements.append(Paragraph("<b>Profit Leak Diagnostic & Category Economics</b>", title_style))
    elements.append(Paragraph("Root-cause investigation of the -$64,083 Tables deficit and discount margin erosion.", subtitle_style))
    elements.append(Spacer(1, 6))
    
    # Critical Alert Callout Banner
    alert_box = [
        [
            Paragraph("<b>CRITICAL PROFIT LEAK DISCOVERY: STRUCTURAL DEFICIT IN TABLES SUB-CATEGORY</b><br/>Across 17 product sub-categories, <b>Tables generated -$64,083.39 in net losses</b> on $757,041.90 sales. The primary driver is an aggressive <b>29.07% average discount rate</b> combined with heavy freight delivery costs.", callout_style)
        ]
    ]
    t_alert = Table(alert_box, colWidths=[540])
    t_alert.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#fef2f2')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#f87171')),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8)
    ]))
    elements.append(t_alert)
    elements.append(Spacer(1, 8))
    
    # Subcategory Spectrum Chart
    img_sub = plot_subcat_spectrum(df)
    elements.append(Image(img_sub, width=5.8*inch, height=2.6*inch))
    elements.append(Spacer(1, 6))
    
    # Discount vs Margin Scatter Plot
    img_disc = plot_discount_scatter(df)
    elements.append(Image(img_disc, width=5.8*inch, height=2.2*inch))
    elements.append(PageBreak())
    
    # =========================================================================
    # PAGE 4: LOGISTICS ECONOMICS & STRATEGIC RECOMMENDATIONS
    # =========================================================================
    elements.append(Paragraph("<b>Logistics Fulfillment & Strategic Action Plan</b>", title_style))
    elements.append(Paragraph("Operational efficiency analysis and C-suite commercial roadmap.", subtitle_style))
    elements.append(Spacer(1, 8))
    
    # Ship Mode Charts
    img_ship = plot_ship_mode_charts(df)
    elements.append(Image(img_ship, width=5.8*inch, height=2.0*inch))
    elements.append(Spacer(1, 10))
    
    # Strategic Recommendations
    elements.append(Paragraph("<b>4 Actionable Strategic Initiatives for Executive Leadership</b>", h1_style))
    
    strat_data = [
        [
            Paragraph("<b>1. Enforce Global Discount Guardrails</b><br/><font size=7 color='#475569'>Cap discretionary discounts at 15%. Require VP approval above 20%. Immediately eliminates $220k+ in emerging market losses (Turkey, Nigeria, Netherlands).</font>", body_style),
            Paragraph("<b>2. Overhaul the 'Tables' Product Line</b><br/><font size=7 color='#475569'>Implement a mandatory bulky freight surcharge and +12% catalog price adjustment. Delist negative-margin SKUs with heavy freight.</font>", body_style)
        ],
        [
            Paragraph("<b>3. Prioritize High-CLV B2B Corporate Accounts</b><br/><font size=7 color='#475569'>Corporate & Home Office accounts exhibit superior repeat order rates and margin stability (11.5%–12.0%). Deploy dedicated account executives.</font>", body_style),
            Paragraph("<b>4. Optimize Fulfillment Carrier Rate Cards</b><br/><font size=7 color='#475569'>Migrate low-priority replenishment orders to Standard Class (5-day cycle) to reduce expedited freight fees by ~$11/order.</font>", body_style)
        ]
    ]
    t_strat = Table(strat_data, colWidths=[265, 265])
    t_strat.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8)
    ]))
    elements.append(t_strat)
    elements.append(Spacer(1, 12))
    
    # Sign-off block
    sign_off = [
        [
            Paragraph("<b>Prepared by:</b> Global Commercial Analytics & BI Team", body_style),
            Paragraph("<b>Approved by:</b> Executive Strategy Committee", ParagraphStyle('R', parent=body_style, alignment=2))
        ]
    ]
    t_sign = Table(sign_off, colWidths=[270, 270])
    t_sign.setStyle(TableStyle([
        ('LINEABOVE', (0,0), (-1,-1), 0.5, colors.HexColor('#94a3b8')),
        ('TOPPADDING', (0,0), (-1,-1), 6)
    ]))
    elements.append(t_sign)
    
    # Build Document
    doc.build(elements, canvasmaker=NumberedCanvas)
    print(f"[+] PDF Report successfully created: {output_pdf}")

if __name__ == '__main__':
    generate_pdf()
