import unittest
from torinbot import TodoListBot


class TestKirill(unittest.TestCase):
    def setUp(self):
        self.bot = TodoListBot("test.db")
        self.tasks = []

    def test_123(self):
        self.bot.add_task(2, 'dasdad')
        self.bot.add_task(2, 'dasdad')
        self.bot.add_task(2, 'dasdad')
        self.bot.change_task_by_index(2,1,'unreal')
        self.bot.delete_task_by_index(2, 0)
        self.bot.delete_task_by_index(2, 1)
        a = self.bot.view_tasks(2)
        b = "Your tasks:\n1. unreal"
        self.assertEqual(a, b)
        self.bot.delete_task_by_index(2, 0)

if __name__ == "__main__":
    unittest.main()
