# Requires pip install telegram

import json
import logging, asyncio, tempfile, glob, os, sys, traceback
from pathlib import Path
from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from telegram.constants import ParseMode
from ctccp import RunState, CheckerResult, check_snippet, SnippetLabel, checkers, compilers
from label import parseLabelFromFile

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

TG_BOT_TOKEN = "REMOVED"
TG_LAB33_GROUP = -939100135
TG_LAB25_GROUP = -4077054704
TG_SEND_TO = TG_LAB25_GROUP

SNIPPETS_GLOB = "../snippets/openssl/*.json"
RESULTS_DIR = "./workdir/results/"
WORK_DIR = "./workdir/work/"

def tg_escape(msg: str) -> str:
    for char in ['\\', '_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']:
        msg = msg.replace(char, "\\%s" % char)
    return msg

async def main() -> None:
    application = Application.builder().token(TG_BOT_TOKEN).build()
    chat = await application.bot.get_chat(TG_SEND_TO)
    
    # Collect snippets
    snippet_labels: list[tuple[SnippetLabel, str]] = []
    for label_path in glob.glob(SNIPPETS_GLOB):
        if "noasm" in label_path:
            print(label_path)
            continue
        snippet_name = ".".join(Path(label_path).name.split(".")[:-1])
        logger.info("Found snippet '%s' at '%s'." % (snippet_name, label_path))
        snippet_labels.append((parseLabelFromFile(Path(label_path)), snippet_name))

    # Collect checkers
    used_checkers = []
    used_checkers.extend(checkers.collector.dudect.registerCheckers())
    used_checkers.extend(checkers.collector.ctgrind.registerCheckers())
    used_checkers.extend(checkers.collector.data.registerCheckers())
    used_checkers.extend(checkers.collector.pitchfork.registerCheckers())

    # Collect compilers
    used_compilers = []
    used_compilers.extend(compilers.collector.gcc.registerCompilers())
    used_compilers.extend(compilers.collector.clang.registerCompilers())
    used_compilers.extend(compilers.collector.icx.registerCompilers())
    used_compilers.extend(compilers.collector.aocc.registerCompilers())

    # Make work directory
    os.makedirs(RESULTS_DIR, exist_ok=False)
    results_path = Path(RESULTS_DIR)

    # Send welcome message
    welcome_msg = "⏳ *Starting to run CTCCP*\nThe following snippets will be checked:\n"
    for (_, name) in snippet_labels:
        welcome_msg += " • %s\n" % tg_escape(name)
    welcome_msg += "\n The following compilers are available:\n"
    for compiler in used_compilers:
        welcome_msg += " • %s \\(%d option sets\\)\n" % (tg_escape(compiler.identifier()), len(compiler.availableOptionPresets()))
    welcome_msg += "\n The following checkers are available:\n"
    for checker in used_checkers:
        welcome_msg += " • %s\n" % (tg_escape(checker.identifier()))
    await chat.send_message(welcome_msg, ParseMode.MARKDOWN_V2)


    for (label, name) in snippet_labels:
        workdir = (Path(WORK_DIR) / name).resolve()
        os.makedirs(workdir, exist_ok=True)
        async def callback(state: RunState, message: str | None = None):
            await chat.send_message("🫡 Snippet _%s_ has reached state `%s`\\." % (tg_escape(name), tg_escape(state.name)), ParseMode.MARKDOWN_V2)
        try:
            result = await check_snippet(label, workdir, used_checkers, used_compilers, callback)
            refined_result = [{
                "id": run.id,
                "binary": str(run.binaryTarget),
                "failed": bool(res.data_oblivious is None),
                "data_oblivious": None if res.data_oblivious is None else bool(res.data_oblivious),
                "timeout": bool(res.timeout)
            } for (run, res) in result]
            success_msg = "🎉 Successfully ran tests for snippet _%s_\\!\nHere are the results:\n" % (tg_escape(name))
            for entry in refined_result:
                if entry["timeout"]:
                    success_msg += " • %s %s\n" % ("⏰", tg_escape(entry["id"]))
                else:
                    success_msg += " • %s %s\n" % ("💣" if entry["failed"] else ("✅" if entry["data_oblivious"] else "❌"), tg_escape(entry["id"]))
            await chat.send_message(success_msg, ParseMode.MARKDOWN_V2)

            with open(results_path / ("%s.json" % name), "w") as res_file:
                json.dump(refined_result, res_file)
        except Exception as e:
            await chat.send_message("🔥 Snippet _%s_ has caused an exception:\n```\n%s\n```" % (tg_escape(name), "".join(traceback.format_exception(e))), ParseMode.MARKDOWN_V2)

if __name__ == "__main__":
    asyncio.run(main())
