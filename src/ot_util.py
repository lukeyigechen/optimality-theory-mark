import pandas as pd
import copy


def gen_long_vowels(dict_feat_cons):
    #print(len(dict_feat_cons.keys()))
    dict_feat_cons_copy = copy.deepcopy(dict_feat_cons)
    for phone, dict_feats_single_phone in dict_feat_cons_copy.items():
        if dict_feats_single_phone['syllabic'] == '+' and dict_feats_single_phone['long'] == '-':
            dict_feat_cons[phone + 'ː'] = dict_feats_single_phone
            dict_feat_cons[phone + 'ː']['long'] = '+'
    #print(len(dict_feat_cons.keys()))
    return dict_feat_cons


def gen_aspirated_consonants(dict_feat_cons):
    #print(len(dict_feat_cons.keys()))
    dict_feat_cons_copy = copy.deepcopy(dict_feat_cons)
    for phone, dict_feats_single_phone in dict_feat_cons_copy.items():
        if dict_feats_single_phone['sonorant'] == '-' and dict_feats_single_phone['spread_gl'] == '-':
            dict_feat_cons[phone + 'ʰ'] = dict_feats_single_phone
            dict_feat_cons[phone + 'ʰ']['spread_gl'] = '+'
    #print(len(dict_feat_cons.keys()))
    return dict_feat_cons


def read_feat_table(in_dir):
    df_feat_cons = pd.read_csv(in_dir, encoding='utf-8').T
    df_feat_cons.rename(columns=df_feat_cons.iloc[0], inplace=True)
    df_feat_cons.drop(df_feat_cons.index[0], inplace=True)
    #print(df_feat_cons.head())
    dict_feat_cons = df_feat_cons.to_dict()

    # generate long vowels and aspirated consonants
    dict_feat_cons = gen_long_vowels(dict_feat_cons)
    dict_feat_cons = gen_aspirated_consonants(dict_feat_cons)

    #print(dict_feat_cons)
    set_cons = set(dict_feat_cons.keys())
    set_feat_cons = set(dict_feat_cons[df_feat_cons.columns[1]].keys())
    #print(set_cons)
    return df_feat_cons, dict_feat_cons, set_cons, set_feat_cons


def proc_candidate(str_cand, dict_phone_encode):
    key_sorted = sorted(list(dict_phone_encode.keys()), key=len, reverse=True)
    for k in key_sorted:
        v = dict_phone_encode[k]
    #for k, v in dict_phone_encode.items():
        str_cand = str_cand.replace(k, v)
    syllables = str(str_cand).strip().split('.')
    no_dot_str = str(str_cand).strip().replace(".", "")
    return syllables, no_dot_str


def proc_candidate_old(str_cand, dict_phone_encode):
    for k, v in dict_phone_encode.items():
        str_cand = str_cand.replace(k, v)
    syllables = str(str_cand).strip().split('.')
    no_dot_str = str(str_cand).strip().replace(".", "")
    return syllables, no_dot_str


# get a dict that convert >1 chars string to 1 char using kana
def encode_as_dict(set_phone):
    set_2char = set()
    dict_phone_encode = dict()
    count = 0
    # unicode_num = int("3041", 16)  # kana
    unicode_num = int("1100", 16)  # hangul
    for phone in set_phone:
        if len(phone) > 1:
            # print(phone)
            count += 1
            set_2char.add(phone)
            dict_phone_encode[phone] = chr(unicode_num)
            unicode_num += 1
        else:
            dict_phone_encode[phone] = phone
    #print(chr(unicode_num))
    return dict_phone_encode, set_2char


def read_file_as_lines(file):
    with open(file, encoding='utf-8') as f:
        lines = f.readlines()
    return lines


def read_file_as_str(file):
    with open(file, 'r', encoding='utf-8') as f:
        str_out = f.read()
    return str_out


def write_output(file, str_in):
    with open(file, 'w', encoding='utf-8') as f:
        f.write(str_in)


# get ur, sr, candidate, encoding from input texts
def proc_input(lines):
    ur = ''
    sr = ''
    cand_list = []
    sr_stress_encode = ''
    cand_stress_encode_list = []
    for line in lines:
        line = str(line).strip()
        if line != '' and line[0] != '#':
            split_line = line.split(':')
            if split_line[0].lower().strip() == 'ur':
                ur = split_line[-1]
            elif split_line[0].lower().strip() == 'sr':
                sr = split_line[-1]
            elif split_line[0].lower().strip() == 'candidates':
                cand_list = split_line[-1].split(',')
            elif split_line[0].lower().strip() == 'sr_stress':
                sr_stress_encode = split_line[-1]
            elif split_line[0].lower().strip() == 'candidates_stress':
                cand_stress_encode_list = split_line[-1].split(',')
    return ur, sr, cand_list, sr_stress_encode, cand_stress_encode_list


def marks_to_hayes_input(ur, sr, dict_sr_out, dict_dict_cand_out, constraint_list):
    if constraint_list is None:
        constraint_list = list(dict_sr_out.keys())
    str_out = '\t\t\t' + '\t'.join(constraint_list) + '\n' + '\t\t\t' + '\t'.join(constraint_list) + '\n'
    list_sr_tmp = []
    for constraint in constraint_list:
        list_sr_tmp.append(str(dict_sr_out[constraint]))
    str_out += ur + '\t' + sr + '\t1\t' + '\t'.join(list_sr_tmp) + '\n'
    for k, v in dict_dict_cand_out.items():
        list_cand_tmp = []
        for constraint in constraint_list:
            list_cand_tmp.append(str(v[constraint]))
        str_out += '\t' + k + '\t\t' + '\t'.join(list_cand_tmp) + '\n'
    return str_out


def marks_to_readable_input(ur, sr, dict_sr_out, dict_dict_cand_out, constraint_list):
    if constraint_list is None:
        constraint_list = list(dict_sr_out.keys())
    str_out = 'UR\t' + ur + '\tStress\t' + '\t'.join(constraint_list) + '\n'
    list_sr_tmp = []
    for constraint in constraint_list:
        list_sr_tmp.append(str(dict_sr_out[constraint]))
    sr = sr.replace('|', '\t')
    str_out += 'SR\t' + sr + '\t' + '\t'.join(list_sr_tmp) + '\n'
    for k, v in dict_dict_cand_out.items():
        list_cand_tmp = []
        is_violated = False
        for constraint in constraint_list:
            sr_num_violate = dict_sr_out[constraint]
            if not is_violated and sr_num_violate < v[constraint]:
                list_cand_tmp.append(str(v[constraint]) + '!')
                is_violated = True
            else:
                list_cand_tmp.append(str(v[constraint]))
        k = k.replace('|', '\t')
        str_out += '\t' + k + '\t' + '\t'.join(list_cand_tmp) + '\n'
    return str_out


def proc_stress(str_in):
    split_strs = str_in.strip().split('.')
    list_syl = []
    list_temp = []
    is_parse = False
    for syl in split_strs:
        syl = syl.strip()
        if syl != '':
            if syl[0] == '(' and syl[-1] == ')':
                list_syl.append([[syl[1:-1]], True])
            elif syl[0] == '(':
                is_parse = True
                syl = syl[1:]
                list_temp.append(syl)
            elif syl[-1] == ')':
                syl = syl[:-1]
                list_temp.append(syl)
                list_syl.append([list_temp, is_parse])
                list_temp = []
                is_parse = False
            elif is_parse:
                list_temp.append(syl)
            else:
                list_syl.append([[syl], is_parse])
    #print(str_in)
    #print(list_syl)
    return list_syl


def rand_cand_replace(syllable_ur, dict_phone_decode, dict_feat):
    # replace chars into something that's 1 feat different
    tmp_num_cand = 0
    list_all_replace = []
    for syl in syllable_ur:
        for char_encoded in syl:
            phone_decoded = dict_phone_decode[char_encoded]
            replace_phone = [phone_decoded]
            for phone_compare, phone_feat_dict in dict_feat.items():
                num_differ = 0
                for feat_key, feat_value in phone_feat_dict.items():
                    original_val = str(dict_feat[phone_decoded][feat_key])
                    this_val = str(feat_value)
                    if original_val != '0' and this_val != '0' and original_val != this_val:
                        num_differ += 1
                if 1 <= num_differ <= 2:  # TODO decide how many we want
                    replace_phone.append(phone_compare)
            #print(char_encoded)
            #print(replace_phone)
            tmp_num_cand += len(replace_phone) - 1
            list_all_replace.append(replace_phone)
        list_all_replace.append(['.'])
    #print(tmp_num_cand)
    list_all_replace = list_all_replace[:-1]

    set_replace_cand = set()
    for idx, sublist_replace in enumerate(list_all_replace):
        if sublist_replace[0] != '.':
            prev_str = ''
            succ_str = ''
            for idx_prev_succ, sublist_replace_prev_succ in enumerate(list_all_replace):
                if idx_prev_succ < idx:
                    prev_str += sublist_replace_prev_succ[0]
                elif idx_prev_succ > idx:
                    succ_str += sublist_replace_prev_succ[0]
            for replaceable_phone in sublist_replace[1:]:
                str_generated = prev_str + replaceable_phone + succ_str
                set_replace_cand.add(str_generated)
                #print(str_generated)
            # print(prev_str + sublist_replace[0] + succ_str)
    #print(len(set_replace_cand))
    return set_replace_cand


def rand_cand_remove(syllable_ur, dict_phone_decode):
    # delete any one char
    list_phone_ur = []
    for syl in syllable_ur:
        for phone in syl:
            list_phone_ur.append(dict_phone_decode[phone])
        list_phone_ur.append('.')
    #print(list_phone_ur)
    list_phone_ur = list_phone_ur[:-1]

    set_all_delete = set()
    for idx, phone in enumerate(list_phone_ur):
        if phone != '.':
            prev_str = ''
            succ_str = ''
            for idx_prev_succ, phone_prev_succ in enumerate(list_phone_ur):
                if idx_prev_succ < idx:
                    prev_str += phone_prev_succ
                elif idx_prev_succ > idx:
                    succ_str += phone_prev_succ
            str_removed = prev_str + succ_str
            str_removed = str_removed.replace('..', '.')
            if str_removed[0] == '.':
                str_removed = str_removed[1:]
            if str_removed[-1] == '.':
                str_removed = str_removed[:-1]
            set_all_delete.add(str_removed)
            #print(prev_str + succ_str)
    #print(len(set_all_delete))
    return set_all_delete


def rand_cand_insert(syllable_ur, dict_phone_decode, insert_token):
    # delete any one char
    list_phone_ur = []
    for syl in syllable_ur:
        for phone in syl:
            list_phone_ur.append(dict_phone_decode[phone])
        list_phone_ur.append('.')
    #print(list_phone_ur)
    list_phone_ur = list_phone_ur[:-1]

    set_all_insert = set()
    for i in range(len(list_phone_ur) + 1):
        list_inserted = list_phone_ur.copy()
        list_inserted.insert(i, insert_token)
        set_all_insert.add(''.join(list_inserted))
        #print(''.join(list_inserted))
    #print(len(set_all_insert))
    return set_all_insert


def rand_cand(syllable_ur, dict_phone_decode, dict_feat):
    set_all = set()
    # replace chars into something that's 1 feat different
    set_replace = rand_cand_replace(syllable_ur, dict_phone_decode, dict_feat)
    # delete any one char
    set_remove = rand_cand_remove(syllable_ur, dict_phone_decode)
    #print()
    # add a cons/vowel to any one char
    set_insert_schwa = rand_cand_insert(syllable_ur, dict_phone_decode, 'ə')
    set_insert_glot_stop = rand_cand_insert(syllable_ur, dict_phone_decode, 'ʔ')

    set_all = set_all.union(set_replace, set_remove, set_insert_schwa, set_insert_glot_stop)
    #print(len(set_all))
    #print(len(set_replace) + len(set_remove) + len(set_insert_schwa) + len(set_insert_glot_stop))
    return set_all


class OTItem:
    def __init__(self, str_input, str_memo):
        self.text = str_input
        split_lines = str_input.strip().split('\n')
        self.ur = ''
        self.sr = ''
        self.cand = []
        self.sr_stress = 'na'
        self.cand_stress = []
        self.index = ''
        self.ident_feat = []
        self.agree_feat = []
        self.mark_feat = []
        self.gen_cand = False
        for line in split_lines:
            line = line.strip()
            if line != '' and line[0] != '#' and line[0] != '=':
                split_tokens = line.split('\t')
                key = split_tokens[0]
                left_tokens = split_tokens[1:]
                if key.strip().lower() == 'ur':
                    self.ur = left_tokens[0].strip()
                elif key.strip().lower() == 'sr':
                    self.sr = left_tokens[0].strip()
                elif key.strip().lower() == 'sr_stress':
                    self.sr_stress = left_tokens[0].strip()
                elif key.strip().lower() == 'candidates':
                    for str_cand in left_tokens:
                        if str_cand.strip() != '':
                            self.cand.append(str_cand.strip())
                elif key.strip().lower() == 'candidates_stress':
                    for str_cand_stress in left_tokens:
                        if str_cand_stress.strip() != '':
                            self.cand_stress.append(str_cand_stress.strip())
                elif key.strip().lower() == 'ident_feat':
                    for str_feat in left_tokens:
                        if str_feat.strip() != '':
                            self.ident_feat.append(str_feat.strip())
                elif key.strip().lower() == 'agree_feat':
                    for str_feat in left_tokens:
                        if str_feat.strip() != '':
                            split_cond = str_feat.strip().split('|')
                            agree_feat_str = split_cond[0].strip()
                            cond_list = split_cond[-1].split(',')
                            dict_cond = {}
                            for cond in cond_list:
                                if cond.strip() != '':
                                    cond_split = cond.strip().split(':')
                                    dict_cond[cond_split[0]] = cond_split[1]
                            self.agree_feat.append([agree_feat_str, dict_cond])
                elif key.strip().lower() == 'mark_feat':
                    for str_feat in left_tokens:
                        if str_feat.strip() != '':
                            mark_feat_list = str_feat.strip().split(',')
                            dict_cond = {}
                            for cond in mark_feat_list:
                                if cond.strip() != '':
                                    cond_split = cond.strip().split(':')
                                    dict_cond[cond_split[0]] = cond_split[1]
                            self.mark_feat.append(dict_cond)
                elif key.strip().lower() == 'generate':
                    self.gen_cand = bool(left_tokens[0].strip().lower() == 'true')
            elif line[0] == '=':
                self.index = str(line[1:].strip())
        if len(self.cand_stress) == 0:
            self.cand_stress = ['na'] * len(self.cand)


def proc_input_str(input_path):
    str_in = read_file_as_str(input_path)
    split_item = str_in.strip().split('item_id')
    list_ot_items = []
    for item in split_item:
        if 'ur\t' in item and 'sr\t' in item:
            list_ot_items.append(OTItem(item, ''))
    return list_ot_items

