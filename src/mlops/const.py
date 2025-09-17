from typing import Final

# Terraform Applyで作成したAWSリソースの値を設定する
MODEL_S3_BUCKET: Final = ""
FEATURE_S3_BUCKET: Final = ""
GLUE_DATABASE: Final = "mlops_db"
FEATURE_DYNAMODB_TABLE: Final = "mlops-impression-feature"
MODEL_REGISTRY_DYNAMODB_TABLE: Final = "mlops-model-registry"
PUBLIC_SUBNET_1A: Final = ""
TRAIN_SECURITY_GROUP: Final = ""
