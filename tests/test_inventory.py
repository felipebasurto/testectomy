import os
import subprocess
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(ROOT, "skills", "testectomy", "scripts", "inventory.sh")

FIXTURE = {
    "web/cart.test.ts": "describe('cart', () => {\n  it('adds', () => {})\n  test('removes', () => {})\n})\n",
    "py/test_cart.py": "def test_adds():\n    pass\n\nasync def test_removes():\n    pass\n",
    "go/cart_test.go": "func TestAdds(t *testing.T) {}\nfunc helper() {}\n",
    "rs/tests/cart.rs": "#[test]\nfn adds() {}\n#[tokio::test]\nasync fn removes() {}\n",
    "java/CartTest.java": "@Test\nvoid adds() {}\n",
    "ios/CartTests.swift": "final class CartTests: XCTestCase {\n    func testAdds() {}\n    @MainActor func testRemoves() async {}\n    func helper() {}\n}\n",
    "features/cart.feature": "Feature: cart\n  Scenario: adds\n  Scenario Outline: removes\n",
    "data/table_test.pdf": "%PDF",
    "web/tsconfig.test.json": "{}",
    "web/__snapshots__/cart.test.ts.snap": "exports[`x`] = 1;\n",
    "node_modules/dep/index.test.js": "it('x', () => {})\n",
}


class InventoryTest(unittest.TestCase):
    def test_INV_1_INV_2_INV_3(self):
        with tempfile.TemporaryDirectory() as repo:
            for path, body in FIXTURE.items():
                full = os.path.join(repo, path)
                os.makedirs(os.path.dirname(full), exist_ok=True)
                with open(full, "w") as f:
                    f.write(body)

            out = subprocess.run(["bash", SCRIPT, repo], capture_output=True, text=True, check=True).stdout

        rows = {
            parts[2]: int(parts[1])
            for parts in (line.split() for line in out.splitlines())
            if len(parts) == 3 and parts[0].isdigit()
        }
        self.assertEqual(
            rows,
            {
                "features/cart.feature": 2,
                "go/cart_test.go": 1,
                "ios/CartTests.swift": 2,
                "java/CartTest.java": 1,
                "py/test_cart.py": 2,
                "rs/tests/cart.rs": 2,
                "web/cart.test.ts": 2,
            },
        )
        self.assertTrue(out.rstrip().splitlines()[-1].startswith("TOTAL: 7 files"))


if __name__ == "__main__":
    unittest.main()
