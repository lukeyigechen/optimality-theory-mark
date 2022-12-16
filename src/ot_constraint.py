import difflib


# max, dep
def cons_max_dep(nodot_ur, nodot_sr):
    diff_list = [li for li in difflib.ndiff(nodot_ur, nodot_sr)]

    diff_str = ''
    for item in diff_list:
        diff_str += item[0]
    len_diff_str_static = len(diff_str)

    len_diff_str = -1
    len_diff_str_prev = -2

    while len_diff_str != len_diff_str_prev:
        diff_str = diff_str.replace('+-', '')
        diff_str = diff_str.replace('-+', '')
        len_diff_str_prev = len_diff_str
        len_diff_str = len(diff_str)

    max_num = diff_str.count('-')
    dep_num = diff_str.count('+')

    return max_num, dep_num


# gets difference in strings for ident
def cons_ident(nodot_ur, nodot_sr):
    diff_list = [li for li in difflib.ndiff(nodot_ur, nodot_sr)]

    replaced_list = []
    last_memory = [0, ' ', '']
    for str_diff in diff_list:
        sign = str_diff[0]
        token = str_diff[-1]
        if sign == ' ':
            last_memory = [0, ' ', '']
        elif sign == '+':
            if last_memory[1] == '+':
                last_memory = [last_memory[0] + 1, last_memory[1], last_memory[2] + token]
            elif last_memory[1] == ' ':
                last_memory = [1, sign, token]
            elif last_memory[1] == '-':
                if last_memory[0] > 1:
                    last_memory = [last_memory[0] - 1, last_memory[1], last_memory[2] + '|' + token]
                else:
                    replaced_list.append(last_memory[2] + '|' + token)
                    last_memory = [0, ' ', '']
        elif sign == '-':
            if last_memory[1] == '-':
                last_memory = [last_memory[0] + 1, last_memory[1], last_memory[2] + token]
            elif last_memory[1] == ' ':
                last_memory = [1, sign, token]
            elif last_memory[1] == '+':
                if last_memory[0] > 1:
                    last_memory = [last_memory[0] - 1, last_memory[1], last_memory[2] + '|' + token]
                else:
                    replaced_list.append(last_memory[2] + '|' + token)
                    last_memory = [0, ' ', '']
    #print(diff_list)
    #print(replaced_list)
    return replaced_list


# ident(feat)
def cons_ident_feat(replaced_list, feat, dict_phone_decode, dict_feat):
    num_violate = 0
    for str_found in replaced_list:
        list_split = str_found.split('|')
        ur = list_split[0]
        sr = ''.join(list_split[1:])
        # print(ur)
        # print(sr)
        for i in range(len(ur)):
            ur_phone = dict_phone_decode[ur[i]]
            sr_phone = dict_phone_decode[sr[i]]
            if dict_feat[ur_phone][feat] != dict_feat[sr_phone][feat]:
                num_violate += 1
                # print(ur_phone)
                # print(sr_phone)
    return num_violate


# mark combination of feats
# dict_mark_feat in the form of {feat1:val(e.g., +, -, 0), feat2:val, ...}
def cons_mark_feat_combine(dict_mark_feat, nodot_sr, dict_phone_decode, dict_feat):
    num_violate = 0
    for phone in nodot_sr:
        decoded = dict_phone_decode[phone]
        match = True
        for key, value in dict_mark_feat.items():
            if dict_feat[decoded][key] != value:
                match = False
        if match:
            num_violate += 1
            #print(decoded)
    return num_violate


# nocoda
def cons_nocoda(syllable_sr, dict_phone_decode, dict_feat):
    num_violate = 0
    for syl in syllable_sr:
        decode = dict_phone_decode[syl[-1]]
        if dict_feat[decode]['syllabic'] == '-': # TODO consonant or syllabic?
            num_violate += 1
    return num_violate


# onset
def cons_onset(syllable_sr, dict_phone_decode, dict_feat):
    num_violate = 0
    for syl in syllable_sr:
        decode = dict_phone_decode[syl[0]]
        if dict_feat[decode]['syllabic'] == '+':
            num_violate += 1
    return num_violate


def helper_agree(decoded, dict_cond_feat, dict_feat):
    match = True
    for key, value in dict_cond_feat.items():
        if dict_feat[decoded][key] != value:
            match = False
    return match


# agree(feat)
# dict_cond_feat is the requirement for the judgement to be made, represented as a dict {feat1: value, ...}
def cons_agree(agree_feat, dict_cond_feat, nodot_sr, dict_phone_decode, dict_feat):
    num_violate = 0
    last_value = ''
    for phone in nodot_sr:
        decoded = dict_phone_decode[phone]
        this_value = dict_feat[decoded][agree_feat]
        # print(last_value, this_value)
        this_meet_cond = helper_agree(decoded, dict_cond_feat, dict_feat)
        if this_meet_cond:
            if last_value != this_value and last_value != '':
                num_violate += 1
                # print(decoded)
            last_value = this_value
        else:
            last_value = ''
    return num_violate


# disagree(feats), where feats represented as a dict {feat1: value, ...}
# e.g. disagree({'syllabic': '-'}) -> *CC
def cons_disagree(dict_cond_feat, nodot_sr, dict_phone_decode, dict_feat):
    num_violate = 0
    last_value = False
    for phone in nodot_sr:
        decoded = dict_phone_decode[phone]
        # print(last_value, this_value)
        this_value = helper_agree(decoded, dict_cond_feat, dict_feat)
        if last_value and this_value:
            num_violate += 1
        last_value = this_value
    return num_violate


# *complex onset
def cons_no_complex_onset(syllable_sr, dict_phone_decode, dict_feat):
    num_violate = 0
    for syl in syllable_sr:
        if len(syl) > 1:
            decode_0 = dict_phone_decode[syl[0]]
            decode_1 = dict_phone_decode[syl[1]]
            if dict_feat[decode_0]['syllabic'] == '-' and dict_feat[decode_1]['syllabic'] == '-':
                num_violate += 1
    return num_violate


# *complex coda
def cons_no_complex_coda(syllable_sr, dict_phone_decode, dict_feat):
    num_violate = 0
    for syl in syllable_sr:
        if len(syl) > 1:
            decode_0 = dict_phone_decode[syl[-1]]
            decode_1 = dict_phone_decode[syl[-2]]
            if dict_feat[decode_0]['syllabic'] == '-' and dict_feat[decode_1]['syllabic'] == '-':
                num_violate += 1
    return num_violate


# align-l
def cons_align_word_left(nodot_ur, nodot_sr, dict_phone_decode):
    num_violate = 0
    decoded_ur = dict_phone_decode[nodot_ur[0]]
    decoded_sr = dict_phone_decode[nodot_sr[0]]
    if decoded_ur != decoded_sr:
        num_violate += 1
    return num_violate


# align-r
def cons_align_word_right(nodot_ur, nodot_sr, dict_phone_decode):
    num_violate = 0
    decoded_ur = dict_phone_decode[nodot_ur[-1]]
    decoded_sr = dict_phone_decode[nodot_sr[-1]]
    if decoded_ur != decoded_sr:
        num_violate += 1
    return num_violate


def dict_count_occur(str_in, dict_count):
    if str_in not in dict_count:
        dict_count[str_in] = 0
    str_out = str_in + str(dict_count[str_in])
    dict_count[str_in] += 1
    return str_out, dict_count


def dict_encode_align_morph(str_in, dict_encode, unicode_num):
    if str_in not in dict_encode:
        dict_encode[str_in] = chr(unicode_num)
        unicode_num += 1
    return dict_encode[str_in], dict_encode, unicode_num


# align-morph, left_right in {'L', 'R'}
# TODO this method cannot solve all cases
def cons_align_morph(syllable_ur, syllable_sr, left_right):
    num_violate = 0
    #print(syllable_ur)
    #print(syllable_sr)
    dict_lr = {'L': 0, 'R': -1}
    dict_encode = {}
    unicode_num = int("1100", 16)  # hangul
    left_ur = []
    dict_ur = {}
    for syl in syllable_ur:
        list_indexed = []
        for char_in in syl:
            str_out, dict_ur = dict_count_occur(char_in, dict_ur)
            str_out, dict_encode, unicode_num = dict_encode_align_morph(str_out, dict_encode, unicode_num)
            list_indexed.append(str_out)
        left_ur.append(list_indexed[dict_lr[left_right]])
    left_sr = []
    dict_sr = {}
    for syl in syllable_sr:
        list_indexed = []
        for char_in in syl:
            str_out, dict_sr = dict_count_occur(char_in, dict_sr)
            str_out, dict_encode, unicode_num = dict_encode_align_morph(str_out, dict_encode, unicode_num)
            list_indexed.append(str_out)
        left_sr.append(list_indexed[dict_lr[left_right]])
    #print(left_ur)
    #print(left_sr)

    # check if num of tokens for each boundary phone matches
    # if not, the script cannot solve; need human intervention
    dict_decode = {v: k for k, v in dict_encode.items()}
    for item in left_ur + left_sr:
        decoded = dict_decode[item][0]
        if decoded in dict_ur and decoded in dict_sr and dict_ur[decoded] != dict_sr[decoded]:
            print('Warning: Align-Morph-' + left_right + ' cannot figure out [' + '.'.join(syllable_sr) + '], human judgement needed.')
            print('The script will return a guess')
            left_ur = []
            left_sr = []
            for syl in syllable_ur:
                left_ur.append(syl[dict_lr[left_right]])
            for syl in syllable_sr:
                left_sr.append(syl[dict_lr[left_right]])
            break

    diff_list = [li for li in difflib.ndiff(''.join(left_ur), ''.join(left_sr))]
    #print(diff_list)
    num_plus = 0
    num_minus = 0
    for item in diff_list:
        sign = item[0]
        if sign == '+':
            num_plus += 1
        elif sign == '-':
            num_minus += 1
    num_violate = max(num_plus, num_minus)

    return num_plus


# binarity, ft-bin
def cons_ft_bin(list_syl_stress):
    num_violate = 0
    for syl_info in list_syl_stress:
        if len(syl_info[0]) != 2 and syl_info[-1]:
            num_violate += 1
    return num_violate


# parse
def cons_parse_syl(list_syl_stress):
    num_violate = 0
    for syl_info in list_syl_stress:
        if not syl_info[-1]:
            num_violate += len(syl_info[0])
            if len(syl_info[0]) != 1:
                print('Warning: len(syl_info[0]) != 1 when trying to count parse')
    return num_violate


# trochaic
def cons_trochaic(list_syl_stress):
    num_violate = 0
    for syl_info in list_syl_stress:
        if syl_info[-1] and len(syl_info[0]) == 2:
            syl = syl_info[0]
            if syl[0] != 'p' and syl[0] != 's':
                num_violate += 1
    return num_violate


# iambic
def cons_iambic(list_syl_stress):
    num_violate = 0
    for syl_info in list_syl_stress:
        if syl_info[-1] and len(syl_info[0]) == 2:
            syl = syl_info[0]
            if syl[-1] != 'p' and syl[-1] != 's':
                num_violate += 1
    return num_violate


# align-ft-l
def cons_align_ft_l(list_syl_stress):
    num_violate = 0
    for syl_info in list_syl_stress:
        if syl_info[-1]:
            break
        else:
            num_violate += len(syl_info[0])
    return num_violate


# align-ft-r
def cons_align_ft_r(list_syl_stress):
    num_violate = 0
    for syl_info in reversed(list_syl_stress):
        if syl_info[-1]:
            break
        else:
            num_violate += len(syl_info[0])
    return num_violate


# leftmost
def cons_leftmost(list_syl_stress):
    num_violate = 0
    for syl_info in list_syl_stress:
        if syl_info[-1] and 'p' in syl_info[0]:
            break
        else:
            num_violate += len(syl_info[0])
    return num_violate


# rightmost
def cons_rightmost(list_syl_stress):
    num_violate = 0
    for syl_info in reversed(list_syl_stress):
        if syl_info[-1] and 'p' in syl_info[0]:
            break
        else:
            num_violate += len(syl_info[0])
    return num_violate


# wsp, heavy syllable = closed (coda) or long vowel
def cons_wsp(syllable_sr, sr_stress_encode, dict_phone_decode, dict_feat):  # long vowels as xx or x:
    num_violate = 0
    str_stress_only = sr_stress_encode.replace('.', '').replace('(', '').replace(')', '')
    for idx, syl in enumerate(syllable_sr):
        syl_stress = str_stress_only[idx]
        is_heavy = False
        if dict_feat[dict_phone_decode[syl[-1]]]['syllabic'] == '-':
            is_heavy = True
        mora_count = 0
        for phone in syl:
            if dict_feat[dict_phone_decode[phone]]['syllabic'] == '+' and dict_feat[dict_phone_decode[phone]]['long'] == '+':
                mora_count += 2
            elif dict_feat[dict_phone_decode[phone]]['syllabic'] == '+':
                mora_count += 1
        if mora_count >= 2:
            is_heavy = True
        if is_heavy and syl_stress == 'n':
            num_violate += 1
            #print(syl, syl_stress)
    return num_violate


# nonfinality-syl-footing
def cons_nonfinality_syl_footing(list_syl_stress):
    num_violate = 0
    if list_syl_stress[-1][-1]:
        num_violate += 1
    return num_violate


# nonfinality-syl-stress
def cons_nonfinality_syl_stress(sr_stress_encode):
    num_violate = 0
    str_stress_only = sr_stress_encode.replace('.', '').replace('(', '').replace(')', '')
    if str_stress_only[-1] != 'n':
        num_violate += 1
    return num_violate


# noclash
def cons_noclash(sr_stress_encode):
    num_violate = 0
    str_stress_only = sr_stress_encode.replace('.', '').replace('(', '').replace(')', '')
    for i in range(len(str_stress_only) - 1):
        if str_stress_only[i] != 'n' and str_stress_only[i + 1] != 'n':
            num_violate += 1
    return num_violate


# nolapse
def cons_nolapse(sr_stress_encode):
    num_violate = 0
    str_stress_only = sr_stress_encode.replace('.', '').replace('(', '').replace(')', '')
    for i in range(len(str_stress_only) - 1):
        if str_stress_only[i] == 'n' and str_stress_only[i + 1] == 'n':
            num_violate += 1
    return num_violate


# all-ft-left
def cons_all_ft_left(sr_stress_encode):
    num_violate = 0
    split_dot = sr_stress_encode.split('.')
    for idx, syl in enumerate(split_dot):
        if '(' in syl:
            num_violate += idx
    return num_violate


# all-ft-right
def cons_all_ft_right(sr_stress_encode):
    num_violate = 0
    split_dot = sr_stress_encode.split('.')
    for idx, syl in enumerate(split_dot):
        if ')' in syl:
            num_violate += len(split_dot) - (idx + 1)
    return num_violate
