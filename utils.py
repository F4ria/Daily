import os
import re

import pendulum

from hashlib import sha256

from typing import Optional
from telebot.types import Message  # type: ignore
from github.IssueComment import IssueComment  # type: ignore

from config import GithubReadmeComments


def fmt_to_today_utc(tz: str) -> pendulum.DateTime:
    today = pendulum.today(tz=tz)
    today_utc = today.in_timezone("UTC")
    return today_utc


def fmt_utc_to_datetime_str(ts: str, tz: str) -> str:
    # return: 2023-11-15 08:39:28
    s = pendulum.instance(ts).in_timezone(tz).to_datetime_string()
    return s


def fmt_utc_to_date_str(ts: str, tz: str) -> str:
    # return: 2023-11-15
    s = pendulum.instance(ts).in_timezone(tz).to_date_string()
    return s


def days_until_today(start_date):
    today = pendulum.today()
    start = pendulum.parse(start_date)

    diff = today.diff(start)
    return diff.in_days() + 1


def github_is_me(comment: IssueComment, me):
    return comment.user.login == me


def read_file_as_dict(f: str, line_sep: str = ",") -> dict:
    d = {}
    if not os.path.exists(f):
        return d

    with open(f, mode="r", encoding="utf-8", errors="ignore") as fr:
        for line in fr:
            line = line.strip()
            if not line:
                continue
            date_str = line.split(line_sep)[0]
            content = line[len(date_str) + len(line_sep) :]

            d.update({date_str: content})

    return d


def read_str_as_dict(s: str, line_sep: str = ",") -> dict:
    d = {}

    for line in s.splitlines():
        line = line.strip()
        if not line:
            continue
        date_str = line.split(line_sep)[0]
        content = line[len(date_str) + len(line_sep) :]

        d.update({date_str: content})

    return d


def write_dict_as_file(data: dict, f: str, line_sep: str = ","):
    with open(file=f, mode="w", encoding="utf-8", errors="ignore") as fw:
        for k in sorted(data):
            fw.write(f"{k}{line_sep}{data.get(k)}\n")


def sha256_hash(string) -> str:
    # Convert the string to bytes using UTF-8 encoding
    bytes_string = string.encode("utf-8")

    # Create a new SHA-256 hash object
    sha256_hash_obj = sha256()

    # Update the hash object with the bytes
    sha256_hash_obj.update(bytes_string)

    # Get the hexadecimal representation of the hash
    hash_hex = sha256_hash_obj.hexdigest()

    return hash_hex


def is_owner(message: Message, owners: Optional[list]) -> bool:
    if not owners:
        return True
    return message.from_user.id in owners


def extract_command(message: Message, bot_name="") -> (str, str):
    cmd = message.text.split()[0]
    cmd_text = message.text[len(cmd) :].strip()
    if "@" in cmd:
        cmd_at = "".join(cmd.split("@")[1:])
        cmd = cmd.split("@")[0]

        if cmd_at != bot_name:
            return None, None

    # return cmd.strip().lstrip("/"), cmd_at.strip(), cmd_text.strip()
    return cmd.strip().lstrip("/"), cmd_text.strip()


def extract_photo_command(message: Message, bot_name="") -> (str, str):
    s = message.text or message.caption
    cmd = s.split()[0]
    cmd_text = s[len(cmd) :].strip()
    if "@" in cmd:
        cmd_at = "".join(cmd.split("@")[1:])
        cmd = cmd.split("@")[0]

        if cmd_at != bot_name:
            return None, None

    # return cmd.strip().lstrip("/"), cmd_at.strip(), cmd_text.strip()
    return cmd.strip().lstrip("/"), cmd_text.strip()


def replace_readme_comments(file_name, comment_str, comments_name):
    with open(file_name, "r+") as f:
        text = f.read()
        # regrex sub from github readme comments
        text = re.sub(
            GithubReadmeComments.format(name=comments_name),
            r"\1{}\n\3".format(comment_str),
            text,
            flags=re.DOTALL,
        )
        f.seek(0)
        f.write(text)
        f.truncate()


def longest_consecutive_dates(date_list) -> (str, str):
    if not date_list:
        return None, None

    date_list = sorted(date_list)  # Sort the list of dates

    start_date = None
    end_date = None
    longest_duration = 0
    current_start = None
    current_end = None

    # Iterate through the sorted list to find the longest consecutive period
    for date_str in date_list:
        date = pendulum.parse(date_str)
        if current_start is None:
            current_start = date
            current_end = date
        elif date.diff(current_end).in_days() == 1:
            current_end = date
        else:
            duration = current_start.diff(current_end).in_days() + 1
            if duration >= longest_duration:
                longest_duration = duration
                start_date = current_start
                end_date = current_end
            current_start = date
            current_end = date

    # Check if the last period is the longest
    duration = current_start.diff(current_end).in_days() + 1
    if duration >= longest_duration:
        longest_duration = duration
        start_date = current_start
        end_date = current_end

    return start_date.to_date_string(), end_date.to_date_string()


def max_days_between_dates(start_date, end_date) -> int:
    start = pendulum.parse(start_date)
    end = pendulum.parse(end_date)
    diff = abs((end - start).in_days())
    return diff


def sort_dict_within_list(input_list: list, key1: str, key2: str = None):
    if key2 is not None:
        return sorted(input_list, key=lambda x: (x.get(key1), -x.get(key2)))

    return sorted(input_list, key=lambda x: x.get(key1))


def fmt_markdown_table_header(header_list: list) -> str:
    """
    input:  ["Name", "Status", "Start Day"]
    output:
        "| Name | Status | Start Day |\n| :---: | :---: | :---: |\n"
    """
    header = "| " + " | ".join(header_list) + " |\n"
    align = "| " + " | ".join([":---:" for _ in header_list]) + " |\n"
    return header + align


def fmt_markdown_table_template(header_list: list) -> str:
    """
    input:  ["Name", "Status", "Start Day"]
    output:
        "| {name} | {status} | {start_day} |\n"
    """
    placeholders = [f"{{{item.lower().replace(' ', '_')}}}" for item in header_list]
    output = "| " + " | ".join(placeholders) + " |\n"
    return output


def list_to_dict(header_list) -> dict:
    return {item.lower().replace(" ", "_"): None for item in header_list}
