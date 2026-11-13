import base64, io, json, math, unittest
import numpy as np
from lab.core import astar, clean
from lab import fridge

class CoreTests(unittest.TestCase):

    def test_astar_routes_around_wall(self):
        path = astar([0, 0], [4, 4], [[2, y] for y in range(4)], 5)
        self.assertEqual(path[-1], [4, 4])
        self.assertTrue(all((p[0] != 2 or p[1] == 4 for p in path)))

    def test_astar_impossible(self):
        self.assertEqual(astar([0, 0], [2, 2], [[1, y] for y in range(3)], 3), [])

    def test_json_serialization(self):
        self.assertEqual(clean({'a': np.int64(2), 'b': float('nan')}), {'a': 2, 'b': None})

class FridgeTests(unittest.TestCase):

    def test_cannot_consume_more_than_stock(self):
        with self.assertRaises(ValueError):
            fridge.Engine().consume({'index': 0, 'quantity': 100000})

    def test_receipt_requires_confirmation(self):
        e = fridge.Engine()
        before = len(e.state['inventory'])
        e.receipt({'text': 'Rice 1 kg'})
        self.assertEqual(len(e.state['inventory']), before)
        e.confirm_receipt({})
        self.assertEqual(e.state['inventory'][-1]['quantity'], 1000)

    def test_constraints(self):
        self.assertTrue(all(fridge.Engine().evaluate({})['checks'].values()))
