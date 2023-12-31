GithubName = "F4ria"
GithubEmail = "f4riacool@gmail.com"
GithubRepo = "Daily"
GithubRepoName = f"{GithubName}/{GithubRepo}"
GithubWorkBranch = "master"

GithubCommitter = {
    "name": GithubName,
    "email": GithubEmail,
}

BotOwner = [728177711]

TimeZone = "Asia/Shanghai"

MyNumberFilenameFormat = f"{{desc}}.txt"
DataDir = "data"
GithubFileAbsPath = (
    f"https://github.com/{GithubName}/{GithubRepo}/blob/{GithubWorkBranch}"
)

IssuePlankLabels = ["plank exercise"]
IssueSquatLabels = ["squat"]
IssuePushUpLabels = ["push-up"]
IssueSitUpLabels = ["sit-up"]
IssueEnglishVocabularyLabels = ["English vocabulary"]
IssueEnglishShadowingLabels = ["English shadowing"]
IssueSkippingRopeLabels = ["skipping rope"]
IssueBurpeeLabels = ["burpee"]
IssueOhMyGodLabels = ["oh my god"]
IssueOhMyGodDLabels = ["oh my god d"]
IssueRunningLabels = ["running"]


def sum_items(items: list) -> int:
    total = sum([float(i) for i in items])
    return int(total)


def sum_second_to_minute(seconds: list) -> float:
    total = sum([int(i) for i in seconds])
    minutes = total / 60.0
    return float(f"{minutes:.2f}")


# bot command
MyNumber = {
    "plank": {
        "allowed_user": BotOwner,
        "desc": "plank_平板支撑",
        "label": IssuePlankLabels,
        "status_func": sum_items,
        "status_unit_str": "(分钟)",
    },
    "squat": {
        "allowed_user": BotOwner,
        "desc": "squat_深蹲",
        "label": IssueSquatLabels,
        "status_func": sum_items,
        "status_unit_str": "(个)",
    },
    "push_up": {
        "allowed_user": BotOwner,
        "desc": "push-up_俯卧撑",
        "label": IssuePushUpLabels,
        "status_func": sum_items,
        "status_unit_str": "(个)",
    },
    "sit_up": {
        "allowed_user": BotOwner,
        "desc": "sit-up_仰卧起坐",
        "label": IssueSitUpLabels,
        "status_func": sum_items,
        "status_unit_str": "(个)",
    },
    "eng_vocabulary": {
        "allowed_user": BotOwner,
        "desc": "英语单词",
        "label": IssueEnglishVocabularyLabels,
    },
    "eng_shadowing": {
        "allowed_user": BotOwner,
        "desc": "英语跟读",
        "label": IssueEnglishShadowingLabels,
    },
    "skipping_rope": {
        "allowed_user": BotOwner,
        "desc": "skipping_rope_跳绳",
        "label": IssueSkippingRopeLabels,
        "status_func": sum_items,
        "status_unit_str": "(个)",
    },
    "burpee": {
        "allowed_user": BotOwner,
        "desc": "burpee_波比跳",
        "label": IssueBurpeeLabels,
        "status_func": sum_items,
        "status_unit_str": "(个)",
    },
    "oh_my_god": {
        "allowed_user": BotOwner,
        "desc": "oh_my_god",
        "label": IssueOhMyGodLabels,
        "skip_readme": True,
    },
    "oh_my_god_d": {
        "allowed_user": BotOwner,
        "desc": "oh_my_god_d",
        "label": IssueOhMyGodDLabels,
        "skip_readme": True,
    },
}

RunningPhoto = {
    "running": {
        "allowed_user": BotOwner,
        "desc": "image for running or running comment xx weeks",
        "label": IssueRunningLabels,
        "path": f"{DataDir}/images/running",
        "skip_readme": True,
    },
}

MyNumberHeader = [
    "Name",
    "Status",
    "Start Day",
    "Latest Day",
    "Win Days",
    "Longest Streak",
]

# bot command /run_daily
GithubWorkflow = {
    "run_daily": {
        "allowed_user": BotOwner,
        "desc": "run daily github action",
        "workflow_id": "run_daily.yml",
        "work_branch": "master",
    },
}

# bot command
MyClockIn = {
    "clock_in_summary": {
        "allowed_user": BotOwner,
        "desc": "clock-in(打卡) summary",
        "number_names": MyNumber.keys(),
    },
}

TelegramBotCommandInfo = {
    "info": {
        "desc": "get my info",
    },
}

TelegramBotCommadMyNumberTodo = {
    "todo_my_number": {
        "desc": "todo list my number",
        "allowed_user": BotOwner,
    }
}

GithubReadmeComments = (
    "(<!--START_SECTION:{name}-->\n)(.*)(<!--END_SECTION:{name}-->\n)"
)
