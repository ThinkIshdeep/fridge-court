import re, subprocess, shutil, tempfile
from pathlib import Path
import numpy as np
from scipy.optimize import milp, LinearConstraint, Bounds
from .core import Base, bounded, decoded
RECIPES = [{'name': 'Tomato rice', 'ingredients': {'rice': 150, 'tomato': 120, 'onion': 50}, 'tags': ['vegan'], 'cost': 35}, {'name': 'Egg fried rice', 'ingredients': {'rice': 150, 'egg': 2, 'onion': 40}, 'tags': ['vegetarian'], 'cost': 50}, {'name': 'Dal bowl', 'ingredients': {'lentils': 100, 'tomato': 60, 'rice': 100}, 'tags': ['vegan'], 'cost': 40}, {'name': 'Paneer wrap', 'ingredients': {'paneer': 100, 'tomato': 80, 'onion': 40}, 'tags': ['vegetarian'], 'cost': 70}, {'name': 'Tomato soup', 'ingredients': {'tomato': 200, 'onion': 40}, 'tags': ['vegan'], 'cost': 25}]

class Engine(Base):
    actions = Base.actions | {'add', 'consume', 'receipt', 'confirm_receipt', 'plan', 'advance'}

    def __init__(self):
        super().__init__()
        self.reset({})

    def reset(self, p):
        self.state = {'day': 0, 'inventory': [{'name': 'rice', 'quantity': 1000.0, 'unit': 'g', 'expires': 35}, {'name': 'tomato', 'quantity': 600.0, 'unit': 'g', 'expires': 4}, {'name': 'onion', 'quantity': 300.0, 'unit': 'g', 'expires': 10}, {'name': 'lentils', 'quantity': 400.0, 'unit': 'g', 'expires': 60}, {'name': 'egg', 'quantity': 6.0, 'unit': 'pieces', 'expires': 12}], 'events': [], 'receipt_preview': [], 'plan': [], 'last_result': None}

    def add(self, p):
        name = str(p.get('name', '')).strip().lower()[:60]
        q = bounded(p, 'quantity', 100, 0.1, 100000)
        days = bounded(p, 'days', 7, 0, 365, True)
        unit = p.get('unit', 'g')
        if not name or unit not in ['g', 'ml', 'pieces']:
            raise ValueError('Enter item name and g, ml, or pieces')
        self.state['inventory'].append({'name': name, 'quantity': q, 'unit': unit, 'expires': self.state['day'] + days})
        self.state['events'].append({'kind': 'purchase', 'name': name, 'quantity': q, 'day': self.state['day']})

    def consume(self, p):
        i = int(p['index'])
        q = bounded(p, 'quantity', 50, 0.1, 100000)
        item = self.state['inventory'][i]
        if q > item['quantity']:
            raise ValueError('Quantity exceeds confirmed stock')
        item['quantity'] -= q
        kind = 'waste' if p.get('waste') else 'consume'
        self.state['events'].append({'kind': kind, 'name': item['name'], 'quantity': q, 'day': self.state['day']})

    def receipt(self, p):
        text = str(p.get('text', ''))
        if 'data' in p:
            raw = decoded(p)
            name = str(p.get('name', ''))
            if name.lower().endswith(('.txt', '.csv')):
                text = raw.decode('utf-8-sig')
            else:
                if not shutil.which('tesseract'):
                    raise ValueError('Image OCR needs Tesseract installed; paste receipt text instead')
                with tempfile.TemporaryDirectory() as td:
                    image = Path(td) / 'receipt.png'
                    image.write_bytes(raw)
                    out = subprocess.run(['tesseract', str(image), 'stdout'], capture_output=True, text=True, timeout=25, check=True)
                    text = out.stdout
        rows = []
        for line in text.splitlines():
            match = re.search('([A-Za-z ]+?)\\s+([\\d.]+)\\s*(kg|g|ml|l|pieces|pcs)?\\b', line, re.I)
            if match:
                name = match[1].strip().lower()
                q = float(match[2])
                unit = (match[3] or 'g').lower()
                if unit in ['kg', 'l']:
                    q *= 1000
                    unit = 'g' if unit == 'kg' else 'ml'
                if unit == 'pcs':
                    unit = 'pieces'
                if q > 0:
                    rows.append({'name': name, 'quantity': q, 'unit': unit, 'days': 7, 'review_required': True})
        self.state['receipt_preview'] = rows
        return {'lines': rows, 'text': text, 'note': 'Review extracted quantities, units, and dates before adding stock.'}

    def confirm_receipt(self, p):
        rows = p.get('rows', self.state['receipt_preview'])
        for row in rows:
            self.add(row)
        self.state['receipt_preview'] = []
        return {'added': len(rows)}

    def advance(self, p):
        self.state['day'] += 1
        return {'day': self.state['day']}

    def plan(self, p):
        diet = p.get('diet', 'any')
        budget = bounded(p, 'budget', 150, 10, 10000)
        recipes = [r for r in RECIPES if diet != 'vegan' or 'vegan' in r['tags']]
        stock = {}
        urgency = {}
        for x in self.state['inventory']:
            if x['expires'] < self.state['day']:
                continue
            stock[x['name']] = stock.get(x['name'], 0) + x['quantity']
            urgency[x['name']] = max(urgency.get(x['name'], 0), 1 / max(1, x['expires'] - self.state['day'] + 1))
        names = sorted({k for r in recipes for k in r['ingredients']})
        A = np.array([[r['ingredients'].get(k, 0) for r in recipes] for k in names] + [[r['cost'] for r in recipes]], float)
        upper = np.array([stock.get(k, 0) for k in names] + [budget])
        utility = np.array([1 + sum((q * urgency.get(k, 0) / 100 for k, q in r['ingredients'].items())) for r in recipes])
        sol = milp(-utility, integrality=np.ones(len(recipes)), bounds=Bounds(np.zeros(len(recipes)), np.ones(len(recipes)) * 2), constraints=LinearConstraint(A, np.zeros(len(upper)), upper), options={'time_limit': 3})
        plan = []
        if sol.x is not None:
            for r, count in zip(recipes, np.rint(sol.x).astype(int)):
                if count:
                    plan.append(dict(r, servings=int(count)))
        self.state['plan'] = plan
        return {'meals': plan, 'cost': sum((x['cost'] * x['servings'] for x in plan)), 'budget': budget, 'method': 'Integer-constrained stock/budget optimization; expiry dates are user input, not food-safety estimates.'}

    def evaluate(self, p):
        e = Engine()
        out = e.plan({'diet': 'vegan', 'budget': 80})
        used = {}
        for r in out['meals']:
            for k, q in r['ingredients'].items():
                used[k] = used.get(k, 0) + q * r['servings']
        stock = {x['name']: x['quantity'] for x in e.state['inventory']}
        result = {'checks': {'budget': out['cost'] <= 80, 'diet': all(('vegan' in r['tags'] for r in out['meals'])), 'stock': all((q <= stock.get(k, 0) for k, q in used.items()))}, 'note': 'Constraint checks, not a measured household waste-reduction study.'}
        self.state['last_result'] = result
        return result
