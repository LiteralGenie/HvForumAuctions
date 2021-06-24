from classes import EquipScraper
from .misc_utils import contains_all, load_yaml
from .global_utils import AUCTION_FORMAT_CONFIG
import re


def wrap(x, tag, arg=None):
    arg= f"={arg}" if arg is not None else ""
    return f"[{tag}{arg}]{x}[/{tag}]"

def color(x, color):
    return wrap(x, 'color', f"#{color}")


def get_visible_stats(link, equips):
    # type: (str, dict) -> dict

    # inits
    settings= load_yaml(AUCTION_FORMAT_CONFIG)['preview']
    ret= {}

    eid= EquipScraper.extract_id_key(link)[0]
    stats= equips[eid]

    # helper funcs
    def get_mandatory(eq_name):
        ret= set()
        for name,lst in settings['mandatory_stats'].items():
            if contains_all(to_search=eq_name, to_find=name):
                ret= ret.union(lst)
        return list(ret)

    def is_mandatory(stat_name, mandatory_lst):
        return any(contains_all(to_search=stat_name, to_find=x) for x in mandatory_lst)

    def val_check(stat_name, val, min_val):
        if stat_name.lower() == 'interference' or stat_name.lower() == 'burden':
            return val <= 100-min_val
        else:
            return val >= min_val

    # amount of info to display
    if "legend" in stats['name'].lower() or 'peerless' in stats['name'].lower():
        display= settings['legendary']['level']
        min_val= settings['legendary']['min_percent']
        min_val_mand= settings['legendary']['min_percent_mandatory']
    else:
        display= settings['other']['level']
        min_val= settings['other']['min_percent']
        min_val_mand= settings['other']['min_percent_mandatory']

    if display <= 0:
        return ret

    # loop stats
    mandatory= get_mandatory(stats['name'])
    for name,val in stats['percentiles'].items():
        if (is_mandatory(name, mandatory) and val_check(name, val, min_val_mand)) or \
            (display >= 2 and val_check(name, val, min_val)):
            ret[name]= val

    # return
    return ret

def format_stats(stats):
    # type: (dict) -> list

    # inits
    ret= []
    settings= load_yaml(AUCTION_FORMAT_CONFIG)['preview']
    abbrvs= settings['abbreviations']

    # iterate stats
    for name,val in stats.items():
        abbrv= abbrvs[name] if name in abbrvs else name
        tmp= f"{int(val)}% {abbrv}"

        # if stat name marked for highlight, add color
        for word,clr in settings['highlights'].items():
            if contains_all(to_search=name, to_find=word):
                tmp= color(tmp, clr)
                break

        ret.append(tmp)

    # return
    return ret

def highlight_name(name):
    settings= load_yaml(AUCTION_FORMAT_CONFIG)['preview']
    for u,v in settings['highlights'].items():
        name= re.sub(rf'({u})', rf'[color=#{v}]\1[/color]', name, flags=re.IGNORECASE)
    return name