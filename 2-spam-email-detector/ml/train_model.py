import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from services.training_service import TrainingService


if __name__ == "__main__":
    trainer = TrainingService()
    result = trainer.train_model()
    print(result)
