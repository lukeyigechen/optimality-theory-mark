from ot_util import write_output, read_feat_table, proc_candidate, encode_as_dict, read_file_as_lines, proc_input
from ot_rank import rcd_ranking, mark_to_rcd_input, flat_ranked_rcd_list
import ot_constraint as otcons
import sys
import os
from ot_util import rand_cand, proc_input_str, marks_to_readable_input, marks_to_hayes_input, proc_stress


def assign_violate(str_sr, dict_phone_encode, dict_phone_decode, nodot_ur, syllable_ur, dict_feat, sr_stress_encode, item_in):
    syllable_sr, nodot_sr = proc_candidate(str_sr, dict_phone_encode)
    list_syl_stress = proc_stress(sr_stress_encode)

    # dict of output
    dict_output = dict()

    max_num, dep_num = otcons.cons_max_dep(nodot_ur, nodot_sr)
    dict_output['Max'] = max_num
    dict_output['Dep'] = dep_num

    replaced_list = otcons.cons_ident(nodot_ur, nodot_sr)
    for ident_f in item_in.ident_feat:
        ident_num = otcons.cons_ident_feat(replaced_list, ident_f, dict_phone_decode, dict_feat)  # allow mod feat
        dict_output['Ident(' + ident_f + ')'] = ident_num

    for mark_f in item_in.mark_feat:
        #dict_mark_feat = {'consonantal': '+', 'voice': '-'}  # allow mod feat
        mark_feat_num = otcons.cons_mark_feat_combine(mark_f, nodot_sr, dict_phone_decode, dict_feat)
        list_name_mark = []
        for mark_k, mark_v in mark_f.items():
            list_name_mark.append(mark_v + mark_k)
        dict_output['*[' + ', '.join(list_name_mark) + ']'] = mark_feat_num

    nocoda_num = otcons.cons_nocoda(syllable_sr, dict_phone_decode, dict_feat)
    dict_output['Nocoda'] = nocoda_num

    onset_num = otcons.cons_onset(syllable_sr, dict_phone_decode, dict_feat)
    dict_output['Onset'] = onset_num

    for agree_f in item_in.agree_feat:
        agree_feat_in = agree_f[0]
        agree_cond_dict = agree_f[-1]
        agree_num = otcons.cons_agree(agree_feat_in, agree_cond_dict, nodot_sr, dict_phone_decode, dict_feat) # allow mod feat
        dict_output['Agree(' + agree_feat_in + ')'] = agree_num

    # new
    no_cc_num = otcons.cons_disagree({'syllabic': '-'}, nodot_sr, dict_phone_decode, dict_feat)
    dict_output['*CC'] = no_cc_num

    # syllable
    complex_onset_num = otcons.cons_no_complex_onset(syllable_sr, dict_phone_decode, dict_feat)
    dict_output['*Complex Onset'] = complex_onset_num
    complex_coda_num = otcons.cons_no_complex_coda(syllable_sr, dict_phone_decode, dict_feat)
    dict_output['*Complex Coda'] = complex_coda_num

    align_word_left_num = otcons.cons_align_word_left(nodot_ur, nodot_sr, dict_phone_decode)
    dict_output['Align-L'] = align_word_left_num
    align_word_right_num = otcons.cons_align_word_right(nodot_ur, nodot_sr, dict_phone_decode)
    dict_output['Align-R'] = align_word_right_num

    #align_morph_left_num = otcons.cons_align_morph(syllable_ur, syllable_sr, 'L')
    #align_morph_right_num = otcons.cons_align_morph(syllable_ur, syllable_sr, 'R')

    # stress
    if sr_stress_encode != '' and sr_stress_encode.lower() != 'na':
        ft_bin_num = otcons.cons_ft_bin(list_syl_stress)
        dict_output['Ft-Bin'] = ft_bin_num
        parse_num = otcons.cons_parse_syl(list_syl_stress)
        dict_output['Parse'] = parse_num
        trochaic_num = otcons.cons_trochaic(list_syl_stress)
        dict_output['Trochaic'] = trochaic_num
        iambic_num = otcons.cons_iambic(list_syl_stress)
        dict_output['Iambic'] = iambic_num
        align_ft_l_num = otcons.cons_align_ft_l(list_syl_stress)
        dict_output['Align-Ft-L'] = align_ft_l_num
        align_ft_r_num = otcons.cons_align_ft_r(list_syl_stress)
        dict_output['Align-Ft-R'] = align_ft_r_num
        leftmost_num = otcons.cons_leftmost(list_syl_stress)
        dict_output['Leftmost'] = leftmost_num
        rightmost_num = otcons.cons_rightmost(list_syl_stress)
        dict_output['Rightmost'] = rightmost_num
        wsp_num = otcons.cons_wsp(syllable_sr, sr_stress_encode, dict_phone_decode, dict_feat)
        dict_output['WSP'] = wsp_num
        nonfin_syl_foot_num = otcons.cons_nonfinality_syl_footing(list_syl_stress)
        dict_output['Nonfinality-syl-footing'] = nonfin_syl_foot_num
        nonfin_syl_stress_num = otcons.cons_nonfinality_syl_stress(sr_stress_encode)
        dict_output['Nonfinality-syl-stress'] = nonfin_syl_stress_num
        all_ft_left_num = otcons.cons_all_ft_left(sr_stress_encode)
        dict_output['All-Ft-Left'] = all_ft_left_num
        all_ft_right_num = otcons.cons_all_ft_right(sr_stress_encode)
        dict_output['All-Ft-Right'] = all_ft_right_num

    return dict_output


def process_single(item_in, dict_phone_encode, dict_phone_decode, dict_feat, output_dir):
    ur = item_in.ur
    sr = item_in.sr
    sr_stress_encode = item_in.sr_stress
    cand_list = item_in.cand
    cand_stress_encode_list = item_in.cand_stress

    print('Processing item ' + item_in.index + ', UR = ' + ur + ', SR = ' + sr)

    # ur, sr, cand_list, sr_stress_encode, cand_stress_encode_list = proc_input(input_lines)
    if len(cand_list) != len(cand_stress_encode_list):
        print('Warning: len(cand_list) != len(cand_stress_encode_list); will treat stress encoding as nas')

    syllable_ur, nodot_ur = proc_candidate(ur, dict_phone_encode)
    #print('ur: ' + ur)

    dict_sr_out = assign_violate(sr, dict_phone_encode, dict_phone_decode, nodot_ur, syllable_ur, dict_feat, sr_stress_encode, item_in)
    #print('sr: ' + sr)
    #print('sr_stress: ' + sr_stress_encode)
    #print(dict_sr_out)

    # add generated cands
    syllable_sr, nodot_sr = proc_candidate(sr, dict_phone_encode)
    if item_in.gen_cand:
        set_gen_cands_ur = rand_cand(syllable_ur, dict_phone_decode, dict_feat)
        set_gen_cands_sr = rand_cand(syllable_sr, dict_phone_decode, dict_feat)
        set_gen_cands = set_gen_cands_ur.union(set_gen_cands_sr)
        if sr in set_gen_cands:
            set_gen_cands.remove(sr)
            #print('sr in set_gen_cands')
        cand_list.extend(list(set_gen_cands))
        cand_stress_encode_list.extend([sr_stress_encode] * len(set_gen_cands))

    dict_dict_cand_out = dict()
    for i in range(len(cand_list)):
        cand = cand_list[i]
        #print('candidate: ' + cand)
        cand_stress_encode = ''
        try:
            cand_stress_encode = cand_stress_encode_list[i]
        except:
            cand_stress_encode = 'na'
        #print('candidate_stress: ' + cand_stress_encode)
        dict_cand_out = assign_violate(cand, dict_phone_encode, dict_phone_decode, nodot_ur, syllable_ur, dict_feat, cand_stress_encode, item_in)
        #print(dict_cand_out)
        dict_dict_cand_out[cand + '|' + cand_stress_encode] = dict_cand_out

    constraint_list = list(dict_sr_out.keys())
    mark_pairs = mark_to_rcd_input(dict_sr_out, list(dict_dict_cand_out.values()))
    #print(mark_pairs)
    list_rcd_ranked = rcd_ranking(constraint_list, mark_pairs)
    list_str_ranked_out = []
    is_challenged = False
    for sublist_cons in list_rcd_ranked:
        if len(sublist_cons) > 0:
            list_str_ranked_out.append('{' + ', '.join(sublist_cons) + '}')
        else:
            is_challenged = True
    str_ranked_out = ' > '.join(list_str_ranked_out)
    str_ranked_out = 'Item ' + str(item_in.index) + ': ' + str_ranked_out
    if is_challenged:
        str_ranked_out += '\nItem ' + str(item_in.index) + ' is successfully challenged by other candidates. Please consider adding other constraints.'
    print(str_ranked_out)
    print('-------------------------------------------------------------------------')

    flat_rcd_list = flat_ranked_rcd_list(list_rcd_ranked)

    str_out_hayes = marks_to_hayes_input(ur, sr + '|' + sr_stress_encode, dict_sr_out, dict_dict_cand_out, flat_rcd_list)
    str_out_read = marks_to_readable_input(ur, sr + '|' + sr_stress_encode, dict_sr_out, dict_dict_cand_out, flat_rcd_list)
    #print(str_out)
    write_output(os.path.join(output_dir, 'out_hayes_form_' + str(item_in.index) + '.tsv'), str_out_hayes)
    write_output(os.path.join(output_dir, 'out_table_form_' + str(item_in.index) + '.tsv'), str_out_read)

    return str_ranked_out


def ot_main():
    if len(sys.argv) != 4:
        print("The script only accepts exactly 3 args: input_data, feature_table, output_dir.")
        return
    # input_lines = read_file_as_lines(sys.argv[1])
    feature_table_dir = sys.argv[2]
    # if feature_table_dir.lower() == 'na':
    #     feature_table_dir = 'E://tempfile/6902/Features.csv'
    output_dir = sys.argv[3]

    df_feat, dict_feat, set_phone, set_feat = read_feat_table(feature_table_dir)
    dict_phone_encode, set_2char = encode_as_dict(set_phone)
    dict_phone_decode = {v: k for k, v in dict_phone_encode.items()}

    list_items_in = proc_input_str(sys.argv[1])

    list_rank_all = []
    print('-------------------------------------------------------------------------')
    for item_in in list_items_in:
        str_this_rank = process_single(item_in, dict_phone_encode, dict_phone_decode, dict_feat, output_dir)
        list_rank_all.append(str_this_rank)

    write_output(os.path.join(output_dir, 'out_ranking.txt'), '\n'.join(list_rank_all))


if __name__ == '__main__':
    ot_main()
