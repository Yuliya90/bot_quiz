import aiosqlite
from main_bot import DB_NAME

results = {}
async def save_result(user_id, score):
    global results
    if user_id not in results:
        results[user_id] = {'score': 0}
    results[user_id]['score'] += score
    await update_results_db(user_id)
async def update_results_db(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''CREATE TABLE IF NOT EXISTS quiz_results (user_id INTEGER PRIMARY KEY, score INTEGER)''')
        await db.execute('''INSERT OR REPLACE INTO quiz_results (user_id, score) VALUES (?,?)''', (user_id, results[user_id]['score']))
        await db.commit()
async def get_stats(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        result = await db.execute('''SELECT score FROM quiz_results WHERE user_id = (?)''', (user_id,))
        stats = await result.fetchone()
        return stats[0] if stats[0] is not None else 0


async def create_table():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''CREATE TABLE IF NOT EXISTS quiz_state (user_id INTEGER PRIMARY KEY, question_index INTEGER)''')
        await db.execute('''CREATE TABLE IF NOT EXISTS quiz_results (user_id INTEGER PRIMARY KEY, score INTEGER)''')
        await db.commit()
