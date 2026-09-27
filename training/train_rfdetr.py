import time
import torch
from rfdetr import RFDETRMedium
from rfdetr.training import RFDETRDataModule, RFDETRModelModule, build_trainer

DATASET_DIR = r"D:\projects\Roadsense\data\processed\rfdetr_rdd2022"
OUTPUT_DIR = r"D:\projects\Roadsense\models\rfdetr_medium_1epoch"

model = RFDETRMedium(num_classes=4)

config = model.get_train_config(dataset_dir=DATASET_DIR)

config.batch_size = 1
config.num_workers = 0
config.epochs = 1
config.tensorboard = False
config.wandb = False
config.mlflow = False
config.clearml = False
config.output_dir = OUTPUT_DIR

datamodule = RFDETRDataModule(model.model_config, config)
module = RFDETRModelModule(model.model_config, config)

trainer = build_trainer(
    config,
    model.model_config,
    accelerator="cpu",
    devices=1,
    include_training_callbacks=False,
    logger=False,
    enable_progress_bar=True,
)

print("=" * 60)
print("RF-DETR MEDIUM - ACTUAL 1 EPOCH TRAINING")
print("=" * 60)
print("Device: CPU")
print("Batch size: 1")
print("Epochs: 1")
print("Dataset: RDD2022")
print("=" * 60)

start = time.time()

trainer.fit(module, datamodule)

elapsed = time.time() - start

print("\n" + "=" * 60)
print("TRAINING COMPLETE")
print("=" * 60)
print(f"Time: {elapsed / 3600:.2f} hours")
print(f"Time: {elapsed / 60:.2f} minutes")
print(f"Output: {OUTPUT_DIR}")