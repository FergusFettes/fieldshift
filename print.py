#!/usr/bin/env python

import csv
from diff_match_patch import diff_match_patch
from rich.console import Console
import re


def _expand_to_full_word(text, start_index, end_index):
    if start_index >= len(text):
        return start_index, end_index, ""

    word_start = start_index
    word_end = end_index

    # Expand to the start of the word
    while word_start > 0 and not re.match(r"\W", text[word_start - 1]):
        word_start -= 1

    # Expand to the end of the word
    while word_end < len(text) and not re.match(r"\W", text[word_end]):
        word_end += 1

    # Return the position and the full word
    full_word = text[word_start:word_end] if text[word_start:word_end] else ''
    return word_start, word_end, full_word


console = Console()


def highlight_differences(prompt, completion):
    dmp = diff_match_patch()
    diffs = dmp.diff_main(prompt, completion)
    dmp.diff_cleanupSemantic(diffs)

    prompt_highlighted = []
    completion_highlighted = []

    cursor = 0  # Keep track of where we are in the original text
    changes_list = []
    last_operation = None

    for op, data in diffs:
        if op == 0:  # No change
            prompt_highlighted.append(data)
            completion_highlighted.append(data)
            cursor += len(data)
        elif op == -1:  # Deletion
            # Find full word for deletion
            start, end, word = _expand_to_full_word(prompt, cursor, cursor + len(data))
            prompt_highlighted.append(f"[red]{word}[/red]")
            if last_operation == 1:  # This deletion follows and insertion, so its a change
                changes_list[-1]['old_text'] = word
            else:
                changes_list.append({
                    'old_text': word,
                    'new_text': '',
                })
            cursor += len(data)
        elif op == 1:  # Insertion
            # Find full word for insertion (there's no original text to reference here)
            adjusted_start = len(''.join(prompt_highlighted))
            if (adjusted_start > 0 and not re.match(r"\W", ''.join(prompt_highlighted)[-1]) and not re.match(r"\W", data[0])):
                start, end, word = _expand_to_full_word(''.join(completion_highlighted), adjusted_start, adjusted_start)
                completion_highlighted.append(f"[green]{word}[/green]")
            else:
                word = data
                completion_highlighted.append(f"[green]{data}[/green]")
            if last_operation == -1:  # This insertion follows a deletion, so its a change
                changes_list[-1]['new_text'] = word
            else:
                changes_list.append({
                    'old_text': '',
                    'new_text': word,
                })

        last_operation = op

    console.print(''.join(prompt_highlighted))
    console.print(''.join(completion_highlighted))

    return changes_list


def print_changes(changes_list):
    # Print the changes
    changes_list = [change for change in changes_list if change != ('', '')]  # Filter out empty changes
    if changes_list:  # If there are changes
        console.print("\nChanges:")
        for change in changes_list:
            old_text = change['old_text']
            new_text = change['new_text']
            if old_text and new_text:
                console.print(f"Changed [red]{old_text}[/red] to [green]{new_text}[/green].")
            elif old_text:
                console.print(f"Deleted [red]{old_text}[/red].")
            elif new_text:
                console.print(f"Inserted [green]{new_text}[/green].")


# Sample code to read a CSV and use the highlights - replace the path with your actual file path
with open('./subcellular_nanobrains.csv', 'r', newline='', encoding='utf-8') as csvfile:
    reader = csv.reader(csvfile)
    next(reader)  # Skip the header row if present

    count = 100
    changes = []
    for row in reader:
        id_, prompt, completion = row
        changes.append(highlight_differences(prompt, completion))
        print()
        count -= 1
        if not count:
            break

    for change in changes:
        print_changes(change)
        print()
