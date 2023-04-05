from utils import*
import argparse
from shutil import copyfile
import multiprocessing as mp


def main(args):

    print("Reading folder : ", args.input_dir)
    print("Selected spacings : ", args.spacing)

    patients = GetPatients(args.input_dir)
    
    nb_workers = args.num_workers
    if nb_workers > mp.cpu_count():
        nb_workers = mp.cpu_count()
    print("Number of workers : ", nb_workers)

    # Create a process to count the number of patients done throughout the process
    nb_patients_done = mp.Manager().list([0 for i in range(nb_workers)])
    nb_patients = len(patients)
    check = mp.Process(target=CheckProgress, args=(nb_patients_done, nb_patients))
    print("Resampling scans for Training...")
    check.start()

    key_split = np.array_split(list(patients.keys()), nb_workers)

    processes = [mp.Process(target=InitScan, args=(args, {key: patients[key] for key in key_split[i]},nb_patients_done,i)) for i in range(nb_workers)]

    for p in processes:p.start()
    for p in processes:p.join()
    
    check.join()


if __name__ ==  '__main__':
    parser = argparse.ArgumentParser(description='MD_reader', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    
    input_group = parser.add_argument_group('Input files')
    input_group.add_argument('-i','--input_dir', type=str, help='Input directory with 3D images',default="")
    input_group.add_argument('-o','--out', type=str, help='Output directory', default='')#parser.parse_args().input_dir+"_NEW")
    input_group.add_argument('-nw','--num_workers', type=int, help='Number of workers', default=1)
    input_group.add_argument('-sp', '--spacing', nargs="+", type=float, help='Wanted output x spacing', default=[0.5,0.5,0.5])

    args = parser.parse_args()
    
    main(args)