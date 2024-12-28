import os
from glob import glob
import json
from googletrans import Translator #pip install googletrans==3.1.0a0, Python 3.13+ break without this specific version

DEST_LANGUAGE = 'sv'
SRC_LANGUAGE = 'en'

PLACE_HOLDER_START_LETTER = [
    '%',
    '{',
    '[',
]

WORDS_TO_NOT_TRANSLATE = [
    'm_c',
    'r_c',
    'c_n',
    's_c',
    'p_l',
    'o_n_g'
]

'''
The proper way forward is probably to make custom file handlers for
different types of files to translate, to maximize speed and adaptation
and minimize the redundatn checks.
'''

KEYS_TO_NOT_TRANSLATE = [
    "comment",
    #resources\lang\sv\events\death
    'event_id',
    'location',
    'season',
    'tags',
    'weight',
    'not_skill',
    'relationship_status',
    #resources\lang\sv\events\disasters
    'event',
    'camp',
    'season',
    'priority',
    'duration',
    'rarity',
    'disaster',
    'triggers_during',
    'chance',
    #resources\lang\sv\events\injury
    'event_id',
    'location',
    'status',
    'trait',
    'age',
    'Values',
    'amount',
    'mutual',
    #resources\lang\sv\events\leader_den
    'interaction_type',
    'rel_change',
    'player_clan_temper',
    'other_clan_temper',
    'skill',
    'relationships',
    #resources\lang\sv\events\misc
    'sub_type',
    'not_trait',
    'current_rep',
    'herbs',
    'injuries',
    'scars',
    'pl_skill_constraint',
    #resources\lang\sv\events\relationship_events\group_interactions
    "id",
    "cat_amount",
    "intensity",
    "relationship_constraint",
    'specific_reaction',
    'trait_constraint',
    'general_reaction',
    'status_constraint',
    #resources\lang\sv\events\relationship_events\normal_interactions
    'reaction_random_cat',
    'main_status_constraint',
    'random_status_constraint',
    'also_influences',
    'main_trait_constraint',
    'random_trait_constraint',
    #resources\lang\sv\events
    'lead_trait',
    'star_trait',
    'rank',
    #resources\lang\sv\patrols
    'patrol_id',
    'biome',
    'types',
    'patrol_art',
    'min_cats',
    'max_cats',
    'min_max_status',
    'chance_of_success',
    'cats_to',
    'cats_from',
    'stat_trait',
    'dead_cats',
    'stat_skill',
    'new_cat',
    'prey'
]

SPECIAL_FILES = [
    f"{DEST_LANGUAGE}\\config.json",
    f"{DEST_LANGUAGE}\\events\\ceremonies\\ceremony-master.json",

]

translator = Translator()

'''
FILE HANDLING
'''


def get_files_to_translate(base_path:str): 
    '''
    Get all .json-files inside base path recursivly
    '''
    language_file_paths = [
        y 
        for x in os.walk(f"{base_path}\\") 
        for y in glob(os.path.join(x[0], '*.json'))
        if y not in SPECIAL_FILES
    ]
    return language_file_paths

def make_backup_file_name(file_path: str):
    '''
    Copy a file and add "_original" in file name
    '''
    backup_file_path = file_path
    if f".{DEST_LANGUAGE}.json" in backup_file_path:
        backup_file_path = backup_file_path.replace(
            f".{DEST_LANGUAGE}.json"
            ,f"_original.{DEST_LANGUAGE}.json"
        )
    else:
        backup_file_path = backup_file_path.replace(
            f".json"
            ,f"_original.json"
        )
    return backup_file_path

def save_json(file_path: str,data):
    '''
    Save a JSON data structure into a .json-file
    '''
    # Open and owerwrite the JSON file
    json_data = json.dumps(data, indent=4)
    with open(file_path, "w") as outfile:
        outfile.write(json_data)

def load_json_file(file_path: str):
    '''
    Open and return data of a .json-file
    '''
    with open(file_path, 'r') as file:
        return json.load(file)

'''
TRANSLATION HANDLING
'''

def translate(data):
    '''
    Translate strings to correct language, ignore all other types
    '''
    if (type(data) is str):
        return translator.translate(data, src=SRC_LANGUAGE,dest=DEST_LANGUAGE).text
    else:
        return data

'''
JSON HANDLING
'''

# Print the data
def get_translated_list_content(data: list):
    '''
    Recursive search and replace for text to translate
    '''
    for index in range(len(data)):
        if (type(data[index]) is list):
            data[index] = get_translated_list_content(data[index])
        elif (type(data[index]) is dict):
            data[index] = get_translated_dict_content(data[index])
        else:
            data[index] = translate(data[index])
    return data

    
def get_translated_dict_content(data: dict):
    '''
    Recursive search and replace for text to translate
    '''
    all_keys = data.keys()
    relevant_keys = [
        key
        for key in all_keys
        if key not in KEYS_TO_NOT_TRANSLATE
    ]
    for key in relevant_keys:
        if (type(data[key]) is list):
            data[key] = get_translated_list_content(data[key])
        elif (type(data[key]) is dict):
            data[key] = get_translated_dict_content(data[key])
        else:
            data[key] = translate(data[key])
    return data

def ceremony_master_special_translation():
    '''
    This is custom made for ceremony_master json.
    '''
    print(f"File to translate: {SPECIAL_FILES[1]}")
    data = load_json_file(SPECIAL_FILES[1])
    if (type(data) is dict and 'translation_type' not in data.keys()):
        for key in data.keys():
            for index in range(len(data[key])):
                if type(data[key][index]) is str:
                    data[key][index] = translate(data[key][index])
        
        translate_entry = {'translation_type': 'Google translate'}
        translate_entry.update(data)
        data = translate_entry
        save_json(SPECIAL_FILES[1],data)
    else:
        print("File already transalted, skipping file")

def translate_all_files(language_file_paths: list[str]):
    '''
    Take a list of json file paths and translate any string type
    that is not specified to not translate.
    '''
    
    #Files following the standard transaltion function
    for language_file_path in language_file_paths:
        if('_original' not in language_file_path):
            print(f"File to translate: {language_file_path}")
            data = load_json_file(language_file_path)
            update_data = False
            #.json-file start with either list or dict type
            #if it has already been tagged as tranlslated, skip it
            if (
                type(data) is list
                and (
                    len(data) == 0
                    or  type(data[0]) is not dict 
                    or 'translation_type' not in data[0].keys()
                )
            ):
                #Translate, and tag as google translated
                get_translated_list_content(data)
                update_data = True
                data = [{'translation_type': 'Google translate'}] + data
            elif (type(data) is dict and 'translation_type' not in data.keys()):
                #Translate, and tag as google translated
                get_translated_dict_content(data)
                update_data = True
                translate_entry = {'translation_type': 'Google translate'}
                translate_entry.update(data)
                data = translate_entry
            if update_data == True:
                save_json(language_file_path,data)
            else:
                print("File already transalted, skipping file")
        print("\n")
    #Any special made function that don't follow standard transaltion flow
    ceremony_master_special_translation()

'''
START
'''

translate_all_files(get_files_to_translate(DEST_LANGUAGE))


