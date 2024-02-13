#!/usr/bin/env python

import csv
from diff_match_patch import diff_match_patch
from rich.console import Console


console = Console()


def highlight_differences(prompt, completion):
    dmp = diff_match_patch()
    diffs = dmp.diff_main(prompt, completion)
    dmp.patch_make(diffs)
    dmp.diff_cleanupSemantic(diffs)

    changes_list = []  # This will hold the changes

    prompt_highlighted = []
    completion_highlighted = []

    last_operation = None
    for operation, text in diffs:
        if operation == -1:  # Deletion
            prompt_highlighted.append(f"[red]{text}[/red]")  # Red for deleted text
            if last_operation == 1:  # This deletion follows an insertion, so record the change
                # Record as a tuple (old text, new text)
                changes_list.append((changes_list[-1][1], text))
                changes_list[-2] = ('', '')  # Clear the last insertion as it's part of a change
            else:
                # Record as a tuple (old text, new text)
                changes_list.append((text, ''))
        elif operation == 1:  # Insertion
            completion_highlighted.append(f"[green]{text}[/green]")  # Green for added text
            if last_operation == -1:  # This insertion follows a deletion, so record the change
                changes_list[-1] = (changes_list[-1][0], text)
            else:
                # Record as a tuple (old text, new text)
                changes_list.append(('', text))
        else:  # No changes
            prompt_highlighted.append(text)
            completion_highlighted.append(text)
        last_operation = operation

    # Print the highlighted text
    console.print(''.join(prompt_highlighted))
    console.print(''.join(completion_highlighted))
    return changes_list


def print_changes(changes_list):
    # Print the changes
    changes_list = [change for change in changes_list if change != ('', '')]  # Filter out empty changes
    if changes_list:  # If there are changes
        console.print("\nChanges:")
        for old_text, new_text in changes_list:
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
