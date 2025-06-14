import logging
from dataclasses import dataclass

from .models.base_model import BaseModel
from .models.lightgbm import LightGBMModel
from .models.sgd_classifier import SGDClassifierModel
from .schema import Schema

logger = logging.getLogger(__name__)


@dataclass
class ModelConfig:
    name: str
    model_class: BaseModel
    schemas: list[Schema]
    target: str
    train_interval_days: int
    lookback_days: int
    test_valid_ratio: dict[str, float]

    @property
    def feature_columns(self) -> list[str]:
        return [schema.name for schema in self.schemas]


model_configs = [
    ModelConfig(
        name="sgd_classifier_ctr",
        model_class=SGDClassifierModel(
            is_optuna=True, args=dict(max_iter=1000, loss="log_loss", penalty="l2", random_state=42)
        ),
        schemas=[
            Schema(name="impression_hour", dtype="int", null_value=-1),
            Schema(name="impression_day", dtype="int", null_value=-1),
            Schema(name="impression_weekday", dtype="int", null_value=-1),
            Schema(name="user_id", dtype="int", null_value=-1),
            Schema(name="app_code", dtype="int", null_value=-1),
            Schema(name="os_version", dtype="str", null_value="null"),
            Schema(name="is_4g", dtype="int", null_value=-1),
            Schema(name="previous_impression_count", dtype="int", null_value=-1),
            Schema(name="previous_view_count", dtype="int", null_value=-1),
            Schema(name="item_id", dtype="int", null_value=-1),
            Schema(name="device_type", dtype="str", null_value="null"),
            Schema(name="item_price", dtype="int", null_value=-1),
            Schema(name="category_1", dtype="int", null_value=-1),
            Schema(name="category_2", dtype="int", null_value=-1),
            Schema(name="category_3", dtype="int", null_value=-1),
            Schema(name="product_type", dtype="int", null_value=-1),
        ],
        target="is_click",
        train_interval_days=28,
        lookback_days=7,
        test_valid_ratio={"test_size": 0.2, "valid_size": 0.1},
    ),
    ModelConfig(
        name="lightgbm_ctr",
        model_class=LightGBMModel(args=dict(num_leaves=31, objective="binary")),
        schemas=[
            Schema(name="impression_hour", dtype="int", null_value=-1),
            Schema(name="impression_day", dtype="int", null_value=-1),
            Schema(name="impression_weekday", dtype="int", null_value=-1),
            Schema(name="user_id", dtype="category", null_value=-1),
            Schema(name="app_code", dtype="category", null_value=-1),
            Schema(name="os_version", dtype="category", null_value="null"),
            Schema(name="is_4g", dtype="int", null_value=-1),
            Schema(name="previous_impression_count", dtype="int", null_value=-1),
            Schema(name="previous_view_count", dtype="int", null_value=-1),
            Schema(name="item_id", dtype="category", null_value=-1),
            Schema(name="device_type", dtype="category", null_value="null"),
            Schema(name="item_price", dtype="int", null_value=-1),
            Schema(name="category_1", dtype="category", null_value=-1),
            Schema(name="category_2", dtype="category", null_value=-1),
            Schema(name="category_3", dtype="category", null_value=-1),
            Schema(name="product_type", dtype="category", null_value=-1),
        ],
        target="is_click",
        train_interval_days=28,
        lookback_days=7,
        test_valid_ratio={"test_size": 0.2, "valid_size": 0.1},
    ),
]


def get_model_config(model_name: str) -> ModelConfig:
    for model_config in model_configs:
        if model_config.name == model_name:
            return model_config
    raise ValueError(f"Invalid model name: {model_name}")
