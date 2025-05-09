import asyncio
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, ContextTypes
from app.services.question_service import (
    add_question,
    update_question,
    delete_question,
    get_all_questions,
    search_questions,
    get_question_count,
    import_questions,
    get_question_by_id
)
from app.services.auth import update_admin_credentials, get_current_admin_credentials

# Telegram Bot Token and Group/Topic Info
BOT_TOKEN = "7696451012:AAH8-zcOzeOprrti5TwK_QxQnJWzo7gFZog"
GROUP_CHAT_ID = "-1002651086083"
TOPIC_ID = "44"

# List of authorized admin Telegram IDs (replace with your Telegram ID)
ADMIN_IDS = [646102582]  # Replace with your actual Telegram user ID

# Initialize the bot
bot = Bot(token=BOT_TOKEN)

# Send notification to the group topic
async def send_telegram_notification(message):
    try:
        await bot.send_message(
            chat_id=GROUP_CHAT_ID,
            message_thread_id=TOPIC_ID,
            text=message
        )
    except Exception as e:
        print(f"Error sending Telegram notification: {e}")

# Restrict bot access to admins only
async def restrict_to_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("Sorry, this bot is for admins only.")
        return False
    return True

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await restrict_to_admin(update, context):
        return
    welcome_message = (
        "Welcome to the IELTS Speaking Admin Bot!\n\n"
        "Commands:\n"
        "/add_question <part> <question> - Add a new question (e.g., /add_question part1 What is your name?)\n"
        "/update_question <part> <id> <new_question> - Update a question\n"
        "/delete_question <part> <id> - Delete a question\n"
        "/update_admin <username> <password> - Update admin credentials\n"
        "/list_questions - List all questions\n"
        "/search <query> - Search questions\n"
        "/count - Show question counts per part\n"
        "/import <json> - Import multiple questions (e.g., /import [{\"part\": \"part1\", \"question\": \"Test question\"}])\n"
    )
    await update.message.reply_text(welcome_message)

# Add question command
async def add_question_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await restrict_to_admin(update, context):
        return
    args = context.args
    if len(args) < 2:
        await update.message.reply_text("Usage: /add_question <part> <question>")
        return
    part = args[0].lower()
    question = " ".join(args[1:])
    try:
        new_id = add_question(part, question)
        await update.message.reply_text(f"Added question to {part} with ID {new_id}: {question}")
        await send_telegram_notification(f"New Question Added to {part}:\nID: {new_id}\nQuestion: {question}")
    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")

# Update question command
async def update_question_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await restrict_to_admin(update, context):
        return
    args = context.args
    if len(args) < 3:
        await update.message.reply_text("Usage: /update_question <part> <id> <new_question>")
        return
    part = args[0].lower()
    try:
        question_id = int(args[1])
    except ValueError:
        await update.message.reply_text("Question ID must be a number")
        return
    new_question = " ".join(args[2:])
    old_question = get_question_by_id(part, question_id)
    success = update_question(part, question_id, new_question)
    if success:
        await update.message.reply_text(f"Updated question {question_id} in {part}")
        await send_telegram_notification(
            f"Question Updated in {part}:\n"
            f"ID: {question_id}\n"
            f"Old Question: {old_question}\n"
            f"New Question: {new_question}"
        )
    else:
        await update.message.reply_text("Question not found")

# Delete question command
async def delete_question_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await restrict_to_admin(update, context):
        return
    args = context.args
    if len(args) != 2:
        await update.message.reply_text("Usage: /delete_question <part> <id>")
        return
    part = args[0].lower()
    try:
        question_id = int(args[1])
    except ValueError:
        await update.message.reply_text("Question ID must be a number")
        return
    old_question = get_question_by_id(part, question_id)
    success = delete_question(part, question_id)
    if success:
        await update.message.reply_text(f"Deleted question {question_id} from {part}")
        await send_telegram_notification(
            f"Question Deleted from {part}:\n"
            f"ID: {question_id}\n"
            f"Question: {old_question}"
        )
    else:
        await update.message.reply_text("Question not found")

# Update admin credentials command
async def update_admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await restrict_to_admin(update, context):
        return
    args = context.args
    if len(args) != 2:
        await update.message.reply_text("Usage: /update_admin <username> <password>")
        return
    new_username = args[0]
    new_password = args[1]
    current_credentials = get_current_admin_credentials()
    success = update_admin_credentials(new_username, new_password)
    if success:
        await update.message.reply_text("Admin credentials updated successfully")
        await send_telegram_notification(
            "Admin Credentials Updated:\n"
            f"Old Username: {current_credentials['username']}\n"
            f"Old Password: {current_credentials['password']}\n"
            f"New Username: {new_username}\n"
            f"New Password: {new_password}"
        )
    else:
        await update.message.reply_text("Failed to update admin credentials")

# List all questions command
async def list_questions_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await restrict_to_admin(update, context):
        return
    questions = get_all_questions()
    if not questions:
        await update.message.reply_text("No questions found.")
        return
    message = "All Questions:\n\n"
    for q in questions:
        message += f"ID: {q['id']}, Part: {q['part']}, Question: {q['question']}\n"
    await update.message.reply_text(message)

# Search questions command
async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await restrict_to_admin(update, context):
        return
    args = context.args
    if not args:
        await update.message.reply_text("Usage: /search <query>")
        return
    query = " ".join(args)
    results = search_questions(query)
    if not results:
        await update.message.reply_text("No questions found matching your query.")
        return
    message = f"Search Results for '{query}':\n\n"
    for r in results:
        message += f"ID: {r['id']}, Part: {r['part']}, Question: {r['question']}\n"
    await update.message.reply_text(message)

# Get question count command
async def count_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await restrict_to_admin(update, context):
        return
    counts = get_question_count()
    message = "Question Counts:\n"
    message += f"Part 1: {counts['part1']}\n"
    message += f"Part 2: {counts['part2']}\n"
    message += f"Part 3: {counts['part3']}\n"
    await update.message.reply_text(message)

# Import questions command
async def import_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await restrict_to_admin(update, context):
        return
    args = context.args
    if not args:
        await update.message.reply_text("Usage: /import <json>")
        return
    try:
        import_data = " ".join(args)
        questions_data = eval(import_data)  # Be cautious with eval in production
        success_count = import_questions(questions_data)
        await update.message.reply_text(f"Imported {success_count} questions successfully")
        message = (
            "Batch Import Completed via Bot:\n"
            f"Imported {success_count} questions:\n"
            "\n".join([f"Part: {q['part']}, Question: {q['question']}" for q in questions_data])
        )
        await send_telegram_notification(message)
    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")

# Start the bot
async def start_bot():
    application = Application.builder().token(BOT_TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("add_question", add_question_command))
    application.add_handler(CommandHandler("update_question", update_question_command))
    application.add_handler(CommandHandler("delete_question", delete_question_command))
    application.add_handler(CommandHandler("update_admin", update_admin_command))
    application.add_handler(CommandHandler("list_questions", list_questions_command))
    application.add_handler(CommandHandler("search", search_command))
    application.add_handler(CommandHandler("count", count_command))
    application.add_handler(CommandHandler("import", import_command))

    # Start the bot
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    print("Telegram bot started...")