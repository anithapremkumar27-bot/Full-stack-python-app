import unittest
import os
from fastapi.testclient import TestClient

# Adjust path to import app correctly
from app.main import app

class TestTodoAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.test_category_name = "Test Category 123"
        cls.test_category_color = "#E0F2FE"

    def test_01_create_category(self):
        # 1. Create a category
        response = self.client.post(
            "/api/categories",
            json={"name": self.test_category_name, "color": self.test_category_color}
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["name"], self.test_category_name)
        self.assertEqual(data["color"], self.test_category_color)
        self.assertIn("id", data)
        self.__class__.category_id = data["id"]

    def test_02_create_duplicate_category_fails(self):
        # 2. Duplicate name should fail with 400
        response = self.client.post(
            "/api/categories",
            json={"name": self.test_category_name, "color": "#FFFFFF"}
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("detail", response.json())

    def test_03_get_categories(self):
        # 3. Retrieve list of categories
        response = self.client.get("/api/categories")
        self.assertEqual(response.status_code, 200)
        categories = response.json()
        self.assertTrue(len(categories) >= 1)
        # Verify our category is in the list
        names = [c["name"] for c in categories]
        self.assertIn(self.test_category_name, names)

    def test_04_create_task(self):
        # 4. Create task in the test category
        task_data = {
            "title": "API Todo Test Task",
            "description": "Verify task creation works perfectly",
            "status": "To Do",
            "priority": "High",
            "due_date": "2026-12-31",
            "category_id": self.category_id
        }
        response = self.client.post(
            "/api/tasks",
            json=task_data
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["title"], task_data["title"])
        self.assertEqual(data["priority"], task_data["priority"])
        self.assertEqual(data["due_date"], task_data["due_date"])
        self.assertEqual(data["category_id"], self.category_id)
        self.__class__.task_id = data["id"]

    def test_05_get_tasks(self):
        # 5. Fetch tasks and verify
        response = self.client.get("/api/tasks")
        self.assertEqual(response.status_code, 200)
        tasks = response.json()
        self.assertTrue(len(tasks) >= 1)
        task_ids = [t["id"] for t in tasks]
        self.assertIn(self.task_id, task_ids)

    def test_06_update_task(self):
        # 6. Update task status, priority, description
        update_payload = {
            "status": "In Progress",
            "priority": "Medium",
            "description": "Updated integration description"
        }
        response = self.client.put(
            f"/api/tasks/{self.task_id}",
            json=update_payload
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "In Progress")
        self.assertEqual(data["priority"], "Medium")
        self.assertEqual(data["description"], "Updated integration description")

    def test_07_delete_task(self):
        # 7. Delete task
        response = self.client.delete(f"/api/tasks/{self.task_id}")
        self.assertEqual(response.status_code, 204)
        
        # Verify it is deleted
        tasks = self.client.get("/api/tasks").json()
        task_ids = [t["id"] for t in tasks]
        self.assertNotIn(self.task_id, task_ids)

    def test_08_delete_category(self):
        # 8. Re-create task, delete category, and verify cascade delete of the task
        task_data = {
            "title": "API Todo Test Cascade Task",
            "description": "Verify cascade delete works",
            "status": "To Do",
            "priority": "Low",
            "due_date": "2026-12-31",
            "category_id": self.category_id
        }
        create_res = self.client.post("/api/tasks", json=task_data)
        self.assertEqual(create_res.status_code, 201)
        new_task_id = create_res.json()["id"]

        # Delete category
        delete_cat_res = self.client.delete(f"/api/categories/{self.category_id}")
        self.assertEqual(delete_cat_res.status_code, 204)
        
        # Verify category is gone
        get_cats = self.client.get("/api/categories").json()
        cat_ids = [c["id"] for c in get_cats]
        self.assertNotIn(self.category_id, cat_ids)

        # Verify task is also deleted by cascade
        tasks = self.client.get("/api/tasks").json()
        task_ids = [t["id"] for t in tasks]
        self.assertNotIn(new_task_id, task_ids)

if __name__ == "__main__":
    unittest.main()
