# MaskTextSpotter
This is the code of "Mask TextSpotter: An End-to-End Trainable Neural Network for Spotting Text with Arbitrary Shapes" (TPAMI version).
It is an extension of the ECCV version while sharing the same title. For more details, please refer to our [TPAMI paper](https://ieeexplore.ieee.org/document/8812908). 

This repo is inherited from [maskrcnn-benchmark](https://github.com/facebookresearch/maskrcnn-benchmark) and follows the same license.


## Installation

### Requirements:
- Python3 (Python3.7 is recommended)
- PyTorch >= 1.0 (1.2 is recommended)
- torchvision from master
- cocoapi
- yacs
- matplotlib
- GCC >= 4.9 (This is very important!)
- OpenCV
- CUDA >= 9.0 (10.0 is recommended)


```bash
  # first, make sure that your conda is setup properly with the right environment
  # for that, check that `which conda`, `which pip` and `which python` points to the
  # right path. From a clean conda env, this is what you need to do

  conda create --name masktextspotter -y
  conda activate masktextspotter

  # this installs the right pip and dependencies for the fresh python
  conda install ipython pip

  # python dependencies
  pip install ninja yacs cython matplotlib tqdm opencv-python shapely scipy tensorboardX

  # install PyTorch
  conda install pytorch torchvision cudatoolkit=10.0 -c pytorch

  export INSTALL_DIR=$PWD

  # install pycocotools
  cd $INSTALL_DIR
  git clone https://github.com/cocodataset/cocoapi.git
  cd cocoapi/PythonAPI
  python setup.py build_ext install

  # install apex (optional)
  cd $INSTALL_DIR
  git clone https://github.com/NVIDIA/apex.git
  cd apex
  python setup.py install --cuda_ext --cpp_ext

  # clone repo
  cd $INSTALL_DIR
  git clone https://github.com/MhLiao/MaskTextSpotter.git
  cd MaskTextSpotter

  # build
  python setup.py build develop


  unset INSTALL_DIR
```

## Models
Download Trained [model](https://drive.google.com/open?id=1pPRS7qS_K1keXjSye0kksqhvoyD0SARz)

Add the downloaded model to ```outputs/finetune/```

## Demo 
You can run a demo script for a multiple image inference by ```python tools/demo.py```.
All the images can be put into the demo_images folder and output can be seen in the ```demo_results``` folder

## Datasets
Download the ICDAR2013([Google Drive](https://drive.google.com/open?id=1sptDnAomQHFVZbjvnWt2uBvyeJ-gEl-A), [BaiduYun](https://pan.baidu.com/s/18W2aFe_qOH8YQUDg4OMZdw)) and ICDAR2015([Google Drive](https://drive.google.com/open?id=1HZ4Pbx6TM9cXO3gDyV04A4Gn9fTf2b5X), [BaiduYun](https://pan.baidu.com/s/16GzPPzC5kXpdgOB_76A3cA)) as examples.

The SCUT dataset used for training can be downloaded [here](https://drive.google.com/file/d/1BpE2GEFF7Ay7jPqgaeHxMmlXvM-1Es5_/view?usp=sharing).

The converted labels of Total-Text dataset can be downloaded [here](https://1drv.ms/u/s!ArsnjfK83FbXgcpti8Zq9jSzhoQrqw?e=99fukk).

The converted labels of SynthText can be downloaded [here](https://1drv.ms/u/s!ArsnjfK83FbXgb5vgOOVPYywgCWuQw?e=UPuNTa).

The root of the dataset directory should be ```MaskTextSpotter/datasets/```.

## Testing
### Prepar dataset
An example of the path of test images: ```MaskTextSpotter/datasets/icdar2015/test_iamges```

### Check the config file (configs/finetune.yaml) for some parameters.
test dataset: ```TEST.DATASETS```; 

input size: ```INPUT.MIN_SIZE_TEST''';

model path: ```MODEL.WEIGHT```;

output directory: ```OUTPUT_DIR```

### run ```sh test.sh```


## Training
Place all the training sets in ```MaskTextSpotter/datasets/``` and check ```DATASETS.TRAIN``` in the config file.
### Pretrain
Trained with SynthText

```python3 -m torch.distributed.launch --nproc_per_node=8 tools/train_net.py --config-file configs/pretrain.yaml ```
### Finetune
Trained with a mixure of SynthText, icdar2013, icdar2015, scut-eng-char, and total-text

check the initial weights in the config file.

```python3 -m torch.distributed.launch --nproc_per_node=8 tools/train_net.py --config-file configs/finetune.yaml ```

## Evaluation
### Evaluation for ICDAR 2015 dataset
download the [lexicons](https://drive.google.com/open?id=1u3NlpIZkE4dYmrcWo0qzU_q7ra5jvDhD) and place them like ```evaluation/lexicons/ic15/```

```
cd evaluation/icdar2015/e2e/
# edit "result_dir" in script.py
python script.py
```

### Evaluation for Total-Text dataset (ToDo)



## Citing the related works

Please cite the related works in your publications if it helps your research:

    @article{liao2019mask,
      author={M. {Liao} and P. {Lyu} and M. {He} and C. {Yao} and W. {Wu} and X. {Bai}},
      journal={IEEE Transactions on Pattern Analysis and Machine Intelligence},
      title={Mask TextSpotter: An End-to-End Trainable Neural Network for Spotting Text with Arbitrary Shapes},
      year={2019},
      volume={},
      number={},
      pages={1-1},
      doi={10.1109/TPAMI.2019.2937086},
      ISSN={},
      month={},
    }
    
    @inproceedings{lyu2018mask,
      title={Mask textspotter: An end-to-end trainable neural network for spotting text with arbitrary shapes},
      author={Lyu, Pengyuan and Liao, Minghui and Yao, Cong and Wu, Wenhao and Bai, Xiang},
      booktitle={Proceedings of the European Conference on Computer Vision (ECCV)},
      pages={67--83},
      year={2018}
    }
    

