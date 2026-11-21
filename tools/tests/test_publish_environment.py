"""LA-4, publish.sh's environment (DIG-657 test plan, knowledge 111 item 825, paths 13 to 17; design D-2, D-9)."""
import pathlib, subprocess, unittest

SH = pathlib.Path(__file__).resolve().parents[1] / "publish.sh"


def run(*args):
    return subprocess.run(["sh", str(SH), *args], capture_output=True, text=True)


class TestPublishEnvironment(unittest.TestCase):
    def test_publish_dev_targets_dev(self):
        r = run("--env", "dev", "--dry-run")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("dev build", r.stdout)
        self.assertIn("Integrationals/databp-demo-dev", r.stdout)

    def test_publish_qa_targets_qa(self):
        r = run("--env", "qa", "--dry-run")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("qa build", r.stdout)
        self.assertIn("Integrationals/databp-demo-qa", r.stdout)

    def test_publish_prod_refused(self):
        r = run("--env", "prod", "--dry-run")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("published by Pages from main", r.stderr)

    def test_publish_no_environment_refused(self):
        r = run()
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("--env dev or qa", r.stderr)

    def test_publish_unknown_environment_refused(self):
        r = run("--env", "staging", "--dry-run")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("--env dev or qa", r.stderr)


if __name__ == "__main__":
    unittest.main()
