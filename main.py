import os
import sys
import time
import argparse
#from src.others.test_rouge_score import RougeScorer

PROJECT_DIR = '/home/uoneway/Project/PreSumm_ko'
DATA_DIR = PROJECT_DIR + '/data'
RAW_DATA_DIR = DATA_DIR + '/raw'
JSON_DATA_DIR = DATA_DIR + '/json_data'
BERT_DATA_DIR = DATA_DIR + '/bert_data' 

MODEL_DIR = PROJECT_DIR + '/models'  
LOG_DIR = PROJECT_DIR + '/logs' # logs -> for storing logs information during preprocess and finetuning
RESULT_DIR = PROJECT_DIR + '/results' 

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-task", default='test', type=str, choices=['data', 'train', 'valid', 'test'])
    parser.add_argument("-train_from", default=None, type=str)
    parser.add_argument("-model_path", default=None, type=str)
    parser.add_argument("-test_from", default=None, type=str)
    parser.add_argument("-target_summary_sent", default='abs', type=str)
    #parser.add_argument("-use_bert_emb", type=str2bool, nargs='?',const=True,default=False)
    args = parser.parse_args()

    os.chdir(PROJECT_DIR + '/src')
    now = time.strftime('%m%d_%H%M')

    if args.task == 'data':
        pass
        # ### 전처리
        # os.system("python make_json_data.py train abs")
        # os.system("python make_json_data.py test")

        # os.system("python make_bert_data.py train")
        # os.system("python make_bert_data.py test")

    # python main.py -task train -target_summary_sent abs -train_from 1204_1540/model_step_32000.pt 
    elif args.task == 'train':
        """
        파라미터별 설명은 trainer_ext 참고
        """
        # python train.py -task ext -mode train -bert_data_path BERT_DATA_PATH -ext_dropout 0.1 -model_path MODEL_PATH -lr 2e-3 -visible_gpus 0,1,2 -report_every 50 -save_checkpoint_steps 1000 -batch_size 3000 -train_steps 50000 -accum_count 2 -log_file ../logs/ext_bert_cnndm -use_interval true -warmup_steps 10000 -max_pos 512
        # !python train.py  -task abs -mode train -train_from /kaggle/input/absbert-weights/model_step_149000.pt -bert_data_path /kaggle/working/bert_data/news  -dec_dropout 0.2  -model_path /kaggle/working/bertsumextabs -sep_optim true -lr_bert 0.002 -lr_dec 0.02 -save_checkpoint_steps 1000 -batch_size 140 -train_steps 150000 -report_every 100 -accum_count 5 -use_bert_emb true -use_interval true -warmup_steps_bert 1000 -warmup_steps_dec 500 -max_pos 512 -visible_gpus 0  -temp_dir /kaggle/working/temp -log_file /kaggle/working/logs/abs_bert_cnndm
        param1 = "-ext_dropout 0.1 -lr 2e-3 -batch_size 500 -train_steps 5000 -accum_count 2 -use_interval true -warmup_steps 3000 -max_pos 512"
        param2 = "-ext_dropout 0.1 -lr 2e-3 -batch_size 1000 -train_steps 5000 -accum_count 2 -use_interval true -warmup_steps 3000 -max_pos 512"
        param3 = "-ext_dropout 0.1 -max_pos 512 -lr 2e-3 -warmup_steps 10000 -batch_size 3000 -accum_count 2 -train_steps 50000  -use_interval true"
        
        param = param3
        param_name = 'p3'

        do_str = f"""\
            python train.py -task ext -mode train \
                -bert_data_path {BERT_DATA_DIR}/train_{args.target_summary_sent} \
                -save_checkpoint_steps 1000 -visible_gpus 0,1 -report_every 50 \
                {param} \
                """ 
        if args.train_from is None:
            os.system(f'mkdir {MODEL_DIR}/{now}')
            do_str += f"""\
                -model_path {MODEL_DIR}/{now} \
                -log_file {LOG_DIR}/train_{now}.log \
                """
        else:
            model_folder, model_name = args.train_from.rsplit('/', 1)
            do_str += f"""\
                -train_from {MODEL_DIR}/{args.train_from} \
                -model_path {MODEL_DIR}/{model_folder} \
                -log_file {LOG_DIR}/train_{model_folder}_{model_name}.log \
                """
            
        print(do_str)
        os.system(do_str)

    # python main.py -task valid -model_path 1208_0747
    elif args.task == 'valid':
        """
        python train.py -task abs -mode validate -batch_size 3000 -test_batch_size 500 
        -bert_data_path BERT_DATA_PATH -log_file ../logs/val_abs_bert_cnndm -model_path MODEL_PATH -result_path ../logs/abs_bert_cnndm 
        -sep_optim true -use_interval true -visible_gpus 1 
        -max_pos 512 -max_length 200 -alpha 0.95 -min_length 50 
        -max_pos 512 -min_length 20 -max_length 100 -alpha 0.9 
        """
        os.system(f"python train.py -task ext -mode validate -test_all True"
            + f" -model_path {MODEL_DIR}/{args.model_path}"
            + f" -bert_data_path {BERT_DATA_DIR}/valid_ext"
            + f" -result_path {RESULT_DIR}/result_{args.model_path}"
            + f" -log_file {LOG_DIR}/valid_{args.model_path}.log"
            + f" -test_batch_size 500  -batch_size 3000"
            + f" -sep_optim true -use_interval true -visible_gpus 0,1"
            + f" -max_pos 512 -max_length 200 -alpha 0.95 -min_length 50"
            + f" -report_rouge True"
            + f" -max_tgt_len 100"
        )

    # python main.py -task test -test_from 1207_1054/model_step_27000.pt
    elif args.task == 'test':
        model_folder, model_name = args.test_from.rsplit('/', 1)
        model_name = model_name.split('_', 1)[1].split('.')[0]
        os.system(f"""\
            python train.py -task ext -mode test \
            -test_from {MODEL_DIR}/{args.test_from} \
            -bert_data_path {BERT_DATA_DIR}/test \
            -result_path {RESULT_DIR}/result_{model_folder} \
            -log_file {LOG_DIR}/test_{model_folder}.log \
            -test_batch_size 1  -batch_size 3000 \
            -sep_optim true -use_interval true -visible_gpus 1 \
            -max_pos 512 -max_length 200 -alpha 0.95 -min_length 50 \
            -report_rouge False \
            -max_tgt_len 100
        """)
        #             -max_pos 512 -max_length 200 -alpha 0.95 -min_length 50 \
        # -report_rouge True  \
        #  -model_path {MODEL_DIR} 
        # args.max_tgt_len=140  이거 수정해도 효과가 거의

        os.system(f"""
            python make_submission.py result_{model_folder}_{model_name}.candidate
        """)

    elif args.task == 'rouge':
        pass
        # rouge_scorer = RougeScorer()
        # str_scores = rouge_scorer.compute_rouge(ref_df, hyp_df)
        # rouge_scorer.save_rouge_scores(str_scores)
        # rouge_scorer.format_rouge_scores(rouge_scorer.scores)

