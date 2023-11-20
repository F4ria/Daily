from github.ContentFile import ContentFile  # type: ignore
from github.Issue import Issue  # type: ignore
from github.IssueComment import IssueComment  # type: ignore
from github.Repository import Repository
from telebot import TeleBot  # type: ignore
from telebot.types import Message  # type: ignore

from config import (
    MyNumber,
    DataDir,
    MyNumberFilenameFormat,
    GithubWorkBranch,
    TimeZone,
)

from utils import (
    read_str_as_dict,
    sort_dict_within_list,
    list_to_dict,
    fmt_to_today_utc,
    fmt_utc_to_datetime_str,
    github_is_me,
)


def respond_info(bot: TeleBot, message: Message) -> None:
    text = {
        "id": message.from_user.id,
        "username": message.from_user.username,
        "chat_id": message.chat.id,
    }
    bot.reply_to(message, str(text))


def get_my_number_dodo_msg(repo: Repository, github_name: str) -> str:
    content_file_dict = dict()
    for cf in repo.get_dir_contents(DataDir, ref=GithubWorkBranch):
        content_file_dict.update({cf.name: cf})

    resp_message = []
    do_fmt = "☑{0}"
    todo_fmt = "☐{0}"
    for task, config in MyNumber.items():
        if config.get("skip_readme"):
            continue
        desc: str = config.get("desc")
        task_name = desc.split("_")[-1]

        labels: list = config.get("label")
        if labels is None:
            resp_message.append(todo_fmt.format(task_name))
            return

        issues = repo.get_issues(labels=labels, creator=github_name)
        if issues.totalCount <= 0:
            resp_message.append(todo_fmt.format(task_name))
            return

        issue: Issue = issues[0]
        today_utc = fmt_to_today_utc(TimeZone)

        comments = issue.get_comments(since=today_utc)
        my_comments = [c for c in comments if github_is_me(c, github_name)]
        if len(my_comments) <= 0:
            resp_message.append(todo_fmt.format(task_name))
            continue

        resp_message.append(do_fmt.format(task_name))

    msg = "MyNumber Todo:\n"
    msg += "\n".join(resp_message)

    return msg


def respond_daily(
    bot: TeleBot,
    message: Message,
    repo: Repository,
    github_name: str,
    task: dict,
    cmd_text: str,
):
    labels: list = task.get("label")
    if labels is None:
        bot.reply_to(message, f"labels empty.")
        return

    issues = repo.get_issues(labels=labels, creator=github_name)
    if issues.totalCount <= 0:
        bot.reply_to(message, f"No issue found associated with the label({labels}).")
        return

    issue: Issue = issues[0]
    today_utc = fmt_to_today_utc(TimeZone)

    # 获取当天issue，避免重复评论
    # 如果当天已经评论过，更新最新评论的内容
    comments = issue.get_comments(since=today_utc)
    my_comments = [c for c in comments if github_is_me(c, github_name)]
    if len(my_comments) > 0:
        latest_comment: IssueComment = my_comments[-1]
        latest_text = latest_comment.body.splitlines()[0]
        if latest_text == cmd_text:
            bot.reply_to(
                message,
                f"same comment.({fmt_utc_to_datetime_str(latest_comment.updated_at, TimeZone)})",
            )
            return
        try:
            latest_comment.edit(body=cmd_text)
            bot.reply_to(
                message,
                f"update comment success:\n"
                + f"{fmt_utc_to_datetime_str(latest_comment.updated_at, TimeZone)}\n"
                + f"({latest_text})->({cmd_text})",
            )
        except Exception as e:
            bot.reply_to(message, f"update comment failed: {e}")

        return

    try:
        issue.create_comment(body=cmd_text)
        bot.reply_to(message, "create comment success.")
    except Exception as e:
        bot.reply_to(message, f"create comment failed: {e}")

    respond_my_number_todo(bot, message, repo, github_name)


def respond_github_workflow(
    bot: TeleBot, message: Message, repo: Repository, task: dict
) -> None:
    try:
        workflow_id = task.get("workflow_id")
        ref = task.get("work_branch")
        workflow = repo.get_workflow(workflow_id)
        state = workflow.create_dispatch(ref=ref)
        resp_message = f"GitHub Action '{workflow.name}' triggered successfully. Run state: {state}."
        bot.reply_to(message, resp_message)
    except Exception as e:
        bot.reply_to(message, f"[action triggered] An error may have occurred: {e}")


def respond_my_number_todo(
    bot: TeleBot, message: Message, repo: Repository, github_name: str
) -> None:
    msg = get_my_number_dodo_msg(repo, github_name)
    bot.send_message(message.chat.id, msg)


def respond_clock_in(bot: TeleBot, message: Message, repo: Repository, clock_in: list):
    content_file_dict = dict()
    for cf in repo.get_dir_contents(DataDir, ref=GithubWorkBranch):
        content_file_dict.update({cf.name: cf})

    resp_message = []
    for tag in clock_in:
        config: dict = MyNumber.get(tag)
        if not config:
            print(f"{tag} not found in 'MyNumber'")
            continue

        filename = MyNumberFilenameFormat.format(**config)
        content: ContentFile = content_file_dict.get(filename)
        if content is None:
            print(f"{tag} not found in repo")
            continue

        text = content.decoded_content.decode("utf-8")
        data: dict = read_str_as_dict(text)

        desc: str = config.get("desc")
        name = desc.split("_")[-1]
        resp_message.append(f"{name} {len(data)} 天")

    msg = ", ".join(resp_message) + "."
    bot.reply_to(message, msg)


def respond_clock_in_summary(
    bot: TeleBot, message: Message, repo: Repository, clock_in: list
):
    resp_list = []
    resp_template = "{name}({start_day}): 打卡({win_days})天\n"

    content_file_dict = dict()
    for cf in repo.get_dir_contents(DataDir, ref=GithubWorkBranch):
        content_file_dict.update({cf.name: cf})

    for tag in clock_in:
        config: dict = MyNumber.get(tag)
        if not config:
            print(f"{tag} not found in 'MyNumber'")
            continue
        if config.get("skip_readme"):
            continue

        filename = MyNumberFilenameFormat.format(**config)
        content: ContentFile = content_file_dict.get(filename)
        if content is None:
            print(f"{tag} not found in repo")
            continue

        text = content.decoded_content.decode("utf-8")
        data = read_str_as_dict(text)

        desc = config.get("desc")
        stat: dict = list_to_dict(["name", "start_day", "win_days"])
        stat["name"] = desc.split("_")[-1]
        stat["start_day"] = list(sorted([i for i in data.keys()]))[0]
        stat["win_days"] = len(data)
        resp_list.append(stat)

    msg = ""
    resp_list = sort_dict_within_list(resp_list, key1="start_day", key2="win_days")
    for stat in resp_list:
        msg += resp_template.format(**stat)

    bot.reply_to(message, msg)
