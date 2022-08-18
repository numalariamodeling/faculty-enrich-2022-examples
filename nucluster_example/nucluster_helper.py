import os
import argparse
import subprocess
from simtools.ExperimentManager import slurm


def parse_args():
    description = "Experiment specifications"
    parser = argparse.ArgumentParser(description=description)

    parser.add_argument(
        "-n",
        "--expt_name",
        type=str,
        help="Name of simulation experiment",
        default=None
    )
    parser.add_argument(
        "-i",
        "--expt_id",
        type=str,
        help="Unique ID of simulation experiment"
    )
    return parser.parse_args()


def shell_header(A='b1139', p='b1139', t='02:00:00', N=1, ntasks_per_node=1, memG=8, job_name='slurmjob',
                 arrayJob=None):
    """Requires a 'log' subfolder to write in .err and .out files, alternatively log/ needs to be removed"""
    header = f'#!/bin/bash\n' \
             f'#SBATCH -A {A}\n' \
             f'#SBATCH -p {p}\n' \
             f'#SBATCH -t {t}\n' \
             f'#SBATCH -N {N}\n' \
             f'#SBATCH --ntasks-per-node={ntasks_per_node}\n' \
             f'#SBATCH --mem={memG}G\n' \
             f'#SBATCH --job-name="{job_name}"\n'
    if arrayJob is not None:
        array = arrayJob
        err = '#SBATCH --error=log/slurm_%A_%a.err\n'
        out = '#SBATCH --output=log/slurm_%A_%a.out\n'
        header = header + array + err + out
    else:
        err = f'#SBATCH --error=log/{job_name}.%j.err\n'
        out = f'#SBATCH --output=log/{job_name}.%j.out\n'
        header = header + err + out
    return header


def create_analyzer_submission_script(expt_name, expt_id, WDIR=os.getcwd(), A='b1139', p='b1139', t='04:00:00',
                                      analyzer_script="analyze_exampleSim_w2.py"):
    analyzer_script_name = f'run_analyzer_{expt_id}.sh'
    job_name = f'analyze_{expt_id}'
    header = f'#!/bin/bash\n#SBATCH -A {A}\n#SBATCH -p {p}\n#SBATCH -t {t}\n#SBATCH -N 1\n' \
             f'#SBATCH --ntasks-per-node=1\n#SBATCH --mem=80G\n#SBATCH --job-name="{expt_id}"\n'
    err = '#SBATCH --error=log/slurm_%A_%a.err\n'
    out = '#SBATCH --output=log/slurm_%A_%a.out\n'
    header_post = header + err + out

    pymodule = f'\n\nmodule purge all\nmodule load python/anaconda3.6' \
               f'\nsource activate /projects/b1139/environments/dtk-tools-p36\n'

    pycommand1 = f'\ncd /projects/b1139/dtk-tools-p36/helper_tools/' \
                 f'\npython local_db_fixer.py  -id {expt_id} --status Succeeded'

    pycommand2 = f'\ncd /projects/b1139/faculty-enrich_IO/faculty-enrich-2022-examples/nucluster_example' \
                 f'\npython {analyzer_script} --expt_name {expt_name} --expt_id {expt_id}'
    file = open(os.path.join(WDIR, analyzer_script_name), 'w')
    file.write(header_post + pymodule + pycommand1 + pycommand2)
    file.close()
    
    return analyzer_script_name


def submit_dependent_job(job_id, sh_fname='run_analyzer.sh'):
    script_path = os.path.join(sh_fname)
    result = subprocess.run([f'sbatch --dependency=afterok:{job_id} {script_path}'], shell=True, stdout=subprocess.PIPE)
    result = result.stdout.decode('utf-8').strip()
    job_id_analyzer = slurm.SBATCH_REGEX.match(result).group('id')

    return (job_id_analyzer)  # can be used to schedule postprocessing/plotter script
