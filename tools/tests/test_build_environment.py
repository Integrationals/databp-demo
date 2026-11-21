"""LA-1, the builder's environment (DIG-657 test plan, knowledge 111 item 825, paths 1 to 5; design D-5)."""
import json, pathlib, re, subprocess, sys, tempfile, unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
ENVS = json.loads((ROOT / "tools" / "environments.json").read_text())


def build(*args):
    return subprocess.run([sys.executable, str(ROOT / "tools" / "build.py"), *args], capture_output=True, text=True)


def chat(folder):
    m = re.search(r'id="chat" data-url="([^"]*)" data-env="([^"]*)"', (folder / "ask.html").read_text())
    return m.groups() if m else None


class TestBuildEnvironment(unittest.TestCase):
    def built(self, env):
        out = pathlib.Path(tempfile.mkdtemp())
        r = build("--env", env, "--out", str(out))
        self.assertEqual(r.returncode, 0, r.stderr)
        return out

    def test_build_dev_writes_dev_address(self):
        self.assertEqual(chat(self.built("dev")), (ENVS["dev"]["morgan"], "dev"))

    def test_build_qa_writes_qa_address(self):
        self.assertEqual(chat(self.built("qa")), (ENVS["qa"]["morgan"], "qa"))

    def test_build_prod_writes_prod_address(self):
        r = build("--env", "prod", "--check")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(chat(ROOT), (ENVS["prod"]["morgan"], "production"))

    def test_build_no_environment_refused(self):
        out = pathlib.Path(tempfile.mkdtemp())
        r = build("--out", str(out))
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("--env dev, qa or prod", r.stderr)
        self.assertEqual(list(out.iterdir()), [])

    def test_build_unknown_environment_refused(self):
        out = pathlib.Path(tempfile.mkdtemp())
        r = build("--env", "staging", "--out", str(out))
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("--env dev, qa or prod", r.stderr)
        self.assertEqual(list(out.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
