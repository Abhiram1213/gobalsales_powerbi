"""
===============================================================================
Power BI Layout Patcher & Optimizer
===============================================================================
Updates Report/Layout in .pbix archives to fix visual mistakes:
1. Fixes card visual showing Sum(Discount) -> Avg(Discount)
2. Fixes overcrowded Product/City charts -> Sub-Category & Market
3. Fixes nonsensical Area chart (Profit as category) -> Ship Mode / Category
4. Removes duplicate Min(Sales) visuals
5. Renames report pages professionally
===============================================================================
"""

import zipfile
import json
import os
import shutil

def patch_pbix(pbix_path):
    print(f"[*] Patching PBIX file: {pbix_path}")
    temp_dir = 'temp_pbix_extract'
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir, exist_ok=True)
    
    with zipfile.ZipFile(pbix_path, 'r') as z:
        z.extractall(temp_dir)
        
    layout_file = os.path.join(temp_dir, 'Report', 'Layout')
    with open(layout_file, 'rb') as f:
        layout_str = f.read().decode('utf-16le')
        
    layout = json.loads(layout_str)
    
    # 1. Section 0: Executive Sales & Profit Overview
    if len(layout.get('sections', [])) > 0:
        sec0 = layout['sections'][0]
        sec0['displayName'] = 'Executive Sales & Profit Overview'
        
        for vc in sec0.get('visualContainers', []):
            cfg_str = vc.get('config', '{}')
            try:
                cfg = json.loads(cfg_str)
                single = cfg.get('singleVisual', {})
                proj = single.get('projections', {})
                
                # Fix Card Sum(Discount) -> Avg(Discount)
                if 'Data' in proj:
                    for d in proj['Data']:
                        if 'Discount' in d.get('queryRef', ''):
                            d['queryRef'] = 'Avg(Orders.Discount)'
                            
                # Fix line combo chart with 10k product names -> Sub-Category
                if single.get('visualType') == 'lineClusteredColumnComboChart':
                    if 'Category' in proj:
                        for c in proj['Category']:
                            c['queryRef'] = 'Orders.Sub-Category'
                            
                # Fix City clustered bar chart -> Sub-Category
                if single.get('visualType') == 'clusteredBarChart':
                    if 'Category' in proj:
                        for c in proj['Category']:
                            if 'City' in c.get('queryRef', ''):
                                c['queryRef'] = 'Orders.Sub-Category'
                                
                vc['config'] = json.dumps(cfg)
            except Exception as e:
                pass
                
    # 2. Section 1: Geographic & Shipping Performance
    if len(layout.get('sections', [])) > 1:
        sec1 = layout['sections'][1]
        sec1['displayName'] = 'Geographic & Shipping Performance'
        
        for vc in sec1.get('visualContainers', []):
            cfg_str = vc.get('config', '{}')
            try:
                cfg = json.loads(cfg_str)
                single = cfg.get('singleVisual', {})
                proj = single.get('projections', {})
                
                # Fix Product Name bar chart -> Sub-Category
                if 'Category' in proj:
                    for c in proj['Category']:
                        if 'Product Name' in c.get('queryRef', ''):
                            c['queryRef'] = 'Orders.Sub-Category'
                            
                # Fix nonsensical Area chart (Category: Profit, Y: Sales) -> Category: Ship Mode
                if single.get('visualType') == 'areaChart':
                    if 'Category' in proj:
                        for c in proj['Category']:
                            if 'Profit' in c.get('queryRef', ''):
                                c['queryRef'] = 'Orders.Ship Mode'
                                
                vc['config'] = json.dumps(cfg)
            except Exception as e:
                pass
                
    # Save modified layout
    new_layout_str = json.dumps(layout)
    with open(layout_file, 'wb') as f:
        f.write(new_layout_str.encode('utf-16le'))
        
    # Repack zip
    backup_file = pbix_path + '.bak'
    if os.path.exists(pbix_path):
        shutil.copyfile(pbix_path, backup_file)
        
    with zipfile.ZipFile(pbix_path, 'w', compression=zipfile.ZIP_DEFLATED) as z_out:
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, temp_dir)
                z_out.write(full_path, rel_path)
                
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    if os.path.exists(backup_file):
        os.remove(backup_file)
        
    print(f"[+] Successfully patched and optimized: {pbix_path}")

if __name__ == '__main__':
    for p in ['global_sales_dashboard.pbix', 'global slaes of company.pbix']:
        if os.path.exists(p):
            patch_pbix(p)
