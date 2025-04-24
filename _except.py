from varialble_tools import STEP_SEQUENCES_INDEX_STR_PROX


def remove_proxi_offset(lists):
    for idx, item in enumerate(lists):
        if item.startswith("POFFSET"):
            lists.pop(idx)

    return lists

def remove_proxi_offset_result(values):
    if(values[0] == STEP_SEQUENCES_INDEX_STR_PROX + 1):
        del values[6]
        del values[4]
    return values

