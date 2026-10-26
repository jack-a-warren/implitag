from typing import List, Set
import lib.tags as taglib
import lib.items as itemlib
from lib.utils import get_db


OPERATORS = ["+", "-", "&", "^"]
OPERAND_COUNTS = {
        "+": 2,
        "-": 1,
        "&": 2,
        "^": 2
        }

class TooManyOperatorsError(Exception):
    pass

def expand_segment(seg: str) -> Set[int] | str:
    if seg in OPERATORS:
        return seg

    seg_tag_id = taglib.get_tag_by_name(seg)
    return taglib.get_full_implying_ids(seg_tag_id)

def tag_query_to_item_query(tag_query):
    for segment in tag_query:
        if segment in OPERATORS:
            yield segment
            continue

        segment_items = set()

        for tag_id in segment:
            items_for_tag = taglib.get_tag_item_ids(tag_id, exclude_unlisted=True)
            segment_items |= items_for_tag

        yield segment_items

def parse_item_query(item_query):
    op_stack = list()
    all_item_ids = itemlib.all_item_ids()

    for segment in item_query:
        if segment in OPERATORS:
            operand_count = OPERAND_COUNTS[segment]
            try:
                ops = [op_stack.pop() for _ in range(operand_count)]
            except IndexError:
                raise TooManyOperatorsError()

            if segment == "+":
                op_stack.append(ops[0] | ops[1])
            elif segment == "-":
                op_stack.append(all_item_ids - ops[0])
            elif segment == "&":
                op_stack.append(ops[0] & ops[1])
            elif segment == "^":
                op_stack.append(ops[0] ^ ops[1])
        else:
            op_stack.append(segment)

    return op_stack

def conjunct_item_stack(stack):
    while len(stack) > 1:
        op1, op2 = stack.pop(), stack.pop()
        new_operand = op1 & op2
        stack.append(new_operand)

    result_ids = stack[0]
    return result_ids

def run_query(query: List[str]) -> Set[int]:
    tag_query = map(expand_segment, query)
    item_query = tag_query_to_item_query(tag_query)
    stack = parse_item_query(item_query)
    result_ids = conjunct_item_stack(stack)
    return result_ids

