from utils import*
import argparse
import glob
import sys
import os
from shutil import copyfile

def main(args):
    mask_name = "CB"

    print("Reading folder : ", args.input_dir)
    print("Selected spacings : ", args.spacing)

    patients = {}

    normpath = os.path.normpath("/".join([args.input_dir, '**', '']))
    for img_fn in sorted(glob.iglob(normpath, recursive=True)):
        #  print(img_fn)
        basename = os.path.basename(img_fn)

        if True in [ext in img_fn for ext in [".nrrd", ".nrrd.gz", ".nii", ".nii.gz", ".gipl", ".gipl.gz"]]:
            file_name = basename.split(".")[0]
            elements_ = file_name.split("_")
            elements_dash = file_name.split("-")
            # print(elements_dash)
            if mask_name in elements_ or "scan" in elements_:
                patient = ""
                if len(elements_) != 0:
                    if len(elements_) > 2:
                        patient = elements_[0] + "_" + elements_[1]
                    elif len(elements_) > 1:
                        patient = elements_[0]
                patient = patient.split("_Seg")[0]           
                # if len(elements_dash) >1:
                #     patient = elements_dash[0]

                # patient = "RC-"+elements_[0]
                # for elem in elements_[1:-1]:
                #     patient += "_" + elem

                # print(patient)

                folder_name = os.path.basename(os.path.dirname(img_fn))
                if folder_name in patient:
                    folder_name = os.path.basename(os.path.dirname(os.path.dirname(img_fn)))
                patient = folder_name + "-" + patient

                print(patient)

                if patient not in patients.keys():
                    patients[patient] = {}
    
                if True in [txt in basename for txt in ["scan","Scan"]]:
                    patients[patient]["scan"] = img_fn
                    patients[patient]["dir"] = os.path.dirname(img_fn)

                elif True in [txt in basename for txt in ["seg","Seg"]]:
                    patients[patient]["seg"] = img_fn
                else:
                    print("----> Unrecognise CBCT file found at :", img_fn)

    # if not os.path.exists(SegOutpath):
    #     os.makedirs(SegOutpath)
    
    error = False
    for patient,data in patients.items():
        if "scan" not in data.keys():
            print("Missing scan for patient :",patient)
            error = True
        if "seg" not in data.keys():
            print("Missing segmentation patient :",patient)
            error = True

    if error:
        print("ERROR : folder have missing/unrecognise files", file=sys.stderr)
        raise
    
    Outpath = args.out
    if not os.path.exists(Outpath):
        os.makedirs(Outpath)



    for patient,data in patients.items():

        scan = data["scan"]
        seg = data["seg"]

        patient_dir = patient.split("-")[0]
        patient_name = patient.split("-")[1]

        patient_dirname =  data["dir"].replace(args.input_dir,'')
        ScanOutpath = os.path.join(Outpath,patient_dir)

        if not os.path.exists(ScanOutpath):
            os.makedirs(ScanOutpath)
            
        # if not os.path.exists(SegOutpath):
        #     os.makedirs(SegOutpath)

        file_basename = os.path.basename(scan)
        file_name = file_basename.split(".")

        # Outpath_Seg = os.path.join(ScanOutpath, patient + "_Correct_Seg")
        # if not os.path.exists(Outpath_Seg):
        #     os.makedirs(Outpath_Seg)

        sp = args.spacing
        spacing = str(sp).replace(".","")
        # scan_name = patient + "_scan_Sp"+ spacing + ".nii.gz"
        # seg_name = patient + "_seg_Sp"+ spacing + ".nii.gz"
        scan_name = patient + "_scan.nii.gz"
        seg_name = patient + "_" + mask_name + "_Mask_Seg.nii.gz"

        

        SetSpacing(scan,output_spacing=sp,outpath= os.path.join(ScanOutpath,scan_name))
        SetSpacing(seg,output_spacing=sp,interpolator="NearestNeighbor",outpath= os.path.join(ScanOutpath,seg_name))


if __name__ ==  '__main__':
    parser = argparse.ArgumentParser(description='MD_reader', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    
    input_group = parser.add_argument_group('Input files')
    input_group.add_argument('-i','--input_dir', type=str, help='Input directory with 3D images',default="/Users/luciacev-admin/Desktop/Luc_Anchling/CB_MASK_TRAINING_DATA/")

    output_params = parser.add_argument_group('Output parameters')
    output_params.add_argument('-o','--out', type=str, help='Output directory', default="/Users/luciacev-admin/Desktop/Luc_Anchling/CB_MASK_TRAINING_DATA_output/")

    input_group.add_argument('-sp', '--spacing', nargs="+", type=float, help='Wanted output x spacing', default=[0.5,0.5,0.5])

    args = parser.parse_args()
    
    main(args)