import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
import cohere
import asyncio
import random

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot and API details
BOT_TOKEN = "7076733440:AAGVxBbBMDelIQZUX9kgbqRpah-XVFT89k4"
YOUTUBE_API_KEY = "AIzaSyBEahpYqLrKw8Yq46WmOqcnSyqmhsq4EUk"
API_ID = '29149446'
API_HASH = 'd4a95c48244165f660d8b4341f0c06b5'
PHONE_NUMBER = '+251926947581'
GEMINI_API_KEY = "AIzaSyBG8sB9lDLUwKmSGSLLruCz53KkRXVn3fA"
COHERE_API_KEY = "KvhLcD5V95t62GCjlbEXW6QU2StDwnaBOv8rVmyi"

# Initialize Cohere client
co = cohere.Client(COHERE_API_KEY)

# Group/channel IDs
GROUP_TOPICS = {
    '2nd_year': 'https://t.me/mechanicaengineeringlfiles/2',
    '3rd_year': 'https://t.me/mechanicaengineeringlfiles/3',
    '4th_year': 'https://t.me/mechanicaengineeringlfiles/4',
    '5th_year': 'https://t.me/mechanicaengineeringlfiles/5',
    'exit_exam': 'https://t.me/mechanicaengineeringlfiles/957'
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a welcome message and shows available options."""
    welcome_message = (
        "🎓Welcome to  AAIT Mechanical Engineering Study Bot (Mechify)!🎓\n\n"
        "Choose an option below to get started:"
    )

    keyboard = [
        [
            InlineKeyboardButton("Resources 📚", callback_data='resources'),
            InlineKeyboardButton("Ai Instructor 🤖", callback_data='studybuddy'),
        ],
        [
            InlineKeyboardButton("About ℹ️", callback_data='about'),
        ],
        [
            InlineKeyboardButton("Developers 👨‍💻", callback_data='developers')
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.callback_query:
        await update.callback_query.message.edit_text(welcome_message, reply_markup=reply_markup)
    else:
        await update.message.reply_text(welcome_message, reply_markup=reply_markup)

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    
    logger.info(f"Received callback query with data: {query.data}")

    if query.data == 'resources':
        await query.edit_message_text(
            text="Select your year or exam category:",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("2nd Year 📚", callback_data='2nd_year')],
                [InlineKeyboardButton("3rd Year 📚", callback_data='3rd_year')],
                [InlineKeyboardButton("4th Year 📚", callback_data='4th_year')],
                [InlineKeyboardButton("5th Year 📚", callback_data='5th_year')],
                [InlineKeyboardButton("Exit Exam 🎓", callback_data='exit_exam')],
                [InlineKeyboardButton("Back", callback_data='start')]
            ])
        )
    elif query.data in GROUP_TOPICS:
        await query.edit_message_text(
            text=f"🌟 Click below to access your study resources and level up your learning! 📚🚀",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📚Open Resources", url=GROUP_TOPICS[query.data])],
                [InlineKeyboardButton("Back", callback_data='start')]
            ])
        )
    
    elif query.data == 'studybuddy':
        await query.edit_message_text(
            text="Please mention the topic you want to learn about 📚, I'm here to help as your Ai Instructor! 🤖\n\n",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Back", callback_data='start')]
            ])
        )
    
    elif query.data == 'about':
        await query.edit_message_text(
            text="""
🌟 Meet MechIfy: Your Ultimate Mechanical Engineering Study Companion! 🌟

📚 Why MechIfy? This summer, we’ve got your back with a study buddy that never gives an F! Whether you’re tackling tricky concepts or just need a quick boost, MechIfy is here to guide you through your mechanical engineering journey. 🚀

🔧 What Can MechIfy Do for You?

1. 📚 Explore Resources: Get access to study materials tailored for your year and exam. Whether it’s for 2nd Year or the Exit Exam, we’ve got you covered!
2. 🤖 AI Instructor: Ask anything! MechIfy provides explanations and even some cool facts, jokes, and helpful videos to keep your learning fun and engaging.

🎉 Dive into a dynamic learning experience and make your studies enjoyable with MechIfy! Let’s make this summer productive and fun together! 🎓✨
""",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Back", callback_data='start')]
            ])
        )
    
    elif query.data == 'developers':
        await query.edit_message_text(
            text="""
👨‍💻 Developed with Passion by the AAIT Mechanical Engineering Team! 👩‍💻

- 👨‍💻 Gashahun Woldeyohannes (@gashu_1) - Second Year Enthusiast 🌟
- 👨‍💻 Nathnael Adinew (@natiAd) - Second Year Innovator 🚀

We’re working hard to bring you even more exciting features soon! Stay tuned and keep learning with MechIfy! 📚✨

""",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Back", callback_data='start')]
            ])
        )
    
    elif query.data == 'start':
        await start(update, context)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_message = update.message.text

    # Create the AI response task
    ai_response_task = asyncio.create_task(get_cohere_response(user_message))

    # Create the loading messages task
    async def display_loading_messages():
        loading_messages = ["Nice topic!", "Loading...", "በርታ"]
        while not ai_response_task.done():
            for message in loading_messages:
                if ai_response_task.done():
                    break
                await update.message.reply_text(message)
                await asyncio.sleep(1)
    
    loading_task = asyncio.create_task(display_loading_messages())
    ai_response = await ai_response_task
    
    # Cancel the loading messages task
    loading_task.cancel()

    # Generate the YouTube video URL based on the user message
    video_url = get_youtube_video_url(user_message + " on mechanical engineering")

    if ai_response:
        response_text = f"{ai_response}\n\nHere's a short video related to your topic:\n{video_url} \n\n You got it? If not, let me know! I am your study buddy! 🤖"
    else:
        response_text = (
            "Sorry, I couldn't generate a response for you right now.\n\n"
            "But here's a short help video related to your query:\n"
            f"{video_url}"
        )
    
    await update.message.reply_text(
        response_text,
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Back", callback_data='start')]
        ])
    )

async def get_cohere_response(query):
    co = cohere.Client(COHERE_API_KEY)
    try:
        response = await asyncio.to_thread(co.generate,
            model='command-xlarge-nightly',
            prompt=f"Explain {query} for a mechanical engineering student in an interesting way. add some emojis to make it better.",
            max_tokens=700
        )
        
        if response.generations:
            return response.generations[0].text.strip()
        else:
            return None
    except Exception as e:
        logger.error(f"Failed to get Cohere AI response. Error: {e}")
        return None
    

def get_youtube_video_url(topic):
    search_url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={topic}+ in mechanical engineering &type=video&videoDuration=short&key={YOUTUBE_API_KEY}"
    response = requests.get(search_url)
    
    if response.status_code == 200:
        videos = response.json().get('items', [])
        if videos:
            video_id = videos[0]['id']['videoId']
            return f"https://www.youtube.com/watch?v={video_id}"
        else:
            return "No video found. 🔍"
    else:
        logger.error(f"Failed to fetch YouTube video. Status code: {response.status_code}")
        return "Failed to fetch video. 🚫"

def main() -> None:
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.run_polling()

if __name__ == '__main__':
    main()
