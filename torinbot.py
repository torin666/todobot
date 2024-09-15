import sqlite3
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import time


class TodoListBot:
    def __init__(self, db_name='todos.db'):
        """
        :param db_name:путь до базы данных
        """
        self.db_name = db_name
        self.create_table()

    def create_table(self):
        """
        Проверка на наличие таблицы и в случае ее отсутствия происходит создание таблицы
        """
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS todos (
                    task_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    task TEXT,
                    added_time REAL
                )
            ''')
            conn.commit()

    def add_task(self, user_id, task):
        """
        Функция добавляет задачу в список
        :param user_id:Определяет пользователя, для дальнейшего взаимодействия с ним
        :param task:Добавляет задачу в базу данных
        :return:отправляет пользователю результат добавления задачи в список
        """
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            added_time = time.time()
            try:
                cursor.execute('INSERT INTO todos (user_id, task, added_time) VALUES (?, ?, ?)',
                               (user_id, task, added_time))
                conn.commit()
                return f"Task added: {task}"
            except sqlite3.IntegrintyError:
                return "Задача уже существует."

    def delete_task_by_index(self, user_id, index):
        """
        Функция удаляет задачу из списка
        :param user_id:Определяет пользователя, для дальнейшего взаимодействия с ним
        :param index:Номер задачи в базе данных
        :return:отправляет пользователю результат об удалении задачи из списка, либо об ее отсутствии
        """
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT task_id, task FROM todos WHERE user_id = ? ORDER BY added_time', (user_id,))
            tasks = cursor.fetchall()
            if 0 <= index < len(tasks):
                task_id_to_delete = tasks[index][0]
                cursor.execute('DELETE FROM todos WHERE task_id = ?', (task_id_to_delete,))
                conn.commit()
                return f"Task deleted: {tasks[index][1]}"
            return "Task not found."

    def change_task_by_index(self, user_id, index, new_task):
        """
        Функция для изменения задачи в списке
        :param user_id:Определяет пользователя, для дальнейшего взаимодействия с ним
        :param index:Номер задачи в базе данных
        :param new_task:принимает новую задачу
        :return:отправляет пользователю результат об изменении в списке, либо об отсутствии заменяемой задачи
        """
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT task_id, task FROM todos WHERE user_id = ? ORDER BY added_time', (user_id,))
            tasks = cursor.fetchall()
            if 0 <= index < len(tasks):
                task_id_to_change = tasks[index][0]
                cursor.execute('UPDATE todos SET task = ? WHERE task_id = ?', (new_task, task_id_to_change))
                conn.commit()
                return f"Task changed: {tasks[index][1]} to {new_task}"
            return "Task not found."

    def view_tasks(self, user_id):
        """
        Функция показывает пользователю список задач.
        :param user_id:Определяет пользователя, для дальнейшего взаимодействия с ним
        :return:отправляет пользователю список его задач
        """
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT task_id, task FROM todos WHERE user_id = ? ORDER BY added_time', (user_id,))
            tasks = cursor.fetchall()
            if tasks:
                return "Your tasks:\n" + "\n".join(f"{i + 1}. {task[1]}" for i, task in enumerate(tasks))
            return "No tasks found."


todo_bot = TodoListBot()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
     Функция отправляет пользователю сообщение о своем функционале
    :param update:отправляет боту информацию о том, что была отправлена команда /start.
    """
    await update.message.reply_text(
        "Добро пожаловать в бот-список дел! Используйте /add <задача>, /remove <номер_задачи>, /change <номер_задачи> <новая_задача> или /list для просмотра задач.")


async def add_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
     Функция добавляет задачу в список
    :param update:используется для получения уникального идентификатора пользователя, который отправил команду /add.
    :param context:Функция сначала проверяет, есть ли какие-либо аргументы. Если аргументы есть, она объединяет их в строку (это будет ваша задача) и добавляет задачу с помощью метода add_task.
    Либо пишет, что нужно указать задачу для добавления.
    """
    if context.args:
        task = ' '.join(context.args)
        response = todo_bot.add_task(update.effective_user.id, task)
        await update.message.reply_text(response)
    else:
        await update.message.reply_text("Укажите задачу для добавления.")


async def change_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
     Функция заменяет старую задачу на новую
    :param update:содержит информацию о последнем событии, произошедшем в чате с ботом.
    :param context:Это список аргументов, переданных пользователем после команды.
    """
    if len(context.args) < 2:
        await update.message.reply_text("Пожалуйста, укажите номер задачи и новое описание задачи.")
        return

    try:
        index = int(context.args[0]) - 1  # Преобразуем в нулевой индекс
        new_task = ' '.join(context.args[1:])
        response = todo_bot.change_task_by_index(update.effective_user.id, index, new_task)
        await update.message.reply_text(response)
    except ValueError:
        await update.message.reply_text("Пожалуйста, укажите корректный номер задачи.")


async def delete_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Функция удаляет задачу из списка
    :param update:содержит информацию о последнем событии, произошедшем в чате с ботом.
    :param context:Это список аргументов, переданных пользователем после команды.
    """
    if context.args:
        try:
            index = int(context.args[0]) - 1  # Преобразуем в нулевой индекс
            response = todo_bot.delete_task_by_index(update.effective_user.id, index)
            await update.message.reply_text(response)
        except ValueError:
            await update.message.reply_text("Укажите действительный номер задачи.")
    else:
        await update.message.reply_text("Укажите номер задачи, которую нужно удалить.")


async def view_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
     Функция показывает пользователю список задач.
    :param update: содержит информацию о последнем событии, произошедшем в чате с ботом
    :param context:Это список аргументов, которые могут быть переданы пользователем после команды
    """
    response = todo_bot.view_tasks(update.effective_user.id)
    await update.message.reply_text(response)


application = ApplicationBuilder().token('Your token').build()
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("add", add_task))
application.add_handler(CommandHandler("change", change_task))
application.add_handler(CommandHandler("remove", delete_task))
application.add_handler(CommandHandler("list", view_tasks))

if __name__ == "__main__":
    application.run_polling()
